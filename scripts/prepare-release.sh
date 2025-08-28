#!/bin/bash

# NB_Streamer - Release Preparation Script
# Prepares everything needed for a GitHub release

set -e

VERSION="${VERSION:-0.3.1}"
RELEASE_BRANCH="${RELEASE_BRANCH:-main}"

echo "🚀 Preparing NB_Streamer v${VERSION} for release"
echo "==============================================="

# Check if we're on the right branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo "📍 Current branch: ${CURRENT_BRANCH}"

if [ "$CURRENT_BRANCH" != "$RELEASE_BRANCH" ] && [ "$CURRENT_BRANCH" != "unknown" ]; then
    echo "⚠️  Warning: Not on release branch (${RELEASE_BRANCH})"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if command -v git >/dev/null 2>&1; then
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "⚠️  Warning: You have uncommitted changes"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Pre-release checks
echo ""
echo "✅ Pre-release Checklist:"
echo "========================="

echo "📋 Checking version consistency..."
# Check if version appears in key files
VERSION_IN_CONFIG=$(grep -o "version: str = \"[0-9.]*\"" src/config.py | grep -o "[0-9.]*" || echo "not found")
VERSION_IN_CHANGELOG=$(head -20 CHANGELOG.md | grep -o "\[0.3.[0-9]*\]" | head -1 | tr -d '[]' || echo "not found")

echo "   - Config version: ${VERSION_IN_CONFIG}"
echo "   - Changelog version: ${VERSION_IN_CHANGELOG}"
echo "   - Target version: ${VERSION}"

if [ "$VERSION_IN_CONFIG" != "$VERSION" ]; then
    echo "❌ Version mismatch in config.py"
    exit 1
fi

echo "📝 Checking documentation..."
if [ ! -f "README.md" ]; then
    echo "❌ README.md missing"
    exit 1
fi

if [ ! -f "CHANGELOG.md" ]; then
    echo "❌ CHANGELOG.md missing"  
    exit 1
fi

if [ ! -f "docs/DEPLOYMENT.md" ]; then
    echo "❌ Deployment documentation missing"
    exit 1
fi

echo "🐳 Checking Docker setup..."
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile missing"
    exit 1
fi

if [ ! -f "docker-compose.production.yml" ]; then
    echo "❌ Production Docker Compose missing"
    exit 1
fi

if [ ! -f "scripts/build-and-push.sh" ]; then
    echo "❌ Build script missing"
    exit 1
fi

if [ ! -f "scripts/deploy.sh" ]; then
    echo "❌ Deploy script missing"
    exit 1
fi

echo "📦 Checking GitHub Actions..."
if [ ! -f ".github/workflows/build-and-push.yml" ]; then
    echo "❌ GitHub Actions workflow missing"
    exit 1
fi

echo ""
echo "✅ All pre-release checks passed!"
echo ""

# Generate release summary
echo "📊 Release Summary"
echo "=================="
echo "Version: ${VERSION}"
echo "Type: Cleanup Release (Breaking Changes)"
echo "Key Changes:"
echo "  - Legacy /events endpoint permanently disabled"  
echo "  - Container registry support added"
echo "  - Documentation consolidated and improved"
echo "  - Codebase simplified and cleaned up"
echo ""

# Instructions for GitHub release
echo "🎯 Next Steps for GitHub Release"
echo "================================"
echo ""
echo "1. **Commit and push all changes:**"
echo "   git add ."
echo "   git commit -m \"Release v${VERSION}: Legacy cleanup and container registry support\""
echo "   git push origin ${RELEASE_BRANCH}"
echo ""
echo "2. **Create and push release tag:**"
echo "   git tag -a v${VERSION} -m \"Release v${VERSION}\""
echo "   git push origin v${VERSION}"
echo ""
echo "3. **Create GitHub release:**"
echo "   - Go to your GitHub repository"
echo "   - Click 'Releases' → 'Create a new release'"
echo "   - Select tag: v${VERSION}"
echo "   - Release title: \"v${VERSION} - Legacy Cleanup & Container Registry\""
echo "   - Copy content from RELEASE_NOTES_v${VERSION}.md"
echo "   - Mark as pre-release if needed"
echo "   - Publish release"
echo ""
echo "4. **Verify automated build:**"
echo "   - Check GitHub Actions tab for build status"
echo "   - Confirm images appear in GitHub Container Registry"
echo "   - Test deployment with: IMAGE_TAG=${VERSION} ./scripts/deploy.sh"
echo ""

if [ -f "RELEASE_NOTES_v${VERSION}.md" ]; then
    echo "📝 Release notes available in: RELEASE_NOTES_v${VERSION}.md"
else
    echo "⚠️  Release notes not found: RELEASE_NOTES_v${VERSION}.md"
fi

echo ""
echo "🎉 Ready for release! Follow the steps above to complete the GitHub release."
