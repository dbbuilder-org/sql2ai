#!/bin/bash
# Build script for SQL2.AI site
# Sets NEXT_PUBLIC_RENDER_GIT_COMMIT from Render env or git

echo "Debug: RENDER_GIT_COMMIT=$RENDER_GIT_COMMIT"
echo "Debug: RENDER=$RENDER"

# Try multiple sources for version
if [ -n "$RENDER_GIT_COMMIT" ]; then
  VERSION="${RENDER_GIT_COMMIT:0:7}"
elif [ -d .git ]; then
  VERSION=$(git rev-parse --short HEAD 2>/dev/null)
elif [ -n "$RENDER_GIT_BRANCH" ]; then
  VERSION="$RENDER_GIT_BRANCH"
else
  VERSION="build-$(date +%m%d%H%M)"
fi

export NEXT_PUBLIC_RENDER_GIT_COMMIT="$VERSION"
echo "Building with version: $NEXT_PUBLIC_RENDER_GIT_COMMIT"

NODE_OPTIONS="--max-old-space-size=1536" npx nx build site --configuration=production
