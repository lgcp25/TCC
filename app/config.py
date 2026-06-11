import os
import flet as ft
from dotenv import load_dotenv

load_dotenv()

APP_DIR = os.path.dirname(os.path.abspath(__file__))


PROJECT_ROOT = os.path.dirname(APP_DIR)


DOCKER_DIR = os.path.join(APP_DIR, "docker")


CACHE_FILE = os.path.join(PROJECT_ROOT, "ai_cache.json")


AI_MODEL = "llama-3.3-70b-versatile"
AI_TEMPERATURE = 0.4 
AI_MAX_TOKENS_DEFAULT = 1000
AI_CACHE_TTL_HOURS = 72  

TEACHER_JAMERSON = (
    "Você é um professor de cibersegurança experiente ensinando um aluno de graduação. "
    "Sempre explique o 'porquê' das coisas, não apenas o 'o quê'. "
    "Use linguagem acessível mas técnica. Responda em Português do Brasil. "
    "Use Markdown para formatar sua resposta."
)



THEME_BG = "#020617"          
THEME_CARD = "#0F172A"        
THEME_BORDER = "#1E293B"      
THEME_INPUT_BG = "#1F2937"    
THEME_TERMINAL_BG = "#05080D" 


INPUT_STYLE = dict(
    border_color="transparent",
    filled=True,
    bgcolor=THEME_INPUT_BG,
    text_size=12,
    label_style=ft.TextStyle(size=12, color=ft.Colors.BLUE_GREY_400),
    content_padding=10,
    height=40
)


DOCKER_SERVICE_DEFAULT = "pentester"
