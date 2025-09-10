import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BatchForm } from '@/components/BatchForm';
import { ResultsCard } from '@/components/ResultsCard';
import { Toaster } from '@/components/ui/toaster';
import { Calculator, Leaf } from 'lucide-react';

function App() {
  const [calculationResults, setCalculationResults] = useState<any>(null);
  const [currentBatchId, setCurrentBatchId] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto py-8">
        <header className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-green-600 rounded-lg">
              <Calculator className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">
              ESG Calculator Oracle
            </h1>
            <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded-full">
              v0.1.0
            </span>
          </div>
          <p className="text-gray-600 flex items-center gap-2">
            <Leaf className="h-4 w-4" />
            ISO 14083 compliant emissions calculator for GreenStemGlobal
          </p>
        </header>

        <Tabs defaultValue="batch" className="space-y-4">
          <TabsList className="grid w-full grid-cols-2 max-w-md">
            <TabsTrigger value="batch">Batch Entry</TabsTrigger>
            <TabsTrigger value="results">Results</TabsTrigger>
          </TabsList>

          <TabsContent value="batch" className="space-y-4">
            <BatchForm 
              onCalculate={(results, batchId) => {
                setCalculationResults(results);
                setCurrentBatchId(batchId);
              }}
            />
          </TabsContent>

          <TabsContent value="results" className="space-y-4">
            {calculationResults ? (
              <ResultsCard 
                results={calculationResults} 
                batchId={currentBatchId}
              />
            ) : (
              <div className="text-center py-12 bg-white rounded-lg shadow">
                <p className="text-gray-500">
                  No calculation results yet. Create and calculate a batch first.
                </p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
      <Toaster />
    </div>
  );
}

export default App;