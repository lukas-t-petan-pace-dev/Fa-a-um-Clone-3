# Nexus AI BR - Framework de Agentes de IA em Python Puro

Um framework modular e extensível para criar agentes de Inteligência Artificial, com suporte a múltiplos tipos de raciocínio (determinístico e LLM).

## Índice

1. [Instalação](#instalação)
2. [Conceitos Básicos](#conceitos-básicos)
3. [Criando seu Primeiro Agente](#criando-seu-primeiro-agente)
4. [Sistema de Raciocínio](#sistema-de-raciocínio)
5. [Sistema de Tools](#sistema-de-tools)
6. [Sistema de Memória](#sistema-de-memória)
7. [CLI - Interface de Linha de Comando](#cli---interface-de-linha-de-comando)
8. [Interface Web via WebSocket](#interface-web-via-websocket)
9. [Exemplos Completos](#exemplos-completos)
10. [Configurações Avançadas](#configurações-avançadas)

---

## Instalação

### Pré-requisitos

- Python 3.8 ou superior
- (Opcional) OpenAI API key para usar LLM real

### Instalação Básica

```bash
# Crie um Projeto e Abra
mkdir Exemplo
cd Exemplo

# Instale as dependências
pip install -e .
```

Ou instale apenas as dependências necessárias:

```bash
pip install openai
```

---

## Conceitos Básicos

### O que é um Agente?

Um **Agente** é uma entidade autônoma que:
1. Recebe uma tarefa do usuário
2. Utiliza **raciocínio** para decidir como executar
3. Pode usar **tools** (funções) para completar a tarefa
4. Mantém **memória** das interações anteriores

### Arquitetura do Framework

```
┌─────────────────────────────────────────────┐
│                 AGENT                       │
│  ┌─────────────────────────────────────┐    │
│  │         Reasoning Engine            │    │
│  │  (Deterministic ou LLM)             │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │         Memory System               │    │
│  │  (ShortTerm + LongTerm)             │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │         Tool Registry               │    │
│  │  (Funções Python)                   │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

---

## Criando seu Primeiro Agente

### Exemplo Básico

```python
from framework import Agent, DeterministicReasoning


def somar(a: float, b: float) -> float:
    """Soma dois números"""
    return a + b


# Criar o agente
agent = Agent(
    name="Calculadora",
    goal="Realizar operações matemáticas",
    reasoning=DeterministicReasoning(),  # Raciocínio offline
    use_tokens=False,                      # Não usa LLM
    verbose=True                           # Mostra logs
)

# Adicionar tools
agent.add_tool(somar)

# Executar uma tarefa
result = agent.run("some 10 + 5")
print(result)  # Output: 15.0
```

### Parâmetros do Agent

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|------------|
| `name` | str | Sim | Nome do agente |
| `goal` | str | Sim | Objetivo do agente |
| `reasoning` | ReasoningEngine | Não | Motor de raciocínio (padrão: DeterministicReasoning) |
| `use_tokens` | bool | Não | Se True, usa LLM. Padrão: False |
| `verbose` | bool | Não | Se True, mostra logs. Padrão: True |
| `max_iterations` | int | Não | Máximo de iterações. Padrão: 10 |
| `memory_size` | int | Não | Tamanho da memória. Padrão: 100 |

---

## Sistema de Raciocínio

O framework oferece diferentes tipos de raciocínio:

### 1. DeterministicReasoning (Offline)

Não usa tokens LLM. Funciona baseado em regras e heurísticas.

```python
from framework import Agent, DeterministicReasoning

agent = Agent(
    name="Bot",
    goal="Ajudar",
    reasoning=DeterministicReasoning(),
    use_tokens=False
)
```

**Características:**
- ✅ Funciona offline
- ✅ Não requer API keys
- ✅ Rápido
- ⚠️ Limitações em tarefas complexas

### 2. RuleBasedReasoning (Offline)

Raciocínio baseado em regras definidas.

```python
from framework import Agent, RuleBasedReasoning

agent = Agent(
    name="Bot",
    goal="Ajudar",
    reasoning=RuleBasedReasoning(),
    use_tokens=False
)
```

### 3. SimulatedLLMReasoning (Simulado)

Simula o comportamento de um LLM.

```python
from framework import Agent, SimulatedLLMReasoning

agent = Agent(
    name="Bot",
    goal="Ajudar",
    reasoning=SimulatedLLMReasoning(),
    use_tokens=True
)
```

### 4. LLMReasoning (Real)

Usa OpenAI GPT para raciocínio real.

```python
from framework import Agent, LLMReasoning
import os

agent = Agent(
    name="Bot",
    goal="Ajudar",
    reasoning=LLMReasoning(
        model="gpt-4",
        api_key=os.environ.get("OPENAI_API_KEY"),
        temperature=0.7
    ),
    use_tokens=True
)
```

**Instalação do cliente OpenAI:**
```bash
pip install openai
```

---

## Sistema de Tools

As tools são funções Python que o agente pode chamar para executar tarefas.

### Definindo Tools

```python
def buscar_produto(produto: str) -> str:
    """Busca um produto no catálogo"""
    catalogo = {
        "iphone": "iPhone 15 - R$ 7.499",
        "macbook": "MacBook Air - R$ 8.999"
    }
    return catalogo.get(produto.lower(), "Produto não encontrado")


def calcular(a: float, b: float, operacao: str = "somar") -> float:
    """Calculadora básica: somar, subtrair, multiplicar, dividir"""
    operacoes = {
        "somar": lambda x, y: x + y,
        "subtrair": lambda x, y: x - y,
        "multiplicar": lambda x, y: x * y,
        "dividir": lambda x, y: x / y if y != 0 else "Erro"
    }
    return operacoes.get(operacao, lambda x, y: "Inválido")(a, b)
```

### Adicionando Tools ao Agente

```python
# Forma 1: Adicionar uma tool
agent.add_tool(buscar_produto)

# Forma 2: Adicionar múltiplas tools
agent.add_tool(buscar_produto, name="buscar", description="Busca produtos")

# Forma 3: Adicionar várias de uma vez
agent.add_tools(buscar_produto, calcular)
```

### Listando Tools Disponíveis

```python
tools = agent.list_tools()
for tool in tools:
    print(f"- {tool['name']}: {tool['description']}")
```

### Decorador @tool

Você também pode usar o decorador:

```python
from framework import tool

@tool(name="saudar", description="Saudar o usuário")
def saudar(nome: str) -> str:
    return f"Olá, {nome}! Bem-vindo!"

agent.add_tool(saudar)
```

---

## Sistema de Memória

O framework possui dois tipos de memória:

### ShortTermMemory (Memória de Curto Prazo)

Armazena as interações recentes.

```python
from framework import ShortTermMemory

memory = ShortTermMemory(max_size=100)

memory.add("Usuário: Olá")
memory.add("Agente: Olá, como posso ajudar?")

# Obter contexto
contexto = memory.get_context(limit=5)
print(contexto)
```

### LongTermMemory (Memória de Longo Prazo)

Armazena informações importantes permanentemente.

```python
from framework import LongTermMemory

long_term = LongTermMemory()

long_term.add("Usuário prefere respostas curtas", metadata={"tipo": "preferência"})

# Buscar na memória
resultados = long_term.search("preferência")
```

### Memory (Memória Combinada)

```python
from framework import Agent, DeterministicReasoning
from framework.memory import Memory

# O Agent já cria uma memória automaticamente
agent = Agent(
    name="Bot",
    goal="Ajudar",
    reasoning=DeterministicReasoning()
)

# Acessar memória
agent.memory.add_interaction("user", "Olá")
agent.memory.add_interaction("assistant", "Olá, como posso ajudar?")

# Obter contexto
contexto = agent.get_memory_context()

# Limpar memória
agent.reset_memory()
```

---

## CLI - Interface de Linha de Comando

### Instalação da CLI

```bash
# Torne o framework instalável
pip install -e .

# Agora você pode usar:
nexus-ai-br --help
```

Ou use diretamente com Python:

```bash
python -m framework.cli --help
```

### Comandos Disponíveis

#### 1. Executar uma tarefa

```bash
# Executar tarefa específica
python -m framework.cli run arquivo.py "somar 10 + 5"

# Executar no modo interativo
python -m framework.cli run arquivo.py
```

#### 2. Modo Chat Interativo

```bash
python -m framework.cli chat arquivo.py
```

#### 3. Criar Novo Projeto

```bash
python -m framework.cli init nome_do_projeto
```

Isso cria:
```
nome_do_projeto/
├── main.py
└── README.md
```

#### 4. Listar Tools

```bash
python -m framework.cli list arquivo.py
```

---

## Interface Web via WebSocket

O framework oferece um servidor WebSocket integrado que permite conectar seu agente a qualquer aplicação web em tempo real.

### Visão Geral

```
┌─────────────┐         WebSocket          ┌─────────────┐
│   Browser   │ ◄────────────────────────► │  Servidor   │
│  (HTML/JS)  │                            │  (Python)   │
└─────────────┘                            └─────────────┘
                                                │
                                          ┌─────┴─────┐
                                          │   Agent   │
                                          │ + Tools   │
                                          │ + Memory  │
                                          └───────────┘
```

### Servidor WebSocket

O servidor WebSocket permite que seu agente receba mensagens de clientes web e responda em tempo real.

#### Criando o Servidor

```python
# server.py
from framework import Agent, DeterministicReasoning, run_agent_server


def buscar_produto(produto: str) -> str:
    """Busca produto no catálogo"""
    catalogo = {
        "iphone": "iPhone 15 Pro - R$ 7.499",
        "macbook": "MacBook Air - R$ 8.999",
    }
    return catalogo.get(produto.lower(), "Produto não encontrado")


agent = Agent(
    name="VendasBot",
    goal="Auxiliar clientes",
    reasoning=DeterministicReasoning(),
    use_tokens=False
)

agent.add_tool(buscar_produto)


if __name__ == "__main__":
    run_agent_server(agent, host="0.0.0.0", port=8765)
```

#### Executando o Servidor

```bash
python server.py
```

O servidor will start em `ws://localhost:8765`

### API de Mensagens WebSocket

O servidor suporta as seguintes mensagens:

#### Cliente → Servidor

| Tipo | Descrição | Dados |
|------|------------|-------|
| `chat` | Enviar mensagem | `{"message": "sua mensagem"}` |
| `ping` | Verificar conexão | `{}` |
| `reset_memory` | Limpar memória | `{}` |
| `get_tools` | Listar tools | `{}` |
| `get_info` | Info do agente | `{}` |

#### Servidor → Cliente

| Tipo | Descrição | Dados |
|------|------------|-------|
| `connected` | Conexão estabelecida | `{"message": "...", "agent_name": "..."}` |
| `thinking` | Agent processando | `{"message": "..."}` |
| `response` | Resposta do agente | `{"message": "...", "agent": "..."}` |
| `tools_list` | Lista de tools | `{"tools": [...]}` |
| `agent_info` | Info do agente | `{"name": "...", "goal": "..."}` |
| `error` | Erro | `{"message": "..."}` |

### Interface Web Pronta

O framework inclui uma interface HTML/JavaScript pronta para uso.

#### Arquivo: `examples/web/index.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>Chat com Agente</title>
</head>
<body>
    <!-- Interface de chat completa -->
    <!-- Veja o arquivo examples/web/index.html -->
</body>
</html>
```

#### Como Usar

1. **Inicie o servidor do agente:**

```bash
python examples/web_agent.py
```

2. **Sirva a página HTML:**

Você pode usar qualquer servidor HTTP:

```bash
# Com Python
cd examples/web
python -m http.server 8080

# Com Node.js (se instalado)
npx http-server -p 8080
```

3. **Acesse no navegador:**

```
http://localhost:8080
```

### Exemplo: Página HTML Personalizada

```html
<!DOCTYPE html>
<html>
<head>
    <title>Meu Chat</title>
</head>
<body>
    <div id="chat"></div>
    <input type="text" id="message">
    <button onclick="sendMessage()">Enviar</button>

    <script>
        const ws = new WebSocket('ws://localhost:8765');
        
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            if (msg.type === 'response') {
                console.log('Resposta:', msg.data.message);
            }
        };
        
        function sendMessage() {
            const text = document.getElementById('message').value;
            ws.send(JSON.stringify({
                type: 'chat',
                data: { message: text }
            }));
        }
    </script>
</body>
</html>
```

### Configurações do Servidor

```python
from framework import WebSocketServer, Agent, DeterministicReasoning

agent = Agent(
    name="Bot",
    goal="Ajudar",
    reasoning=DeterministicReasoning()
)

server = WebSocketServer(
    agent=agent,
    host="0.0.0.0",    # Host (0.0.0.0 para aceitar conexões externas)
    port=8765,         # Porta
    cors_origin="*"    # Origens permitidas para CORS
)

server.run()  # Inicia o servidor bloqueante
```

### Servidor com asyncio

Se você precisa de mais controle:

```python
import asyncio
from framework import WebSocketServer, Agent, DeterministicReasoning

async def main():
    agent = Agent(
        name="Bot",
        goal="Ajudar",
        reasoning=DeterministicReasoning()
    )
    
    server = WebSocketServer(agent=agent, port=8765)
    await server.start()

asyncio.run(main())
```

### Broadcast para Múltiplos Clientes

```python
# Enviar mensagem para todos os clientes conectados
await server.broadcast(WebSocketMessage(
    type="announcement",
    data={"message": "Manutenção em 5 minutos"}
))
```

### Considerações de Produção

1. **HTTPS/WSS**: Em produção, use WebSocket Secure (WSS) com SSL/TLS
2. **Autenticação**: Implemente autenticação na conexão WebSocket
3. **Rate Limiting**: Limite o número de mensagens por cliente
4. **Logs**: Configure logging apropriado para monitorar
5. **Replicas**: Para alta disponibilidade, considere usar Redis Pub/Sub

---

## Exemplos Completos

### Exemplo 1: Agente de Matemática

```python
# math_agent.py
from framework import Agent, DeterministicReasoning


def somar(a: float, b: float) -> float:
    return a + b


def subtrair(a: float, b: float) -> float:
    return a - b


def multiplicar(a: float, b: float) -> float:
    return a * b


def dividir(a: float, b: float) -> str:
    if b == 0:
        return "Erro: divisão por zero"
    return a / b


agent = Agent(
    name="MathAgent",
    goal="Resolver operações matemáticas",
    reasoning=DeterministicReasoning(),
    use_tokens=False
)

agent.add_tools(somar, subtrair, multiplicar, dividir)


if __name__ == "__main__":
    result = agent.run("some 10 + 5")
    print(result)
```

**Executar:**
```bash
python -m framework.cli run math_agent.py "some 10 + 5"
```

---

### Exemplo 2: Assistente Virtual

```python
# assistant.py
from framework import Agent, DeterministicReasoning


def buscar_informacao(query: str) -> str:
    base = {
        "python": "Python é uma linguagem de programação de alto nível.",
        "framework": "Framework é uma estrutura de software.",
    }
    for chave, valor in base.items():
        if chave in query.lower():
            return valor
    return "Informação não encontrada."


def traduzir(texto: str, idioma: str = "inglês") -> str:
    traducoes = {
        "hello": {"português": "olá", "espanhol": "hola"},
        "goodbye": {"português": "adeus", "espanhol": "adiós"},
    }
    texto_lower = texto.lower()
    if texto_lower in traducoes and idioma in traducoes[texto_lower]:
        return traducoes[texto_lower][idioma]
    return "Tradução não disponível"


agent = Agent(
    name="Assistente",
    goal="Auxiliar o usuário",
    reasoning=DeterministicReasoning(),
    use_tokens=False
)

agent.add_tools(buscar_informacao, traduzir)


if __name__ == "__main__":
    agent.chat()  # Modo interativo
```

**Executar:**
```bash
python -m framework.cli chat assistant.py
```

---

### Exemplo 3: Bot de Vendas com LLM

```bash
# Defina a variável de ambiente
export OPENAI_API_KEY=sua_chave_aqui
```

```python
# sales_bot.py
from framework import Agent, LLMReasoning
import os


def buscar_produto(produto: str) -> str:
    catalogo = {
        "iphone": "iPhone 15 Pro - R$ 7.499",
        "samsung": "Samsung Galaxy S24 - R$ 5.999",
    }
    return catalogo.get(produto.lower(), "Produto não encontrado")


api_key = os.environ.get("OPENAI_API_KEY")

if api_key:
    agent = Agent(
        name="VendasBot",
        goal="Auxiliar clientes",
        reasoning=LLMReasoning(
            model="gpt-4",
            api_key=api_key,
            temperature=0.7
        ),
        use_tokens=True
    )

    agent.add_tool(buscar_produto)

    if __name__ == "__main__":
        result = agent.run("Qual o preço do iPhone?")
        print(result)
```

---

### Exemplo 4: Criando Projeto com CLI

```bash
# Criar novo projeto
python -m framework.cli init meu_bot

# Entrar no diretório
cd meu_bot

# Executar
python main.py
```

O arquivo `main.py` gerado:

```python
from framework import Agent, DeterministicReasoning


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
```

### Exemplo 5: Agente com Interface Web

Este exemplo mostra como criar um agente que pode ser acessado por um site via WebSocket.

#### 1. Servidor do Agente (Python)

```python
# web_agent.py
from framework import Agent, DeterministicReasoning, run_agent_server


def buscar_produto(produto: str) -> str:
    """Busca produto no catálogo"""
    catalogo = {
        "iphone": "iPhone 15 Pro - R$ 7.499",
        "samsung": "Samsung Galaxy S24 - R$ 5.999",
        "macbook": "MacBook Air M3 - R$ 8.999",
    }
    return catalogo.get(produto.lower(), "Produto não encontrado")


def calcular_frete(valor_compra: float, distancia: int) -> str:
    """Calcula o frete"""
    if valor_compra >= 500:
        return "Frete grátis!"
    taxa_frete = distancia * 0.50
    return f"Frete: R$ {taxa_frete:.2f}"


agent = Agent(
    name="VendasBot",
    goal="Auxiliar clientes em compras",
    reasoning=DeterministicReasoning(),
    use_tokens=False
)

agent.add_tool(buscar_produto)
agent.add_tool(calcular_frete)


if __name__ == "__main__":
    run_agent_server(agent, host="0.0.0.0", port=8765)
```

#### 2. Interface Web (HTML/JavaScript)

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Chat com Agente</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 50px auto; }
        #messages { border: 1px solid #ccc; height: 300px; overflow-y: auto; padding: 10px; }
        .user { text-align: right; color: blue; }
        .agent { text-align: left; color: green; }
    </style>
</head>
<body>
    <h1>Chat com Agente</h1>
    <div id="messages"></div>
    <input id="message" placeholder="Digite sua mensagem...">
    <button onclick="send()">Enviar</button>

    <script>
        const ws = new WebSocket('ws://localhost:8765');
        
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            if (msg.type === 'response') {
                document.getElementById('messages').innerHTML += 
                    `<div class="agent">Agente: ${msg.data.message}</div>`;
            }
        };
        
        function send() {
            const text = document.getElementById('message').value;
            document.getElementById('messages').innerHTML += 
                `<div class="user">Você: ${text}</div>`;
            ws.send(JSON.stringify({ type: 'chat', data: { message: text } }));
        }
    </script>
</body>
</html>
```

#### 3. Executando

```bash
# Terminal 1: Iniciar servidor do agente
python web_agent.py

# Terminal 2: Servir página HTML
cd examples/web
python -m http.server 8080

# Acessar no navegador: http://localhost:8080
```

---

## Configurações Avançadas

### Personalizando o Raciocínio Determinístico

```python
from framework import DeterministicReasoning

# Criar instância com configurações
reasoning = DeterministicReasoning()

# Adicionar sequências de ações customizadas
reasoning.action_sequences = {
    "saudar": "respond",
    "calcular": "calcular"
}
```

### Usando Memória Persistente

```python
from framework import Agent, DeterministicReasoning
from framework.memory import Memory

# Criar memória com configurações
memory = Memory(short_term_max_size=50)

agent = Agent(
    name="Bot",
    goal="Ajudar",
    reasoning=DeterministicReasoning(),
    use_tokens=False
)

# Adicionar à memória de longo termo
agent.memory.add_to_long_term(
    "Informação importante",
    metadata={"categoria": "importante"}
)
```

### Logging Customizado

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

agent = Agent(
    name="Bot",
    goal="Ajudar",
    reasoning=DeterministicReasoning(),
    verbose=True  # Ativar logs
)
```

### Criando Custom Reasoning Engine

```python
from framework.reasoning import ReasoningEngine, ReasoningResult


class MyCustomReasoning(ReasoningEngine):
    def think(self, task, memory_context, available_tools):
        # Seu lógica customizada
        return ReasoningResult(
            thought="Processando...",
            action="responder",
            action_input={"resposta": "Olá!"}
        )
    
    def supports_tokens(self):
        return False


agent = Agent(
    name="Bot",
    goal="Ajudar",
    reasoning=MyCustomReasoning()
)
```

---

## Troubleshooting

### "Module not found: framework"

Execute com o PYTHONPATH configurado:

```bash
# Linux/Mac
export PYTHONPATH=.

# Windows (PowerShell)
$env:PYTHONPATH = "."

# Ou execute diretamente
python -c "import sys; sys.path.insert(0, '.'); from framework import Agent"
```

### "OpenAI API key not found"

Defina a variável de ambiente:

```bash
# Linux/Mac
export OPENAI_API_KEY=sk-...

# Windows
set OPENAI_API_KEY=sk-...
```

### Problemas com encoding no Windows

O framework usa UTF-8. Configure o terminal:

```cmd
chcp 65001
```

---

## Roadmap

- [ ] Suporte a mais provedores de LLM (Anthropic, Google)
- [ ] Sistema de agentes múltiplos
- [ ] Persistência de memória em arquivo
- [ ] Sistema de plugins
- [ ] Interface web

---

## Licença

MIT License
