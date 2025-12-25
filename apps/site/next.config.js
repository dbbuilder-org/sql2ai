// @ts-check
const { composePlugins, withNx } = require('@nx/next');

/**
 * @type {import('@nx/next/plugins/with-nx').WithNxOptions}
 **/
const nextConfig = {
  nx: {
    svgr: false,
  },
  output: 'standalone',
  reactStrictMode: true,
  transpilePackages: [
    '@sql2ai/ui-components',
    '@sql2ai/shared-types',
  ],
  images: {
    domains: ['sql2.ai'],
  },
};

const plugins = [withNx];

module.exports = composePlugins(...plugins)(nextConfig);
