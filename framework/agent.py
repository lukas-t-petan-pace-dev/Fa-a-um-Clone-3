from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
import logging

from .memory import Memory
from .tools import ToolRegistry, ToolExecutor
from .reasoning import ReasoningEngine, ReasoningResult


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@dataclass
class AgentConfig:
    name: str
    goal: str
    reasoning: ReasoningEngine
    use_tokens: bool = False
    verbose: bool = True
    max_iterations: int = 10
    tools: List[Callable] = field(default_factory=list)


class Agent:
    def __init__(
        self,
        name: str,
        goal: str,
        reasoning: Optional[ReasoningEngine] = None,
        use_tokens: bool = False,
        verbose: bool = True,
        max_iterations: int = 10,
        memory_size: int = 100
    ):
        self.name = name
        self.goal = goal
        self.use_tokens = use_tokens
        self.verbose = verbose
        self.max_iterations = max_iterations
        
        if reasoning is None:
            from .reasoning import DeterministicReasoning
            reasoning = DeterministicReasoning()
        
        self.reasoning = reasoning
        
        if use_tokens and not reasoning.supports_tokens():
            from .reasoning import SimulatedLLMReasoning
            self.reasoning = SimulatedLLMReasoning()
        
        self.memory = Memory(short_term_max_size=memory_size)
        self.tool_registry = ToolRegistry()
        self.tool_executor = ToolExecutor(self.tool_registry)
        
        self.logger = logging.getLogger(f"Agent.{name}")
        
        if self.verbose:
            self.logger.info(f"Agent '{name}' inicializado. Goal: {goal}")
            self.logger.info(f"Modo tokens: {use_tokens}, Raciocínio: {reasoning.__class__.__name__}")
    
    def add_tool(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None) -> None:
        self.tool_registry.register(func, name=name, description=description)
        if self.verbose:
            self.logger.info(f"Tool adicionada: {name or func.__name__}")
    
    def add_tools(self, *tools: Callable) -> None:
        for tool in tools:
            self.add_tool(tool)
    
    def list_tools(self) -> List[Dict[str, str]]:
        return self.tool_registry.list_tools()
    
    def run(self, task: str) -> str:
        if self.verbose:
            self.logger.info(f"Iniciando tarefa: {task}")
        
        self.memory.add_interaction("user", task)
        
        available_tools = self.list_tools()
        
        result = self.reasoning.think(
            task=task,
            memory_context=self.memory.get_context(),
            available_tools=available_tools
        )
        
        if self.verbose:
            self.logger.info(f"Pensamento: {result.thought}")
            self.logger.info(f"Ação: {result.action}")
        
        if result.action and result.action != "respond" and result.action != "error":
            observation = self._execute_tool(result.action, result.action_input or {})
            
            if self.verbose:
                self.logger.info(f"Observação: {observation}")
            
            result.observation = str(observation)
            
            response = f"{result.thought}\n\nResultado: {observation}"
        else:
            response = result.thought
            if result.action_input and "response" in result.action_input:
                response = result.action_input["response"]
        
        self.memory.add_interaction("assistant", response)
        
        return response
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        tool = self.tool_registry.get(tool_name)
        
        if tool is None:
            for available_tool in self.list_tools():
                if tool_name.lower() in available_tool["name"].lower():
                    tool = self.tool_registry.get(available_tool["name"])
                    break
        
        if tool is None:
            return f"Tool '{tool_name}' não encontrada"
        
        try:
            return tool(**arguments)
        except TypeError as e:
            return f"Erro de parâmetros: {str(e)}"
        except Exception as e:
            return f"Erro ao executar: {str(e)}"
    
    def chat(self) -> None:
        print(f"\n{'='*50}")
        print(f"Agent: {self.name}")
        print(f"Goal: {self.goal}")
        print(f"{'='*50}")
        print("Digite 'sair' para encerrar\n")
        
        while True:
            try:
                user_input = input("Você: ").strip()
                
                if user_input.lower() in ["sair", "exit", "quit"]:
                    print("\nEncerrando chat...")
                    break
                
                if not user_input:
                    continue
                
                response = self.run(user_input)
                print(f"\nAgent: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nEncerrando chat...")
                break
            except Exception as e:
                print(f"Erro: {str(e)}")
    
    def reset_memory(self) -> None:
        self.memory.clear()
        if self.verbose:
            self.logger.info("Memória resetada")
    
    def get_memory_context(self) -> str:
        return self.memory.get_context()
    
    def __repr__(self) -> str:
        return f"Agent(name='{self.name}', goal='{self.goal}', tools={len(self.tool_registry)}, reasoning={self.reasoning.__class__.__name__})"
