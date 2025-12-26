#!/bin/bash
# Build script for SQL2.AI site
# Sets NEXT_PUBLIC_RENDER_GIT_COMMIT from Render env or git

echo "=== Build Environment ==="
echo "RENDER_GIT_COMMIT: ${RENDER_GIT_COMMIT:-not set}"
echo "RENDER: ${RENDER:-not set}"
echo "PWD: $PWD"

# Try multiple sources for version
if [ -n "$RENDER_GIT_COMMIT" ]; then
  VERSION="${RENDER_GIT_COMMIT:0:7}"
elif [ -d .git ]; then
  VERSION=$(git rev-parse --short HEAD 2>/dev/null || echo "nogit")
else
  VERSION="b$(date +%m%d%H%M)"
fi

echo "VERSION: $VERSION"

# Write to .env.local for Next.js to pick up
echo "NEXT_PUBLIC_RENDER_GIT_COMMIT=$VERSION" > apps/site/.env.local
cat apps/site/.env.local

echo "=== Starting NX Build ==="
NODE_OPTIONS="--max-old-space-size=1536" npx nx build site --configuration=production --skip-nx-cache
