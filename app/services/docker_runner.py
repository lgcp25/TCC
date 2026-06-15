import subprocess
import threading
import os
import logging
import asyncio
import traceback
from config import DOCKER_DIR

logger = logging.getLogger(__name__)

def docker_init():
    cwd = DOCKER_DIR
    try: subprocess.Popen(["docker-compose", "up", "-d"], cwd=DOCKER_DIR)
    except Exception: subprocess.Popen(["docker", "compose", "up", "-d"], cwd=DOCKER_DIR)
    
def restart_environment():
    try:
        subprocess.run(
            ["docker", "compose", "down"],
            cwd=DOCKER_DIR,
            check=True
        )

        subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=DOCKER_DIR,
            check=True
        )

        return True

    except Exception as e:
        logger.error(f"Erro ao reiniciar ambiente: {e}")
        return False
    
def run_docker_turbo(caller_obj, service, cmd_list, on_output, on_finish=None):
    docker_dir = DOCKER_DIR
    loop = asyncio.get_event_loop()
    
    docker_cmd = ["docker", "compose", "exec", "-u", "root", "-T", service] + cmd_list

    def target():
        try:
            proc = subprocess.Popen(
                docker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                cwd=docker_dir,
                text=False,
                bufsize=0   
            )
            
            caller_obj.current_proc = proc
            
            buffer_str = ""
            while True:
                char = proc.stdout.read(128) 
                if not char and proc.poll() is not None:
                    break
                
                if char:
                    texto = char.decode('utf-8', errors='ignore')
                    buffer_str += texto
                    
                    
                    if '\n' in buffer_str or len(buffer_str) > 50:
                        if on_output:
                            asyncio.run_coroutine_threadsafe(on_output(buffer_str), loop)
                        buffer_str = ""

           
            if buffer_str and on_output:
                asyncio.run_coroutine_threadsafe(on_output(buffer_str), loop)

            proc.stdout.close()
            rc = proc.wait()
            
            if on_output:
                asyncio.run_coroutine_threadsafe(on_output(f"\n[Finalizado] Código: {rc}\n"), loop)

        except Exception as e:
            err_msg = f"ERRO: {e}\n{traceback.format_exc()}"
            if on_output:
                asyncio.run_coroutine_threadsafe(on_output(err_msg), loop)

        finally:
            caller_obj.current_proc = None
            on_finish()
                    

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()

def cancel_process(caller_obj, on_output=None):
    proc = getattr(caller_obj, "current_proc", None)
    if proc:
        try:
            proc.terminate()
            if on_output:
                loop = asyncio.get_event_loop()
                asyncio.run_coroutine_threadsafe(on_output("\n[PROCESSO CANCELADO PELO USUÁRIO]\n"), loop)
        except:
            pass
        caller_obj.current_proc = None