"""Close the running game (or pass QUIT_EDITOR for the editor) through its MCP console.   python gquit.py [command]"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts")
import mcp
cmd = sys.argv[1] if len(sys.argv) > 1 else "quit"
try:
    print(mcp.call("call_tool", {"toolset_name": "ConsoleToolset.ConsoleToolset", "tool_name": "RunConsoleCommand", "arguments": {"command": cmd}}, 30))
except Exception as exc:
    print("sent (connection closed):", str(exc)[:120])
