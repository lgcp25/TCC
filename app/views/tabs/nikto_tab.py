import flet as ft
from views.tool_tab import ToolTab
from config import INPUT_STYLE
from models.nikto import Nikto


class NiktoTab(ToolTab):
    def __init__(self, app, name):
        super().__init__(
            app,
            name,
            "Avaliação Web / Servidor",
            "https://cirt.net/Nikto2",
            ft.Icons.LANGUAGE,
            ft.Icons.WEB,
            description="O Nikto é um scanner de servidores web. Ele executa testes extensivos buscando por milhares de arquivos e programas perigosos, versões desatualizadas de softwares e problemas de configuração.",
            help_text="""GUIA TÉCNICO COMPLETO DO NIKTO:

╔══════════════════════════════════════════════════════════════╗
║                       NIKTO - AJUDA                         ║
╚══════════════════════════════════════════════════════════════╝

O Nikto é um scanner de servidores web que procura por:

• Configurações inseguras
• Arquivos sensíveis
• Softwares desatualizados
• Tecnologias expostas
• Cabeçalhos de segurança ausentes
• Possíveis vulnerabilidades conhecidas

═══════════════════════════════════════════════════════════════
[1] ALVO (URL OU IP)
═══════════════════════════════════════════════════════════════

O servidor web que será analisado.

Exemplos:

• http://dvwa
• http://192.168.1.10
• https://empresa.com

═══════════════════════════════════════════════════════════════
[2] PORTA
═══════════════════════════════════════════════════════════════

Porta onde o serviço web está executando.

Exemplos:

80    = HTTP
443   = HTTPS
8080  = HTTP alternativo
8443  = HTTPS alternativo

Se deixado vazio, o Nikto utilizará a porta padrão.

═══════════════════════════════════════════════════════════════
[3] FORÇAR SSL / HTTPS
═══════════════════════════════════════════════════════════════

Utilize quando o alvo estiver usando HTTPS.

Exemplos:

✓ https://empresa.com
✓ https://192.168.1.10

Isso evita falhas durante a conexão.

═══════════════════════════════════════════════════════════════
[4] OBJETIVO DO SCAN
═══════════════════════════════════════════════════════════════

[COMPLETO]
    Executa todas as verificações disponíveis.
    Mais lento, porém mais abrangente.

[EXECUÇÃO DE COMANDOS]
    Prioriza verificações relacionadas a
    funcionalidades potencialmente perigosas.

[INJEÇÕES]
    Procura indicadores de:
    • SQL Injection
    • XSS
    • Command Injection

[ARQUIVOS VAZADOS]
    Procura:
    • Backups
    • Configurações
    • Arquivos esquecidos
    • Dados expostos

[CONFIGURAÇÕES E HEADERS]
    Analisa:
    • Cabeçalhos HTTP
    • Configurações inseguras
    • Boas práticas de segurança

═══════════════════════════════════════════════════════════════
[5] USER-AGENT
═══════════════════════════════════════════════════════════════

Identificação enviada ao servidor.

Exemplos:

• Win11 Chrome
• Mac Chrome
• Linux Firefox

Alguns servidores apresentam comportamentos
diferentes dependendo do navegador informado.

═══════════════════════════════════════════════════════════════
[O QUE O NIKTO PODE ENCONTRAR?]
═══════════════════════════════════════════════════════════════

• Diretórios sensíveis
• Arquivos de backup
• Painéis administrativos
• Versões desatualizadas
• Configurações inseguras
• Headers ausentes
• Tecnologias utilizadas
• Certificados incorretos
• Possíveis vulnerabilidades conhecidas

═══════════════════════════════════════════════════════════════
[INTERPRETANDO OS RESULTADOS]
═══════════════════════════════════════════════════════════════

[Informação]
    Dados úteis para reconhecimento.

[Configuração Insegura]
    Ajustes inadequados encontrados.

[Arquivo Sensível]
    Recursos que não deveriam estar expostos.

[Possível Vulnerabilidade]
    Achado que merece investigação adicional.

═══════════════════════════════════════════════════════════════
[DICA DE OURO]
═══════════════════════════════════════════════════════════════

O Nikto não confirma invasões.

Ele ajuda a responder:

• O servidor está bem configurado?
• Existem arquivos esquecidos?
• Há tecnologias desatualizadas?
• Existem indícios de vulnerabilidades?

Use os resultados como ponto de partida para
aprofundar a análise com outras ferramentas da suíte.
"""
        )
        self.nikto = Nikto()

        input_style = INPUT_STYLE

        # Controles
        self.host = ft.TextField(
            label="Alvo (URL ou IP)",
            value="http://dvwa",
            **input_style
        )

        self.port = ft.TextField(
            label="Porta (opcional, ex: 8081)",
            value="",
            **input_style
        )

        self.ssl_switch = ft.Switch(
            label="Forçar SSL/HTTPS (-ssl)",
            value=False,
            active_color=ft.Colors.AMBER_400
        )

        self.tuning = ft.Dropdown(
            label="Objetivo da Análise",
            value="Varredura Completa (Padrão)",
            options=[
                ft.dropdown.Option("Varredura Completa (Padrão)"),
                ft.dropdown.Option("Foco em execução de comandos (Command Execution)"),
                ft.dropdown.Option("Foco em Injeções (SQLi, XSS, Command Injection)"),
                ft.dropdown.Option("Foco em Arquivos Vazados (Backups, Configs)"),
                ft.dropdown.Option("Foco em Configurações Erradas e Headers")
            ],
            **input_style
        )

        self.user_agent = ft.Dropdown(
            label="User-Agent (Identificação enviada ao servidor)",
            value="Win11 Chrome",
            options=[
                ft.dropdown.Option("Win11 Chrome"),
                ft.dropdown.Option("Mac Chrome"),
                ft.dropdown.Option("Linux Firefox")
            ],
            **input_style
        )

        # Montagem da UI
        self.left_col.controls.extend([
            ft.Container(height=10),
            self.host,
            self.port,
            self.ssl_switch,
            self.tuning,
            self.user_agent,
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.host.value = "dvwa"
        self.port.value = ""
        self.ssl_switch.value = False
        self.tuning.value = "Varredura Completa (Padrão)"
        self.user_agent.value = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Vaporeon"
        self.free_cmd_switch.value = False
        self.raw_cmd.value = ""
        self.raw_cmd.disabled = True
        self.left_col.update()
        self.app.page.update()

    async def run(self, e):
        await self.clear_terminal()
        try:
            if self.free_cmd_switch.value:
                import shlex
                cmd_list = shlex.split(self.raw_cmd.value)
            else:
                cmd_list = self.nikto.build_command(
                    host=self.host.value,
                    port=self.port.value,
                    ssl_switch=self.ssl_switch.value,
                    tuning=self.tuning.value,
                    user_agent=self.user_agent.value
                )
            self.last_command = self.nikto.pretty_command(cmd_list)
            await self.write_terminal(f"[COMANDO] {self.last_command}\n\n")
            await self.app.run_docker(self.nikto.docker_service, cmd_list, on_output=self.write_terminal, tab=self)
        except Exception as err:
            await self.write_terminal(f"[ERRO] {err}\n")
