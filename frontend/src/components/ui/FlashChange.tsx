/**
 * FlashChange Component - Animated flash effect for value changes
 * 
 * Highlights price/value changes with a brief color flash
 * Used in real-time data displays
 */

import React, { useEffect, useState, useRef } from 'react';

export interface FlashChangeProps {
  /** Value to display */
  value: number | string;
  /** CSS class for the element */
  className?: string;
  /** Flash duration in milliseconds */
  flashDuration?: number;
  /** Flash color for increase (default: red for stock prices) */
  increaseColor?: string;
  /** Flash color for decrease (default: green for stock prices) */
  decreaseColor?: string;
  /** Format function for display */
  format?: (value: number | string) => string;
  /** Children to wrap (if provided, value is ignored) */
  children?: React.ReactNode;
}

/**
 * Flash animation component for highlighting changes
 * 
 * @example
 * ```tsx
 * <FlashChange value={stock.current_price} format={formatPrice} />
 * <FlashChange value={stock.change_pct}>
 *   <Badge value={stock.change_pct} />
 * </FlashChange>
 * ```
 */
export function FlashChange({
  value,
  className = '',
  flashDuration = 200,
  increaseColor = 'bg-red-100 dark:bg-red-900/30',
  decreaseColor = 'bg-green-100 dark:bg-green-900/30',
  format,
  children,
}: FlashChangeProps) {
  const [flashClass, setFlashClass] = useState('');
  const prevValueRef = useRef<number | string>(value);
  const timeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);

  useEffect(() => {
    const prevValue = prevValueRef.current;
    const currentValue = value;

    // Skip first render
    if (prevValue === currentValue) {
      return;
    }

    // Determine flash direction
    let flash = '';
    if (typeof currentValue === 'number' && typeof prevValue === 'number') {
      if (currentValue > prevValue) {
        flash = increaseColor;
      } else if (currentValue < prevValue) {
        flash = decreaseColor;
      }
    }

    // Apply flash
    if (flash) {
      setFlashClass(flash);
      
      // Clear previous timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      // Remove flash after duration
      timeoutRef.current = setTimeout(() => {
        setFlashClass('');
      }, flashDuration);
    }

    // Update ref
    prevValueRef.current = currentValue;

    // Cleanup
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [value, flashDuration, increaseColor, decreaseColor]);

  const displayValue = children || (format ? format(value) : value);

  return (
    <span
      className={`
        inline-block transition-colors duration-200 rounded px-1
        ${flashClass}
        ${className}
      `}
    >
      {displayValue}
    </span>
  );
}
