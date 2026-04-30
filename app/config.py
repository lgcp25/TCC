import os
import flet as ft
from dotenv import load_dotenv

# Carrega variáveis de ambiente imediatamente
load_dotenv()

# Raiz do pacote app/ (diretório onde este arquivo está)
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Raiz do projeto (um nível acima de app/)
PROJECT_ROOT = os.path.dirname(APP_DIR)

# Docker
DOCKER_DIR = os.path.join(APP_DIR, "docker")

# Cache da IA
CACHE_FILE = os.path.join(PROJECT_ROOT, "ai_cache.json")

# Configurações da IA
AI_MODEL = "llama-3.3-70b-versatile"
AI_TEMPERATURE = 0.4 # Nivel de criatividade da IA de 0 a 1
AI_MAX_TOKENS_DEFAULT = 1000 #limite de tokens de saída
AI_CACHE_TTL_HOURS = 72  # Expiração do cache em horas

# Tom pedagógico aplicado em todos os prompts
TEACHER_JAMERSON = (
    "Você é um professor de cibersegurança experiente ensinando um aluno de graduação. "
    "Sempre explique o 'porquê' das coisas, não apenas o 'o quê'. "
    "Use linguagem acessível mas técnica. Responda em Português do Brasil. "
    "Use Markdown para formatar sua resposta."
)


# TEMA DA INTERFACE (cores)
THEME_BG = "#020617"          # Fundo principal da aplicação
THEME_CARD = "#0F172A"        # Fundo de cards e painéis
THEME_BORDER = "#1E293B"      # Bordas dos containers
THEME_INPUT_BG = "#1F2937"    # Fundo dos campos de input
THEME_TERMINAL_BG = "#05080D" # Fundo do terminal de output

# ESTILO PADRÃO DOS INPUTS (reutilizável em todas as tabs)
INPUT_STYLE = dict(
    border_color="transparent",
    filled=True,
    bgcolor=THEME_INPUT_BG,
    text_size=12,
    label_style=ft.TextStyle(size=12, color=ft.Colors.BLUE_GREY_400),
    content_padding=10,
    height=40
)

# DOCKER
DOCKER_SERVICE_DEFAULT = "pentester"
