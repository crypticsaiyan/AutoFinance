"""
Copilot Chatbox Component - Interactive Chat Interface
"""
import subprocess
import json
import requests
from typing import List, Dict, Optional
from collections import deque
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED
from rich.markdown import Markdown


class ChatMessage:
    """Represents a chat message."""
    
    def __init__(self, role: str, content: str, timestamp: Optional[str] = None):
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.timestamp = timestamp or self._get_timestamp()
    
    @staticmethod
    def _get_timestamp():
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp
        }


class MCPToolExecutor:
    """Execute MCP tools via HTTP requests."""
    
    def __init__(self, base_url: str = "http://localhost", ports: Dict[str, int] = None):
        self.base_url = base_url
        self.ports = ports or {
            "market": 9001,
            "risk": 9002,
            "execution": 9003,
            "compliance": 9004,
            "technical": 9005,
            "fundamental": 9006,
            "volatility": 9007,
            "portfolio": 9008,
            "news": 9009,
            "macro": 9010,
            "alert": 9011,
            "simulation": 9012,
            "notification": 9013,
        }
    
    def call_tool(self, server: str, method: str, params: Dict = None) -> Dict:
        """Call an MCP tool."""
        if server not in self.ports:
            return {"error": f"Unknown server: {server}"}
        
        url = f"{self.base_url}:{self.ports[server]}/mcp"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_available_tools(self, server: str) -> List[str]:
        """Get list of available tools from a server."""
        response = self.call_tool(server, "tools/list")
        if "result" in response:
            return [tool["name"] for tool in response["result"].get("tools", [])]
        return []
    
    def get_all_tools(self) -> Dict[str, List[str]]:
        """Get all available tools from all servers."""
        all_tools = {}
        for server in self.ports.keys():
            all_tools[server] = self.get_available_tools(server)
        return all_tools


