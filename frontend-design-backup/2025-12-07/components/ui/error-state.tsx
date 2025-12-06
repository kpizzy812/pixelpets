'use client';

import { Button } from './button';
import { Icon, type IconName } from './icon';

interface ErrorStateProps {
  title?: string;
  message?: string;
  icon?: IconName;
  onRetry?: () => void;
  retryLabel?: string;
}

export function ErrorState({
  title = 'Something went wrong',
  message = 'An error occurred. Please try again.',
  icon = 'error',
  onRetry,
  retryLabel = 'Try Again',
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <Icon name={icon} size={48} className="text-[#64748b] mb-4" />
      <h3 className="text-lg font-semibold text-[#f1f5f9] mb-2">{title}</h3>
      <p className="text-sm text-[#64748b] mb-6 max-w-xs">{message}</p>
      {onRetry && (
        <Button variant="cyan" onClick={onRetry}>
          {retryLabel}
        </Button>
      )}
    </div>
  );
}

// Network Error
export function NetworkError({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorState
      icon="network"
      title="No Connection"
      message="Please check your internet connection and try again."
      onRetry={onRetry}
    />
  );
}

// Server Error
export function ServerError({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorState
      icon="maintenance"
      title="Server Error"
      message="Our servers are having issues. Please try again later."
      onRetry={onRetry}
    />
  );
}

// Empty State
interface EmptyStateProps {
  title: string;
  message: string;
  icon?: IconName;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function EmptyState({
  title,
  message,
  icon = 'empty',
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <Icon name={icon} size={48} className="text-[#64748b] mb-4" />
      <h3 className="text-lg font-semibold text-[#f1f5f9] mb-2">{title}</h3>
      <p className="text-sm text-[#64748b] mb-6 max-w-xs">{message}</p>
      {action && (
        <Button variant="lime" onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </div>
  );
}

// Inline Error Message
interface InlineErrorProps {
  message: string;
  onDismiss?: () => void;
}

export function InlineError({ message, onDismiss }: InlineErrorProps) {
  return (
    <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3">
      <Icon name="warning" size={18} className="text-red-400" />
      <span className="text-sm text-red-400 flex-1">{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-400 hover:text-red-300 transition-colors"
        >
          <Icon name="close" size={14} />
        </button>
      )}
    </div>
  );
}

// Success Message
interface SuccessMessageProps {
  message: string;
  onDismiss?: () => void;
}

export function SuccessMessage({ message, onDismiss }: SuccessMessageProps) {
  return (
    <div className="p-3 rounded-xl bg-[#c7f464]/10 border border-[#c7f464]/30 flex items-center gap-3">
      <Icon name="check" size={18} className="text-[#c7f464]" />
      <span className="text-sm text-[#c7f464] flex-1">{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-[#c7f464] hover:text-[#d4f87a] transition-colors"
        >
          <Icon name="close" size={14} />
        </button>
      )}
    </div>
  );
}
