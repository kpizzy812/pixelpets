import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const backendUrl = process.env.BACKEND_URL && !process.env.BACKEND_URL.startsWith('http')
  ? `https://${process.env.BACKEND_URL}`
  : process.env.BACKEND_URL;

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || backendUrl || 'http://localhost:8000',
  },
};

const withNextIntl = createNextIntlPlugin("./i18n/request.ts");

export default withNextIntl(nextConfig);
