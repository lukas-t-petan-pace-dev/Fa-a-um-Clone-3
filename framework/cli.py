#!/usr/bin/env python3
import argparse
import importlib.util
import sys
import os
from pathlib import Path


def load_agent_from_file(filepath: str):
    filepath = Path(filepath)
    
    if not filepath.exists():
        print(f"Erro: Arquivo '{filepath}' não encontrado")
        sys.exit(1)
    
    module_name = filepath.stem
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    
    if spec is None or spec.loader is None:
        print(f"Erro: Não foi possível carregar '{filepath}'")
        sys.exit(1)
    
    module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Erro ao executar arquivo: {e}")
        sys.exit(1)
    
    agent = None
    for item_name in dir(module):
        item = getattr(module, item_name)
        from framework.agent import Agent
        if isinstance(item, Agent):
            agent = item
            break
    
    if agent is None:
        print("Erro: Nenhum agente encontrado no arquivo")
        print("Certifique-se de criar um Agent e atribuí-lo a uma variável")
        sys.exit(1)
    
    return agent


def run_agent(filepath: str, task: str = None):
    agent = load_agent_from_file(filepath)
    
    if task:
        print(f"\n>>> {task}\n")
        result = agent.run(task)
        print(f"{result}\n")
    else:
        print(f"\nExecutando agente: {agent.name}")
        print(f"Objetivo: {agent.goal}")
        print(f"\nFerramentas disponíveis:")
        for tool in agent.list_tools():
            print(f"  - {tool['name']}: {tool['description']}")
        print()
        
        while True:
            try:
                task_input = input("Tarefa: ").strip()
                if not task_input:
                    continue
                if task_input.lower() in ["sair", "exit", "quit"]:
                    break
                
                result = agent.run(task_input)
                print(f"\nResultado: {result}\n")
            except KeyboardInterrupt:
                print("\nEncerrando...")
                break
            except Exception as e:
                print(f"Erro: {e}")


def chat_with_agent(filepath: str):
    agent = load_agent_from_file(filepath)
    agent.chat()


def init_project(project_name: str):
    project_path = Path(project_name)
    
    if project_path.exists():
        print(f"Erro: Diretório '{project_name}' já existe")
        sys.exit(1)
    
    project_path.mkdir(parents=True)
    
    main_py_content = '''from framework import Agent, DeterministicReasoning


def saudar(nome: str) -> str:
    """Saudar o usuário pelo nome"""
    return f"Olá, {nome}! Bem-vindo ao agente!"


def calcular(a: float, b: float, operacao: str = "somar") -> float:
    """Calculadora básica"""
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
'''

    readme_content = f'''# Projeto {project_name}

Este é um projeto criado com o framework de agentes de IA.

## Como usar

Execute o agente:
```bash
python main.py
```

## Estrutura

- `main.py`: Arquivo principal com a definição do agente
'''

    (project_path / "main.py").write_text(main_py_content)
    (project_path / "README.md").write_text(readme_content)
    
    print(f"Projeto '{project_name}' criado com sucesso!")
    print(f"\nPara começar:")
    print(f"  cd {project_name}")
    print(f"  python main.py")


def main():
    parser = argparse.ArgumentParser(
        description="Nexus AI BR Framework - CLI",
        prog="nexus-ai-br"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    run_parser = subparsers.add_parser("run", help="Executar agente com uma tarefa")
    run_parser.add_argument("file", help="Arquivo Python com o agente")
    run_parser.add_argument("task", nargs="?", help="Tarefa opcional")
    
    chat_parser = subparsers.add_parser("chat", help="Modo interativo")
    chat_parser.add_argument("file", help="Arquivo Python com o agente")
    
    init_parser = subparsers.add_parser("init", help="Criar novo projeto")
    init_parser.add_argument("name", help="Nome do projeto")
    
    list_parser = subparsers.add_parser("list", help="Listar tools disponíveis")
    list_parser.add_argument("file", help="Arquivo Python com o agente")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_agent(args.file, args.task)
    elif args.command == "chat":
        chat_with_agent(args.file)
    elif args.command == "init":
        init_project(args.name)
    elif args.command == "list":
        agent = load_agent_from_file(args.file)
        print(f"\nAgent: {agent.name}")
        print(f"Goal: {agent.goal}")
        print(f"\nFerramentas disponíveis:")
        for tool in agent.list_tools():
            print(f"  - {tool['name']}: {tool['description']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
