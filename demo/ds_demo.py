#!/usr/bin/env python3
"""Feed a JSON-RPC session to the DemandScope MCP server and print the exchange."""
import json
import subprocess
import sys

SERVER = "/home/ubuntu/.hermes/workspace/autonomous-income/projects/demandscope/mcp_server.py"

messages = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "demo", "version": "0.1"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
     "params": {"name": "hn_signal",
                "arguments": {"query": "MCP server", "days": 365}}},
]

proc = subprocess.run(
    [sys.executable, SERVER],
    input="\n".join(json.dumps(m) for m in messages) + "\n",
    capture_output=True, text=True, timeout=120,
)
for line in proc.stdout.splitlines():
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        continue
    if obj.get("id") == 1:
        r = obj.get("result", {})
        print("initialize ->", json.dumps({
            "serverInfo": r.get("serverInfo"),
            "protocolVersion": r.get("protocolVersion"),
        }))
    elif obj.get("id") == 2:
        content = obj.get("result", {}).get("content", [])
        for c in content:
            if c.get("type") == "text":
                data = json.loads(c["text"])
                print("tools/call hn_signal ->", json.dumps(data, indent=2)[:1200])
if proc.returncode != 0:
    print("STDERR:", proc.stderr[:500], file=sys.stderr)
