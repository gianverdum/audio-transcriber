#!/bin/bash

# Script for AWS Lambda deployment using SAM CLI

set -e

# Configurations
STACK_NAME="audio-transcriber"
REGION="us-east-1"
STAGE="dev"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Audio Transcriber Deploy to AWS Lambda${NC}"
echo "=================================="

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ SAM CLI not found. Install at: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html${NC}"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not configured. Run: aws configure${NC}"
    exit 1
fi

# Request OpenAI key if not in .env
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}🔑 OpenAI key not found${NC}"
    read -sp "Enter your OpenAI key: " OPENAI_API_KEY
    echo
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OpenAI key is required${NC}"
    exit 1
fi

# Optional parameters
read -p "AWS Region (default: us-east-1): " input_region
REGION=${input_region:-$REGION}

read -p "Stage (dev/staging/prod, default: dev): " input_stage
STAGE=${input_stage:-$STAGE}

read -p "Stack Name (default: audio-transcriber): " input_stack
STACK_NAME=${input_stack:-$STACK_NAME}

echo -e "${GREEN}📋 Deploy Configuration:${NC}"
echo "  Stack Name: $STACK_NAME"
echo "  Region: $REGION"
echo "  Stage: $STAGE"
echo

# Confirm deploy
read -p "Continue with deploy? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo -e "${YELLOW}⏹️  Deploy cancelled${NC}"
    exit 0
fi

# Navigate to AWS directory
cd "$(dirname "$0")"

echo -e "${GREEN}🔨 Building application...${NC}"
sam build --template-file template.yaml

echo -e "${GREEN}📦 Deploying...${NC}"
sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name "$STACK_NAME-$STAGE" \
    --region "$REGION" \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        OpenAIApiKey="$OPENAI_API_KEY" \
        Stage="$STAGE" \
    --no-fail-on-empty-changeset \
    --resolve-s3

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deploy completed successfully!${NC}"
    
    # Get API URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME-$STAGE" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
        --output text)
    
    echo -e "${GREEN}🌐 API URL: $API_URL${NC}"
    echo -e "${GREEN}📖 Documentation: $API_URL/docs${NC}"
    
    # Test health check
    echo -e "${GREEN}🧪 Testing health check...${NC}"
    curl -s "$API_URL/health" | python -m json.tool
    
else
    echo -e "${RED}❌ Deploy error${NC}"
    exit 1
fi
