from typing import Any, Dict, List, Optional
from .base import ReasoningEngine, ReasoningResult


class LLMReasoning(ReasoningEngine):
    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
        self._initialized = False
    
    def _ensure_client(self):
        if self._initialized:
            return
        
        try:
            from openai import OpenAI
            if self.api_key:
                self._client = OpenAI(api_key=self.api_key, base_url=self.api_base)
            else:
                self._client = OpenAI(base_url=self.api_base)
            self._initialized = True
        except ImportError:
            raise ImportError("openai library is required for LLMReasoning. Install with: pip install openai")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM client: {e}")
    
    def think(self, task: str, memory_context: str, available_tools: List[Dict[str, str]]) -> ReasoningResult:
        tools_description = self._format_tools_for_prompt(available_tools)
        
        system_prompt = self._build_system_prompt(tools_description)
        user_prompt = self._build_user_prompt(task, memory_context)
        
        try:
            response = self._call_llm(system_prompt, user_prompt)
            return self._parse_llm_response(response, available_tools)
        except Exception as e:
            return ReasoningResult(
                thought=f"Erro ao chamar LLM: {str(e)}",
                action="error",
                action_input={"error": str(e)},
                confidence=0.0
            )
    
    def _format_tools_for_prompt(self, available_tools: List[Dict[str, str]]) -> str:
        if not available_tools:
            return "Nenhuma ferramenta disponível."
        
        tools_text = "Ferramentas disponíveis:\n"
        for tool in available_tools:
            tools_text += f"- {tool['name']}: {tool['description']}\n"
        return tools_text
    
    def _build_system_prompt(self, tools_description: str) -> str:
        return f"""Você é um agente de IA que ajuda o usuário a completar tarefas.

{tools_description}

Instruções:
1. Analise a tarefa do usuário
2. Determine se precisa usar alguma ferramenta
3. Se precisar, escolha a ferramenta apropriada e extraia os parâmetros
4. Responda de forma clara e concisa

Responda no formato:
Thought: <seu raciocínio>
Action: <nome da ferramenta ou 'respond'>
Action Input: <dicionário com parâmetros ou resposta>"""

    def _build_user_prompt(self, task: str, memory_context: str) -> str:
        prompt = f"Tarefa: {task}\n"
        if memory_context:
            prompt += f"\nContexto da memória:\n{memory_context}\n"
        return prompt
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        self._ensure_client()
        
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content
    
    def _parse_llm_response(self, response: str, available_tools: List[Dict[str, str]]) -> ReasoningResult:
        lines = response.split('\n')
        thought = ""
        action = None
        action_input = {}
        
        for line in lines:
            if line.startswith("Thought:"):
                thought = line[8:].strip()
            elif line.startswith("Action:"):
                action = line[7:].strip().lower()
            elif line.startswith("Action Input:"):
                input_str = line[13:].strip()
                action_input = self._parse_action_input(input_str)
        
        if not action:
            return ReasoningResult(
                thought=thought or response,
                action="respond",
                action_input={"response": response},
                confidence=0.7
            )
        
        tool_found = False
        for tool in available_tools:
            if action in tool["name"].lower():
                tool_found = True
                break
        
        if not tool_found and action != "respond":
            action = "respond"
            action_input = {"response": thought}
        
        return ReasoningResult(
            thought=thought,
            action=action if action else "respond",
            action_input=action_input,
            confidence=0.8
        )
    
    def _parse_action_input(self, input_str: str) -> Dict[str, Any]:
        import json
        
        if not input_str or input_str == "{}":
            return {}
        
        try:
            if input_str.startswith("{"):
                return json.loads(input_str)
        except json.JSONDecodeError:
            pass
        
        return {"response": input_str}
    
    def supports_tokens(self) -> bool:
        return True


class SimulatedLLMReasoning(ReasoningEngine):
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
    
    def think(self, task: str, memory_context: str, available_tools: List[Dict[str, str]]) -> ReasoningResult:
        task_lower = task.lower()
        
        tool_match = self._identify_tool_from_task(task_lower, available_tools)
        if tool_match:
            action_input = self._extract_parameters_from_task(task, tool_match)
            return ReasoningResult(
                thought=f"Pensando: A tarefa '{task}' requer a ferramenta '{tool_match}'. "
                        f"Parâmetros identificados: {action_input}",
                action=tool_match,
                action_input=action_input,
                confidence=0.85
            )
        
        response = self._generate_simulated_response(task, memory_context)
        return ReasoningResult(
            thought=f"Pensando: Analisando a tarefa '{task}'. Gerando resposta...",
            action="respond",
            action_input={"response": response},
            confidence=0.7
        )
    
    def _identify_tool_from_task(self, task: str, available_tools: List[Dict[str, str]]) -> str:
        keywords = {
            "somar": ["somar", "some", "adição", "add"],
            "subtrair": ["subtrair", "subtraia", "subtração"],
            "multiplicar": ["multiplicar", "multiplique", "vezes"],
            "dividir": ["dividir", "divida", "divisão"],
            "buscar": ["buscar", "pesquisar", "procurar"],
            "calcular": ["calcular", "calcule"],
        }
        
        for tool_name, kw_list in keywords.items():
            if any(kw in task for kw in kw_list):
                for available in available_tools:
                    if tool_name in available["name"].lower():
                        return available["name"]
        
        return ""
    
    def _extract_parameters_from_task(self, task: str, tool_name: str) -> Dict[str, Any]:
        import re
        numbers = re.findall(r'\d+\.?\d*', task)
        
        params = {}
        
        if "a" in task.lower() and "b" in task.lower():
            if len(numbers) >= 2:
                params["a"] = float(numbers[0])
                params["b"] = float(numbers[1])
        elif len(numbers) >= 2:
            if "somar" in tool_name.lower() or "add" in tool_name.lower():
                params["a"] = float(numbers[0])
                params["b"] = float(numbers[1])
            elif "subtrair" in tool_name.lower():
                params["a"] = float(numbers[0])
                params["b"] = float(numbers[1])
            elif "multiplicar" in tool_name.lower():
                params["a"] = float(numbers[0])
                params["b"] = float(numbers[1])
            elif "dividir" in tool_name.lower():
                params["a"] = float(numbers[0])
                params["b"] = float(numbers[1])
        
        return params
    
    def _generate_simulated_response(self, task: str, memory_context: str) -> str:
        task_lower = task.lower()
        
        greetings = ["olá", "ola", "hello", "hi", "hey"]
        if any(g in task_lower for g in greetings):
            return "Olá! Como posso ajudá-lo hoje?"
        
        if "seu nome" in task_lower or "who are you" in task_lower:
            return "Sou um agente de IA criado com o framework."
        
        if "ajuda" in task_lower or "help" in task_lower:
            return "Posso ajudá-lo com diversas tarefas. Como posso ajudar?"
        
        return f"Entendi: '{task}'. Como posso processar isso?"
    
    def supports_tokens(self) -> bool:
        return True
