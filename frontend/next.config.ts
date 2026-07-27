import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@splinetool/react-spline"],
  images: {
    qualities: [70, 75, 80, 85],
    unoptimized: true,
  },
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8002";
    // Remover a barra final, se houver
    const targetUrl = backendUrl.replace(/\/$/, "");
    return [
      {
        source: '/api/:path*',
        destination: `${targetUrl}/api/:path*`,
      },
    ]
  },
};

export default nextConfig;
