"""
Nexus AI BR - Framework de Agentes de IA em Python Puro
=========================================================

Um framework modular e extensível para criar agentes de IA,
com suporte a múltiplos tipos de raciocínio.

Uso básico:
    from framework import Agent, DeterministicReasoning
    
    agent = Agent(
        name="MeuAgente",
        goal="Ajudar o usuário",
        reasoning=DeterministicReasoning(),
        use_tokens=False
    )
    
    agent.add_tool(minha_funcao)
    result = agent.run("minha tarefa")
"""

from .agent import Agent, AgentConfig
from .memory import Memory, ShortTermMemory, LongTermMemory
from .tools import Tool, ToolRegistry, ToolExecutor, tool
from .reasoning import (
    ReasoningEngine,
    ReasoningResult,
    DeterministicReasoning,
    RuleBasedReasoning,
    LLMReasoning,
    SimulatedLLMReasoning,
)
from .websocket_server import WebSocketServer, create_websocket_app, run_agent_server

__version__ = "1.90.2"

__all__ = [
    "Agent",
    "AgentConfig",
    "Memory",
    "ShortTermMemory", 
    "LongTermMemory",
    "Tool",
    "ToolRegistry",
    "ToolExecutor",
    "tool",
    "ReasoningEngine",
    "ReasoningResult",
    "DeterministicReasoning",
    "RuleBasedReasoning",
    "LLMReasoning",
    "SimulatedLLMReasoning",
    "WebSocketServer",
    "create_websocket_app",
    "run_agent_server",
]
