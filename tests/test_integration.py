import unittest
import sys
import os
import asyncio
import subprocess

# Adiciona o diretório raiz e o diretório app ao path para poder importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from services.tool_executor import ToolExecutor
from config import DOCKER_DIR

def is_docker_env_available():
    """Verifica se os containers do Docker Compose do Vaporeon estão online."""
    try:
        res = subprocess.run(
            ["docker", "compose", "ps", "--status", "running"], 
            cwd=DOCKER_DIR, 
            capture_output=True, 
            text=True
        )
        if "pentester" in res.stdout:
            return True
    except Exception:
        pass

    try:
        res = subprocess.run(
            ["docker-compose", "ps", "--status", "running"], 
            cwd=DOCKER_DIR, 
            capture_output=True, 
            text=True
        )
        if "pentester" in res.stdout:
            return True
    except Exception:
        pass

    return False

class TestIntegration(unittest.IsolatedAsyncioTestCase):

    @unittest.skipUnless(is_docker_env_available(), "Containers Docker Compose do Vaporeon não estão rodando")
    async def test_docker_command_execution_integration(self):
        executor = ToolExecutor()
        outputs = []
        finished_event = asyncio.Event()

        async def on_output(text):
            outputs.append(text)

        async def on_finish():
            finished_event.set()

        # Executa um simples comando 'echo' de teste dentro do container 'pentester'
        executor.execute(
            container="pentester", 
            cmd=["echo", "integration_test_success"], 
            on_output=on_output,
            on_finish=on_finish
        )

        # Aguarda a conclusão do comando com timeout de 10 segundos
        try:
            await asyncio.wait_for(finished_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            self.fail("O comando integrado no Docker excedeu o tempo limite.")

        # Consolida a saída
        full_output = "".join(outputs)
        
        # Verifica se o fluxo inteiro (Executor -> Runner -> Docker -> Callback) funcionou
        self.assertIn("integration_test_success", full_output)
        self.assertIn("[Finalizado]", full_output)

if __name__ == '__main__':
    unittest.main()
