import asyncio
from typing import Dict, Optional, Literal
from fastapi import FastAPI
from pydantic import BaseModel

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition

app = FastAPI(title="Handoff demo (Claude Agent SDK + FastAPI)")

ActiveAgent = Literal["ux", "docs"]

SESSIONS: Dict[str, Dict] = {}


class ChatIn(BaseModel):
    session_id: str
    message: str


class ChatOut(BaseModel):
    session_id: str
    active_agent: ActiveAgent
    reply: str


def pick_agent(user_text: str, current: Optional[ActiveAgent]) -> ActiveAgent:
    """
    Router simple para demo.
    - Si detecta intención documental/burocrática: handoff a 'docs'
    - Si no: 'ux'
    """
    text = user_text.lower()
    doc_signals = ["pdf", "expediente", "boe", "decreto", "pliego", "alegación", "licitación", "anexo", "burocr"]
    if any(s in text for s in doc_signals):
        return "docs"
    return current or "ux"


def build_options(active: ActiveAgent) -> ClaudeAgentOptions:
    """
    Cada 'agente' es el mismo modelo por debajo, pero con:
    - system_prompt distinto (rol)
    - permisos/herramientas distintos
    - subagents disponibles (especialistas)
    """
    agents = {
        "doc-extractor": AgentDefinition(
            description="Extrae puntos clave, requisitos, plazos y referencias de documentos administrativos.",
            prompt=(
                "Eres un analista de documentos administrativos. "
                "Devuelve un resumen estructurado: (1) objetivo, (2) requisitos, (3) plazos, "
                "(4) riesgos/ambigüedades, (5) lista de preguntas para el usuario."
            ),
            tools=["Read", "Grep", "Glob"], 
            model="inherit",
        ),
        "formal-writer": AgentDefinition(
            description="Redacta respuestas claras, formales y accionables para funcionarios.",
            prompt=(
                "Eres un redactor institucional. Escribe en español formal, "
                "con bullets, pasos numerados y definiciones. Evita jerga técnica."
            ),
            tools=[],
            model="inherit",
        ),
    }

    if active == "ux":
        system = (
            "Eres el agente de UX/triage para una plataforma usada por funcionarios. "
            "Tu objetivo es: (1) entender la petición, (2) pedir aclaraciones mínimas, "
            "(3) proponer el siguiente paso de forma clara y breve. "
            "Si detectas trabajo documental largo o jurídico-administrativo, delega en subagentes."
        )
        return ClaudeAgentOptions(
            system_prompt=system,
            max_turns=1,
            agents=agents,
            allowed_tools=[],
        )


    system = (
        "Eres el agente documental para administración pública. "
        "Analiza textos largos, extrae obligaciones y resume con trazabilidad. "
        "Si hace falta, usa subagentes para extraer o redactar formalmente."
    )
    return ClaudeAgentOptions(
        system_prompt=system,
        max_turns=1,
        agents=agents,
        allowed_tools=[],
    )


async def get_client(session_id: str, active: ActiveAgent) -> ClaudeSDKClient:
    """
    Crea/reusa un cliente por sesión. Si cambia el active_agent -> handoff:
    recreamos cliente con otro system_prompt/opciones.
    """
    state = SESSIONS.get(session_id)
    if not state or state["active_agent"] != active:
        options = build_options(active)
        client = ClaudeSDKClient(options=options)
        await client.__aenter__() 

        if state and state.get("client"):
            try:
                await state["client"].__aexit__(None, None, None)
            except Exception:
                pass

        SESSIONS[session_id] = {"active_agent": active, "client": client}
        return client

    return state["client"]


async def ask(client: ClaudeSDKClient, prompt: str) -> str:
    await client.query(prompt)
    chunks = []
    async for msg in client.receive_response():
        chunks.append(str(msg))
    return "\n".join(chunks).strip()


@app.post("/chat", response_model=ChatOut)
async def chat(payload: ChatIn):
    state = SESSIONS.get(payload.session_id, {})
    current = state.get("active_agent")
    active: ActiveAgent = pick_agent(payload.message, current)

    client = await get_client(payload.session_id, active)
    reply = await ask(client, payload.message)

    return ChatOut(session_id=payload.session_id, active_agent=active, reply=reply)
