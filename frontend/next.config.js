/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Disable SSR for Monaco Editor compatibility
  experimental: {
    // Enable server actions for form handling
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  // Output standalone for Docker deployment
  output: 'standalone',
}

module.exports = nextConfig
