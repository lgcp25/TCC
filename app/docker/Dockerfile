FROM python:3.10-slim

# Atualiza sistema e instala dependências básicas
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    perl\
    nmap \
    netcat-openbsd \
    gobuster \
    && apt-get clean

# -------------------------
# Nikto (via Git)
# -------------------------
RUN git clone https://github.com/sullo/nikto.git /opt/nikto
# -------------------------
# SQLmap
# -------------------------
RUN git clone https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap \
    && ln -s /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap \
    && chmod +x /usr/local/bin/sqlmap


# -------------------------
# Nuclei
# -------------------------

# === NUCLEI: VERSÃO FIXA (3.4.10) ===
RUN echo "Baixando Nuclei v3.4.10..." && \
    wget -qO /tmp/nuclei.zip \
        "https://github.com/projectdiscovery/nuclei/releases/download/v3.4.10/nuclei_3.4.10_linux_amd64.zip" && \
    unzip -j /tmp/nuclei.zip nuclei -d /usr/local/bin && \
    chmod +x /usr/local/bin/nuclei && \
    rm -f /tmp/nuclei.zip

# Criar usuário
RUN useradd -m -s /bin/bash pentester

# Criar diretórios
RUN mkdir -p /home/pentester/.config \
    /home/pentester/.nuclei-templates && \
    chown -R pentester:pentester /home/pentester

# Trocar usuário
USER pentester

# Instalar templates 
RUN nuclei -update-templates

USER root
# -------------------------
# Dirsearch
# -------------------------
RUN git clone https://github.com/maurosoria/dirsearch.git /opt/dirsearch

# -------------------------
# Commix
# -------------------------
RUN git clone https://github.com/commixproject/commix.git /opt/commix

# -------------------------
# Ajusta PATH (opcional)
# -------------------------
ENV PATH="/opt/sqlmap:/opt/dirsearch:/opt/commix:${PATH}"

# Diretório de trabalho
WORKDIR /app

# Copia seu projeto
COPY . .

USER pentester

# Comando padrão
CMD ["bash"]