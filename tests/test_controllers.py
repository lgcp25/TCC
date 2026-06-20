import unittest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Adiciona o diretório raiz e o diretório app ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from controllers.ai_controller import AiController
from controllers.report_controller import ReportController

class TestControllers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Mocks para o app principal
        self.mock_app = MagicMock()
        self.mock_app.report_findings = []
        self.mock_app.set_loading = MagicMock()

        # Mocks para a aba (view)
        self.mock_tab = AsyncMock()
        self.mock_tab.name = "Nmap"
        self.mock_tab.terminal_buffer = "Some terminal scan output"
        self.mock_tab.last_command = "nmap -sT 127.0.0.1"
        self.mock_tab.phase = "Reconnaissance"
        
        # Síncronos mockados na aba
        self.mock_tab.show_popup = MagicMock()

    @patch('controllers.ai_controller.ai_service')
    async def test_ai_controller_explain(self, mock_ai_service):
        mock_ai_service.analyze_results = AsyncMock(return_value="Explicação da IA")
        controller = AiController(self.mock_app)
        
        await controller.explain(self.mock_tab)
        
        # Verifica se limpou a tela de IA, chamou o analyze_results com os parâmetros corretos e escreveu o resultado
        self.mock_tab.clear_ai.assert_called_once()
        mock_ai_service.analyze_results.assert_called_once_with(
            "Nmap", "Some terminal scan output", command="nmap -sT 127.0.0.1"
        )
        self.mock_tab.write_ai.assert_called_once_with("Explicação da IA")
        self.mock_app.set_loading.assert_any_call("IA analisando resultados...")
        self.mock_app.set_loading.assert_any_call("", False)

    @patch('controllers.ai_controller.ai_service')
    async def test_ai_controller_explain_empty_terminal(self, mock_ai_service):
        self.mock_tab.terminal_buffer = ""
        controller = AiController(self.mock_app)
        
        await controller.explain(self.mock_tab)
        
        # Não deve chamar analyze_results e deve avisar o usuário
        mock_ai_service.analyze_results.assert_not_called()
        self.mock_tab.show_popup.assert_called_once_with("Aviso", "Terminal vazio.")

    @patch('controllers.report_controller.ai_service')
    async def test_report_controller_add_to_report(self, mock_ai_service):
        mock_ai_service.generate_formal_report = AsyncMock(return_value="Relatório Formal da IA")
        controller = ReportController(self.mock_app)
        
        await controller.add_to_report(self.mock_tab)
        
        # Verifica se gerou o relatório e inseriu no app
        mock_ai_service.generate_formal_report.assert_called_once_with(
            "Nmap", "Some terminal scan output", command="nmap -sT 127.0.0.1"
        )
        self.assertEqual(len(self.mock_app.report_findings), 1)
        self.assertEqual(self.mock_app.report_findings[0], {
            "tool": "Nmap",
            "analysis": "Relatório Formal da IA",
            "command": "nmap -sT 127.0.0.1"
        })
        self.mock_tab.show_popup.assert_called_once_with("Sucesso", "Achado adicionado ao relatório.")

    async def test_report_controller_add_to_report_empty(self):
        self.mock_tab.terminal_buffer = ""
        controller = ReportController(self.mock_app)
        
        await controller.add_to_report(self.mock_tab)
        
        self.mock_tab.show_popup.assert_called_once_with("Aviso", "Nada para adicionar.")
        self.assertEqual(len(self.mock_app.report_findings), 0)

if __name__ == '__main__':
    unittest.main()
