'use client';

import { Toaster } from 'react-hot-toast';

export function ToastProvider() {
  return (
    <Toaster
      position="top-center"
      toastOptions={{
        duration: 3000,
        style: {
          background: '#0d1220',
          color: '#f1f5f9',
          border: '1px solid rgba(30, 41, 59, 0.5)',
          borderRadius: '16px',
          padding: '12px 16px',
          fontSize: '14px',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.5)',
        },
        success: {
          iconTheme: {
            primary: '#c7f464',
            secondary: '#0d1220',
          },
          style: {
            borderColor: 'rgba(199, 244, 100, 0.3)',
          },
        },
        error: {
          iconTheme: {
            primary: '#ef4444',
            secondary: '#0d1220',
          },
          style: {
            borderColor: 'rgba(239, 68, 68, 0.3)',
          },
        },
        loading: {
          iconTheme: {
            primary: '#00f5d4',
            secondary: '#0d1220',
          },
        },
      }}
    />
  );
}
