'use client';

import { ReactNode, useEffect, useState } from 'react';
import { WebSocketErrorFallback } from '@/components/ui/ErrorBoundary';

interface WebSocketErrorWrapperProps {
  children: ReactNode;
  wsEnabled?: boolean;
}

/**
 * Wrapper component that monitors WebSocket connection status
 * and displays an error fallback when connection is lost
 */
export function WebSocketErrorWrapper({ children, wsEnabled = true }: WebSocketErrorWrapperProps) {
  const [hasError, setHasError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    if (!wsEnabled) return;

    // Monitor WebSocket connection status
    // This is a placeholder - integrate with actual WebSocket context
    const checkConnection = () => {
      // TODO: Check actual WebSocket connection status from context
      // For now, just use a simple timeout to detect connection issues
      const timeout = setTimeout(() => {
        // Connection check logic would go here
      }, 5000);

      return () => clearTimeout(timeout);
    };

    return checkConnection();
  }, [wsEnabled, retryCount]);

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    setHasError(false);
    // Trigger reconnection
    window.location.reload();
  };

  if (hasError) {
    return (
      <div onClick={handleRetry}>
        <WebSocketErrorFallback />
      </div>
    );
  }

  return <>{children}</>;
}
