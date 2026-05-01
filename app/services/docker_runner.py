import subprocess
import threading
import os
import asyncio
import traceback
from config import DOCKER_DIR

def run_docker_turbo(caller_obj, service, cmd_list, on_output, on_finish=None):
    docker_dir = DOCKER_DIR
    loop = asyncio.get_event_loop()
    
    # Comando do Docker limpo e seguro
    docker_cmd = ["docker", "compose", "run", "-T", "--rm", service] + cmd_list



    
    def target():
        try:
            proc = subprocess.Popen(
                docker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL, # GARANTIA 1: Docker nunca vai travar esperando teclado
                cwd=docker_dir,
                text=False, # Lendo em binário para controle absoluto do buffer
                bufsize=0   # GARANTIA 2: Buffering completamente desligado (Unbuffered)
            )
            
            caller_obj.current_proc = proc
            
            # GARANTIA 3: Leitura agressiva. Lê blocos pequenos na velocidade da luz.
            # Acumula um pouco antes de mandar pro Flet para a tela não congelar.
            buffer_str = ""
            while True:
                char = proc.stdout.read(128) # Lê 128 bytes por vez
                if not char and proc.poll() is not None:
                    break
                
                if char:
                    texto = char.decode('utf-8', errors='ignore')
                    buffer_str += texto
                    
                    # Se tiver quebra de linha ou o buffer passar de 50 chars, envia pra UI
                    if '\n' in buffer_str or len(buffer_str) > 50:
                        if on_output:
                            asyncio.run_coroutine_threadsafe(on_output(buffer_str), loop)
                        buffer_str = ""

            # Envia o que sobrou no buffer
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
            if on_finish:
                if asyncio.iscoroutinefunction(on_finish):
                    asyncio.run_coroutine_threadsafe(on_finish(), loop)
                else:
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