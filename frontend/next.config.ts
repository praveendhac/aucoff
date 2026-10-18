import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Image optimisation needs `sharp`, whose libvips is LGPL (constitution LIC-2); a stub replaces it.
  images: { unoptimized: true },
};

export default nextConfig;
