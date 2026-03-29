import re
from typing import Any, Dict, List
from .base import ReasoningEngine, ReasoningResult


class DeterministicReasoning(ReasoningEngine):
    def __init__(self):
        self.action_sequences: Dict[str, str] = {}
    
    def think(self, task: str, memory_context: str, available_tools: List[Dict[str, str]]) -> ReasoningResult:
        task_lower = task.lower()
        
        tool_match = self._identify_tool(task_lower, available_tools)
        if tool_match:
            return self._execute_tool_reasoning(task, tool_match)
        
        return self._simple_response_reasoning(task, memory_context)
    
    def _identify_tool(self, task: str, available_tools: List[Dict[str, str]]) -> str:
        tool_keywords = {
            "search": ["buscar", "pesquisar", "procurar", "search", "find", "lookup"],
            "buscar_informacao": ["o que é", "o que sao", "o que e", "o que sao", "me explique", "explique", "o que", "quem é", "quem sao", "definir", "o que significa", "diga-me", "informacao", "informação", "sobre", "sobre o", "sobre a", "dizer", "saber", "conceito de", "quem created", "created by", "developed by"],
            "calculate": ["calcular", "somar", "subtrair", "multiplicar", "dividir", "calculate", "add", "subtract", "multiply", "divide"],
            "somar": ["some", "somar", "adição", "add"],
            "subtrair": ["subtraia", "subtrair", "subtração", "subtract", "menos"],
            "multiplicar": ["multiplique", "multiplicar", "vezes", "multiply", "times"],
            "dividir": ["divida", "dividir", "divisão", "divide", "por"],
            "print": ["imprimir", "mostrar", "exibir", "print", "show", "display"],
            "http": ["requisitar", "request", "http", "url", "fetch"],
            "file": ["ler arquivo", "escrever arquivo", "read file", "write file"],
            "tradutor": ["traduzir", "traduz", "translation", "translate", "em ingles", "em espanhol", "em frances", "para o ingles", "para ingles"],
            "get_horario": ["horario", "hora", "que horas"],
            "get_data": ["data", "que dia", "data de hoje"],
            "get_clima": ["clima", "tempo", "temperatura", "esta como"],
        }
        
        for tool_name, keywords in tool_keywords.items():
            for keyword in keywords:
                if keyword in task:
                    for available in available_tools:
                        if tool_name in available["name"].lower():
                            return available["name"]
        
        for available in available_tools:
            tool_name_lower = available["name"].lower()
            if tool_name_lower in task:
                return available["name"]
        
        if "?" in task or "o que" in task or "me diga" in task:
            for available in available_tools:
                if "buscar" in available["name"].lower() or "informacao" in available["name"].lower():
                    return available["name"]
        
        return ""
    
    def _execute_tool_reasoning(self, task: str, tool_name: str) -> ReasoningResult:
        action_input = self._extract_parameters(task, tool_name)
        
        thought = f"Identifiquei que a tarefa requer a ferramenta '{tool_name}'. "
        thought += f"Parâmetros extraídos: {action_input}"
        
        return ReasoningResult(
            thought=thought,
            action=tool_name,
            action_input=action_input,
            confidence=0.9
        )
    
    def _extract_parameters(self, task: str, tool_name: str) -> Dict[str, Any]:
        params = {}
        task_lower = task.lower()
        
        numbers = re.findall(r'-?\d+\.?\d*', task)
        
        if tool_name.lower() in ["somar", "add", "calculate"]:
            if len(numbers) >= 2:
                params["a"] = float(numbers[0])
                params["b"] = float(numbers[1])
        elif tool_name.lower() in ["subtrair", "subtract"]:
            if len(numbers) >= 2:
                params["a"] = float(numbers[0])
                params["b"] = float(numbers[1])
        elif tool_name.lower() in ["multiplicar", "multiply"]:
            if len(numbers) >= 2:
                params["a"] = float(numbers[0])
                params["b"] = float(numbers[1])
        elif tool_name.lower() in ["dividir", "divide"]:
            if len(numbers) >= 2:
                params["a"] = float(numbers[0])
                params["b"] = float(numbers[1])
        
        if "query" in task_lower or "busca" in task_lower or "search" in task_lower:
            query_match = re.search(r'["\']([^"\']+)["\']', task)
            if query_match:
                params["query"] = query_match.group(1)
            else:
                words = task.split()
                if len(words) > 2:
                    params["query"] = " ".join(words[2:])
        
        if "buscar_informacao" in tool_name.lower():
            query_match = re.search(r'["\']([^"\']+)["\']', task)
            if query_match:
                params["query"] = query_match.group(1)
            else:
                task_clean = task
                for word in ["o que é", "o que e", "o que sao", "o que sao", "me explique", "explique", "diga-me", "diz", "quem é", "sobre", "?", "o que"]:
                    task_clean = task_clean.lower().replace(word, "")
                params["query"] = task_clean.strip().capitalize()
        
        if "url" in task_lower or "http" in task_lower:
            url_match = re.search(r'https?://[^\s]+', task)
            if url_match:
                params["url"] = url_match.group(0)
        
        return params
    
    def _simple_response_reasoning(self, task: str, memory_context: str) -> ReasoningResult:
        import random
        task_lower = task.lower()
        
        if any(phrase in task_lower for phrase in ["adeus", "tchau", "bye", "ate mais", "flw", "ate logo", "ate mais"]):
            responses = [
                "Tchau! Foi um prazer ajudar!",
                "Até logo! Volte sempre!",
                "Adeus! Em caso de dúvidas, é só chamar!",
                "Tchau! Foi bom conversar com você!"
            ]
            return ReasoningResult(
                thought="O usuário está se despindo.",
                action="respond",
                action_input={"response": random.choice(responses)},
                confidence=0.95
            )
        
        if any(phrase in task_lower for phrase in ["obrigado", "obrigada", "valeu", "thanks", "thx", "grato", "muy obrigado", "muito obrigado"]):
            responses = [
                "De nada! Estou aqui para ajudar!",
                "Por nada! Precisa de mais alguma coisa?",
                "Disponha! Estou sempre à disposição!",
                "Imagina! Qualquer dúvida, é só perguntar!"
            ]
            return ReasoningResult(
                thought="O usuário está agradecendo.",
                action="respond",
                action_input={"response": random.choice(responses)},
                confidence=0.95
            )
        
        if any(phrase in task_lower for phrase in ["qual seu nome", "quem e voce", "quem e você", "quem voce e", "seu nome e", "como voce se chama", "como voce se chama", "seu nome"]):
            return ReasoningResult(
                thought="O usuário quer saber meu nome.",
                action="respond",
                action_input={"response": "Meu nome é Nova IA! Sou um assistente virtual criado para ajudar você."},
                confidence=0.95
            )
        
        if any(phrase in task_lower for phrase in ["como voce funciona", "o que voce faz", "o que você faz", "me ajude", "ajuda", "help", "comandos", "o que voce pode fazer", "quais sao suas funcoes", "quais são suas funções"]):
            return ReasoningResult(
                thought="O usuário quer saber como me usar.",
                action="respond",
                action_input={"response": "Posso ajudá-lo com:\n\n• Perguntas sobre tecnologia e diversos temas\n• Traduções para outros idiomas\n• Cálculos matemáticos\n• Informações de horário e data\n• Consulta de clima\n\nÉ só perguntar!"},
                confidence=0.9
            )
        
        if any(phrase in task_lower for phrase in ["tudo bem", "tudo bom", "como vc", "como voce", "como esta", "como você está", "beleza", "legal", "blz", "ok", "e ai", "eai", "iai"]):
            responses = [
                "Tudo bem! E com você?",
                "Estou bem, obrigado! Em que posso ajudar?",
                "Ótimo! E você?",
                "Beleza! Como posso ser útil?",
                "Estou aqui e pronto para ajudar!"
            ]
            return ReasoningResult(
                thought="O usuário está fazendo uma pergunta casual.",
                action="respond",
                action_input={"response": random.choice(responses)},
                confidence=0.95
            )
        
        greetings = ["olá", "ola", "hello", "hi", "hey", "bom dia", "boa tarde", "boa noite", "eai", "iai", "yo", "oi"]
        if any(greeting in task_lower for greeting in greetings):
            responses = [
                "Olá! Como posso ajudá-lo hoje?",
                "Olá! Em que posso ser útil?",
                "Oi! Tudo bem? Como posso ajudar?",
                "Olá! Precisa de algo?",
                "Hey! Estou aqui para ajudar!"
            ]
            return ReasoningResult(
                thought="O usuário está cumprimentando. Vou responder de forma amigável.",
                action="respond",
                action_input={"response": random.choice(responses)},
                confidence=0.95
            )
            return ReasoningResult(
                thought="O usuário quer saber como me usar.",
                action="respond",
                action_input={"response": "Posso ajudá-lo com:\n\n• Perguntas sobre tecnologia e diversos temas\n• Traduções para outros idiomas\n• Cálculos matemáticos\n• Informações de horário e data\n• Consulta de clima\n\nÉ só perguntar!"},
                confidence=0.9
            )
        
        if "?" in task or "como" in task_lower or "o que" in task_lower:
            return ReasoningResult(
                thought="O usuário está fazendo uma pergunta.",
                action="respond",
                action_input={"response": "Interessante pergunta! Tente ser mais específico ou faça uma pergunta sobre um tema que eu possa conhecer."},
                confidence=0.5
            )
        
        return ReasoningResult(
            thought="A tarefa não requer ferramentas específicas. Vou responder diretamente.",
            action="respond",
            action_input={"response": f"Entendi: '{task}'. Posso ajudá-lo com perguntas, traduções, cálculos e muito mais!"},
            confidence=0.7
        )
    
    def supports_tokens(self) -> bool:
        return False


