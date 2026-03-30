export const config = {
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
    timeout: 10000, // 10 seconds
  },
  app: {
    name: 'Cyber Intelligence Platform',
    version: '1.0.0',
  },
} as const; 