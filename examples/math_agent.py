from framework import Agent, DeterministicReasoning


def somar(a: float, b: float) -> float:
    """Soma dois números"""
    return a + b


def subtrair(a: float, b: float) -> float:
    """Subtrai dois números"""
    return a - b


def multiplicar(a: float, b: float) -> float:
    """Multiplica dois números"""
    return a * b


def dividir(a: float, b: float) -> str:
    """Divide dois números"""
    if b == 0:
        return "Erro: divisão por zero"
    return a / b


agent = Agent(
    name="MathAgent",
    goal="Resolver operações matemáticas",
    reasoning=DeterministicReasoning(),
    use_tokens=False,
    verbose=True
)

agent.add_tool(somar)
agent.add_tool(subtrair)
agent.add_tool(multiplicar)
agent.add_tool(dividir)


if __name__ == "__main__":
    print("=== Agente de Matemática ===\n")
    
    tasks = [
        "some 10 + 5",
        "subtraia 20 - 8",
        "multiplique 7 * 6",
        "divida 100 / 4"
    ]
    
    for task in tasks:
        print(f"Tarefa: {task}")
        result = agent.run(task)
        print(f"Resultado: {result}\n")
