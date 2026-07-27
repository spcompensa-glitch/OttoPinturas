import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@splinetool/react-spline"],
  images: {
    qualities: [70, 75, 80, 85],
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8002/api/:path*',
      },
    ]
  },
};

export default nextConfig;
