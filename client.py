"""Safe Eval Expression AST Sandbox.
100% Python Standard Library.
"""
import ast
import math
from typing import Dict, Any, Optional

class SafeEvalASTSandbox:
    """Zero-dependency AST safe mathematical and boolean expression evaluator."""
    ALLOWED_OPERATORS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.FloorDiv: lambda a, b: a // b,
        ast.Mod: lambda a, b: a % b,
        ast.Pow: lambda a, b: a ** b,
        ast.USub: lambda a: -a,
        ast.UAdd: lambda a: +a,
        ast.Not: lambda a: not a,
    }

    ALLOWED_COMPARISONS = {
        ast.Eq: lambda a, b: a == b,
        ast.NotEq: lambda a, b: a != b,
        ast.Lt: lambda a, b: a < b,
        ast.LtE: lambda a, b: a <= b,
        ast.Gt: lambda a, b: a > b,
        ast.GtE: lambda a, b: a >= b,
    }

    SAFE_FUNCTIONS = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "exp": math.exp,
        "ceil": math.ceil,
        "floor": math.floor,
        "len": len,
    }

    @classmethod
    def validate_expression(cls, expression: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(expression.strip(), mode="eval")
        except SyntaxError as e:
            return {"valid": False, "error": f"SyntaxError: {e.msg}", "complexity": 0}

        variables = set()
        node_count = 0
        unsafe_nodes = []

        for node in ast.walk(tree):
            node_count += 1
            if isinstance(node, ast.Name):
                if node.id not in cls.SAFE_FUNCTIONS:
                    variables.add(node.id)
            elif isinstance(node, (ast.Import, ast.ImportFrom, ast.Attribute, ast.Lambda, ast.Yield, ast.YieldFrom)):
                unsafe_nodes.append(type(node).__name__)

        if unsafe_nodes:
            return {
                "valid": False,
                "error": f"Disallowed syntax constructs: {unsafe_nodes}",
                "complexity": node_count
            }

        return {
            "valid": True,
            "variables_found": sorted(list(variables)),
            "complexity_nodes": node_count
        }

    @classmethod
    def safe_eval(cls, expression: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        vars_dict = variables or {}
        check = cls.validate_expression(expression)
        if not check["valid"]:
            return {"success": False, "error": check["error"]}

        tree = ast.parse(expression.strip(), mode="eval")

        def _eval_node(node):
            if isinstance(node, ast.Expression):
                return _eval_node(node.body)
            elif isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Name):
                if node.id in vars_dict:
                    return vars_dict[node.id]
                elif node.id in cls.SAFE_FUNCTIONS:
                    return cls.SAFE_FUNCTIONS[node.id]
                elif node.id in ("True", "False", "None"):
                    return {"True": True, "False": False, "None": None}[node.id]
                raise NameError(f"Undefined variable '{node.id}'")
            elif isinstance(node, ast.BinOp):
                op_type = type(node.op)
                if op_type not in cls.ALLOWED_OPERATORS:
                    raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
                left = _eval_node(node.left)
                right = _eval_node(node.right)
                return cls.ALLOWED_OPERATORS[op_type](left, right)
            elif isinstance(node, ast.UnaryOp):
                op_type = type(node.op)
                if op_type not in cls.ALLOWED_OPERATORS:
                    raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
                return cls.ALLOWED_OPERATORS[op_type](_eval_node(node.operand))
            elif isinstance(node, ast.Compare):
                left = _eval_node(node.left)
                for op, comparator in zip(node.ops, node.comparators):
                    op_type = type(op)
                    if op_type not in cls.ALLOWED_COMPARISONS:
                        raise ValueError(f"Unsupported comparison operator: {op_type.__name__}")
                    right = _eval_node(comparator)
                    if not cls.ALLOWED_COMPARISONS[op_type](left, right):
                        return False
                    left = right
                return True
            elif isinstance(node, ast.BoolOp):
                if isinstance(node.op, ast.And):
                    return all(_eval_node(val) for val in node.values)
                elif isinstance(node.op, ast.Or):
                    return any(_eval_node(val) for val in node.values)
                raise ValueError("Unsupported boolean operator")
            elif isinstance(node, ast.IfExp):
                test = _eval_node(node.test)
                return _eval_node(node.body) if test else _eval_node(node.orelse)
            elif isinstance(node, ast.Call):
                func = _eval_node(node.func)
                if func not in cls.SAFE_FUNCTIONS.values():
                    raise ValueError("Execution of untrusted function disallowed")
                args = [_eval_node(arg) for arg in node.args]
                return func(*args)
            elif isinstance(node, ast.List):
                return [_eval_node(el) for el in node.elts]
            elif isinstance(node, ast.Dict):
                return {_eval_node(k): _eval_node(v) for k, v in zip(node.keys, node.values)}
            else:
                raise ValueError(f"Unsupported AST node: {type(node).__name__}")

        try:
            result = _eval_node(tree)
            return {"success": True, "result": result, "expression": expression}
        except Exception as e:
            return {"success": False, "error": str(e), "expression": expression}
