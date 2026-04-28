#!/bin/bash
# ==========================================
# Pentester Suite (Vaporeon) - Install Script
# ==========================================

echo "[*] Iniciando a instalação das dependências do Vaporeon..."

# Verifica se é root ou tem privilégios sudo
if [ "$EUID" -ne 0 ]; then
  echo "[!] Por favor, execute este script com permissões de administrador (sudo ./install.sh)"
  exit
fi

echo "[*] Atualizando repositórios..."
apt-get update -y

echo "[*] Instalando pacotes de sistema essenciais (Área de Transferência e utilitários)..."
# wl-clipboard (Wayland), xclip (X11)
apt-get install -y wl-clipboard xclip curl wget python3-pip python3-venv

echo "[*] Instalando dependências do Python..."
# Instala o Flet no sistema ou no ambiente de usuário
pip3 install flet --break-system-packages 2>/dev/null || pip3 install flet

echo "[*] Verificando Docker..."
if ! command -v docker &> /dev/null
then
    echo "[!] Docker não encontrado. Por favor, instale o Docker Compose para rodar as ferramentas."
else
    echo "[+] Docker detectado."
fi

echo "[+] Instalação concluída com sucesso! Para abrir o painel, digite:"
echo "    python3 app/main.py"