class RuleBasedReasoning(ReasoningEngine):
    def __init__(self):
        self.rules: List[Dict[str, Any]] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        self.rules = [
            {
                "pattern": r"(somar|adição|add|some)\s+(\d+)\s+\+?\s+(\d+)",
                "action": "somar"
            },
            {
                "pattern": r"(subtrair|subtração|subtract)\s+(\d+)\s+\-\s+(\d+)",
                "action": "subtrair"
            },
            {
                "pattern": r"(multiplicar|multiply|vezes)\s+(\d+)\s+\*\s+(\d+)",
                "action": "multiplicar"
            },
            {
                "pattern": r"(dividir|divide)\s+(\d+)\s+/\s+(\d+)",
                "action": "dividir"
            },
        ]
    
    def think(self, task: str, memory_context: str, available_tools: List[Dict[str, str]]) -> ReasoningResult:
        for rule in self.rules:
            match = re.search(rule["pattern"], task.lower())
            if match:
                numbers = re.findall(r'\d+', task)
                if len(numbers) >= 2:
                    action_input = {
                        "a": float(numbers[0]),
                        "b": float(numbers[1])
                    }
                    return ReasoningResult(
                        thought=f"Padrão identificado: {rule['action']}. Extraindo números: {action_input}",
                        action=rule["action"],
                        action_input=action_input,
                        confidence=0.95
                    )
        
        return ReasoningResult(
            thought="Nenhuma regra específica encontrada. Retornando resposta direta.",
            action="respond",
            action_input={"response": task},
            confidence=0.3
        )
    
    def supports_tokens(self) -> bool:
        return False
