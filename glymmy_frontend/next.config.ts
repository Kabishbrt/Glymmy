import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Required for the multi-stage Docker build (produces .next/standalone/server.js)
  output: "standalone",
  allowedDevOrigins: ["127.0.0.1", "localhost", "192-168-1-78.sslip.io", "192-168-1-78.sslip.io:8080", "rzrfk-2400-1a00-4b26-7d8b-7da8-40eb-c76e-9c3a.run.pinggy-free.link"],
  async rewrites() {
    return [
      { source: "/api/v1/:path*", destination: "http://127.0.0.1:8000/api/v1/:path*" },
      { source: "/health", destination: "http://127.0.0.1:8000/health" },
      { source: "/graphql", destination: "http://127.0.0.1:8000/graphql" }
    ];
  },
};

export default nextConfig;
