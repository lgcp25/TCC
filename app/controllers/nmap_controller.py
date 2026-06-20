import shlex
from models.nmap import Nmap
from services.tool_executor import ToolExecutor


class NmapController:

    def __init__(self, app):
        self.app = app
        self.model = Nmap()
        self.executor = app.executor

    async def execute(self, target, scan_profile, port, script_scan, manual_mode, raw_command, on_output, tab):
        if tab:
            tab.set_executing(True)

        self.app.set_loading("Scanner em execução...", True)

        async def on_finish():
            if tab:
                tab.set_executing(False)

            self.app.set_loading("", False)

        if manual_mode:
            command_str = raw_command
            cmd_list = shlex.split(command_str)
            await on_output(f"[COMANDO] {command_str}\n\n")
            self.executor.execute("pentester", cmd_list, on_output, tab, on_finish)
            
            return command_str

        cmd_list = self.model.build_command(target=target, mode=scan_profile, port=port, os_detect=False, script_scan=script_scan, verbose=False)
        command_str = self.model.pretty_command(cmd_list)
        await on_output(f"[COMANDO] {command_str}\n\n")
        self.executor.execute("pentester", cmd_list, on_output, tab, on_finish)
        
        return command_str
    
    
    
    