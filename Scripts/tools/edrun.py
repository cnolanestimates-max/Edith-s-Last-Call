"""Run a python file inside the running editor (MCP) and print its `result` variable.  python edrun.py <file.py>"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts")
from mcp import pyv
NL = chr(10)
print(pyv(open(sys.argv[1], encoding="utf-8").read() + NL + "result" + NL, int(sys.argv[2]) if len(sys.argv) > 2 else 120))
