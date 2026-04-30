import shlex
from models.base_tool import BaseTool

class Netcat(BaseTool):
    @property
    def name(self) -> str: return "Netcat"
    @property
    def binary(self) -> str: return "nc"
    @property
    def docker_service(self) -> str: return "pentester"

    def build_command(self, mode, host, port, file_path, raw_cmd, extra_params):
        if mode == "Raw Command (avançado)":
            if not raw_cmd: raise ValueError("Você deve fornecer o comando Raw.")
            return [self.binary] + shlex.split(raw_cmd)
            
        cmd = [self.binary]
        
        if mode == "Escutar (servidor)":
            cmd += ["-lvnp", port]
        elif mode == "Conectar (cliente)":
            if not host: raise ValueError("Host é obrigatório para conectar.")
            cmd += ["-v", host, port]
        elif mode == "Banner Grab":
            if not host: raise ValueError("Host é obrigatório para conectar.")
            cmd += ["-v", "-w", "5", host, port]
        elif mode == "Enviar arquivo":
            if not host: raise ValueError("Host é obrigatório para enviar.")
            cmd += ["-v", host, port]
            # Redirecionamento não suportado nativamente pelo subprocess_exec sem shell
            raise NotImplementedError("Envio de arquivos não é suportado pelo wrapper Docker atualmente.")
        elif mode == "Receber arquivo":
            cmd += ["-lvnp", port]
            raise NotImplementedError("Recebimento de arquivos não é suportado pelo wrapper Docker atualmente.")
            
        if extra_params: cmd += shlex.split(extra_params)
        
        return cmd