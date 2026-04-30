import flet as ft
from ui.tool_tab import ToolTab
from config import INPUT_STYLE
from tools.gobuster import Gobuster


class GobusterTab(ToolTab):
    def __init__(self, app, name):
        super().__init__(
            app,
            name,
            "Enumeração / Brute-Force",
            "https://github.com/OJ/gobuster",
            ft.Icons.FOLDER_OPEN,
            ft.Icons.MANAGE_SEARCH,
            description="O Gobuster é uma ferramenta usada para descobrir URLs, diretórios e arquivos escondidos em servidores web via força bruta rápida utilizando wordlists pesadas.",
            help_text="""GUIA TÉCNICO GOBUSTER:

Ferramenta de 'Brute-Force' para descoberta de objetos em servidores.

1. EXPLICAÇÃO DOS CAMPOS:
   - MODO: 
     * dir: Busca por pastas e arquivos (usa a flag 'dir -u').
     * dns: Busca por subdomínios (usa a flag 'dns -d').
   - WORDLIST (-w): O arquivo de dicionário que contém as tentativas. No Vaporeon, usamos por padrão o /wordlists/common.txt.
   - EXTENSÕES (-x): Se você definir 'php', o Gobuster testará 'arquivo' e também 'arquivo.php'. Fundamental para encontrar backups (ex: index.php.bak).
   - STATUS CODES (-s): Define o que é considerado 'encontrado'. 200 é sucesso, 301/302 são redirecionamentos.

2. EXEMPLOS DE COMANDO GERADO:
   - Busca de Diretórios: gobuster dir -u http://dvwa -w /wordlists/common.txt
   - Busca de Arquivos Sensíveis: gobuster dir -u http://dvwa -w common.txt -x php,txt,bak,zip
   - Busca de Subdomínios: gobuster dns -d empresa.com -w subdomains.txt

3. DICA: 
   O Gobuster é essencial para a 'Enumeração de Superfície'. Muitas vezes a falha não está na página principal, mas em um arquivo esquecido como '/config.php.old' ou '/.env'."""
        )
        self.gobuster = Gobuster()

        input_style = INPUT_STYLE

        # Controles
        self.target = ft.TextField(
            label="URL / Host / Domínio",
            value="http://dvwa",
            **input_style
        )

        self.mode = ft.Dropdown(
            label="Modo",
            value="dir",
            options=[
                ft.dropdown.Option("dir"),
                ft.dropdown.Option("dns"),
                ft.dropdown.Option("vhost"),
                ft.dropdown.Option("fuzz"),
            ],
            **input_style
        )

        self.wordlist = ft.TextField(
            label="Caminho da Wordlist",
            value="/usr/share/wordlists/dirb/common.txt",
            **input_style
        )

        self.threads = ft.TextField(
            label="Threads",
            value="50",
            **input_style
        )

        self.extensions = ft.TextField(
            label="Extensões (php,txt,html)",
            value="",
            **input_style
        )

        self.status_codes = ft.TextField(
            label="Status válidos (200,204,301)",
            value="",
            **input_style
        )

        self.follow_redirect = ft.Switch(
            label="Seguir Redirects (-r)",
            value=False,
            active_color=ft.Colors.GREEN_400
        )

        self.timeout = ft.TextField(
            label="Timeout (s)",
            value="10",
            **input_style
        )

        self.extra_params = ft.TextField(
            label="Parâmetros extras",
            value="",
            **input_style
        )

        # Montagem da UI
        self.left_col.controls.extend([
            ft.Container(height=10),
            self.target,
            self.mode,
            self.wordlist,
            self.threads,
            self.extensions,
            self.status_codes,
            self.follow_redirect,
            self.timeout,
            self.extra_params,
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.target.value = "http://dvwa:80"
        self.mode.value = "dir"
        self.wordlist.value = "/wordlists/common.txt"
        self.threads.value = "10"
        self.extensions.value = ""
        self.status_codes.value = "200,204,301,302,307,401,403"
        self.follow_redirect.value = False
        self.timeout.value = "10"
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
                cmd_list = [self.gobuster.binary] + shlex.split(self.raw_cmd.value)
            else:
                cmd_list = self.gobuster.build_command(
                    target=self.target.value,
                    mode=self.mode.value,
                    wordlist=self.wordlist.value,
                    threads=self.threads.value,
                    extensions=self.extensions.value,
                    status_codes=self.status_codes.value,
                    follow_redirect=self.follow_redirect.value,
                    timeout=self.timeout.value,
                    extra_params=self.extra_params.value
                )
            self.last_command = self.gobuster.pretty_command(cmd_list)
            await self.write_terminal(f"[COMANDO] {self.last_command}\n\n")
            await self.app.run_docker(self.gobuster.docker_service, cmd_list, on_output=self.write_terminal, tab=self)
        except Exception as err:
            await self.write_terminal(f"[ERRO] {err}\n")
