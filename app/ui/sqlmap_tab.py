import flet as ft
from ui.tool_tab import ToolTab
from tools.sqlmap import Sqlmap

class SqlmapTab(ToolTab):
    def __init__(self, app, name):
        super().__init__(
            app, 
            name, 
            "Exploração / Injeção", 
            "https://github.com/sqlmapproject/sqlmap/wiki/Usage",
            ft.Icons.STORAGE,
            ft.Icons.DATA_EXPLORATION
        )
        self.sqlmap = Sqlmap()

        input_style = dict(
            border_color="transparent", 
            filled=True, 
            bgcolor="#1F2937", 
            text_size=12, 
            label_style=ft.TextStyle(size=12, color=ft.Colors.BLUE_GREY_400), 
            content_padding=10, 
            height=40
        )

        self.target = ft.TextField(label="URL Alvo (com parâmetro)", value="http://site.com/page.php?id=1", **input_style)
        self.param = ft.TextField(label="Parâmetro (-p)", value="id", **input_style)
        self.data = ft.TextField(label="Dados POST (--data)", value="", **input_style)
        self.mode = ft.Dropdown(
            label="Modo de Operação",
            value="Teste básico de SQLi (--batch)",
            options=[
                ft.dropdown.Option("Teste básico de SQLi (--batch)"),
                ft.dropdown.Option("Dump de Banco de Dados (--dump)"),
                ft.dropdown.Option("Listar Bancos (--dbs)"),
                ft.dropdown.Option("Listar Tabelas (--tables)"),
            ],
            **input_style
        )

        self.left_col.controls.extend([
            self.target,
            self.param,
            self.data,
            self.mode
        ])

    def reset_fields(self):
        self.target.value = "http://site.com/page.php?id=1"
        self.param.value = "id"
        self.data.value = ""
        self.mode.value = "Teste básico de SQLi (--batch)"
        self.app.page.update()

    async def run(self, e):
        await self.clear_terminal()
        try:
            mode_map = {
                "Teste básico de SQLi (--batch)": ["--batch"],
                "Dump de Banco de Dados (--dump)": ["--dump", "--batch"],
                "Listar Bancos (--dbs)": ["--dbs", "--batch"],
                "Listar Tabelas (--tables)": ["--tables", "--batch"],
            }
            args = ["-u", self.target.value, "-p", self.param.value] + mode_map.get(self.mode.value, [])
            if self.data.value:
                args += ["--data", self.data.value]

            cmd_list = self.sqlmap.build_command(args)
            self.last_command = " ".join(cmd_list)
            await self.app.run_docker("pentester", cmd_list, on_output=self.write_terminal)
        except Exception as err:
            await self.write_terminal(f"ERRO: {err}")
