from framework import Agent, SimulatedLLMReasoning


def buscar_informacao(query: str) -> str:
    """Busca informações em uma base de conhecimento"""
    base_conhecimento = {
        "python": "Python é uma linguagem de programação de alto nível, interpretada e multiparadigma.",
        "framework": "Framework é uma estrutura de software que fornece abstração e ferramentas para desenvolvimento.",
        "ia": "Inteligência Artificial é o campo da ciência da computação que busca criar sistemas capazes de realizar tarefas que requerem inteligência humana.",
    }
    
    query_lower = query.lower()
    for chave, valor in base_conhecimento.items():
        if chave in query_lower:
            return valor
    
    return f"Informação sobre '{query}' não encontrada na base de conhecimento."


def traduzir(texto: str, idioma: str = "inglês") -> str:
    """Traduz texto para o idioma especificado"""
    traducoes = {
        "hello": {"português": "olá", "espanhol": "hola"},
        "goodbye": {"português": "adeus", "espanhol": "adiós"},
        "thank you": {"português": "obrigado", "espanhol": "gracias"},
    }
    
    texto_lower = texto.lower()
    if texto_lower in traducoes:
        if idioma in traducoes[texto_lower]:
            return traducoes[texto_lower][idioma]
    
    return f"Tradução não disponível"


agent = Agent(
    name="AssistenteVirtual",
    goal="Auxiliar o usuário com informações e traduções",
    reasoning=SimulatedLLMReasoning(),
    use_tokens=True,
    verbose=True
)

agent.add_tool(buscar_informacao)
agent.add_tool(traduzir)


if __name__ == "__main__":
    print("=== Assistente Virtual ===\n")
    
    tasks = [
        "O que é Python?",
        "traduzir hello para português",
        "me explique sobre ia"
    ]
    
    for task in tasks:
        print(f"Tarefa: {task}")
        result = agent.run(task)
        print(f"Resultado: {result}\n")
