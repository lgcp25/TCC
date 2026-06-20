import unittest
import sys
import os
import tempfile

# Adiciona o diretório raiz e o diretório app ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from services.pdf_service import generate_pentest_pdf

class TestPdfService(unittest.TestCase):

    def setUp(self):
        # Cria um caminho para o PDF de teste
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_pdf_path = os.path.join(self.temp_dir.name, "test_report.pdf")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_generate_pentest_pdf(self):
        findings = [
            {
                "tool": "Nmap",
                "command": "nmap -sT 127.0.0.1",
                "analysis": "### Portas Abertas:\n- 80/tcp (http): Apache\n- 443/tcp (https): Apache"
            },
            {
                "tool": "Gobuster",
                "command": "gobuster dir -u http://127.0.0.1 -w w.txt",
                "analysis": "### Diretórios:\n- /admin (Status: 200)\n- /config.php (Status: 200)"
            }
        ]
        
        # Gera o PDF
        path = generate_pentest_pdf(
            findings=findings,
            output_path=self.output_pdf_path,
            summary_text="Sumário de teste executivo do pentest."
        )
        
        # Verifica se o arquivo foi criado
        self.assertEqual(path, self.output_pdf_path)
        self.assertTrue(os.path.exists(self.output_pdf_path))
        
        # Verifica se o arquivo tem conteúdo (tamanho > 0)
        self.assertGreater(os.path.getsize(self.output_pdf_path), 0)

if __name__ == '__main__':
    unittest.main()
