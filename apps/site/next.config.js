// @ts-check
const { composePlugins, withNx } = require('@nx/next');

/**
 * @type {import('@nx/next/plugins/with-nx').WithNxOptions}
 **/
const nextConfig = {
  nx: {
    svgr: false,
  },
  output: 'export',
  reactStrictMode: true,
  transpilePackages: [
    '@sql2ai/ui-components',
    '@sql2ai/shared-types',
  ],
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
  env: {
    NEXT_PUBLIC_RENDER_GIT_COMMIT: process.env.NEXT_PUBLIC_RENDER_GIT_COMMIT || 'dev',
  },
};

const plugins = [withNx];

module.exports = composePlugins(...plugins)(nextConfig);
