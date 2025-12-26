#!/bin/bash
# Build script for SQL2.AI site
# Version is computed in next.config.js at build time

echo "=== Starting Build ==="
echo "RENDER_GIT_COMMIT: ${RENDER_GIT_COMMIT:-not set}"

# Pass Render's commit SHA if available
if [ -n "$RENDER_GIT_COMMIT" ]; then
  export NEXT_PUBLIC_RENDER_GIT_COMMIT="${RENDER_GIT_COMMIT:0:7}"
fi

NODE_OPTIONS="--max-old-space-size=1536" npx nx build site --configuration=production --skip-nx-cache
