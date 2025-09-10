// File: Agora/Site--GreenStemGlobal__PROD@v1.0.0/src/app/trace/[id]/loading.tsx
// Task 1: Loading state for trace detail page

export default function Loading() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-light to-white">
      <div className="container mx-auto px-4 py-16">
        <div className="animate-pulse">
          {/* Header skeleton */}
          <div className="mb-8">
            <div className="h-8 bg-gray-300 rounded w-1/3 mb-2" />
            <div className="h-5 bg-gray-200 rounded w-1/4" />
          </div>
          
          {/* Main info card skeleton */}
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <div className="h-6 bg-gray-300 rounded w-3/4 mb-4" />
                <div className="space-y-3">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="flex justify-between">
                      <div className="h-4 bg-gray-200 rounded w-1/3" />
                      <div className="h-4 bg-gray-200 rounded w-1/3" />
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <div className="h-6 bg-gray-300 rounded w-3/4 mb-4" />
                <div className="space-y-3">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="flex justify-between">
                      <div className="h-4 bg-gray-200 rounded w-1/3" />
                      <div className="h-4 bg-gray-200 rounded w-1/3" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          
          {/* Timeline skeleton */}
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <div className="h-6 bg-gray-300 rounded w-1/3 mb-6" />
            <div className="space-y-4">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="flex items-start">
                  <div className="flex-shrink-0 w-10 h-10 bg-gray-300 rounded-full" />
                  <div className="ml-4 flex-grow">
                    <div className="h-5 bg-gray-200 rounded w-1/4 mb-2" />
                    <div className="h-4 bg-gray-100 rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
