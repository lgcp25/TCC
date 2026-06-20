import unittest
import sys
import os

# Adiciona o diretório raiz e o diretório app ao path para poder importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from unittest.mock import patch, MagicMock, AsyncMock
from utils import sanitize, valid_url, valid_port, format_cookies, normalize_logs, copy_to_clipboard, open_url

class TestUtils(unittest.IsolatedAsyncioTestCase):

    def test_sanitize(self):
        self.assertEqual(sanitize("http://example.com"), "example.com")
        self.assertEqual(sanitize("https://example.com"), "example.com")
        self.assertEqual(sanitize("example.com"), "example.com")
        self.assertEqual(sanitize(""), "")
        self.assertEqual(sanitize(None), "")

    def test_valid_url(self):
        self.assertTrue(valid_url("example.com"))
        self.assertTrue(valid_url("192.168.1.1"))
        self.assertFalse(valid_url(""))
        self.assertFalse(valid_url("example com"))

    def test_valid_port(self):
        self.assertTrue(valid_port("80"))
        self.assertTrue(valid_port("443"))
        self.assertTrue(valid_port("65535"))
        self.assertFalse(valid_port("0"))
        self.assertFalse(valid_port("65536"))
        self.assertFalse(valid_port("-80"))
        self.assertFalse(valid_port("abc"))

    def test_format_cookies(self):
        cookies = {"PHPSESSID": "abcdef123456", "security": "low"}
        self.assertEqual(format_cookies(cookies), "PHPSESSID=abcdef123456; security=low")
        self.assertIsNone(format_cookies({}))
        self.assertIsNone(format_cookies(None))

    def test_normalize_logs(self):
        raw_logs = "[10:20:30] Starting @ Example\n\x1b[31mError message\x1b[0m\n[=======] 100%"
        expected = "Error message"
        self.assertEqual(normalize_logs(raw_logs), expected)
        self.assertEqual(normalize_logs(""), "")
        self.assertEqual(normalize_logs(None), "")

    @patch('subprocess.Popen')
    def test_copy_to_clipboard_with_page(self, mock_popen):
        mock_popen.side_effect = Exception("No clip tool")
        mock_page = MagicMock()
        result = copy_to_clipboard("test text", page=mock_page)
        self.assertTrue(result)
        self.assertEqual(mock_page.clipboard, "test text")
        mock_page.update.assert_called_once()

    async def test_open_url_page(self):
        mock_page = AsyncMock()
        # Força falha no Popen para testar o fallback na chamada do flet page
        with patch('subprocess.Popen', side_effect=Exception("No subp")):
            await open_url(mock_page, "http://target.com")
            mock_page.launch_url.assert_called_once_with("http://target.com")

if __name__ == '__main__':
    unittest.main()
