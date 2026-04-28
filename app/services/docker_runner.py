import asyncio
import traceback
import os

# Variável global para controle de processos
current_proc = None

async def run_docker(app, service, cmd_list, on_output, on_finish=None):
    global current_proc
    # O diretório do docker agora é relativo ao projeto
    docker_dir = os.path.join(os.getcwd(), "app", "docker")
    
    docker_cmd = ["docker", "compose", "run", "--quiet", "--rm", "--remove-orphans", service] + cmd_list
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *docker_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=docker_dir
        )
        
        current_proc = proc

        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            
            text = line.decode('utf-8', errors='ignore')
            if asyncio.iscoroutinefunction(on_output):
                await on_output(text)
            else:
                on_output(text)

        rc = await proc.wait()
        finish_msg = f"\n[Finalizado] Código: {rc}\n"
        if asyncio.iscoroutinefunction(on_output):
            await on_output(finish_msg)
        else:
            on_output(finish_msg)

    except Exception as e:
        err_msg = f"ERRO: {e}\n{traceback.format_exc()}"
        if asyncio.iscoroutinefunction(on_output):
            await on_output(err_msg)
        else:
            on_output(err_msg)

    finally:
        current_proc = None
        if on_finish:
            if asyncio.iscoroutinefunction(on_finish):
                await on_finish()
            else:
                on_finish()

def cancel_process(on_output=None):
    global current_proc
    if current_proc:
        try:
            current_proc.terminate()
            if on_output:
                on_output("\n[PROCESSO CANCELADO PELO USUÁRIO]\n")
        except:
            pass
        current_proc = None