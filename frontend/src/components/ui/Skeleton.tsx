import React from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}

export function Skeleton({
  className = '',
  variant = 'rectangular',
  width,
  height,
  animation = 'pulse',
}: SkeletonProps) {
  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  };

  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer',
    none: '',
  };

  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  return (
    <div
      className={`bg-gray-200 dark:bg-gray-700 ${variantClasses[variant]} ${animationClasses[animation]} ${className}`}
      style={style}
    />
  );
}

// Market Overview Skeleton
export function MarketOverviewSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <Skeleton width={120} height={24} className="rounded" />
        <Skeleton width={80} height={20} className="rounded-full" />
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        {Array.from({ length: 7 }).map((_, i) => (
          <div key={i} className="text-center">
            <Skeleton width="100%" height={16} className="mb-2" />
            <Skeleton width={60} height={28} className="mx-auto" />
          </div>
        ))}
      </div>
    </div>
  );
}

// Hot Stock List Skeleton
export function HotStockListSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} width={80} height={32} className="rounded-lg" />
          ))}
        </div>
      </div>
      <div className="divide-y divide-gray-100 dark:divide-gray-700">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="p-4 flex items-center justify-between">
            <div className="flex-1">
              <Skeleton width={100} height={20} className="mb-2" />
              <Skeleton width={60} height={16} />
            </div>
            <div className="flex items-center gap-4">
              <Skeleton width={80} height={24} />
              <Skeleton width={60} height={20} className="rounded-full" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Core Indices Skeleton
export function CoreIndicesSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton width={120} height={28} className="rounded" />
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-5 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <Skeleton width={100} height={20} className="mb-2" />
                <Skeleton width={60} height={14} />
              </div>
              <Skeleton width={60} height={24} className="rounded-full" />
            </div>
            <div className="flex items-baseline justify-between">
              <Skeleton width={100} height={32} />
              <Skeleton width={80} height={20} className="rounded" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Quick Start Guide Skeleton
export function QuickStartGuideSkeleton() {
  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900 rounded-xl p-8 border border-blue-100 dark:border-gray-700">
      <Skeleton width={200} height={32} className="mb-6 mx-auto" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="text-center">
            <Skeleton width={48} height={48} variant="circular" className="mx-auto mb-4" />
            <Skeleton width={120} height={20} className="mx-auto mb-2" />
            <Skeleton width="100%" height={40} className="mb-2" />
          </div>
        ))}
      </div>
      <Skeleton width={160} height={48} className="mx-auto rounded-xl" />
    </div>
  );
}

// Feature Showcase Skeleton
export function FeatureShowcaseSkeleton() {
  return (
    <div>
      <Skeleton width={200} height={32} className="mb-8 mx-auto" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Array.from({ length: 3 }).map((_, i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700"
          >
            <Skeleton width={48} height={48} variant="circular" className="mb-4" />
            <Skeleton width={150} height={24} className="mb-4" />
            <Skeleton width="100%" height={60} className="mb-6" />
            <div className="space-y-2 mb-6">
              {Array.from({ length: 4 }).map((_, j) => (
                <Skeleton key={j} width="100%" height={16} />
              ))}
            </div>
            <Skeleton width={120} height={40} className="rounded-lg" />
          </div>
        ))}
      </div>
    </div>
  );
}

// Education Footer Skeleton
export function EducationFooterSkeleton() {
  return (
    <div className="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-20">
      <div className="container mx-auto px-4">
        <Skeleton width={300} height={40} className="mx-auto mb-4" />
        <Skeleton width={400} height={20} className="mx-auto mb-12" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="space-y-4">
              <Skeleton width={150} height={24} className="mb-6" />
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, j) => (
                  <Skeleton key={j} width="100%" height={80} className="rounded-lg" />
                ))}
              </div>
            </div>
          ))}
        </div>
        <Skeleton width={200} height={56} className="mx-auto rounded-xl" />
      </div>
    </div>
  );
}
