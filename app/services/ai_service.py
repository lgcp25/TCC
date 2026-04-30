import os
import json
import hashlib
import logging
from groq import AsyncGroq
from config import CACHE_FILE, AI_MODEL, AI_TEMPERATURE, TEACHER_JAMERSON

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
                # Mecanismo simples de LRU: Evita que o cache cresça infinitamente
                if len(self.cache) > 50:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                self._save_cache()
                logger.info(f"Cache SAVE: {cache_key[:16]}…")
            return result
        except Exception as e:
            return f"Erro na IA: {e}"

    # ─── BOTÃO: Explicar Resultado ───────────────────────────────────────
    async def analyze_results(self, tool, logs, command=""):
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
            system = (
                f"{TEACHER_JAMERSON}\n"
                "Você é um analista de segurança sênior. Sua tarefa é analisar logs de pentest.\n"
                "OBJETIVO: Identifique exatamente o que a ferramenta ENCONTROU ou EXTRAIU.\n\n"
                "REGRAS CRÍTICAS:\n"
                "1. Se houver nomes de BANCOS DE DADOS, TABELAS ou USUÁRIOS extraídos, liste-os em destaque.\n"
                "2. Classifique os achados: [CRÍTICO], [ALTO], [MÉDIO] ou [BAIXO].\n"
                "3. Explique o significado técnico de cada descoberta para um aluno.\n"
                "4. Sugira o próximo passo óbvio baseado nos dados obtidos (ex: se listou DBs, agora listar tabelas).\n"
                "5. NÃO explique apenas o que a ferramenta faz em geral, foque nos DADOS REAIS nos logs."
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

    # ─── BOTÃO: Explicar Comando ─────────────────────────────────────────
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

    # ─── BOTÃO: Dicas e Passos ───────────────────────────────────────────
    async def get_tool_tips(self, tool, phase, command="", logs=""):
        h = self._make_key("tips", f"{tool}:{command}", logs)
        system = (
            f"{TEACHER_JAMERSON}\n"
            "Sugira exatamente 3 próximos passos lógicos para o aluno seguir no pentest. "
            "Para cada passo, dê o comando exato e uma justificativa curta (1 linha). "
            "Não repita o que já foi feito. Seja objetivo."
        )
        user = f"Fase: {phase}\nFerramenta: {tool}\nComando executado: {command}\nLogs:\n{logs}"
        return await self._ask_ai(system, user, max_tokens=600, cache_key=h)

    # ─── BOTÃO: Adicionar ao Relatório ───────────────────────────────────
    async def generate_formal_report(self, tool, logs, command=""):
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

    # ─── BOTÃO: Gerar PDF (Sumário Executivo) ────────────────────────────
    async def generate_executive_summary(self, findings):
        # Para o sumário, o cache é baseado nos comandos presentes nos findings
        cmds = "|".join([f.get("command", "") for f in findings]) if isinstance(findings, list) else str(findings)
        h = self._make_key("summary", cmds)
        system = (
            "Você é um CISO. Crie um sumário executivo curto (máx 3 parágrafos) "
            "focado em risco e recomendações. Use Português do Brasil."
        )
        return await self._ask_ai(system, f"Achados:\n{findings}", max_tokens=1000, cache_key=h)

ai_service = AIContext()