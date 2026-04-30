import shlex
from tools.base_tool import BaseTool

class Metasploit(BaseTool):
    @property
    def name(self) -> str: return "Metasploit / Msfvenom"
    @property
    def binary(self) -> str: return "./msfvenom" # O container oficial roda no workdir, e o entrypoint padrão passa msfconsole. Para usar msfvenom usamos o comando direto. Mas o docker exec msfvenom funciona também.
    @property
    def docker_service(self) -> str: return "metasploit"

    def build_command(self, action, payload, lhost, lport, file_format, extra_params, raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            if parts[0] == self.binary: return parts
            return [self.binary] + parts

        if action == "Gerar Payload (Msfvenom)":
            cmd = ["msfvenom", "-p", payload]
            if lhost: cmd += [f"LHOST={lhost}"]
            if lport: cmd += [f"LPORT={lport}"]
            cmd += ["-f", file_format]
            
            # Msfvenom printa no stdout por padrão, se quiser salvar arquivo a gente adiciona > ou -o
            # No docker subprocess do Flet, é melhor usar -o para salvar no volume ./results
            output_file = f"/results/payload.{file_format}"
            cmd += ["-o", output_file]

            if extra_params: cmd += shlex.split(extra_params)
            return cmd
        
        elif action == "Iniciar Listener (Msfconsole)":
            # Automação de handler
            rc_file = "/results/handler.rc"
            rc_content = f"use exploit/multi/handler\nset PAYLOAD {payload}\n"
            if lhost: rc_content += f"set LHOST {lhost}\n"
            if lport: rc_content += f"set LPORT {lport}\n"
            rc_content += "exploit -j\n"
            
            # Aqui deveríamos criar o arquivo .rc localmente e mapear.
            # Como hack rápido, podemos passar os comandos via -x
            script = f"use exploit/multi/handler; set PAYLOAD {payload}; set LHOST {lhost or '0.0.0.0'}; set LPORT {lport or '4444'}; exploit"
            cmd = ["msfconsole", "-x", script]
            return cmd
            
        return ["msfconsole", "-q"]
