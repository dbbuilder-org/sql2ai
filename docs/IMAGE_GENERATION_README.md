# Image Generation Workflow - Overview

This directory contains all resources needed to generate marketing images for the SQL2.AI website.

## Quick Start

```bash
# 1. Check prerequisites
./tools/generate-images.sh --check

# 2. Review the specifications
cat docs/IMAGE_GENERATION_QUEUE.md

# 3. Review tool recommendations
cat docs/TOOL_RECOMMENDATIONS.md

# 4. Generate images using recommended tools (see below)

# 5. Check progress
./tools/generate-images.sh --status

# 6. Optimize generated images
./tools/generate-images.sh --optimize
```

## Files in this Workflow

### Documentation
- **`IMAGE_GENERATION_QUEUE.md`** - Complete specifications for all 7 images
  - Exact prompts for AI generation
  - Recommended dimensions
  - File naming conventions
  - Quality checklist
  - Usage locations

- **`TOOL_RECOMMENDATIONS.md`** - AI tool selection guide
  - Recommended tools: Midjourney, FLUX.1 Pro, Recraft
  - Pros/cons for our specific use case
  - Pricing and budget estimates
  - Tool selection matrix
  - Setup tips and best practices

- **`IMAGE_GENERATION_README.md`** (this file) - Workflow overview

### Tools
- **`tools/generate-images.sh`** - Workflow automation script
  - Check prerequisites
  - Track generation status
  - Optimize images
  - Interactive guide

### Directories
- **`public/images/marketing/`** - Final optimized images (for production)
- **`public/images/marketing/originals/`** - High-res backups

## Image List (7 Total)

| Priority | Filename | Tool | Used On |
|----------|----------|------|---------|
| HIGH | `hero-schema-visualization.png` | Midjourney | Homepage Hero |
| HIGH | `query-optimization-before-after.png` | FLUX.1 Pro | Homepage, Features |
| HIGH | `terminal-cli-interface.png` | FLUX.1 Pro | Homepage, Docs |
| HIGH | `lifecycle-circular-diagram.png` | Midjourney/Recraft | Homepage, Features |
| MEDIUM | `execution-plan-tree.png` | Midjourney | Features, Docs |
| MEDIUM | `cross-platform-bridge.png` | Midjourney/Recraft | Homepage, Features |
| MEDIUM | `mcp-ide-integration.png` | FLUX.1 Pro | Features |

## Recommended Tools

### Primary: Midjourney ($30/month)
- Best for: High-quality marketing images with dark themes
- Use for: Images #1, #3, #5, #7
- Setup: Join Discord, subscribe to Standard plan
- Strengths: Exceptional quality, consistent style, professional output

### Secondary: FLUX.1 Pro ($10-20/month)
- Best for: Images with code, terminal text, UI elements
- Use for: Images #2, #4, #6
- Setup: Sign up for Replicate or FAL.ai
- Strengths: Excellent text rendering, photorealistic, fast

### Optional: Recraft ($20/month)
- Best for: Vector graphics, editable SVGs
- Use for: Images #5, #7 (alternative to Midjourney)
- Setup: Sign up for Pro plan
- Strengths: Vector format, brand consistency

## Budget

- **Minimal:** ~$40-45 (Midjourney + FLUX for 1 month)
- **Recommended:** ~$70 (all three tools for flexibility)
- **Strategy:** Generate all images in one month, then cancel

## Generation Workflow

### Phase 1: Setup (Day 1)
1. Review all documentation
2. Set up tool accounts
3. Verify prerequisites with script

### Phase 2: Generation (Days 2-10)
1. Start with HIGH priority images
2. Generate 3-5 variations per image
3. Select best results
4. Download high-resolution versions
5. Save to `public/images/marketing/`

### Phase 3: Optimization (Days 11-12)
1. Run optimization script
2. Verify dimensions and quality
3. Test on actual website
4. Get team feedback

