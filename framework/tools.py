from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
import inspect
import re


@dataclass
class Tool:
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]

    @property
    def signature(self) -> str:
        sig = inspect.signature(self.function)
        return str(sig)

    def execute(self, **kwargs) -> Any:
        try:
            return self.function(**kwargs)
        except Exception as e:
            return f"Erro ao executar tool '{self.name}': {str(e)}"


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Callable:
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or "No description"

        params = {}
        sig = inspect.signature(func)
        for param_name, param in sig.parameters.items():
            param_info = {
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "any",
                "required": param.default == inspect.Parameter.empty
            }
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
            params[param_name] = param_info

        tool = Tool(
            name=tool_name,
            description=tool_description,
            function=func,
            parameters=params
        )
        self._tools[tool_name] = func
        return func

    def get(self, name: str) -> Optional[Callable]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        result = []
        for name, func in self._tools.items():
            result.append({
                "name": name,
                "description": func.__doc__ or "No description"
            })
        return result

    def get_tool_info(self, name: str) -> Optional[Tool]:
        if name not in self._tools:
            return None
        func = self._tools[name]
        tool_description = func.__doc__ or "No description"
        
        params = {}
        sig = inspect.signature(func)
        for param_name, param in sig.parameters.items():
            param_info = {
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "any",
                "required": param.default == inspect.Parameter.empty
            }
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
            params[param_name] = param_info
        
        return Tool(
            name=name,
            description=tool_description,
            function=func,
            parameters=params
        )

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        tool = self.registry.get(tool_name)
        if tool is None:
            return f"Tool '{tool_name}' não encontrada"
        
        try:
            return tool(**arguments)
        except TypeError as e:
            missing = re.findall(r"missing (\w+) argument", str(e))
            if missing:
                return f"Parâmetros necessários faltando: {', '.join(missing)}"
            return f"Erro ao executar: {str(e)}"
        except Exception as e:
            return f"Erro: {str(e)}"

    def execute_by_description(self, task: str) -> Dict[str, Any]:
        available_tools = self.registry.list_tools()
        
        for tool_info in available_tools:
            tool_name = tool_info["name"]
            tool_description = tool_info["description"].lower()
            
            if tool_name.lower() in task.lower() or tool_description in task.lower():
                return {
                    "tool": tool_name,
                    "found": True
                }
        
        return {"found": False}


def tool(name: Optional[str] = None, description: Optional[str] = None):
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or "No description"
        
        func._is_tool = True
        func._tool_name = tool_name
        func._tool_description = tool_description
        
        return func
    
    return decorator