class CopilotChat:
    """Copilot-style chat interface with MCP tool integration."""
    
    def __init__(
        self,
        width: int = 80,
        height: int = 30,
        max_history: int = 100,
        mcp_base_url: str = "http://localhost",
        mcp_ports: Dict[str, int] = None
    ):
        self.width = width
        self.height = height
        self.max_history = max_history
        self.messages: deque = deque(maxlen=max_history)
        self.console = Console()
        self.mcp_executor = MCPToolExecutor(mcp_base_url, mcp_ports)
        
        # Add welcome message
        self.add_message(
            "assistant",
            "🤖 **AutoFinance Copilot** ready!\n\n"
            "I can help you with:\n"
            "- Market analysis and price queries\n"
            "- Portfolio management\n"
            "- Risk assessment\n"
            "- Trade execution\n"
            "- Technical and fundamental analysis\n\n"
            "Just ask me anything or use commands like:\n"
            "`/tools` - List available MCP tools\n"
            "`/call <server> <method>` - Call an MCP tool\n"
            "`/clear` - Clear chat history"
        )
    
    def add_message(self, role: str, content: str):
        """Add a message to the chat history."""
        message = ChatMessage(role, content)
        self.messages.append(message)
    
    def clear_history(self):
        """Clear chat history."""
        self.messages.clear()
        self.add_message("assistant", "Chat history cleared.")
    
    def process_command(self, user_input: str) -> str:
        """Process special commands."""
        parts = user_input.strip().split()
        command = parts[0].lower()
        
        if command == "/tools":
            tools = self.mcp_executor.get_all_tools()
            response = "**Available MCP Tools:**\n\n"
            for server, tool_list in tools.items():
                if tool_list:
                    response += f"**{server.upper()}:**\n"
                    for tool in tool_list:
                        response += f"  - {tool}\n"
            return response
        
        elif command == "/call":
            if len(parts) < 3:
                return "Usage: /call <server> <method> [params_json]"
            
            server = parts[1]
            method = parts[2]
            params = {}
            
            if len(parts) > 3:
                try:
                    params = json.loads(" ".join(parts[3:]))
                except json.JSONDecodeError:
                    return "Invalid JSON parameters"
            
            result = self.mcp_executor.call_tool(server, method, params)
            return f"**Result:**\n```json\n{json.dumps(result, indent=2)}\n```"
        
        elif command == "/clear":
            self.clear_history()
            return ""
        
        elif command == "/help":
            return (
                "**Available Commands:**\n\n"
                "`/tools` - List all available MCP tools\n"
                "`/call <server> <method> [params]` - Call an MCP tool\n"
                "`/clear` - Clear chat history\n"
                "`/help` - Show this help message\n\n"
                "**Example:**\n"
                "`/call market get_price {\"symbol\": \"AAPL\"}`"
            )
        
        else:
            return f"Unknown command: {command}. Type `/help` for available commands."
    
    def send_message(self, user_input: str) -> str:
        """Process user input and generate response."""
        # Add user message
        self.add_message("user", user_input)
        
        # Check if it's a command
        if user_input.startswith("/"):
            response = self.process_command(user_input)
            if response:
                self.add_message("assistant", response)
            return response
        
        # For now, we'll provide a simple response
        # In a real implementation, this would call the actual Copilot API
        response = self._generate_response(user_input)
        self.add_message("assistant", response)
        
        return response
    
    def _generate_response(self, user_input: str) -> str:
        """Generate a response (placeholder for actual AI integration)."""
        # This is a placeholder. In production, this would:
        # 1. Send to Copilot CLI or API
        # 2. Include context about available MCP tools
        # 3. Execute tool calls as needed
        
        lower_input = user_input.lower()
        
        if any(word in lower_input for word in ["price", "quote", "market"]):
            return (
                "To get market data, you can use:\n"
                "`/call market get_price {\"symbol\": \"AAPL\"}`\n\n"
                "Or try these commands:\n"
                "- `/call technical get_rsi {\"symbol\": \"AAPL\"}`\n"
                "- `/call fundamental get_metrics {\"symbol\": \"AAPL\"}`"
            )
        
        elif any(word in lower_input for word in ["portfolio", "holdings", "positions"]):
            return (
                "To view your portfolio:\n"
                "`/call execution get_portfolio`\n\n"
                "Or get portfolio analytics:\n"
                "`/call portfolio get_analytics`"
            )
        
        elif any(word in lower_input for word in ["risk", "validate"]):
            return (
                "To assess risk:\n"
                "`/call risk validate_trade {\"symbol\": \"AAPL\", \"quantity\": 10, \"action\": \"BUY\"}`"
            )
        
        elif any(word in lower_input for word in ["buy", "sell", "trade"]):
            return (
                "To execute a trade:\n"
                "`/call execution execute_trade {\"symbol\": \"AAPL\", \"quantity\": 10, \"action\": \"BUY\"}`"
            )
        
        else:
            return (
                f"I understand you're asking about: *{user_input}*\n\n"
                "I can help you access any of the 13 MCP servers. "
                "Use `/tools` to see all available tools, or `/help` for command syntax."
            )
    
    def render(self, show_last_n: int = 10) -> Panel:
        """Render the chat interface as a Rich Panel."""
        # Get last N messages
        recent_messages = list(self.messages)[-show_last_n:]
        
        if not recent_messages:
            content = Text("No messages yet. Type a message to start!", style="dim")
        else:
            content = Text()
            for msg in recent_messages:
                # Role indicator
                if msg.role == "user":
                    content.append(f"[{msg.timestamp}] ", style="dim")
                    content.append("You: ", style="bold cyan")
                else:
                    content.append(f"[{msg.timestamp}] ", style="dim")
                    content.append("🤖 Copilot: ", style="bold magenta")
                
                content.append(f"{msg.content}\n\n", style="white")
        
        panel = Panel(
            content,
            title="[bold magenta]💬 Copilot Chat[/bold magenta]",
            subtitle=f"[dim]{len(self.messages)} messages[/dim]",
            box=ROUNDED,
            border_style="magenta",
            height=self.height
        )
        
        return panel


# Example usage
if __name__ == "__main__":
    console = Console()
    
    chat = CopilotChat(width=80, height=30)
    
    # Simulate conversation
    test_inputs = [
        "What's the price of AAPL?",
        "/tools",
        "/call market get_price {\"symbol\": \"AAPL\"}",
        "Show me my portfolio",
    ]
    
    for user_input in test_inputs:
        chat.send_message(user_input)
        console.print(chat.render())
        console.print("\n" + "="*80 + "\n")
