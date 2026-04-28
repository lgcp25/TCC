from fpdf import FPDF
import datetime
import os
import re

class PentestPDF(FPDF):
    def header(self):
        # Cabeçalho Formal e Sóbrio
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 0, 0) # Preto total
        self.cell(0, 10, 'VAPOREON PENTESTER SUITE - RELATÓRIO TÉCNICO', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.set_text_color(50, 50, 50)
        self.cell(0, 5, f'Gerado em: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        self.ln(5)
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'VaporeonAI Security Report - Página {self.page_no()} / {{nb}}', 0, 0, 'C')

    def add_executive_summary(self, summary_text):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0) # Título Preto
        self.cell(0, 10, '1. SUMÁRIO EXECUTIVO', 0, 1, 'L')
        self.ln(2)
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        
        # Limpeza para o sumário
        clean_summary = self._clean_markdown(summary_text)
        self.multi_cell(0, 6, clean_summary)
        self.ln(10)

    def _clean_markdown(self, text):
        # Remove asteriscos duplos (bold)
        text = text.replace('**', '')
        # Tenta substituir marcadores de lista (* ou -) por numeração simples
        lines = text.split('\n')
        new_lines = []
        list_count = 1
        for line in lines:
            trimmed = line.strip()
            if trimmed.startswith('* ') or trimmed.startswith('- '):
                new_lines.append(f"{list_count}. {trimmed[2:]}")
                list_count += 1
            else:
                new_lines.append(line)
                if not trimmed: list_count = 1 # Reseta contador em parágrafos novos
        
        return "\n".join(new_lines).replace('###', '').replace('🔴', '[!]').replace('🟠', '[+]').replace('🟡', '[-]').replace('🟢', '[*]')

    def add_finding(self, index, tool_name, analysis, command="N/A"):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(0, 0, 0) # Preto
        self.cell(0, 10, f' Achado #{index}: {tool_name.upper()}', 0, 1, 'L', fill=True)
        
        self.ln(2)
        self.set_font('Courier', 'B', 8)
        self.set_text_color(60, 60, 60)
        self.cell(0, 5, f' > Comando: {command}', 0, 1, 'L')
        self.ln(2)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        
        clean_analysis = self._clean_markdown(analysis)
        self.multi_cell(0, 6, clean_analysis)
        self.ln(10)

def generate_pentest_pdf(findings, output_path, summary_text="Relatório técnico consolidado."):
    pdf = PentestPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Capa em tons de cinza e preto
    pdf.ln(60)
    pdf.set_font('Arial', 'B', 28)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 20, 'RELATÓRIO DE PENTEST', 0, 1, 'C')
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, 'Auditoria de Segurança - VaporeonAI', 0, 1, 'C')
    pdf.ln(80)
    
    # Próxima Página: Sumário Executivo
    pdf.add_page()
    pdf.add_executive_summary(summary_text)
    
    # Detalhes Técnicos
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, '2. DETALHES TÉCNICOS POR FERRAMENTA', 0, 1, 'L')
    pdf.ln(5)
    
    for i, item in enumerate(findings, 1):
        tool = item.get('tool', 'Desconhecida')
        analysis = item.get('analysis', 'Sem análise')
        cmd = item.get('command', 'N/A')
        pdf.add_finding(i, tool, analysis, command=cmd)
    
    pdf.output(output_path)
    return output_path
