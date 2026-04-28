import flet as ft
import os
import datetime
import subprocess

class ToolTab:
    def __init__(self, app, name, phase, doc_url, icon, icon_off):
        self.app = app
        self.name = name
        self.phase = phase
        self.doc_url = doc_url
        self.icon = icon
        self.icon_off = icon_off
        self.last_command = ""

        # ESTILO DOS TÍTULOS (Aumentado e Estilizado)
        self.TEXT_TITLE = ft.TextStyle(
            size=14, 
            weight="bold", 
            color="white",
        )
        
        # Terminal (Fonte Aumentada para 13px)
        self.terminal_output = ft.ListView(expand=True, spacing=0, auto_scroll=True)
        self.terminal_container = ft.Container(
            content=self.terminal_output, 
            expand=True, 
            bgcolor="#05080D", 
            border_radius=8, 
            padding=15, 
            border=ft.border.all(1, "#1E293B")
        )
        self.terminal_buffer = ""

        # IA
        self.ai_output = ft.ListView(expand=True, spacing=10)
        self.ai_container = ft.Container(
            content=self.ai_output, 
            expand=True, 
            bgcolor="#0F172A", 
            border_radius=8, 
            padding=15, 
            border=ft.border.all(1, "#1E293B")
        )

        self.left_col = ft.Column(spacing=20, scroll=ft.ScrollMode.ALWAYS)
        
        # Header
        self.header = ft.Row([
            ft.Column([
                ft.Row([ft.Icon(icon, color="blue400", size=32), ft.Text(f"{name} - Tool", size=30, weight="bold", color="white")]),
                ft.Row([
                    ft.Text("Fase do Pentest:", size=12, color="blueGrey400"),
                    ft.Container(
                        content=ft.Row([ft.Icon(ft.Icons.TRACK_CHANGES, size=14, color="amber"), ft.Text(phase, size=11, color="amber", weight="bold")], spacing=5),
                        padding=ft.padding.symmetric(horizontal=12, vertical=4), border=ft.border.all(1, "amber"), border_radius=20
                    )
                ])
            ], expand=True),
            ft.ElevatedButton("Documentação Oficial", icon=ft.Icons.DESCRIPTION, on_click=self.open_doc, bgcolor="#1E293B", color="white")
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Ações
        self.actions_section = ft.Container(
            content=ft.Column([
                ft.Row([ft.Container(width=5, height=15, bgcolor="blue400"), ft.Text("AÇÕES", style=self.TEXT_TITLE)]),
                ft.Row([
                    ft.ElevatedButton("Executar Scan", icon=ft.Icons.PLAY_ARROW, bgcolor="green700", color="white", on_click=self.run, height=45, expand=True),
                    ft.ElevatedButton("Explicar Resultado (IA)", icon=ft.Icons.AUTO_AWESOME, bgcolor="blue700", color="white", on_click=self.explain, height=45, expand=True),
                    ft.ElevatedButton("Dicas e Passos", icon=ft.Icons.LIGHTBULB_OUTLINE, bgcolor="purple700", color="white", on_click=self.show_tips, height=45, expand=True),
                    ft.OutlinedButton("Explicar Comando", icon=ft.Icons.CODE, on_click=self.explain_cmd, height=45, expand=True, style=ft.ButtonStyle(color="white"))
                ], spacing=10),
                ft.Row([
                    ft.ElevatedButton("Adicionar ao Relatório", icon=ft.Icons.ADD_CIRCLE_OUTLINE, bgcolor="teal700", color="white", on_click=self.add_to_report, height=50, expand=True),
                    ft.ElevatedButton("Salvar Relatório (.pdf)", icon=ft.Icons.PICTURE_AS_PDF, bgcolor="orange700", color="white", on_click=self.finalize_pdf, height=50, expand=True),
                    ft.ElevatedButton("Cancelar", icon=ft.Icons.STOP, on_click=self.cancel, height=50, bgcolor="red900", color="white", expand=True)
                ], spacing=10)
            ], spacing=10),
            padding=15, bgcolor="#0F172A", border_radius=10, border=ft.border.all(1, "#1E293B")
        )

        self.view = ft.Container(
            content=ft.Column([
                self.header,
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Container(content=ft.Row([ft.Container(width=5, height=15, bgcolor="blue400"), ft.Text("CONFIGURAÇÃO", style=self.TEXT_TITLE)]), padding=ft.padding.only(bottom=10)),
                            self.left_col,
                            ft.Container(expand=True),
                            ft.OutlinedButton("Limpar Campos", icon=ft.Icons.DELETE_OUTLINE, on_click=lambda _: self.reset_fields() if hasattr(self, 'reset_fields') else None, width=float("inf"), style=ft.ButtonStyle(color="blueGrey200"))
                        ], expand=True),
                        width=300, bgcolor="#0F172A", padding=20, border_radius=10, border=ft.border.all(1, "#1E293B")
                    ),
                    ft.Column([
                        ft.Container(content=ft.Row([ft.Row([ft.Container(width=5, height=15, bgcolor="blue400"), ft.Text("RESULTADO DO SCAN", style=self.TEXT_TITLE)]), ft.OutlinedButton("Copiar Logs", icon=ft.Icons.COPY, on_click=self.copy_logs, style=ft.ButtonStyle(color="blueGrey200"))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=ft.padding.only(bottom=5)),
                        self.terminal_container,
                        self.actions_section
                    ], expand=True, spacing=10),
                    ft.Column([
                        ft.Container(content=ft.Row([ft.Container(width=5, height=15, bgcolor="blue400"), ft.Text("ANÁLISE DA IA", style=self.TEXT_TITLE)]), padding=ft.padding.only(bottom=5)),
                        self.ai_container,
                        ft.Container(content=ft.Column([ft.Row([ft.Icon(ft.Icons.REPORT_PROBLEM_OUTLINED, color="amber", size=16), ft.Text("Aviso Importante", color="amber", weight="bold", size=12)]), ft.Text("Esta análise é gerada por IA e deve ser interpretada com cautela.", size=10, color="blueGrey400")], spacing=5), padding=15, border=ft.border.all(1, "amber800"), bgcolor="#1A1500", border_radius=8)
                    ], width=500, spacing=10)
                ], expand=True, spacing=15)
            ], expand=True, spacing=20),
            padding=20, bgcolor="#020617"
        )

    async def open_doc(self, e):
        try: subprocess.Popen(["xdg-open", self.doc_url])
        except: await self.app.page.launch_url(self.doc_url)

    async def write_ai(self, text):
        try:
            md = ft.Markdown(text, selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB)
            self.ai_output.controls.append(md)
        except: self.ai_output.controls.append(ft.Text(text, color="blueGrey100", size=13))
        self.ai_output.update()

    async def explain(self, e):
        if not self.terminal_buffer.strip(): return self.show_popup("Aviso", "Terminal vazio.")
        from services.ai_service import ai_service
        await self.clear_ai()
        self.app.set_loading("IA analisando resultados...")
        ans = await ai_service.analyze_results(self.name, self.terminal_buffer, command=self.last_command)
        await self.write_ai(ans)
        self.app.set_loading("", False)

    async def explain_cmd(self, e):
        if not self.last_command: return self.show_popup("Aviso", "Nenhum comando.")
        from services.ai_service import ai_service
        await self.clear_ai()
        self.app.set_loading("IA explicando comando...")
        prompt = f"Explique: `{self.last_command}`. Use Markdown."
        ans = await ai_service.analyze_results("Explicação", prompt, command=self.last_command)
        await self.write_ai(ans)
        self.app.set_loading("", False)

    async def show_tips(self, e):
        from services.ai_service import ai_service
        await self.clear_ai()
        self.app.set_loading("IA buscando dicas...")
        ans = await ai_service.get_tool_tips(self.name, self.phase, logs=self.terminal_buffer)
        await self.write_ai(ans)
        self.app.set_loading("", False)

    async def add_to_report(self, e):
        if not self.terminal_buffer.strip(): return self.show_popup("Aviso", "Nada para adicionar.")
        from services.ai_service import ai_service
        self.app.set_loading("Formatando descoberta...")
        analysis = await ai_service.generate_formal_report(self.name, self.terminal_buffer)
        self.app.report_findings.append({"tool": self.name, "analysis": analysis, "command": self.last_command})
        self.app.set_loading("", False)
        self.show_popup("Sucesso", "Achado adicionado ao relatório.")

    async def finalize_pdf(self, e):
        if not self.app.report_findings: return self.show_popup("Erro", "Relatório vazio.")
        from services.ai_service import ai_service
        from services.pdf_service import generate_pentest_pdf
        self.app.set_loading("Gerando Sumário...")
        summary = await ai_service.generate_executive_summary(self.app.report_findings)
        self.app.set_loading("Criando PDF...")
        try:
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(os.getcwd(), f"Relatorio_Vaporeon_{now}.pdf")
            generate_pentest_pdf(self.app.report_findings, path, summary_text=summary)
            self.app.report_findings = []
            self.show_popup("🏆 Relatório Gerado", f"Salvo em: {os.path.basename(path)}")
        except Exception as err: self.show_popup("Erro no PDF", str(err))
        self.app.set_loading("", False)

    def show_popup(self, title, message):
        def close_dlg(e): dlg.open = False; self.app.page.update()
        dlg = ft.AlertDialog(title=ft.Text(title, weight="bold"), content=ft.Text(message), actions=[ft.TextButton("OK", on_click=close_dlg)])
        self.app.page.dialog = dlg; dlg.open = True; self.app.page.update()

    def copy_logs(self, e):
        try: self.app.page.clipboard = self.terminal_buffer; self.app.page.update(); self.show_snack("📋 Logs copiados!", "blue")
        except: pass

    async def write_terminal(self, text):
        self.terminal_output.controls.append(ft.Text(text, color="#2DD4BF", font_family="RobotoMono", size=13))
        self.terminal_output.update(); self.terminal_buffer += text

    async def clear_ai(self): self.ai_output.controls.clear(); self.ai_output.update()
    async def clear_terminal(self): self.terminal_buffer = ""; self.terminal_output.controls.clear(); self.terminal_output.update()
    async def cancel(self, e):
        from services.docker_runner import cancel_process
        cancel_process()
        self.app.set_loading("Interrompido", False)
        await self.write_terminal("\n[PROCESSO CANCELADO PELO USUÁRIO]\n")
    def show_snack(self, m, c):
        sn = ft.SnackBar(ft.Text(m, color="white"), bgcolor=c); self.app.page.snack_bar = sn; sn.open = True; self.app.page.update()