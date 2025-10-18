'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CheckCircle, XCircle, Server } from 'lucide-react';

interface ApiTestResult {
  endpoint: string;
  status: 'success' | 'error' | 'loading';
  message: string;
  data?: any;
}

export default function ApiTest() {
  const [results, setResults] = useState<ApiTestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const testEndpoint = async (endpoint: string, testFn: () => Promise<any>) => {
    setResults(prev => [...prev, { endpoint, status: 'loading', message: 'Testing...' }]);
    
    try {
      const response = await testFn();
      setResults(prev => 
        prev.map(r => 
          r.endpoint === endpoint 
            ? { endpoint, status: 'success', message: 'Success', data: response }
            : r
        )
      );
    } catch (error) {
      let errorMessage = 'Unknown error';
      
      if (error instanceof Error) {
        if (error.message.includes('Backend server is not running')) {
          errorMessage = 'Backend server not running on port 5000';
        } else if (error.message.includes('Failed to fetch')) {
          errorMessage = 'Cannot connect to backend server';
        } else {
          errorMessage = error.message;
        }
      }
      
      setResults(prev => 
        prev.map(r => 
          r.endpoint === endpoint 
            ? { endpoint, status: 'error', message: errorMessage }
            : r
        )
      );
    }
  };

  const runAllTests = async () => {
    setIsRunning(true);
    setResults([]);

    const tests = [
      {
        endpoint: 'Health Check',
        testFn: () => apiClient.healthCheck()
      },
      {
        endpoint: 'Sources API',
        testFn: () => apiClient.getSources({ page: 1, per_page: 5 })
      },
      {
        endpoint: 'Content API',
        testFn: () => apiClient.getContent({ page: 1, per_page: 5 })
      },
      {
        endpoint: 'OSINT API',
        testFn: () => apiClient.getOSINTInfo()
      },
      {
        endpoint: 'Dashboard API',
        testFn: () => apiClient.getDashboardInfo()
      }
    ];

    for (const test of tests) {
      await testEndpoint(test.endpoint, test.testFn);
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    setIsRunning(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'loading':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      default:
        return <Server className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return <Badge variant="default" className="bg-green-500">Success</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      case 'loading':
        return <Badge variant="secondary">Loading</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            API Connection Test
          </CardTitle>
          <CardDescription>
            Test the connection between the frontend and Flask backend
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button 
            onClick={runAllTests} 
            disabled={isRunning}
            className="w-full"
          >
            {isRunning ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Running Tests...
              </>
            ) : (
              'Run API Tests'
            )}
          </Button>
        </CardContent>
      </Card>

      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Test Results</h3>
          {results.map((result, index) => (
            <Card key={index}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(result.status)}
                    <span className="font-medium">{result.endpoint}</span>
                  </div>
                  {getStatusBadge(result.status)}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-2">
                  {result.message}
                </p>
                {result.status === 'success' && result.data && (
                  <Alert>
                    <AlertDescription className="text-xs">
                      <pre className="whitespace-pre-wrap">
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {results.length > 0 && !isRunning && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Summary:</span>
              <div className="flex gap-2">
                <Badge variant="outline">
                  Total: {results.length}
                </Badge>
                <Badge variant="default" className="bg-green-500">
                  Success: {results.filter(r => r.status === 'success').length}
                </Badge>
                <Badge variant="destructive">
                  Errors: {results.filter(r => r.status === 'error').length}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 
