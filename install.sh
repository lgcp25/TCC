#!/bin/bash
# =====================================================
#  🐉 VAPOREON PENTESTER SUITE — Instalador Automático
#  Sistema: Linux (Ubuntu/Debian/Kali)
# =====================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════╗"
echo "║     🐉 VAPOREON PENTESTER SUITE — INSTALADOR     ║"
echo "║          TCC — Segurança da Informação            ║"
echo "╚═══════════════════════════════════════════════════╝"
echo -e "${NC}"

# ─── 1. Verificar se é root ──────────────────────────────
if [ "$EUID" -ne 0 ]; then
    SUDO="sudo"
    echo -e "${YELLOW}[!] Será solicitada sua senha para instalar pacotes.${NC}"
else
    SUDO=""
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ─── 2. Atualizar sistema ────────────────────────────────
echo -e "\n${CYAN}[1/6] Atualizando lista de pacotes...${NC}"
$SUDO apt-get update -qq

# ─── 3. Python ────────────────────────────────────────────
echo -e "${CYAN}[2/6] Verificando Python...${NC}"
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}  ✅ Python encontrado: $PY_VERSION${NC}"
else
    echo -e "${YELLOW}  ⬇ Instalando Python3...${NC}"
    $SUDO apt-get install -y python3 python3-pip python3-venv python3-tk
fi

$SUDO apt-get install -y python3-pip python3-tk xclip 2>/dev/null || true

# ─── 4. Docker ────────────────────────────────────────────
echo -e "${CYAN}[3/6] Verificando Docker...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version 2>&1 | awk '{print $3}' | tr -d ',')
    echo -e "${GREEN}  ✅ Docker encontrado: $DOCKER_VERSION${NC}"
else
    echo -e "${YELLOW}  ⬇ Instalando Docker...${NC}"
    $SUDO apt-get install -y docker.io docker-compose
    $SUDO systemctl start docker
    $SUDO systemctl enable docker
    $SUDO usermod -aG docker $USER
    echo -e "${YELLOW}  ⚠ Faça logout/login para o Docker funcionar sem sudo.${NC}"
fi

if ! docker compose version &> /dev/null 2>&1; then
    echo -e "${YELLOW}  ⬇ Instalando Docker Compose plugin...${NC}"
    $SUDO apt-get install -y docker-compose-plugin 2>/dev/null || $SUDO apt-get install -y docker-compose
fi

# ─── 5. Dependências Python ──────────────────────────────
echo -e "${CYAN}[4/6] Instalando dependências Python...${NC}"

cat > "$SCRIPT_DIR/requirements.txt" << 'EOF'
flet>=0.21.0
groq
requests
fpdf2
python-dotenv
httpx
EOF

pip3 install --user -r "$SCRIPT_DIR/requirements.txt" --quiet 2>/dev/null || pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet
echo -e "${GREEN}  ✅ Dependências Python instaladas${NC}"

# ─── 6. Construir Container Docker ───────────────────────
echo -e "${CYAN}[5/6] Construindo container de ferramentas (primeira vez demora ~5min)...${NC}"
cd "$SCRIPT_DIR/app/docker"

if docker compose build 2>/dev/null; then
    echo -e "${GREEN}  ✅ Container 'pentester' construído${NC}"
elif docker-compose build 2>/dev/null; then
    echo -e "${GREEN}  ✅ Container 'pentester' construído${NC}"
else
    echo -e "${RED}  ❌ Falha ao construir container. Verifique se o Docker está rodando.${NC}"
fi

docker pull vulnerables/web-dvwa 2>/dev/null && echo -e "${GREEN}  ✅ Imagem DVWA baixada${NC}" || true

cd "$SCRIPT_DIR"

# ─── 7. Configurar .env ──────────────────────────────────
echo -e "${CYAN}[6/6] Configurando variáveis de ambiente...${NC}"
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}  ⚠ Arquivo .env não encontrado.${NC}"
    read -p "  Cole sua GROQ_API_KEY (ou Enter para pular): " GROQ_KEY
    if [ -n "$GROQ_KEY" ]; then
        echo "GROQ_API_KEY=$GROQ_KEY" > "$SCRIPT_DIR/.env"
        echo -e "${GREEN}  ✅ Chave salva${NC}"
    else
        echo "GROQ_API_KEY=" > "$SCRIPT_DIR/.env"
        echo -e "${YELLOW}  ⚠ .env criado vazio. Edite depois: nano .env${NC}"
    fi
else
    echo -e "${GREEN}  ✅ .env já existe${NC}"
fi

# ─── Finalização ─────────────────────────────────────────
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Para iniciar o Vaporeon:"
echo -e "  ${CYAN}cd $SCRIPT_DIR && python3 app/main.py${NC}"
echo ""
