#!/bin/bash
# Build and publish Docker image to Docker Hub

set -e

# Configuration
IMAGE_NAME="gianverdum/audio-transcriber"
VERSION="1.0.0"
LATEST_TAG="latest"

echo "🐳 Building Audio Transcriber Docker image for Docker Hub..."

# Build multi-platform image
echo "📦 Building image with tags: ${IMAGE_NAME}:${VERSION} and ${IMAGE_NAME}:${LATEST_TAG}"

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t "${IMAGE_NAME}:${VERSION}" \
  -t "${IMAGE_NAME}:${LATEST_TAG}" \
  --push \
  .

echo "✅ Image published successfully!"
echo "🎯 Available at:"
echo "   - docker pull ${IMAGE_NAME}:${VERSION}"
echo "   - docker pull ${IMAGE_NAME}:${LATEST_TAG}"
echo ""
echo "🚀 Usage examples:"
echo "   # REST API Server"
echo "   docker run -e OPENAI_API_KEY=your_key -p 8000:8000 ${IMAGE_NAME}:${LATEST_TAG}"
echo ""
echo "   # MCP STDIO Server"
echo "   docker run -it -e OPENAI_API_KEY=your_key ${IMAGE_NAME}:${LATEST_TAG} uv run audio-transcriber-mcp"
echo ""
echo "   # MCP HTTP Server"
echo "   docker run -e OPENAI_API_KEY=your_key -p 8003:8003 ${IMAGE_NAME}:${LATEST_TAG} uv run audio-transcriber-mcp-http"
