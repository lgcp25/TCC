import flet as ft
import os
import shutil
import datetime
import tempfile
import subprocess
from config import THEME_BG, THEME_CARD, THEME_BORDER, THEME_INPUT_BG, THEME_TERMINAL_BG, INPUT_STYLE

class ToolTab:
    def __init__(self, app, name, phase, doc_url, icon, icon_off, description="", help_text=""):
        self.app = app
        self.name = name
        self.phase = phase
        self.doc_url = doc_url
        self.icon = icon
        self.icon_off = icon_off
        self.description = description
        self.help_text = help_text
        self.last_command = ""

        self.TEXT_TITLE = ft.TextStyle(
            size=14, 
            weight="bold", 
            color="white",
        )
        
        self.terminal_output = ft.TextField(
            value="",
            multiline=True,
            read_only=True,
            expand=True,
            border=ft.InputBorder.NONE, 
            filled=False,              
            text_size=13,
            text_style=ft.TextStyle(font_family="RobotoMono", color="#2DD4BF"),
            content_padding=0,
        )

        self.terminal_container = ft.Container(
            content=self.terminal_output, 
            expand=True, 
            bgcolor=THEME_TERMINAL_BG, 
            border_radius=8, 
            padding=15, 
            border=ft.border.all(1, THEME_BORDER)
        )




        # IA
        self.ai_output = ft.ListView(expand=True, spacing=10)
        self.ai_container = ft.Container(
            content=self.ai_output, 
            expand=True, 
            bgcolor=THEME_CARD, 
            border_radius=8, 
            padding=15, 
            border=ft.border.all(1, THEME_BORDER)
        )

        self.left_col = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
        
        self.free_cmd_switch = ft.Switch(
            label="Modo Comando Manual", 
            value=False, 
            active_color=ft.Colors.PURPLE_400
        )
        self.raw_cmd = ft.TextField(
            label="Comando Manual Completo",
            value="",
            disabled=True,
            **INPUT_STYLE
        )

        self.free_cmd_switch.on_change = self._toggle_free_mode_base

        # Cabeçalho
        self.header = ft.Row([
            ft.Column([
                ft.Row([ft.Icon(icon, color="blue400", size=32), ft.Text(f"{name} - Tool", size=30, weight="bold", color="white")]),
                ft.Row([
                    ft.Text("Fase do Pentest:", size=12, color="blueGrey400"),
                    ft.Container(
                        content=ft.Row([ft.Icon(ft.Icons.TRACK_CHANGES, size=14, color="amber"), ft.Text(phase, size=11, color="amber", weight="bold")], spacing=5),
                        padding=ft.padding.symmetric(horizontal=12, vertical=4), border=ft.border.all(1, "amber"), border_radius=20
                    )
                ]),
                ft.Container(height=5),
                ft.Text(self.description, size=12, color="blueGrey300", max_lines=3, overflow=ft.TextOverflow.ELLIPSIS)
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
            padding=15, bgcolor=THEME_CARD, border_radius=10, border=ft.border.all(1, THEME_BORDER)
        )

        self.view = ft.Container(
            content=ft.Column([
                self.header,
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Container(content=ft.Row([ft.Container(width=5, height=15, bgcolor="blue400"), ft.Text("CONFIGURAÇÃO", style=self.TEXT_TITLE)]), padding=ft.padding.only(bottom=10)),
                            self.left_col,

                            ft.OutlinedButton("Limpar Campos", icon=ft.Icons.DELETE_OUTLINE, on_click=lambda _: self.reset_fields() if hasattr(self, 'reset_fields') else None, width=float("inf"), style=ft.ButtonStyle(color="blueGrey200"))
                        ], expand=True),
                        width=300, bgcolor=THEME_CARD, padding=20, border_radius=10, border=ft.border.all(1, THEME_BORDER)
                    ),
                    ft.Column([
                        ft.Container(
                            content=ft.Row([
                                ft.Row([
                                    ft.Container(width=5, height=15, bgcolor="blue400"), 
                                    ft.Text("RESULTADO DO SCAN", style=self.TEXT_TITLE),
                                    ft.IconButton(
                                        icon=ft.Icons.HELP_OUTLINE, 
                                        icon_color="blue400", 
                                        icon_size=18,
                                        tooltip="Ajuda sobre os campos desta ferramenta",
                                        on_click=self.show_help
                                    ),
                                ], spacing=5), 
                                ft.OutlinedButton(
                                    "Copiar Logs", 
                                    icon=ft.Icons.COPY, 
                                    on_click=self.copy_logs, 
                                    style=ft.ButtonStyle(color="blueGrey200")
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), 
                            padding=ft.padding.only(bottom=5)
                        ),
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
        )

    @property
    def terminal_buffer(self):
        return self.terminal_output.value or ""

    def _toggle_free_mode_base(self, e):

        is_free = self.free_cmd_switch.value
        self.raw_cmd.disabled = not is_free
        
        for control in self.left_col.controls:
            if control not in [self.free_cmd_switch, self.raw_cmd] and hasattr(control, 'disabled'):
                control.disabled = is_free
                
        self.left_col.update()

    def add_manual_controls(self):
        self.left_col.controls.extend([
            ft.Divider(color=THEME_BORDER),
            self.free_cmd_switch,
            self.raw_cmd
        ])

    async def open_doc(self, e):
        try: subprocess.Popen(["xdg-open", self.doc_url])
        except: await self.app.page.launch_url(self.doc_url)
        
    async def show_help(self, e):
        await self.clear_terminal()
        help_header = f"--- GUIA DE USO: {self.name} ---\n\n"
        if not self.help_text:
            content = "Nenhuma ajuda detalhada disponível para esta ferramenta."
        else:
            content = self.help_text
        
        await self.write_terminal(help_header + content + "\n\n" + "-"*30 + "\n")

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
        ans = await ai_service.explain_command(self.last_command)
        await self.write_ai(ans)
        self.app.set_loading("", False)

    async def show_tips(self, e):
        from services.ai_service import ai_service
        await self.clear_ai()
        self.app.set_loading("IA buscando dicas...")
        ans = await ai_service.get_tool_tips(self.name, self.phase, command=self.last_command, logs=self.terminal_buffer)
        await self.write_ai(ans)
        self.app.set_loading("", False)

    async def add_to_report(self, e):
        if not self.terminal_buffer.strip(): return self.show_popup("Aviso", "Nada para adicionar.")
        from services.ai_service import ai_service
        self.app.set_loading("Formatando descoberta...")
        analysis = await ai_service.generate_formal_report(self.name, self.terminal_buffer, command=self.last_command)
        self.app.report_findings.append({"tool": self.name, "analysis": analysis, "command": self.last_command})
        self.app.set_loading("", False)
        self.show_popup("Sucesso", "Achado adicionado ao relatório.")

    async def finalize_pdf(self, e):
        if not self.app.report_findings:
            return self.show_popup("Erro", "Relatório vazio. Use 'Adicionar ao Relatório' primeiro.")

        from services.ai_service import ai_service
        from services.pdf_service import generate_pentest_pdf

        self.app.set_loading("Gerando Sumário...")
        summary = await ai_service.generate_executive_summary(self.app.report_findings)
        self.app.set_loading("Preparando PDF...")

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"Relatorio_Vaporeon_{now}.pdf"

        try:
            temp_path = os.path.join(tempfile.gettempdir(), default_name)
            generate_pentest_pdf(self.app.report_findings, temp_path, summary_text=summary)
        except Exception as err:
            self.app.set_loading("", False)
            return self.show_popup("Erro no PDF", str(err))

        save_path = None
        is_fallback = False
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            save_path = filedialog.asksaveasfilename(
                title="Salvar Relatório de Pentest",
                initialfile=default_name,
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("Todos os arquivos", "*.*")]
            )
            root.destroy()
        except Exception as tk_err:
            print(f"[PDF] Falha ao abrir diálogo salvar (tkinter): {tk_err}")
            try:
                downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                if not os.path.exists(downloads_dir):
                    downloads_dir = os.path.expanduser("~")
                save_path = os.path.join(downloads_dir, default_name)
                is_fallback = True
            except Exception as fallback_err:
                print(f"[PDF] Falha ao definir caminho fallback: {fallback_err}")
                save_path = None

        if not save_path:
            try:
                os.remove(temp_path)
            except:
                pass
            self.app.set_loading("", False)
            self.show_popup("Cancelado", "Exportação do PDF cancelada pelo usuário.")
            return

        if not save_path.endswith(".pdf"):
            save_path += ".pdf"

        try:
            shutil.copy2(temp_path, save_path)
            try:
                os.remove(temp_path)
            except:
                pass
        except Exception as err:
            self.app.set_loading("", False)
            return self.show_popup("Erro ao salvar", str(err))

        self.app.report_findings = []
        self.app.set_loading("", False)
        
        if is_fallback:
            self.show_popup(
                "Relatório Gerado (Fallback)", 
                f"Não foi possível abrir a janela para escolher a pasta. O relatório foi salvo automaticamente em:\n{save_path}"
            )
        else:
            self.show_popup("Relatório Gerado", f"Salvo em: {save_path}")

    def show_popup(self, title, message):
        def close_dlg(e): dlg.open = False; self.app.page.update()
        dlg = ft.AlertDialog(title=ft.Text(title, weight="bold"), content=ft.Text(message), actions=[ft.TextButton("OK", on_click=close_dlg)])
        self.app.page.dialog = dlg; dlg.open = True; self.app.page.update()

    async def copy_logs(self, e):
        if not self.terminal_buffer.strip():
            self.show_snack("⚠ Terminal vazio. Nada para copiar.", "amber800")
            return
            
        import platform
        import subprocess
        
        try:
            sistema = platform.system()
            
            if sistema == "Linux":
                try:
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
                    process.communicate(input=self.terminal_buffer.encode('utf-8'))
                except:
                    self.app.page.clipboard = self.terminal_buffer
                    
            elif sistema == "Windows":
                try:
                    process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
                    process.communicate(input=self.terminal_buffer.encode('utf-8'))
                except:
                    self.app.page.clipboard = self.terminal_buffer
            
            else:
                self.app.page.clipboard = self.terminal_buffer
            
            self.app.page.update()
            self.show_snack(f"{len(self.terminal_buffer)} caracteres copiados!", "blue")
            
        except Exception as err:
            self.show_snack("Erro ao copiar. Selecione manualmente no terminal.", "red900")

    async def write_terminal(self, text, force_update=False):
        import time
        import re
        
        if "Container docker-pentester" in text:
            text = re.sub(r"Container docker-pentester-run-[a-z0-9]+ (Creating|Created)[ \r\n]*", "", text)

        if not text: return

        if self.terminal_output.value is None:
            self.terminal_output.value = ""
        self.terminal_output.value += text
        
        current_time = time.time()
        if force_update or not hasattr(self, "_last_terminal_update") or (current_time - self._last_terminal_update) > 0.1:
            self.terminal_output.update()
            self._last_terminal_update = current_time

    async def clear_ai(self): 
        self.ai_output.controls.clear() 
        self.ai_output.update()
    async def clear_terminal(self): 
        self.terminal_output.value = "" 
        self.terminal_output.update()

    async def cancel(self, e):
        self.app.cancel_process(on_output=self.write_terminal, tab=self)
        
    def show_snack(self, m, c):
        sn = ft.SnackBar(ft.Text(m, color="white"), bgcolor=c) 
        self.app.page.snack_bar = sn
        sn.open = True 
        self.app.page.update()