import shlex

from models.nikto import Nikto
from services.tool_executor import ToolExecutor


class NiktoController:

    def __init__(self, app):

        self.app = app
        self.model = Nikto()
        self.executor = app.executor

    async def execute(
        self,
        host,
        port,
        ssl_switch,
        tuning,
        user_agent,
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

            cmd_list = shlex.split(
                command_str
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
            host=host,
            port=port,
            ssl_switch=ssl_switch,
            tuning=tuning,
            user_agent=user_agent
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