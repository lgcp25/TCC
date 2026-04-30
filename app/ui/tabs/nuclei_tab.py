import flet as ft
from ui.tool_tab import ToolTab
from config import INPUT_STYLE
from tools.nuclei import Nuclei


class NucleiTab(ToolTab):
    def __init__(self, app, name):
        super().__init__(
            app,
            name,
            "Análise Dinâmica / Templates",
            "https://nuclei.projectdiscovery.io/",
            ft.Icons.RADAR,
            ft.Icons.SEARCH,
            description="O Nuclei é um scanner de vulnerabilidades muito rápido, baseado em templates YAML. Ele consegue identificar milhares de falhas conhecidas (CVEs), painéis expostos e erros de configuração.",
            help_text="""GUIA TÉCNICO NUCLEI:

Scanner de vulnerabilidades baseado em 'Templates' (provas de conceito escritas em YAML).

1. EXPLICAÇÃO DOS CAMPOS:
   - ALVO (-u): A URL ou IP que será analisado (ex: http://meu-alvo.com).
   - GRUPO DE TEMPLATES: 
     * CVEs: Busca falhas específicas com ID mundial (ex: CVE-2021-44228).
     * Web: Foca em vulnerabilidades de aplicações (XSS, LFI, RCE).
     * Painéis: Identifica telas de login que não deveriam estar públicas.
   - SEVERIDADE: Filtra as falhas encontradas. 'Critical' e 'High' indicam riscos imediatos de invasão.
   - RPS (Rate Limit): Controla a velocidade do scan. Valores altos (300+) podem ser interpretados como um ataque de negação de serviço (DoS).
   - ATUALIZAR TEMPLATES: Garante que o Nuclei baixe as centenas de novos templates criados pela comunidade toda semana.

2. EXEMPLOS DE COMANDO GERADO:
   - Scan Geral de CVEs: nuclei -u http://dvwa -t cves/ -severity critical,high
   - Scan Web com Limite de Velocidade: nuclei -u http://dvwa -t views/ -rl 100
   - Scan Completo com Logs: nuclei -u http://dvwa -o resultado.txt

3. DICA: 
   O Nuclei é revolucionário por ser 'Community Powered'. Ele permite que um pesquisador descubra uma falha de manhã e, à tarde, o mundo todo já tenha um template para se proteger."""
        )
        self.nuclei = Nuclei()

        input_style = INPUT_STYLE

        # Controles
        self.target = ft.TextField(
            label="URL / Host Alvo",
            value="http://dvwa:80",
            **input_style
        )

        self.template_group = ft.Dropdown(
            label="Grupo de Templates",
            value="Todos (Padrão)",
            options=[
                ft.dropdown.Option("Todos (Padrão)"),
                ft.dropdown.Option("CVEs"),
                ft.dropdown.Option("Vulnerabilidades Web"),
                ft.dropdown.Option("Painéis Expostos"),
                ft.dropdown.Option("Configurações Padrão"),
                ft.dropdown.Option("Tecnologias"),
            ],
            **input_style
        )

        self.severity = ft.Dropdown(
            label="Severidade Mínima",
            value="Todas",
            options=[
                ft.dropdown.Option("Todas"),
                ft.dropdown.Option("info"),
                ft.dropdown.Option("low"),
                ft.dropdown.Option("medium"),
                ft.dropdown.Option("high"),
                ft.dropdown.Option("critical"),
            ],
            **input_style
        )

        self.rate_limit = ft.TextField(
            label="Limite de Requisições (RPS)",
            value="150",
            **input_style
        )

        self.update_templates = ft.Switch(
            label="Atualizar Templates antes de rodar",
            value=False
        )

        # Montagem da UI
        self.left_col.controls.extend([
            ft.Container(height=10),
            self.target,
            self.template_group,
            self.severity,
            self.rate_limit,
            self.update_templates
        ])
        self.add_manual_controls()

    def reset_fields(self):
        self.target.value = "http://dvwa:80"
        self.template_group.value = "Todos (Padrão)"
        self.severity.value = "Todas"
        self.rate_limit.value = "150"
        self.update_templates.value = False
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
                cmd_list = [self.nuclei.binary] + shlex.split(self.raw_cmd.value)
            else:
                cmd_list = self.nuclei.build_command(
                    target=self.target.value,
                    template_group=self.template_group.value,
                    severity=self.severity.value,
                    rate_limit=self.rate_limit.value,
                    update_templates=self.update_templates.value
                )
            self.last_command = self.nuclei.pretty_command(cmd_list)
            await self.write_terminal(f"[COMANDO] {self.last_command}\n\n")
            await self.app.run_docker(self.nuclei.docker_service, cmd_list, on_output=self.write_terminal, tab=self)
        except Exception as err:
            await self.write_terminal(f"[ERRO] {err}\n")
