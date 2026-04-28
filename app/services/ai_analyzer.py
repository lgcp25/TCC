from services.ai_service import ai_service

async def analyze_nmap(log_content):
    return await ai_service.analyze_results("Nmap", log_content)

async def analyze_sqlmap(log_content):
    return await ai_service.analyze_results("SQLmap", log_content)
