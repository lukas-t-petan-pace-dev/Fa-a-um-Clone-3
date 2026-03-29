import asyncio
import json
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebSocketServer")


@dataclass
class WebSocketMessage:
    type: str
    data: Any
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WebSocketMessage':
        data = json.loads(json_str)
        return cls(
            type=data.get("type", ""),
            data=data.get("data"),
            timestamp=data.get("timestamp")
        )


class WebSocketServer:
    def __init__(
        self,
        agent,
        host: str = "localhost",
        port: int = 8765,
        cors_origin: str = "*"
    ):
        self.agent = agent
        self.host = host
        self.port = port
        self.cors_origin = cors_origin
        self.clients: set = set()
        self._server = None
        self._is_running = False
    
    async def handle_client(self, websocket, path):
        self.clients.add(websocket)
        client_id = f"client_{len(self.clients)}"
        logger.info(f"Cliente conectado: {client_id}")
        
        await self._send_message(websocket, WebSocketMessage(
            type="connected",
            data={"message": "Conectado ao agente", "agent_name": self.agent.name}
        ))
        
        try:
            async for message in websocket:
                try:
                    ws_message = WebSocketMessage.from_json(message)
                    await self._process_message(websocket, ws_message, client_id)
                except json.JSONDecodeError:
                    await self._send_message(websocket, WebSocketMessage(
                        type="error",
                        data={"message": "Mensagem inválida"}
                    ))
        except Exception as e:
            logger.error(f"Erro com cliente {client_id}: {e}")
        finally:
            self.clients.discard(websocket)
            logger.info(f"Cliente desconectado: {client_id}")
    
    async def _process_message(self, websocket, message: WebSocketMessage, client_id: str):
        msg_type = message.type
        data = message.data
        
        if msg_type == "chat":
            task = data.get("message", "")
            logger.info(f"Mensagem de {client_id}: {task}")
            
            await self._send_message(websocket, WebSocketMessage(
                type="thinking",
                data={"message": "Processando..."}
            ))
            
            try:
                response = self.agent.run(task)
                
                await self._send_message(websocket, WebSocketMessage(
                    type="response",
                    data={
                        "message": response,
                        "agent": self.agent.name
                    }
                ))
            except Exception as e:
                await self._send_message(websocket, WebSocketMessage(
                    type="error",
                    data={"message": str(e)}
                ))
        
        elif msg_type == "ping":
            await self._send_message(websocket, WebSocketMessage(
                type="pong",
                data={"timestamp": datetime.now().isoformat()}
            ))
        
        elif msg_type == "reset_memory":
            self.agent.reset_memory()
            await self._send_message(websocket, WebSocketMessage(
                type="memory_reset",
                data={"message": "Memória resetada"}
            ))
        
        elif msg_type == "get_tools":
            tools = self.agent.list_tools()
            await self._send_message(websocket, WebSocketMessage(
                type="tools_list",
                data={"tools": tools}
            ))
        
        elif msg_type == "get_info":
            await self._send_message(websocket, WebSocketMessage(
                type="agent_info",
                data={
                    "name": self.agent.name,
                    "goal": self.agent.goal,
                    "reasoning": self.agent.reasoning.__class__.__name__,
                    "use_tokens": self.agent.use_tokens
                }
            ))
        
        else:
            await self._send_message(websocket, WebSocketMessage(
                type="error",
                data={"message": f"Tipo de mensagem desconhecido: {msg_type}"}
            ))
    
    async def _send_message(self, websocket, message: WebSocketMessage):
        try:
            await websocket.send(message.to_json())
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
    
    async def broadcast(self, message: WebSocketMessage):
        """Envia mensagem para todos os clientes conectados"""
        if self.clients:
            await asyncio.gather(
                *[self._send_message(client, message) for client in self.clients],
                return_exceptions=True
            )
    
    async def start(self):
        """Inicia o servidor WebSocket"""
        self._server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        self._is_running = True
        addr = self._server.sockets[0].getsockname()
        logger.info(f"Servidor WebSocket iniciado em ws://{addr[0]}:{addr[1]}")
        logger.info(f"Agente: {self.agent.name}")
        
        async with self._server:
            await self._server.serve_forever()
    
    def run(self):
        """Executa o servidor (bloqueante)"""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            logger.info("Servidor encerrado")
    
    async def stop(self):
        """Encerra o servidor"""
        self._is_running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        logger.info("Servidor WebSocket encerrado")


def create_websocket_app(agent, host: str = "localhost", port: int = 8765):
    """Cria e retorna uma instância do servidor WebSocket"""
    return WebSocketServer(agent=agent, host=host, port=port)


def run_agent_server(agent, host: str = "localhost", port: int = 8765):
    """Executa o agente em um servidor WebSocket"""
    server = create_websocket_app(agent, host, port)
    server.run()
