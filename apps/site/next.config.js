// @ts-check
const { composePlugins, withNx } = require('@nx/next');
const { execSync } = require('child_process');

// Get version at config time
function getBuildVersion() {
  // Try env var first (set by build.sh or Render)
  if (process.env.NEXT_PUBLIC_RENDER_GIT_COMMIT) {
    return process.env.NEXT_PUBLIC_RENDER_GIT_COMMIT;
  }
  // Try RENDER_GIT_COMMIT directly
  if (process.env.RENDER_GIT_COMMIT) {
    return process.env.RENDER_GIT_COMMIT.slice(0, 7);
  }
  // Try git (use -C to find repo root)
  try {
    // Try current dir, then parent dirs
    const result = execSync('git rev-parse --short HEAD 2>/dev/null || git -C ../.. rev-parse --short HEAD 2>/dev/null', {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe']
    }).trim();
    if (result) return result;
  } catch {
    // Git not available
  }
  // Fallback to timestamp
  const d = new Date();
  return `b${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}${String(d.getHours()).padStart(2,'0')}${String(d.getMinutes()).padStart(2,'0')}`;
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
