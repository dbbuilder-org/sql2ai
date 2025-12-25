#!/bin/bash

################################################################################
# SQL2.AI Image Generation Workflow Script
#
# Purpose: Document and automate the workflow for generating marketing images
#          for the SQL2.AI website using AI image generation tools.
#
# Author: Chris Therriault <chris@servicevision.net>
# Created: 2024-12-24
# Last Updated: 2024-12-24
#
# Prerequisites:
# - Access to Midjourney (Discord account with subscription)
# - Access to FLUX.1 Pro (Replicate or FAL.ai account)
# - Optional: Recraft account for vector graphics
# - Image optimization tools (ImageOptim, pngquant, or Squoosh CLI)
#
# Usage:
#   ./generate-images.sh [options]
#
# Options:
#   --help          Show this help message
#   --check         Check prerequisites and tool availability
#   --optimize      Optimize existing images in public/images/marketing/
#   --status        Show generation status for all images
#
################################################################################

set -e  # Exit on error
# Note: set -u disabled to allow optional parameters
# set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="${PROJECT_ROOT}/docs"
PUBLIC_DIR="${PROJECT_ROOT}/public/images/marketing"
ARCHIVE_DIR="${PROJECT_ROOT}/public/images/marketing/originals"

# Image specifications (from IMAGE_GENERATION_QUEUE.md)
declare -a IMAGES=(
    "hero-schema-visualization.png|1920x1080|HIGH|Midjourney"
    "query-optimization-before-after.png|1920x1080|HIGH|FLUX"
    "execution-plan-tree.png|1200x900|MEDIUM|Midjourney"
    "terminal-cli-interface.png|1600x900|HIGH|FLUX"
    "cross-platform-bridge.png|1920x800|MEDIUM|Midjourney"
    "mcp-ide-integration.png|1920x1080|MEDIUM|FLUX"
    "lifecycle-circular-diagram.png|1200x1200|HIGH|Midjourney"
)

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

################################################################################
# Check Prerequisites
################################################################################

check_prerequisites() {
    print_header "Checking Prerequisites"

    local all_good=true

    # Check if docs exist
    if [[ -f "${DOCS_DIR}/IMAGE_GENERATION_QUEUE.md" ]]; then
        print_success "Found IMAGE_GENERATION_QUEUE.md"
    else
        print_error "Missing IMAGE_GENERATION_QUEUE.md"
        all_good=false
    fi

    if [[ -f "${DOCS_DIR}/TOOL_RECOMMENDATIONS.md" ]]; then
        print_success "Found TOOL_RECOMMENDATIONS.md"
    else
        print_error "Missing TOOL_RECOMMENDATIONS.md"
        all_good=false
    fi

    # Check for image optimization tools
    print_info "Checking for image optimization tools..."

    if command -v pngquant &> /dev/null; then
        print_success "pngquant installed"
    else
        print_warning "pngquant not found (optional, for PNG optimization)"
        echo "          Install with: brew install pngquant"
    fi

    if command -v jpegoptim &> /dev/null; then
        print_success "jpegoptim installed"
    else
        print_warning "jpegoptim not found (optional, for JPEG optimization)"
        echo "          Install with: brew install jpegoptim"
    fi

    if command -v convert &> /dev/null; then
        print_success "ImageMagick installed"
    else
        print_warning "ImageMagick not found (useful for format conversion)"
        echo "          Install with: brew install imagemagick"
    fi

    # Check directories
    print_info "Checking directories..."

    if [[ -d "${PUBLIC_DIR}" ]]; then
        print_success "Marketing images directory exists"
    else
        print_warning "Creating ${PUBLIC_DIR}"
        mkdir -p "${PUBLIC_DIR}"
    fi

    if [[ -d "${ARCHIVE_DIR}" ]]; then
        print_success "Archive directory exists"
    else
        print_warning "Creating ${ARCHIVE_DIR}"
        mkdir -p "${ARCHIVE_DIR}"
    fi

    echo ""
    if [[ "$all_good" = true ]]; then
        print_success "All prerequisites met!"
    else
        print_error "Some prerequisites missing. Please review above."
        return 1
    fi
}

################################################################################
# Show Generation Status
################################################################################

