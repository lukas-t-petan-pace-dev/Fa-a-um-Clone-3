from framework import Agent, DeterministicReasoning


def saudar(nome: str) -> str:
    """Saudar o usuário pelo nome"""
    return f"Olá, {nome}! Bem-vindo ao Python agente!"


def calcular(a: float, b: float, operacao: str = "somar") -> float:
    """Calculadora basica"""
    if operacao == "somar":
        return a + b
    elif operacao == "subtrair":
        return a - b
    elif operacao == "multiplicar":
        return a * b
    elif operacao == "dividir":
        return a / b if b != 0 else "Erro: divisão por zero"
    return "Operação inválida"


agent = Agent(
    name="MeuAgente",
    goal="Ajudar o usuário com tarefas",
    reasoning=DeterministicReasoning(),
    use_tokens=False,
    verbose=True
)

agent.add_tool(saudar)
agent.add_tool(calcular)


if __name__ == "__main__":
    print("Modo interativo. Digite 'sair' para encerrar.")
    agent.chat()
