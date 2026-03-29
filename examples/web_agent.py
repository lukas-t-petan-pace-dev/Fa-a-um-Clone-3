"""
Exemplo: Agente com Interface Web via WebSocket
Executa o agente em um servidor WebSocket para ser acessado por um site
"""

from framework import Agent, DeterministicReasoning, run_agent_server


def buscar_produto(produto: str) -> str:
    """Busca produto no catálogo"""
    catalogo = {
        "iphone": "iPhone 15 Pro - R$ 7.499",
        "samsung": "Samsung Galaxy S24 - R$ 5.999",
        "macbook": "MacBook Air M3 - R$ 8.999",
        "ipad": "iPad Pro 11 - R$ 6.999",
    }
    
    produto_lower = produto.lower()
    for chave, valor in catalogo.items():
        if chave in produto_lower:
            return valor
    
    return "Produto não encontrado"


def calcular_frete(valor_compra: float, distancia: int) -> str:
    """Calcula o frete baseado no valor e distância"""
    if valor_compra >= 500:
        return "Frete grátis!"
    
    taxa_frete = distancia * 0.50
    return f"Frete: R$ {taxa_frete:.2f}"


def get_horario() -> str:
    """Retorna o horário atual"""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")


agent = Agent(
    name="VendasBot",
    goal="Auxiliar clientes em compras",
    reasoning=DeterministicReasoning(),
    use_tokens=False,
    verbose=True
)

agent.add_tool(buscar_produto)
agent.add_tool(calcular_frete)
agent.add_tool(get_horario)


if __name__ == "__main__":
    print("=" * 50)
    print("Servidor WebSocket do Agente")
    print("=" * 50)
    print(f"Agente: {agent.name}")
    print(f"Objetivo: {agent.goal}")
    print("\nConecte-se em: ws://localhost:8765")
    print("Ou use a interface web em: http://localhost:8765")
    print("\nFerramentas disponíveis:")
    for tool in agent.list_tools():
        print(f"  - {tool['name']}: {tool['description']}")
    print("\nPressione Ctrl+C para encerrar\n")
    
    run_agent_server(agent, host="0.0.0.0", port=8765)
