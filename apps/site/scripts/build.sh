#!/bin/bash
# Build script for SQL2.AI site
# Sets NEXT_PUBLIC_RENDER_GIT_COMMIT from Render env or git

if [ -n "$RENDER_GIT_COMMIT" ]; then
  export NEXT_PUBLIC_RENDER_GIT_COMMIT="${RENDER_GIT_COMMIT:0:7}"
else
  export NEXT_PUBLIC_RENDER_GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "dev")
fi

echo "Building with version: $NEXT_PUBLIC_RENDER_GIT_COMMIT"

NODE_OPTIONS="--max-old-space-size=1536" npx nx build site --configuration=production
