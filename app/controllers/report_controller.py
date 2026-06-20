from services.ai_service import ai_service
import os
import datetime
import tempfile
import shutil

class ReportController:
    def __init__(self, app):
        self.app = app

    async def add_to_report(self, tab):
        if not tab.terminal_buffer.strip():
            tab.show_popup("Aviso", "Nada para adicionar.")
            return
        self.app.set_loading("Formatando descoberta...")
        analysis = await ai_service.generate_formal_report(tab.name, tab.terminal_buffer, command=tab.last_command)
        self.app.report_findings.append({"tool": tab.name, "analysis": analysis, "command": tab.last_command})
        self.app.set_loading("", False)
        tab.show_popup("Sucesso", "Achado adicionado ao relatório.")

    async def finalize_pdf(self, tab):
        if not self.app.report_findings:
            tab.show_popup("Erro", "Relatório vazio. Use 'Adicionar ao Relatório' primeiro.")
            return

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
            tab.show_popup("Erro no PDF", str(err))
            return

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
            tab.show_popup("Cancelado", "Exportação do PDF cancelada pelo usuário.")
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
            tab.show_popup("Erro ao salvar", str(err))
            return

        self.app.report_findings = []
        self.app.set_loading("", False)
        
        if is_fallback:
            tab.show_popup(
                "Relatório Gerado (Fallback)", 
                f"Não foi possível abrir a janela para escolher a pasta. O relatório foi salvo automaticamente em:\n{save_path}"
            )
        else:
            tab.show_popup("Relatório Gerado", f"Salvo em: {save_path}")
