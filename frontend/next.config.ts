import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    // Disable ESLint during builds for Docker
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Disable TypeScript errors during builds for Docker (optional)
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
