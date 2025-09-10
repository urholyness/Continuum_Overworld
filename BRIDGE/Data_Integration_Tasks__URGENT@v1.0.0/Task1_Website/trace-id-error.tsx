// File: Agora/Site--GreenStemGlobal__PROD@v1.0.0/src/app/trace/[id]/error.tsx
// Task 1: Error boundary for trace detail page

'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Trace page error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-light to-white flex items-center justify-center">
      <div className="text-center max-w-md mx-auto px-4">
        <div className="mb-8">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg 
              className="w-10 h-10 text-red-600" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-soil mb-2">
            Trace Data Temporarily Unavailable
          </h2>
          <p className="text-gray-600 mb-6">
            We're having trouble loading the trace information. This might be due to network issues or the data being updated.
          </p>
        </div>
        
        <div className="space-y-3">
          <button
            onClick={reset}
            className="w-full px-6 py-3 bg-leaf text-white rounded-lg hover:bg-green-600 transition-colors font-medium"
          >
            Try Again
          </button>
          
          <button
            onClick={() => window.history.back()}
            className="w-full px-6 py-3 bg-gray-200 text-soil rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Go Back
          </button>
        </div>
        
        {process.env.NODE_ENV === 'development' && error.digest && (
          <p className="text-xs text-gray-500 mt-4">
            Error ID: {error.digest}
          </p>
        )}
      </div>
    </div>
  );
}
