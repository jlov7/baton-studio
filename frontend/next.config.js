/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    optimizePackageImports: ["reactflow", "framer-motion"],
  },
};

module.exports = nextConfig;
