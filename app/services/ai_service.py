import os
import json
import hashlib
import logging
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Tom pedagógico aplicado em todos os prompts
TEACHER_TONE = (
    "Você é um professor de cibersegurança experiente ensinando um aluno de graduação. "
    "Sempre explique o 'porquê' das coisas, não apenas o 'o quê'. "
    "Use linguagem acessível mas técnica. Responda em Português do Brasil. "
    "Use Markdown para formatar sua resposta."
)

# Diretório raiz do projeto (2 níveis acima deste arquivo: app/services -> raiz)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AIContext:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = "llama-3.3-70b-versatile"
        self.cache_file = os.path.join(_PROJECT_ROOT, "ai_cache.json")
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

    def _make_key(self, action, command):
        """Gera chave de cache baseada na ação + comando completo."""
        raw = f"{action}::{command.strip()}"
        h = hashlib.sha256(raw.encode()).hexdigest()
        logger.info(f"Cache key: action={action}, cmd='{command.strip()}' → {h[:16]}…")
        return h

    async def _ask_ai(self, system_prompt, user_content, max_tokens=1000, cache_key=None):
        if not self.api_key:
            return "⚠️ GROQ_API_KEY não configurada."

        if cache_key and cache_key in self.cache:
            logger.info(f"✅ Cache HIT: {cache_key[:16]}…")
            return self.cache[cache_key]

        logger.info(f"❌ Cache MISS: {cache_key[:16] if cache_key else 'sem-key'}… — chamando API")
        try:
            client = AsyncGroq(api_key=self.api_key)
            completion = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.4,
                max_tokens=max_tokens
            )
            result = completion.choices[0].message.content
            if cache_key:
                self.cache[cache_key] = result
                self._save_cache()
                logger.info(f"💾 Cache SAVE: {cache_key[:16]}…")
            return result
        except Exception as e:
            return f"❌ Erro na IA: {e}"

    # ─── BOTÃO: Explicar Resultado ───────────────────────────────────────
    async def analyze_results(self, tool, logs, command=""):
        if len(logs.strip()) < 10 and not command:
            return "Conteúdo insuficiente."

        h = self._make_key("analyze", command)

        if "Explicação" in tool:
            system = (
                f"{TEACHER_TONE}\n"
                "Liste cada flag/parâmetro do comando com uma explicação de 1 linha. "
                "Formato: `flag` — o que faz. Sem introdução nem conclusão."
            )
            max_t = 350
        elif self._is_low_value_result(logs):
            system = (
                f"{TEACHER_TONE}\n"
                "Os resultados mostram portas fechadas ou filtradas. "
                "Explique de forma breve o que isso significa para o aluno: "
                "por que as portas estão assim, se o alvo pode estar protegido por firewall, "
                "e sugira 2 comandos alternativos para tentar obter mais informações. "
                "Seja curto e direto."
            )
            max_t = 400
        else:
            system = (
                f"{TEACHER_TONE}\n"
                "Analise os logs de pentest abaixo. Identifique vulnerabilidades usando os níveis: "
                "[CRÍTICO], [ALTO], [MÉDIO], [BAIXO]. "
                "Explique cada achado como se o aluno estivesse vendo isso pela primeira vez. "
                "Sugira o que ele deveria investigar em seguida."
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
            f"{TEACHER_TONE}\n"
            "Liste cada flag/parâmetro do comando com uma explicação de 1 linha. "
            "Formato: `flag` — o que faz. Sem introdução nem conclusão."
        )
        user = f"Explique: `{command}`. Use Markdown."
        return await self._ask_ai(system, user, max_tokens=350, cache_key=h)

    # ─── BOTÃO: Dicas e Passos ───────────────────────────────────────────
    async def get_tool_tips(self, tool, phase, command="", logs=""):
        h = self._make_key("tips", f"{tool}:{command}")
        system = (
            f"{TEACHER_TONE}\n"
            "Sugira exatamente 3 próximos passos lógicos para o aluno seguir no pentest. "
            "Para cada passo, dê o comando exato e uma justificativa curta (1 linha). "
            "Não repita o que já foi feito. Seja objetivo."
        )
        user = f"Fase: {phase}\nFerramenta: {tool}\nComando executado: {command}\nLogs:\n{logs}"
        return await self._ask_ai(system, user, max_tokens=600, cache_key=h)

    # ─── BOTÃO: Adicionar ao Relatório ───────────────────────────────────
    async def generate_formal_report(self, tool, logs, command=""):
        h = self._make_key("report", f"{tool}:{command}")
        system = (
            f"{TEACHER_TONE}\n"
            "Crie uma análise técnica formal para relatório de pentest. "
            "Inclua: Resumo, Vulnerabilidades, Impacto e Mitigação."
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