import shlex

from models.netcat import Netcat
from services.tool_executor import ToolExecutor


class NetcatController:

    def __init__(self, app):

        self.app = app
        self.model = Netcat()
        self.executor = app.executor

    async def execute(
        self,
        mode,
        host,
        port,
        manual_mode,
        raw_command,
        on_output,
        tab
    ):

        if tab:
            tab.set_executing(True)

        self.app.set_loading(
            "Scanner em execução...",
            True
        )

        async def on_finish():
            if tab:
                tab.set_executing(False)

            self.app.set_loading(
                "",
                False
            )

        if manual_mode:

            command_str = raw_command

            cmd_list = self.model.build_command(
                mode=None,
                host=None,
                port=None,
                raw_cmd=raw_command
            )

            await on_output(
                f"[COMANDO] {command_str}\n\n"
            )

            self.executor.execute(
                "pentester",
                cmd_list,
                on_output,
                tab,
                on_finish
            )

            return command_str

        cmd_list = self.model.build_command(
            mode=mode,
            host=host,
            port=port
        )

        command_str = self.model.pretty_command(
            cmd_list
        )

        await on_output(
            f"[COMANDO] {command_str}\n\n"
        )

        self.executor.execute(
            "pentester",
            cmd_list,
            on_output,
            tab,
            on_finish
        )

        return command_str