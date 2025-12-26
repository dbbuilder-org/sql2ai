// @ts-check
const { composePlugins, withNx } = require('@nx/next');
const { execSync } = require('child_process');

// Get version at config time
function getBuildVersion() {
  // Try env var first (set by build.sh or Render)
  if (process.env.NEXT_PUBLIC_RENDER_GIT_COMMIT) {
    return process.env.NEXT_PUBLIC_RENDER_GIT_COMMIT;
  }
  // Try git
  try {
    return execSync('git rev-parse --short HEAD', { encoding: 'utf-8' }).trim();
  } catch {
    // Fallback to timestamp
    const d = new Date();
    return `b${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}${String(d.getHours()).padStart(2,'0')}${String(d.getMinutes()).padStart(2,'0')}`;
  }
}

const buildVersion = getBuildVersion();
console.log('Build version:', buildVersion);

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
    NEXT_PUBLIC_RENDER_GIT_COMMIT: buildVersion,
  },
};

const plugins = [withNx];

module.exports = composePlugins(...plugins)(nextConfig);
