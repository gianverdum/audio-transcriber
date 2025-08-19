#!/bin/bash

# Script para deploy no AWS Lambda usando SAM CLI

set -e

# Configurações
STACK_NAME="audio-transcriber"
REGION="us-east-1"
STAGE="dev"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploy do Audio Transcriber para AWS Lambda${NC}"
echo "=================================="

# Verifica se SAM CLI está instalado
if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ SAM CLI não encontrado. Instale em: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html${NC}"
    exit 1
fi

# Verifica se AWS CLI está configurado
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS CLI não configurado. Execute: aws configure${NC}"
    exit 1
fi

# Solicita chave da OpenAI se não estiver no .env
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}🔑 Chave da OpenAI não encontrada${NC}"
    read -sp "Digite sua chave da OpenAI: " OPENAI_API_KEY
    echo
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ Chave da OpenAI é obrigatória${NC}"
    exit 1
fi

# Parâmetros opcionais
read -p "AWS Region (default: us-east-1): " input_region
REGION=${input_region:-$REGION}

read -p "Stage (dev/staging/prod, default: dev): " input_stage
STAGE=${input_stage:-$STAGE}

read -p "Stack Name (default: audio-transcriber): " input_stack
STACK_NAME=${input_stack:-$STACK_NAME}

echo -e "${GREEN}📋 Configurações do Deploy:${NC}"
echo "  Stack Name: $STACK_NAME"
echo "  Region: $REGION"
echo "  Stage: $STAGE"
echo

# Confirma deploy
read -p "Continuar com o deploy? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo -e "${YELLOW}⏹️  Deploy cancelado${NC}"
    exit 0
fi

# Navega para o diretório AWS
cd "$(dirname "$0")"

echo -e "${GREEN}🔨 Fazendo build da aplicação...${NC}"
sam build --template-file template.yaml

echo -e "${GREEN}📦 Fazendo deploy...${NC}"
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
    echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}"
    
    # Obtém URL da API
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME-$STAGE" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
        --output text)
    
    echo -e "${GREEN}🌐 URL da API: $API_URL${NC}"
    echo -e "${GREEN}📖 Documentação: $API_URL/docs${NC}"
    
    # Testa health check
    echo -e "${GREEN}🧪 Testando health check...${NC}"
    curl -s "$API_URL/health" | python -m json.tool
    
else
    echo -e "${RED}❌ Erro no deploy${NC}"
    exit 1
fi
