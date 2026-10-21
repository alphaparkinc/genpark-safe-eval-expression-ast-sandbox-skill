"""MCP Stdio Server for Safe Eval Expression AST Sandbox.
100% Python Standard Library.
"""
import sys
import json
from client import SafeEvalASTSandbox

sandbox = SafeEvalASTSandbox()

def handle_rpc(line):
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-safe-eval-expression-ast-sandbox-skill", "version": "1.0.1"},
            "capabilities": {"tools": {}}
        }
        send_response(req_id, res)
    elif method == "tools/list":
        tools = [
            {
                "name": "validate_expression",
                "description": "Inspect and syntax-check expression AST without executing",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"}
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "safe_eval",
                "description": "Safely evaluate math and boolean formulas in sandboxed AST environment",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"},
                        "variables": {"type": "object"}
                    },
                    "required": ["expression"]
                }
            }
        ]
        send_response(req_id, {"tools": tools})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "validate_expression":
            out = sandbox.validate_expression(args.get("expression", ""))
        elif name == "safe_eval":
            out = sandbox.safe_eval(args.get("expression", ""), args.get("variables", {}))
        else:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return
        send_response(req_id, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]})

def send_response(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()
