from fpdf import FPDF
import datetime


class PentestPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 0, 0) 
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
        self.cell(0, 10, f'RELATÓRIO TÉCNICO - Página {self.page_no()} / {{nb}}', 0, 0, 'C')

    def add_executive_summary(self, summary_text):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0) 
        self.cell(0, 10, '1. SUMÁRIO EXECUTIVO', 0, 1, 'L')
        self.ln(2)
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        
        self.add_formatted_multicell(summary_text, regular_font_size=11, bold_font_size=11)
        self.ln(10)

    def add_formatted_multicell(self, text, regular_font_size=10, bold_font_size=10):
        lines = text.split('\n')
        processed_lines = []
        list_count = 1
        for line in lines:
            trimmed = line.strip()
            if trimmed.startswith('* ') or trimmed.startswith('- '):
                processed_lines.append((f"{list_count}. {trimmed[2:]}", False))
                list_count += 1
            else:

                is_bold = False
                clean_line = line
                if trimmed.startswith('###'):
                    is_bold = True
                    clean_line = trimmed.replace('###', '').strip()
                elif trimmed.startswith('**') and (trimmed.endswith('**') or trimmed.endswith('**:') or '**:' in trimmed):
                    is_bold = True
                    clean_line = trimmed.replace('**', '').strip()
                elif (trimmed.endswith(':') and len(trimmed.split()) <= 5) and not trimmed.startswith('http'):
                    is_bold = True
                    clean_line = trimmed
                
            
                if not trimmed:
                    list_count = 1
                    
                processed_lines.append((clean_line, is_bold))

        for line_text, is_bold in processed_lines:
            line_text = line_text.replace('🔴', '[!]').replace('🟠', '[+]').replace('🟡', '[-]').replace('🟢', '[*]')
            line_text = line_text.replace('**', '')
            
            trimmed = line_text.strip()
            if not trimmed:
                self.ln(3)
                continue
                
            self.set_x(self.l_margin)
            
            if is_bold:
                self.set_font('Arial', 'B', bold_font_size)
                self.multi_cell(self.epw, 6, line_text)
            else:
                self.set_font('Arial', '', regular_font_size)
                self.multi_cell(self.epw, 6, line_text)

    def add_finding(self, index, tool_name, analysis, command="N/A"):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(0, 0, 0) 
        self.cell(0, 10, f' Achado #{index}: {tool_name.upper()}', 0, 1, 'L', fill=True)
        
        self.ln(2)
        self.set_font('Courier', 'B', 8)
        self.set_text_color(60, 60, 60)
        self.cell(0, 5, f' > Comando: {command}', 0, 1, 'L')
        self.ln(2)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        
        self.add_formatted_multicell(analysis, regular_font_size=10, bold_font_size=10)
        self.ln(10)

def generate_pentest_pdf(findings, output_path, summary_text="Relatório técnico consolidado."):
    pdf = PentestPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.ln(60)
    pdf.set_font('Arial', 'B', 28)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 20, 'RELATÓRIO DE PENTEST', 0, 1, 'C')
    pdf.set_font('Arial', '', 16)
    pdf.cell(0, 10, 'Auditoria de Segurança - VaporeonAI', 0, 1, 'C')
    pdf.ln(80)
    
    pdf.add_page()
    pdf.add_executive_summary(summary_text)
    
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
