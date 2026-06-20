import flet as ft
from views.tool_tab import ToolTab
from config import INPUT_STYLE
from models.nikto import Nikto


class NiktoTab(ToolTab):
    def __init__(self, app, name, controller):
        self.controller = controller
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
            value="1",
            options=[
            ft.dropdown.Option("1", "1. Varredura Completa (Padrão)"),
            ft.dropdown.Option("2", "2. Foco em execução de comandos (Command Execution)"),
            ft.dropdown.Option("3", "3. Foco em Injeções (SQLi, XSS, Command Injection)"),
            ft.dropdown.Option("4", "4. Foco em Arquivos Vazados (Backups, Configs)"),
            ft.dropdown.Option("5", "5. Foco em Configurações Erradas e Headers")
            ],
            **input_style
        )

        self.user_agent = ft.Dropdown(
            label="User-Agent (Identificação enviada ao servidor)",
            value="1",
            options=[
                ft.dropdown.Option("1","Win11 Chrome"),
                ft.dropdown.Option("2","Mac Chrome"),
                ft.dropdown.Option("3","Linux Firefox")
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
        self.tuning.value = "1"
        self.user_agent.value = "1"
        self.free_cmd_switch.value = False
        self.raw_cmd.value = ""
        self.raw_cmd.disabled = True
        self.left_col.update()
        self.app.page.update()

    async def run(self, e):

        await self.clear_terminal()

        try:

            self.last_command = await self.controller.execute(
                host=self.host.value,
                port=self.port.value,
                ssl_switch=self.ssl_switch.value,
                tuning=self.tuning.value,
                user_agent=self.user_agent.value,
                manual_mode=self.free_cmd_switch.value,
                raw_command=self.raw_cmd.value,
                on_output=self.write_terminal,
                tab=self
            )

        except Exception as err:

            await self.write_terminal(
                f"[ERRO] {err}\n"
            )
