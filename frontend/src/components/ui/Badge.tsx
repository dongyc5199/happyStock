/**
 * Badge Component - Display percentage changes with automatic color variants
 * 
 * Supports auto color selection based on positive/negative values
 */

import React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps {
  /** Percentage value (e.g., 5.23 for +5.23%) */
  value: number;
  /** Color variant - 'auto' selects based on value sign */
  variant?: 'red' | 'green' | 'gray' | 'auto';
  /** Badge size */
  size?: 'sm' | 'md' | 'lg';
  /** Additional CSS classes */
  className?: string;
  /** Show plus sign for positive values */
  showPlus?: boolean;
  /** Number of decimal places */
  decimals?: number;
}

/**
 * Badge component for displaying percentage changes
 * 
 * @example
 * ```tsx
 * <Badge value={5.23} variant="auto" /> // Green with +5.23%
 * <Badge value={-2.45} variant="auto" /> // Red with -2.45%
 * <Badge value={0} variant="gray" /> // Gray with 0.00%
 * ```
 */
export function Badge({
  value,
  variant = 'auto',
  size = 'md',
  className,
  showPlus = true,
  decimals = 2,
}: BadgeProps) {
  // Determine effective variant
  const effectiveVariant = variant === 'auto' 
    ? value > 0 
      ? 'green' 
      : value < 0 
        ? 'red' 
        : 'gray'
    : variant;

  // Size classes
  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-2 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  // Variant classes
  const variantClasses = {
    red: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    green: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    gray: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400',
  };

  // Format value
  const formattedValue = value.toFixed(decimals);
  const displayValue = value > 0 && showPlus 
    ? `+${formattedValue}%` 
    : `${formattedValue}%`;

  return (
    <span
      className={cn(
        'inline-flex items-center justify-center rounded-md font-medium transition-colors',
        sizeClasses[size],
        variantClasses[effectiveVariant],
        className
      )}
    >
      {displayValue}
    </span>
  );
}