### Phase 4: Finalize (Days 13-14)
1. Make any final adjustments
2. Commit to git
3. Update Next.js components
4. Document actual prompts used
5. Cancel subscriptions if done

## Quality Standards

Every image must meet these criteria:

- ✅ Exact dimensions as specified
- ✅ Dark background (#09090f or close)
- ✅ Colors match design tokens
- ✅ Text is sharp and readable (if applicable)
- ✅ No obvious AI artifacts
- ✅ Professional, enterprise-grade appearance
- ✅ File size optimized (< 200KB ideal, < 500KB max)
- ✅ Works on both light and dark backgrounds

## Tips for Success

### Midjourney
- Use `--ar 16:9` for aspect ratios
- Use `--v 6` for latest model
- Use `--style raw` for photorealism
- Add "dark theme, dark background" to prompts
- Generate multiple variations

### FLUX.1 Pro
- Be very specific about text to render
- Specify "monospace font" for code
- Request "photorealistic software screenshot" style
- Use higher step counts (--steps 50) for quality

### General
- Iterate at least 5 times per image
- Test on actual site before finalizing
- Keep prompt history in git
- Document what works and what doesn't

## Troubleshooting

### Image dimensions are wrong
- Use ImageMagick to verify: `identify -format "%wx%h" image.png`
- Resize if needed: `convert image.png -resize 1920x1080 output.png`

### File size too large
- Run optimization script: `./tools/generate-images.sh --optimize`
- Install pngquant: `brew install pngquant`
- Use online tools: [Squoosh.app](https://squoosh.app)

### Colors don't match design system
- Post-process in Figma or Photoshop
- Adjust color curves/levels
- Add overlay layer with exact colors

### Text is blurry or wrong
- Don't rely on AI for text generation
- Use FLUX.1 Pro for text-heavy images
- Add text overlays in post-production if needed

## Next Steps

1. **Read the docs:**
   - `/Users/admin/Dev2/sql2ai/docs/IMAGE_GENERATION_QUEUE.md`
   - `/Users/admin/Dev2/sql2ai/docs/TOOL_RECOMMENDATIONS.md`

2. **Set up accounts:**
   - [Midjourney](https://midjourney.com) - Subscribe to Standard ($30/month)
   - [Replicate](https://replicate.com) or [FAL.ai](https://fal.ai) - For FLUX.1 Pro
   - Optional: [Recraft](https://recraft.ai) - For vector graphics

3. **Start generating:**
   - Begin with HIGH priority images
   - Follow prompts from IMAGE_GENERATION_QUEUE.md
   - Save results to `public/images/marketing/`

4. **Track progress:**
   - Run `./tools/generate-images.sh --status` regularly
   - Document what works in git commits
   - Share results with team for feedback

## Resources

### Research Sources
- Best AI Design Tools 2025: https://aitools.inc/categories/ai-design-tools/best
- FLUX vs Midjourney Comparison: https://upthrust.co/2025/01/best-ai-image-generators-in-2025-flux-1-pro-stable-diffusion-3-5-recraft-v3-midjourney-and-dall-e-3
- AI Image Generator Reviews: https://www.toolworthy.ai/blog/best-ai-image-generator

### Design Reference
- Design Specification: `/Users/admin/Dev2/sql2ai/docs/DESIGN_SPECIFICATION.md`
- Section 6: Image Specifications (source of all prompts)
- Section 4: Visual Design System (color tokens, typography)

### Tools
- Midjourney: https://midjourney.com
- FLUX (via Replicate): https://replicate.com/black-forest-labs/flux-1.1-pro
- FLUX (via FAL.ai): https://fal.ai/models/flux-pro
- Recraft: https://recraft.ai
- Squoosh (optimization): https://squoosh.app

---

**Created:** 2024-12-24
**Author:** Chris Therriault <chris@servicevision.net>
**Last Updated:** 2024-12-24

**Status:** Ready for image generation
