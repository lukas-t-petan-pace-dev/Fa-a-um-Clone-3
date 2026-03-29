from framework import Agent, DeterministicReasoning


def get_weather(cidade: str) -> str:
    """Retorna informações meteorológicas (simulado)"""
    clima = {
        "são paulo": "Ensolarado, 25°C",
        "rio de janeiro": "Parcialmente nublado, 28°C",
        "brasília": "Seco, 30°C",
        "curitiba": "Nublado, 18°C",
    }
    
    cidade_lower = cidade.lower()
    return clima.get(cidade_lower, f"Clima para {cidade} não disponível")


def get_time(cidade: str = "brasilia") -> str:
    """Retorna a hora atual (simulado)"""
    import datetime
    return datetime.datetime.now().strftime("%H:%M:%S")


def calcular(a: float, b: float, operacao: str = "somar") -> float:
    """Calculadora básica"""
    operacoes = {
        "somar": lambda x, y: x + y,
        "subtrair": lambda x, y: x - y,
        "multiplicar": lambda x, y: x * y,
        "dividir": lambda x, y: x / y if y != 0 else "Erro",
    }
    
    func = operacoes.get(operacao)
    if func:
        return func(a, b)
    return "Operação inválida"


agent = Agent(
    name="ChatBot",
    goal="Conversar e ajudar o usuário",
    reasoning=DeterministicReasoning(),
    use_tokens=False,
    verbose=True
)

agent.add_tool(get_weather)
agent.add_tool(get_time)
agent.add_tool(calcular)


if __name__ == "__main__":
    print("=== Chat Interativo ===")
    print("Digite 'sair' para encerrar\n")
    
    agent.chat()
