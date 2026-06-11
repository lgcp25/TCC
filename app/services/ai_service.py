import os
import json
import hashlib
import logging
from groq import AsyncGroq
from config import CACHE_FILE, AI_MODEL, AI_TEMPERATURE, TEACHER_JAMERSON
from utils import normalize_logs

logger = logging.getLogger(__name__)


class AIContext:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = AI_MODEL
        self.cache_file = CACHE_FILE
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"Cache carregado: {len(data)} entradas de {self.cache_file}")
                    return data
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Erro ao carregar cache, iniciando vazio: {e}")
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.error(f"Erro ao salvar cache: {e}")

    def _make_key(self, action, command, logs=""):
        """Gera chave de cache baseada na ação + comando + hash dos logs."""
        logs_hash = hashlib.md5(logs.strip().encode()).hexdigest()[:8] if logs else ""
        raw = f"{action}::{command.strip()}::{logs_hash}"
        h = hashlib.sha256(raw.encode()).hexdigest()
        logger.info(f"Cache key: action={action}, cmd='{command.strip()[:20]}...', logs_hash={logs_hash} → {h[:16]}…")
        return h

    async def _ask_ai(self, system_prompt, user_content, max_tokens=1000, cache_key=None):
        if not self.api_key:
            return "GROQ_API_KEY não configurada."

        if cache_key and cache_key in self.cache:
            logger.info(f"Cache HIT: {cache_key[:16]}…")
            return self.cache[cache_key]

        logger.info(f"Cache MISS: {cache_key[:16] if cache_key else 'sem-key'}… — chamando API")
        try:
            client = AsyncGroq(api_key=self.api_key)
            completion = await client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=AI_TEMPERATURE,
                max_tokens=max_tokens
            )
            result = completion.choices[0].message.content
            if cache_key:
                self.cache[cache_key] = result
                if len(self.cache) > 50:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                self._save_cache()
            return result
        except Exception as e:
            return f"Erro na IA: {e}"

    #BOTÃO: Explicar Resultado 
    async def analyze_results(self, tool, logs, command=""):
        logs = normalize_logs(logs, tool)
        if len(logs.strip()) < 10 and not command:
            return "Conteúdo insuficiente."

        h = self._make_key("analyze", command, logs)
        
        if self._is_low_value_result(logs):
            system = (
                f"{TEACHER_JAMERSON}\n"
                "Os resultados mostram pouco ou nenhum progresso (portas fechadas/timeout). "
                "Explique por que isso pode estar acontecendo (firewall, alvo offline) "
                "e sugira 2 alternativas técnicas para tentar contornar. Seja breve."
            )
            max_t = 400
        else:
            tool_instructions = {

                "Nmap": (
                    "Analise exclusivamente a saída do Nmap.\n"

                    "Extraia:\n"
                    "- Portas abertas.\n"
                    "- Serviços detectados.\n"
                    "- Versões detectadas.\n"
                    "- Sistema operacional detectado.\n"
                    "- Hostnames.\n"
                    "- Resultados NSE.\n"
                    "- CVEs explicitamente encontrados.\n\n"

                    "Explique brevemente a função de cada serviço encontrado.\n"
                    "Não invente informações ausentes."
                ),

                "Gobuster": (
                    "Analise exclusivamente a saída do Gobuster.\n"

                    "Extraia:\n"
                    "- Diretórios encontrados.\n"
                    "- Arquivos encontrados.\n"
                    "- Status HTTP.\n"
                    "- Redirecionamentos.\n\n"

                    "Explique em uma frase por que cada descoberta pode ser interessante durante a enumeração."
                ),

                "Nikto": (
                    "Analise exclusivamente a saída do Nikto.\n"

                    "Liste:\n"
                    "- Vulnerabilidades encontradas.\n"
                    "- Cabeçalhos ausentes.\n"
                    "- Tecnologias detectadas.\n"
                    "- Softwares desatualizados.\n\n"

                    "Explique brevemente o impacto de cada achado.\n"
                    "Não ensine exploração."
                ),

                "Sqlmap": (
                    "Analise exclusivamente a saída do SQLMap.\n"

                    "Informe:\n"
                    "- Se a injeção foi confirmada.\n"
                    "- Técnica utilizada.\n"
                    "- Bancos encontrados.\n"
                    "- Tabelas encontradas.\n"
                    "- Colunas encontradas.\n"
                    "- Credenciais encontradas.\n\n"

                    "Explique o significado dos resultados.\n"
                    "Não invente dados."
                ),

                "Netcat": (
                    "Analise exclusivamente a saída do Netcat.\n"

                    "Informe:\n"
                    "- Se houve conexão.\n"
                    "- Tipo de conexão.\n"
                    "- Dados recebidos.\n"
                    "- Comandos executados (se existirem).\n\n"

                    "Explique brevemente o que foi obtido."
                )
            }
            tool_spec = tool_instructions.get(tool, "")

            system = (
                    f"{TEACHER_JAMERSON}\n"

                    "Você é um instrutor e analista de segurança ofensiva.\n"
                    "Sua tarefa é analisar os logs da ferramenta e explicar exatamente o que foi encontrado.\n\n"

                    "OBJETIVO:\n"
                    "Extrair os resultados relevantes do scan e ensinar ao aluno o significado das descobertas.\n\n"

                    "REGRAS CRÍTICAS:\n"

                    "1. Vá direto ao ponto.\n"

                    "2. Classifique cada descoberta em uma das categorias:\n"
                    "[Reconhecimento]\n"
                    "[Serviço Exposto]\n"
                    "[Informação Sensível]\n"
                    "[Possível Vulnerabilidade]\n"
                    "[Acesso Obtido]\n\n"

                    "3. Explique brevemente por que cada descoberta é importante durante um pentest.\n"

                    "4. Utilize apenas informações presentes nos logs.\n"

                    "5. Nunca invente CVEs, vulnerabilidades, versões ou serviços.\n"

                    "6. Não forneça exploração passo a passo.\n"

                    "7. Não sugira próximos passos.\n"

                    "8. Não faça recomendações de correção.\n"

                    "9. Não faça avaliações subjetivas de risco.\n\n"

                    f"{tool_spec}\n\n"

                    "10. Use Markdown.\n"
                    "11. Destaque informações importantes com negrito.\n"
                    "12. Use tabelas quando apropriado.\n"
                    "13. Se uma informação não estiver presente nos logs, informe 'Não identificado'."
                )
            max_t = 1200

        user = f"Ferramenta: {tool}\nComando: {command}\nLogs:\n{logs}"
        return await self._ask_ai(system, user, max_tokens=max_t, cache_key=h)

    def _is_low_value_result(self, logs):
        """Detecta se o scan retornou apenas portas closed/filtered (pouco relevante)."""
        lower = logs.lower()
        has_open = "open" in lower and "closed" not in lower.split("open")[0]
        has_closed = "closed" in lower or "filtered" in lower
        if has_closed and ("0 hosts up" in lower or "all 1000" in lower):
            return True
        if has_closed and "open" not in lower:
            return True
        return False

    #BOTÃO: Explicar Comando 
    async def explain_command(self, command):
        """Cache pelo comando completo."""
        if not command:
            return "Nenhum comando para explicar."
        h = self._make_key("explain_cmd", command)
        system = (
            f"{TEACHER_JAMERSON}\n"
            "Liste cada flag/parâmetro do comando com uma explicação de 1 linha. "
            "Formato: `flag` — o que faz. Sem introdução nem conclusão."
        )
        user = f"Explique: `{command}`. Use Markdown."
        return await self._ask_ai(system, user, max_tokens=350, cache_key=h)

    #BOTÃO: Dicas e Passos 
    async def get_tool_tips(self, tool, phase, command="", logs=""):
        logs = normalize_logs(logs, tool)
        h = self._make_key("tips", f"{tool}:{command}", logs)
        
        tool_tips = {

            "Nmap": (
                "- Se encontrar HTTP ou HTTPS, priorize Gobuster ou Nikto.\n"
                "- Se encontrar SMB, priorize enumeração SMB.\n"
                "- Se encontrar bancos de dados, priorize SQLMap.\n"
                "- Se encontrar apenas host ativo, aprofunde o reconhecimento.\n"
                "- Se não encontrar portas abertas, sugira modos mais completos de Nmap."
            ),

            "Gobuster": (
                "- Se encontrar login ou painel administrativo, explique sua relevância.\n"
                "- Se encontrar diretórios sensíveis, destaque seu potencial valor.\n"
                "- Se encontrar aplicações dinâmicas, considere SQLMap.\n"
                "- Se não encontrar resultados relevantes, sugira nova enumeração."
            ),

            "Nikto": (
                "- Explique a importância das vulnerabilidades encontradas.\n"
                "- Se identificar páginas interessantes, considere Gobuster.\n"
                "- Se identificar formulários ou parâmetros, considere SQLMap.\n"
                "- Se identificar possível RCE, considere Netcat."
            ),

            "Sqlmap": (
                "- Se bancos forem encontrados, sugerir enumeração de tabelas.\n"
                "- Se tabelas forem encontradas, sugerir enumeração de colunas.\n"
                "- Se credenciais forem encontradas, destacar o impacto.\n"
                "- Se execução de comandos estiver disponível, considerar Netcat."
            ),

            "Netcat": (
                "- Se uma shell for obtida, explicar o que pode ser investigado.\n"
                "- Se apenas banner grabbing ocorrer, sugerir retornar à enumeração.\n"
                "- Se a conexão falhar, sugerir revisar a etapa anterior."
            )
        }
        tip_spec = tool_tips.get(tool, "Sugira os próximos passos baseados na fase atual do pentest.")

        system = (
            f"{TEACHER_JAMERSON}\n"

            "Você é um instrutor de Pentest para iniciantes.\n"
            "Sua tarefa é sugerir os próximos passos mais adequados com base nos resultados obtidos.\n\n"

            "REGRAS CRÍTICAS:\n"

            "1. Forneça entre 1 e 3 passos.\n"

            "2. Para cada passo utilize o formato:\n"
            "PASSO X\n"
            "O que fazer: ...\n"
            "Por quê: ...\n"
            "O que procurar: ...\n\n"

            "3. Priorize funcionalidades disponíveis no Vaporeon.\n"

            "4. Explique brevemente o raciocínio por trás da recomendação.\n"

            "5. Não invente vulnerabilidades, serviços ou resultados.\n"

            "6. Baseie-se apenas nos logs recebidos.\n"

            "7. Se os resultados forem insuficientes, explique isso e sugira um próximo teste adequado.\n"

            "8. Evite linguagem excessivamente técnica para iniciantes.\n"

            "9. O objetivo é ensinar metodologia de Pentest, não apenas listar ações.\n\n"

            f"DIRETRIZES DA FERRAMENTA ATUAL ({tool}):\n{tip_spec}\n\n"

            "10. Considere RCE apenas quando os logs demonstrarem claramente execução remota de comandos.\n"

            "11. Se houver evidência clara de execução remota de comandos, o primeiro passo deve envolver a aba Netcat.\n\n"

            "12. Quando sugerir um comando manual, adicione obrigatoriamente:\n"
            "*(Ative a chave 'Modo Comando Manual' na barra lateral para colar e executar este comando exato)*"
)
        user = f"Fase atual: {phase}\nFerramenta usada: {tool}\nÚltimo comando: {command}\nLogs recebidos:\n{logs}"
        return await self._ask_ai(system, user, max_tokens=600, cache_key=h)

    #BOTÃO: Adicionar ao Relatório 
    async def generate_formal_report(self, tool, logs, command=""):
        logs = normalize_logs(logs, tool)
        h = self._make_key("report", f"{tool}:{command}", logs)
        system = (
            f"{TEACHER_JAMERSON}\n"
            "Crie uma análise técnica formal e OBJETIVA para relatório de pentest.\n"
            "REGRAS:\n"
            "1. DADOS EXTRAÍDOS: Se os logs contêm nomes de bancos de dados, tabelas, colunas, "
            "usuários ou senhas, liste-os EXPLICITAMENTE em uma seção dedicada.\n"
            "2. RESULTADO CONCRETO: Diga exatamente o que a ferramenta conseguiu fazer "
            "(ex: 'O SQLmap confirmou injeção SQL do tipo UNION no parâmetro id e extraiu 5 bancos de dados').\n"
            "3. Estruture em: Resumo (2 linhas), Dados Extraídos (lista), Vulnerabilidade, Impacto e Mitigação.\n"
            "4. NÃO seja genérico. NÃO explique o que é SQL Injection em geral. Foque nos RESULTADOS reais."
        )
        return await self._ask_ai(system, f"Comando: {command}\nLogs da ferramenta {tool}:\n{logs}", max_tokens=2000, cache_key=h)

    #BOTÃO: Gerar PDF (Sumário Executivo)
    async def generate_executive_summary(self, findings):
        cmds = "|".join([f.get("command", "") for f in findings]) if isinstance(findings, list) else str(findings)
        h = self._make_key("summary", cmds)
        system = (
            "Você é um CISO. Crie um sumário executivo curto (máx 3 parágrafos) "
            "focado em risco e recomendações. Use Português do Brasil."
            "Coloque os subtitulos em negrito "
        )
        return await self._ask_ai(system, f"Achados:\n{findings}", max_tokens=1000, cache_key=h)

ai_service = AIContext()