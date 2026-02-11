import type { NextConfig } from "next";

const backendUrl = process.env.BACKEND_URL && !process.env.BACKEND_URL.startsWith('http')
  ? `https://${process.env.BACKEND_URL}`
  : process.env.BACKEND_URL;

const nextConfig: NextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || backendUrl || 'http://localhost:8000',
  },
};

export default nextConfig;
