const path = require('path')

/** @type {import('next').NextConfig} */
const nextConfig = {
  outputFileTracingRoot: path.resolve(__dirname),
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  webpack: (config, { isServer }) => {
    // Force the alias resolution
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(process.cwd(), 'src'),
    }
    
    // Add src to module resolution
    config.resolve.modules = [
      path.resolve(process.cwd(), 'src'),
      'node_modules'
    ]
    
    // Ensure extensions are resolved
    config.resolve.extensions = ['.ts', '.tsx', '.js', '.jsx', '.json']
    
    return config
  },
}

module.exports = nextConfig
