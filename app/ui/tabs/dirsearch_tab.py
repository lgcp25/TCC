import flet as ft
from ui.tool_tab import ToolTab
from config import INPUT_STYLE
from tools.dirsearch import Dirsearch


class DirsearchTab(ToolTab):
    def __init__(self, app, name):
        super().__init__(
            app,
            name,
            "Enumeração Web Avançada",
            "https://github.com/maurosoria/dirsearch",
            ft.Icons.ACCOUNT_TREE,
            ft.Icons.SNIPPET_FOLDER,
            description="O Dirsearch é uma alternativa versátil para descoberta de caminhos web. Ele foca em encontrar diretórios secretos e painéis administrativos com alta performance e suporte a extensões e exclusões de status HTTP.",
            help_text="""GUIA TÉCNICO DIRSEARCH:

Um fuzzer de diretórios web moderno e altamente customizável.

1. EXPLICAÇÃO DOS CAMPOS:
   - RECURSÃO (-r): Se o Dirsearch encontrar '/admin', ele automaticamente começará um novo scan dentro de '/admin/'.
   - PROFUNDIDADE: Define até quantos níveis de pastas a recursão deve ir.
   - EXCLUIR STATUS (-e): Se o servidor retorna erro 403 (Proibido) em tudo, use este campo para ocultar esses resultados e focar apenas no que retorna 200 (OK).
   - THREADS (-t): Quantidade de requisições simultâneas. Mais threads = mais rápido, mas pode causar instabilidade no servidor.

2. EXEMPLOS DE COMANDO GERADO:
   - Scan Simples: dirsearch -u http://dvwa -e 404,403
   - Scan Recursivo Profundo: dirsearch -u http://dvwa -r --depth 3
   - Scan com Extensões: dirsearch -u http://dvwa -e php,zip,tar.gz

3. DICA: 
   O Dirsearch é conhecido por ter uma das melhores lógicas de 'Auto-recursão'. Ele é ideal para mapear toda a estrutura de diretórios de um alvo complexo rapidamente."""
        )
        self.dirsearch = Dirsearch()

        input_style = INPUT_STYLE

        # Controles
        self.target = ft.TextField(
            label="URL alvo",
            value="http://dvwa",
            **input_style
        )

        self.wordlist = ft.TextField(
            label="Caminho da Wordlist",
            value="/usr/share/wordlists/dirb/common.txt",
            **input_style
        )

        self.extensions = ft.TextField(
            label="Extensões (.php,.txt,.html)",
            value="",
            **input_style
        )

        self.http_method = ft.Dropdown(
            label="Método HTTP",
            value="GET",
            options=[
                ft.dropdown.Option("GET"),
                ft.dropdown.Option("POST"),
                ft.dropdown.Option("HEAD"),
                ft.dropdown.Option("PUT"),
            ],
            **input_style
        )

        self.recursion_depth = ft.TextField(
            label="Nível de Recursão",
            value="1",
            **input_style
        )

        self.exclude_status = ft.TextField(
            label="Excluir status (404,403)",
            value="",
            **input_style
        )

        self.threads = ft.TextField(
            label="Threads",
            value="30",
            **input_style
        )

        self.timeout = ft.TextField(
            label="Timeout (s)",
            value="10",
            **input_style
        )

        self.lowercase_switch = ft.Switch(
            label="Forçar lowercase (--lowercase)",
            value=False,
            active_color=ft.Colors.CYAN_400
        )

        self.json_switch = ft.Switch(
            label="Salvar JSON (--json-report)",
            value=False,
            active_color=ft.Colors.TEAL_400
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
            self.wordlist,
            self.extensions,
            self.http_method,
            self.recursion_depth,
            self.exclude_status,
            self.threads,
            self.timeout,
            self.lowercase_switch,
            self.json_switch,
            self.extra_params,
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.target.value = "http://dvwa:80"
        self.wordlist.value = "/wordlists/common.txt"
        self.extensions.value = "php,txt,bak"
        self.http_method.value = "GET"
        self.recursion_depth.value = "1"
        self.exclude_status.value = "404,403"
        self.threads.value = "30"
        self.timeout.value = "10"
        self.lowercase_switch.value = False
        self.json_switch.value = True
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
                cmd_list = [self.dirsearch.binary] + shlex.split(self.raw_cmd.value)
            else:
                cmd_list = self.dirsearch.build_command(
                    target=self.target.value,
                    wordlist=self.wordlist.value,
                    extensions=self.extensions.value,
                    http_method=self.http_method.value,
                    recursion_depth=self.recursion_depth.value,
                    exclude_status=self.exclude_status.value,
                    threads=self.threads.value,
                    timeout=self.timeout.value,
                    lowercase_switch=self.lowercase_switch.value,
                    json_switch=self.json_switch.value,
                    extra_params=self.extra_params.value
                )
            self.last_command = self.dirsearch.pretty_command(cmd_list)
            await self.write_terminal(f"[COMANDO] {self.last_command}\n\n")
            await self.app.run_docker(self.dirsearch.docker_service, cmd_list, on_output=self.write_terminal, tab=self)
        except Exception as err:
            await self.write_terminal(f"[ERRO] {err}\n")
