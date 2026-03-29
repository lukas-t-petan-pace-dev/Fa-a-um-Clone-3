"""
Exemplo 4: Agente com LLM Real (OpenAI)
Requer: pip install openai
"""

from framework import Agent, LLMReasoning


def buscar_produto(produto: str) -> str:
    """Busca produto no catálogo"""
    catalogo = {
        "iphone": "iPhone 15 Pro - R$ 7.499",
        "samsung": "Samsung Galaxy S24 - R$ 5.999",
        "macbook": "MacBook Air M3 - R$ 8.999",
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


import os

api_key = os.environ.get("OPENAI_API_KEY")

if api_key:
    reasoning = LLMReasoning(
        model="gpt-4",
        api_key=api_key,
        temperature=0.7
    )
    
    agent = Agent(
        name="VendasBot",
        goal="Auxiliar clientes em compras",
        reasoning=reasoning,
        use_tokens=True,
        verbose=True
    )
    
    agent.add_tool(buscar_produto)
    agent.add_tool(calcular_frete)
    
    if __name__ == "__main__":
        print("=== Bot de Vendas com LLM ===\n")
        
        tasks = [
            "Qual o preço do iPhone?",
            "Quanto fica o frete para São Paulo?",
            "Qual o produto mais caro?"
        ]
        
        for task in tasks:
            print(f"Tarefa: {task}")
            result = agent.run(task)
            print(f"Resultado: {result}\n")
else:
    print("Este exemplo requer a variável de ambiente OPENAI_API_KEY")
    print("Defina: export OPENAI_API_KEY=sua_chave")
