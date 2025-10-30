/**
 * useStockSparkline Hook - Generate sparkline data for stock price trends
 * 
 * Creates a simplified price trend visualization (last 20 data points)
 * Used for quick visual indicators in hot stock lists
 */

import { useMemo } from 'react';
import type { HotStock } from './useHotStocks';

export interface SparklinePoint {
  x: number;
  y: number;
}

export interface SparklineData {
  points: SparklinePoint[];
  min: number;
  max: number;
  change: number; // Overall change from first to last point
  trend: 'up' | 'down' | 'flat';
}

/**
 * Generate sparkline data from stock information
 * 
 * @param stock - Stock data
 * @param dataPoints - Number of points to generate (default: 20)
 * @returns Sparkline data for rendering
 * 
 * @example
 * ```tsx
 * const sparkline = useStockSparkline(stock);
 * if (sparkline) {
 *   return <Sparkline data={sparkline} />;
 * }
 * ```
 */
export function useStockSparkline(
  stock: HotStock | null,
  dataPoints: number = 20
): SparklineData | null {
  return useMemo(() => {
    if (!stock) return null;

    // Generate simulated intraday price movement based on current data
    // In production, this would come from actual historical tick data
    const current_price = stock.current_price;
    const previous_close = stock.previous_close;
    
    // Simulate open/high/low based on current price and change
    const open_price = previous_close;
    
    // Estimate high/low based on volatility
    const price_range = Math.abs(current_price - open_price);
    const high_price = Math.max(current_price, open_price) + price_range * 0.3;
    const low_price = Math.min(current_price, open_price) - price_range * 0.3;
    
    // Create a realistic price path from open to current
    const points: SparklinePoint[] = [];
    const range = high_price - low_price;
    
    // Starting point
    points.push({ x: 0, y: open_price });
    
    // Generate intermediate points with some randomness
    // that respects high/low bounds and trends toward current price
    let currentY = open_price;
    const targetY = current_price;
    const stepSize = (targetY - open_price) / (dataPoints - 1);
    
    for (let i = 1; i < dataPoints - 1; i++) {
      // Add trend component
      currentY += stepSize;
      
      // Add some noise but stay within bounds
      const noise = (Math.random() - 0.5) * range * 0.3;
      let nextY = currentY + noise;
      
      // Constrain to high/low bounds
      nextY = Math.max(low_price, Math.min(high_price, nextY));
      
      points.push({ x: i, y: nextY });
      currentY = nextY;
    }
    
    // Final point is current price
    points.push({ x: dataPoints - 1, y: current_price });
    
    // Calculate min/max for scaling
    const yValues = points.map(p => p.y);
    const min = Math.min(...yValues);
    const max = Math.max(...yValues);
    
    // Calculate overall change
    const change = ((current_price - open_price) / open_price) * 100;
    
    // Determine trend
    let trend: 'up' | 'down' | 'flat';
    if (change > 0.1) {
      trend = 'up';
    } else if (change < -0.1) {
      trend = 'down';
    } else {
      trend = 'flat';
    }
    
    return {
      points,
      min,
      max,
      change,
      trend,
    };
  }, [stock, dataPoints]);
}

/**
 * Convert sparkline data to SVG path string
 * 
 * @param data - Sparkline data
 * @param width - SVG width
 * @param height - SVG height
 * @param padding - Padding around the line
 * @returns SVG path 'd' attribute string
 */
export function sparklineToPath(
  data: SparklineData,
  width: number = 60,
  height: number = 30,
  padding: number = 2
): string {
  const { points, min, max } = data;
  
  if (points.length === 0) return '';
  
  const xScale = (width - padding * 2) / (points.length - 1);
  const yRange = max - min || 1; // Avoid division by zero
  const yScale = (height - padding * 2) / yRange;
  
  // Convert points to SVG coordinates (Y is inverted in SVG)
  const svgPoints = points.map((point) => {
    const x = point.x * xScale + padding;
    const y = height - ((point.y - min) * yScale + padding);
    return { x, y };
  });
  
  // Build path string
  let path = `M ${svgPoints[0].x},${svgPoints[0].y}`;
  
  for (let i = 1; i < svgPoints.length; i++) {
    // Use smooth curves for better visual
    if (i === 1) {
      path += ` L ${svgPoints[i].x},${svgPoints[i].y}`;
    } else {
      // Quadratic bezier curve for smoothing
      const prevPoint = svgPoints[i - 1];
      const currentPoint = svgPoints[i];
      const cpX = (prevPoint.x + currentPoint.x) / 2;
      path += ` Q ${cpX},${prevPoint.y} ${currentPoint.x},${currentPoint.y}`;
    }
  }
  
  return path;
}
