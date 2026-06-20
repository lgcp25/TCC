import unittest
import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

# Adiciona o diretório raiz e o diretório app ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from services.ai_service import AIContext

class TestAIService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Cria um arquivo temporário para ser usado como arquivo de cache nos testes
        self.temp_cache_fd, self.temp_cache_path = tempfile.mkstemp()
        
        # Instancia o AIContext mas aponta para o cache temporário
        self.ai_context = AIContext()
        self.ai_context.cache_file = self.temp_cache_path
        self.ai_context.cache = {}

    def tearDown(self):
        # Fecha e remove o arquivo temporário
        os.close(self.temp_cache_fd)
        if os.path.exists(self.temp_cache_path):
            os.remove(self.temp_cache_path)

    def test_make_key(self):
        # Chaves iguais para os mesmos parâmetros
        key1 = self.ai_context.make_key("test_action", "nmap -sT", "some logs")
        key2 = self.ai_context.make_key("test_action", "nmap -sT", "some logs")
        self.assertEqual(key1, key2)

        # Chaves diferentes para logs ou comandos diferentes
        key3 = self.ai_context.make_key("test_action", "nmap -sT", "different logs")
        self.assertNotEqual(key1, key3)

    def test_load_cache_missing(self):
        # Se o arquivo não existir, retorna um cache vazio
        self.ai_context.cache_file = "non_existent_file.json"
        cache = self.ai_context.load_cache()
        self.assertEqual(cache, {})

    def test_load_cache_invalid_json(self):
        # Se o JSON for corrompido, retorna um cache vazio
        with open(self.temp_cache_path, "w", encoding="utf-8") as f:
            f.write("{invalid json")
        
        cache = self.ai_context.load_cache()
        self.assertEqual(cache, {})

    def test_save_and_load_cache(self):
        # Insere dados no cache, salva no disco e recarrega
        self.ai_context.cache = {"key123": "cached response"}
        self.ai_context.save_cache()

        new_context = AIContext()
        new_context.cache_file = self.temp_cache_path
        loaded_cache = new_context.load_cache()

        self.assertEqual(loaded_cache, {"key123": "cached response"})

    async def test_ask_ai_cache_hit(self):
        # Simula cache HIT: o método ask_ai deve retornar o valor do cache sem chamar o cliente AsyncGroq
        self.ai_context.api_key = "dummy_api_key"
        self.ai_context.cache = {"hash_key_123": "Resposta em cache do LLM"}

        # Chamamos ask_ai passando a key correspondente ao cache HIT
        result = await self.ai_context.ask_ai(
            system_prompt="sys", 
            user_content="user", 
            cache_key="hash_key_123"
        )
        
        self.assertEqual(result, "Resposta em cache do LLM")

if __name__ == '__main__':
    unittest.main()
