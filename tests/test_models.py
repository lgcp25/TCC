import unittest
import sys
import os

# Adiciona o diretório raiz e o diretório app ao path para poder importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from models.nmap import Nmap
from models.gobuster import Gobuster
from models.sqlmap import Sqlmap
from models.nikto import Nikto
from models.netcat import Netcat

class TestModels(unittest.TestCase):

    def test_nmap_build_command(self):
        nmap = Nmap()
        self.assertEqual(nmap.name, "Nmap")
        self.assertEqual(nmap.binary, "nmap")
        
        # Teste do Profile 1
        cmd = nmap.build_command(target="http://example.com", mode="1")
        self.assertIn("nmap", cmd)
        self.assertIn("-sT", cmd)
        self.assertIn("example.com", cmd)

        # Teste do Profile 5 com porta válida
        cmd = nmap.build_command(target="127.0.0.1", mode="5", port="80")
        self.assertIn("-p", cmd)
        self.assertIn("80", cmd)

        # Teste do Profile 5 com porta inválida
        with self.assertRaises(ValueError):
            nmap.build_command(target="127.0.0.1", mode="5", port="invalid_port")

        # Teste com alvo inválido
        with self.assertRaises(ValueError):
            nmap.build_command(target="http://example com", mode="1")

    def test_gobuster_build_command(self):
        gobuster = Gobuster()
        self.assertEqual(gobuster.name, "Gobuster")
        self.assertEqual(gobuster.binary, "gobuster")

        # Teste de execução padrão do modo dir
        cmd = gobuster.build_command(
            target="http://example.com",
            mode="1",
            wordlist="/wordlist.txt",
            threads="10",
            extensions="php,txt",
            status_codes="200,301",
            follow_redirect=True,
            timeout=10,
            cookies="PHPSESSID=123"
        )
        self.assertIn("gobuster", cmd)
        self.assertIn("dir", cmd)
        self.assertIn("-u", cmd)
        self.assertIn("http://example.com", cmd)
        self.assertIn("-w", cmd)
        self.assertIn("/wordlist.txt", cmd)
        self.assertIn("-x", cmd)
        self.assertIn("php,txt", cmd)
        self.assertIn("-c", cmd)
        self.assertIn("PHPSESSID=123", cmd)

    def test_sqlmap_build_command(self):
        sqlmap = Sqlmap()
        self.assertEqual(sqlmap.name, "SQLmap")
        self.assertEqual(sqlmap.binary, "sqlmap")

        # Teste de execução padrão do sqlmap
        cmd = sqlmap.build_command(
            target="http://example.com/vuln.php?id=1",
            level="3",
            risk="2",
            technique="U",
            get_dbs=True,
            cookies_str="PHPSESSID=123"
        )
        self.assertIn("sqlmap", cmd)
        self.assertIn("-u", cmd)
        self.assertIn("http://example.com/vuln.php?id=1", cmd)
        self.assertIn("--level", cmd)
        self.assertIn("3", cmd)
        self.assertIn("--risk", cmd)
        self.assertIn("2", cmd)
        self.assertIn("--technique", cmd)
        self.assertIn("U", cmd)
        self.assertIn("--dbs", cmd)
        self.assertIn("--cookie", cmd)
        self.assertIn("PHPSESSID=123", cmd)

    def test_nikto_build_command(self):
        nikto = Nikto()
        self.assertEqual(nikto.name, "Nikto")
        self.assertTrue(nikto.binary.endswith("nikto.pl"))

        cmd = nikto.build_command(
            host="127.0.0.1",
            port="8080",
            ssl_switch=True,
            tuning="2",
            user_agent="1"
        )
        self.assertIn("-h", cmd)
        self.assertIn("127.0.0.1", cmd)
        self.assertIn("-p", cmd)
        self.assertIn("8080", cmd)
        self.assertIn("-ssl", cmd)
        self.assertIn("-Tuning", cmd)
        self.assertIn("8", cmd)
        self.assertIn("-useragent", cmd)

    def test_netcat_build_command(self):
        netcat = Netcat()
        self.assertEqual(netcat.name, "Netcat")
        self.assertEqual(netcat.binary, "nc")

        # Modo listener
        cmd = netcat.build_command(mode="1", host=None, port="4444")
        self.assertIn("-lvnp", cmd)
        self.assertIn("4444", cmd)

        # Modo conexão com host ausente
        with self.assertRaises(ValueError):
            netcat.build_command(mode="2", host=None, port="4444")

if __name__ == '__main__':
    unittest.main()
