"""Example usage for GenPark Safe Eval Expression AST Sandbox."""
from client import SafeEvalASTSandbox

def main():
    expr = "round(sqrt(width ** 2 + height ** 2), 2) <= max_diagonal"
    vars_ctx = {"width": 1920, "height": 1080, "max_diagonal": 2500}

    print("Validating expression AST...")
    val = SafeEvalASTSandbox.validate_expression(expr)
    print("Valid:", val["valid"], "| Variables:", val["variables_found"])

    print("
Evaluating formula safely...")
    res = SafeEvalASTSandbox.safe_eval(expr, vars_ctx)
    print("Eval Success:", res["success"], "| Result:", res.get("result"))

    print("
Attempting malicious exploit injection...")
    malicious = SafeEvalASTSandbox.safe_eval("__import__('os').system('rm -rf /')")
    print("Exploit Blocked:", not malicious["success"], "| Error:", malicious["error"])

if __name__ == "__main__":
    main()
