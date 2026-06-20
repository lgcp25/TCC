import asyncio
import logging
import services.docker_runner as docker_runner
from config import THEME_BG, THEME_CARD, THEME_BORDER, DOCKER_DIR


logger = logging.getLogger(__name__)


class ToolExecutor:
    def __init__(self):
        self.current_proc = None
        
    def execute(self, container, cmd, on_output, tab=None, on_finish=None):
                
        docker_runner.run_docker_turbo(self, container, cmd, on_output,on_finish)
        
    async def restart_docker(self):
            success = await asyncio.to_thread(
                docker_runner.restart_environment
            )
            return success
            
    def initialize_docker(self):        
        
        docker_runner.docker_init()

   

    def cancel_process(self, on_output=None):
        docker_runner.cancel_process(self, on_output)
        