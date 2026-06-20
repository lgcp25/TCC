from services.ai_service import ai_service

class AiController:
    def __init__(self, app):
        self.app = app

    async def explain(self, tab):
        if not tab.terminal_buffer.strip():
            tab.show_popup("Aviso", "Terminal vazio.")
            return
        await tab.clear_ai()
        self.app.set_loading("IA analisando resultados...")
        ans = await ai_service.analyze_results(tab.name, tab.terminal_buffer, command=tab.last_command)
        await tab.write_ai(ans)
        self.app.set_loading("", False)

    async def explain_cmd(self, tab):
        if not tab.last_command:
            tab.show_popup("Aviso", "Nenhum comando.")
            return
        await tab.clear_ai()
        self.app.set_loading("IA explicando comando...")
        ans = await ai_service.explain_command(tab.last_command)
        await tab.write_ai(ans)
        self.app.set_loading("", False)

    async def show_tips(self, tab):
        if not tab.last_command:
            tab.show_popup("Aviso", "Nenhum comando.")
            return
        await tab.clear_ai()
        self.app.set_loading("IA buscando dicas...")
        ans = await ai_service.get_tool_tips(tab.name, tab.phase, command=tab.last_command, logs=tab.terminal_buffer)
        await tab.write_ai(ans)
        self.app.set_loading("", False)
