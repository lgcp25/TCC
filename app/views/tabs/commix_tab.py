import flet as ft
from views.tool_tab import ToolTab
from config import INPUT_STYLE
from models.commix import Commix


class CommixTab(ToolTab):
    def __init__(self, app, name):
        super().__init__(
            app,
            name,
            "Injeção de Comando de SO",
            "https://github.com/commixproject/commix",
            ft.Icons.TERMINAL,
            ft.Icons.CODE,
            description="O Commix (Command Injection Exploiter) automatiza a descoberta e a exploração de vulnerabilidades de Injeção de Comando no Sistema Operacional (OS Command Injection) em aplicações web.",
            help_text="""GUIA TÉCNICO COMMIX:

Exploração automatizada de vulnerabilidades onde o atacante executa comandos no SO.

1. EXPLICAÇÃO DOS CAMPOS:
   - DADOS POST (--data): Payload que contém os campos do formulário (ex: host=8.8.8.8). O Commix tentará injetar comandos como '8.8.8.8; whoami' nesses campos.
   - COOKIES (--cookie): Necessário se a falha estiver atrás de um login.
   - TÉCNICA: Define como o Commix confirma a falha. 
     * In-band: O resultado do comando aparece na tela.
     * Blind: O Commix confirma a falha pelo tempo que o servidor leva para responder.
   - OS SHELL (--os-shell): Se vulnerável, o Commix abre um terminal semi-interativo para você digitar comandos de sistema livremente.

2. EXEMPLOS DE COMANDO GERADO:
   - Teste Simples via GET: commix -u "http://alvo/ping.php?host=8.8.8.8"
   - Teste via POST com Login: commix -u "http://alvo/ping" --data="host=8.8.8.8" --cookie="PHPSESSID=..."
   - Tentar Abrir Shell: commix -u "http://alvo/ping.php?host=1" --os-shell

3. DICA: 
   Command Injection é o 'Santo Graal' do pentest web. Enquanto o SQLi ataca os dados, o Commix ataca a infraestrutura, permitindo que você controle o próprio servidor.
   
4. ENTENDENDO A URL E PARÂMETROS:
   URLs com `?param=valor` são o alvo principal. O Commix tenta substituir o `valor` por comandos de sistema (como `ls`, `cat`, `whoami`). O `?` inicia os parâmetros e o `&` separa múltiplos parâmetros. Sem parâmetros na URL ou no campo de Dados (POST), a ferramenta não tem onde injetar o código!"""
        )
        self.commix = Commix()

        input_style = INPUT_STYLE

        # Controles
        self.url = ft.TextField(
            label="URL alvo",
            value="http://dvwa/vulnerabilities/exec/",
            **input_style
        )

        self.data = ft.TextField(
            label="POST data (opcional)",
            value="",
            **input_style
        )

        self.cookie = ft.TextField(
            label="Cookie (opcional)",
            value="",
            **input_style
        )

        self.header = ft.TextField(
            label="Header customizado",
            value="",
            **input_style
        )

        self.technique = ft.Dropdown(
            label="Técnica de Injeção",
            value="se",
            options=[
                ft.dropdown.Option("se"),
                ft.dropdown.Option("classic"),
                ft.dropdown.Option("eval-based"),
                ft.dropdown.Option("time-based"),
                ft.dropdown.Option("file-based"),
            ],
            **input_style
        )

        self.os_cmd_switch = ft.Switch(
            label="OS Command Injection (--os-cmd)",
            value=False,
            active_color=ft.Colors.RED_400
        )

        self.os_shell_switch = ft.Switch(
            label="OS Interactive Shell (--os-shell)",
            value=False,
            active_color=ft.Colors.RED_400
        )

        self.json_switch = ft.Switch(
            label="Salvar saída JSON (--output-json)",
            value=False,
            active_color=ft.Colors.TEAL_400
        )

        self.extra_params = ft.TextField(
            label="Parâmetros extras",
            value="",
            **input_style
        )

        # Montagem da UI
        # Montagem da UI
        self.left_col.controls.extend([
            ft.Container(height=10),
            self.url,
            self.data,
            self.cookie,
            self.header,
            self.technique,
            ft.Row([self.os_cmd_switch, self.os_shell_switch, self.json_switch], wrap=True),
            self.extra_params,
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.url.value = "http://dvwa/vulnerabilities/exec/"
        self.data.value = "ip=127.0.0.1&Submit=Submit"
        self.cookie.value = "security=low; PHPSESSID=..."
        self.header.value = ""
        self.technique.value = ""
        self.os_cmd_switch.value = False
        self.os_shell_switch.value = False
        self.json_switch.value = False
        self.extra_params.value = ""
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
                cmd_list = [self.commix.binary] + shlex.split(self.raw_cmd.value)
            else:
                cookie_val = self.cookie.value
                if ("PHPSESSID=..." in cookie_val or not cookie_val.strip()) and self.app.dvwa_cookies:
                    cookie_val = "; ".join([f"{k}={v}" for k, v in self.app.dvwa_cookies.items()])

                cmd_list = self.commix.build_command(
                    url=self.url.value,
                    data=self.data.value,
                    cookie=cookie_val,
                    header=self.header.value,
                    technique=self.technique.value,
                    os_cmd_switch=self.os_cmd_switch.value,
                    os_shell_switch=self.os_shell_switch.value,
                    json_switch=self.json_switch.value,
                    extra_params=self.extra_params.value
                )
            self.last_command = self.commix.pretty_command(cmd_list)
            await self.write_terminal(f"[COMANDO] {self.last_command}\n\n")
            await self.app.run_docker(self.commix.docker_service, cmd_list, on_output=self.write_terminal, tab=self)
        except Exception as err:
            await self.write_terminal(f"[ERRO] {err}\n")