show_status() {
    print_header "Image Generation Status"

    echo ""
    printf "%-40s %-15s %-10s %-15s %s\n" "Filename" "Dimensions" "Priority" "Tool" "Status"
    echo "────────────────────────────────────────────────────────────────────────────────────────"

    for image_spec in "${IMAGES[@]}"; do
        IFS='|' read -r filename dimensions priority tool <<< "$image_spec"

        if [[ -f "${PUBLIC_DIR}/${filename}" ]]; then
            # Get actual dimensions
            if command -v identify &> /dev/null; then
                actual_dims=$(identify -format "%wx%h" "${PUBLIC_DIR}/${filename}" 2>/dev/null || echo "unknown")
            else
                actual_dims="unknown"
            fi

            if [[ "$actual_dims" == "$dimensions" ]]; then
                status="${GREEN}✓ Generated${NC}"
            else
                status="${YELLOW}⚠ Wrong size (${actual_dims})${NC}"
            fi
        else
            status="${RED}✗ Missing${NC}"
        fi

        printf "%-40s %-15s %-10s %-15s " "$filename" "$dimensions" "$priority" "$tool"
        echo -e "$status"
    done

    echo ""

    # Summary
    local total=${#IMAGES[@]}
    local generated=0

    for image_spec in "${IMAGES[@]}"; do
        IFS='|' read -r filename _ _ _ <<< "$image_spec"
        if [[ -f "${PUBLIC_DIR}/${filename}" ]]; then
            ((generated++))
        fi
    done

    echo "Summary: ${generated}/${total} images generated"

    if [[ $generated -eq $total ]]; then
        print_success "All images generated!"
    else
        print_warning "$((total - generated)) images still need to be generated"
    fi
}

################################################################################
# Optimize Images
################################################################################

optimize_images() {
    print_header "Optimizing Images"

    if ! command -v pngquant &> /dev/null; then
        print_error "pngquant not installed. Cannot optimize."
        echo "Install with: brew install pngquant"
        return 1
    fi

    echo ""

    for image_spec in "${IMAGES[@]}"; do
        IFS='|' read -r filename _ _ _ <<< "$image_spec"

        local filepath="${PUBLIC_DIR}/${filename}"

        if [[ -f "$filepath" ]]; then
            # Get original size
            local original_size=$(stat -f%z "$filepath" 2>/dev/null || stat -c%s "$filepath" 2>/dev/null)

            print_info "Optimizing ${filename}..."

            # Backup original to archive if not already there
            if [[ ! -f "${ARCHIVE_DIR}/${filename}" ]]; then
                cp "$filepath" "${ARCHIVE_DIR}/${filename}"
                print_success "Backed up original to archive"
            fi

            # Optimize PNG
            if [[ "${filename}" == *.png ]]; then
                pngquant --force --quality=80-95 --output "${filepath}" "${filepath}" 2>/dev/null || true

                # Get new size
                local new_size=$(stat -f%z "$filepath" 2>/dev/null || stat -c%s "$filepath" 2>/dev/null)
                local saved=$((original_size - new_size))
                local percent=$((saved * 100 / original_size))

                print_success "Saved ${saved} bytes (${percent}%)"
            fi
        else
            print_warning "Skipping ${filename} (not found)"
        fi
    done

    echo ""
    print_success "Optimization complete!"
}

################################################################################
# Interactive Generation Guide
################################################################################

interactive_guide() {
    print_header "SQL2.AI Image Generation Workflow"

    echo ""
    echo "This script documents the workflow for generating marketing images."
    echo "Since AI image generation tools are primarily web/Discord-based,"
    echo "this script serves as a guide and checklist."
    echo ""
    echo "📋 WORKFLOW STEPS:"
    echo ""
    echo "1. READ THE DOCUMENTATION"
    echo "   - Review: ${DOCS_DIR}/IMAGE_GENERATION_QUEUE.md"
    echo "   - Review: ${DOCS_DIR}/TOOL_RECOMMENDATIONS.md"
    echo ""
    echo "2. SET UP ACCOUNTS"
    echo "   - Midjourney: Join Discord, subscribe ($30/month Standard)"
    echo "   - FLUX.1 Pro: Sign up for Replicate or FAL.ai (~$10-20/month)"
    echo "   - Optional: Recraft for vector graphics ($20/month)"
    echo ""
    echo "3. GENERATE IMAGES (Priority Order)"
    echo "   HIGH Priority:"
    for image_spec in "${IMAGES[@]}"; do
        IFS='|' read -r filename _ priority tool <<< "$image_spec"
        if [[ "$priority" == "HIGH" ]]; then
            echo "   - ${filename} (${tool})"
        fi
    done
    echo ""
    echo "   MEDIUM Priority:"
    for image_spec in "${IMAGES[@]}"; do
        IFS='|' read -r filename _ priority tool <<< "$image_spec"
        if [[ "$priority" == "MEDIUM" ]]; then
            echo "   - ${filename} (${tool})"
        fi
    done
    echo ""
    echo "4. FOR EACH IMAGE:"
    echo "   a. Copy prompt from IMAGE_GENERATION_QUEUE.md"
    echo "   b. Generate 3-5 variations in your chosen tool"
    echo "   c. Select best result"
    echo "   d. Download high-resolution version"
    echo "   e. Save to: ${PUBLIC_DIR}"
    echo "   f. Run: ./generate-images.sh --optimize"
    echo ""
    echo "5. QUALITY CHECK:"
    echo "   - Verify dimensions: ./generate-images.sh --status"
    echo "   - Check dark theme consistency"
    echo "   - Ensure text is readable (if applicable)"
    echo "   - Test on actual website"
    echo ""
    echo "6. FINALIZE:"
    echo "   - Commit images to git"
    echo "   - Update Next.js Image components"
    echo "   - Cancel subscriptions if one-time generation"
    echo ""

    print_header "Quick Reference"
    echo ""
    echo "Midjourney Discord prompts should include:"
    echo "  --ar [width]:[height]  (aspect ratio)"
    echo "  --v 6                  (use version 6)"
    echo "  --style raw            (more photorealistic)"
    echo ""
    echo "Example Midjourney prompt:"
    echo "  /imagine [your prompt] --ar 16:9 --v 6 --style raw"
    echo ""
    echo "FLUX prompts should specify:"
    echo "  - Exact text to render (if any)"
    echo "  - Font family (e.g., 'monospace font')"
    echo "  - 'photorealistic software screenshot' style"
    echo ""

    print_header "Next Steps"
    echo ""
    echo "1. Run: ./generate-images.sh --check"
    echo "2. Review documentation in ${DOCS_DIR}/"
    echo "3. Set up Midjourney and FLUX accounts"
    echo "4. Start generating images (HIGH priority first)"
    echo "5. Run: ./generate-images.sh --status (to track progress)"
    echo ""
}

################################################################################
# Show Help
################################################################################

show_help() {
    cat << EOF
SQL2.AI Image Generation Workflow Script

USAGE:
    ./generate-images.sh [OPTIONS]

OPTIONS:
    --help          Show this help message
    --check         Check prerequisites and tool availability
    --optimize      Optimize existing images in public/images/marketing/
    --status        Show generation status for all images
    (no options)    Show interactive generation guide

EXAMPLES:
    ./generate-images.sh                # Show interactive guide
    ./generate-images.sh --check        # Check if ready to generate
    ./generate-images.sh --status       # See which images are done
    ./generate-images.sh --optimize     # Compress generated images

DIRECTORIES:
    Docs:     ${DOCS_DIR}/
    Images:   ${PUBLIC_DIR}/
    Archive:  ${ARCHIVE_DIR}/

FILES:
    Required:
    - IMAGE_GENERATION_QUEUE.md  (prompts and specifications)
    - TOOL_RECOMMENDATIONS.md    (tool selection guide)

WORKFLOW:
    1. Read documentation (IMAGE_GENERATION_QUEUE.md)
    2. Set up AI tool accounts (Midjourney, FLUX)
    3. Generate images using prompts from docs
    4. Save to public/images/marketing/
    5. Optimize with --optimize flag
    6. Check status with --status flag

For detailed instructions, see:
    ${DOCS_DIR}/IMAGE_GENERATION_QUEUE.md
    ${DOCS_DIR}/TOOL_RECOMMENDATIONS.md

EOF
}

################################################################################
# Main Script Logic
################################################################################

main() {
    # Parse command line arguments
    case "${1:-}" in
        --help)
            show_help
            ;;
        --check)
            check_prerequisites
            ;;
        --status)
            show_status
            ;;
        --optimize)
            optimize_images
            ;;
        "")
            interactive_guide
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Run './generate-images.sh --help' for usage information."
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
