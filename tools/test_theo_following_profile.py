#!/usr/bin/env python3
"""Dependency-free regression check for Theo's custom following profile."""

import ast
from pathlib import Path


SOURCE = Path(__file__).parents[1] / "openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py"
EXPECTED_T_FOLLOW = {
  "relaxed": 1.75 / 3.0,
  "standard": 1.45 / 3.0,
  "aggressive": 1.25 / 3.0,
}
EXPECTED_STOP_DISTANCE = 6.0 / 3.0


def evaluate(node: ast.AST) -> float:
  if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
    return evaluate(node.left) / evaluate(node.right)
  return float(ast.literal_eval(node))


def main() -> None:
  tree = ast.parse(SOURCE.read_text())
  stop_distance = None
  returns: list[float] = []

  for node in tree.body:
    if isinstance(node, ast.Assign):
      if any(isinstance(target, ast.Name) and target.id == "STOP_DISTANCE" for target in node.targets):
        stop_distance = evaluate(node.value)
    elif isinstance(node, ast.FunctionDef) and node.name == "get_T_FOLLOW":
      for child in ast.walk(node):
        if isinstance(child, ast.Return) and child.value is not None:
          returns.append(evaluate(child.value))

  expected_returns = list(EXPECTED_T_FOLLOW.values())
  assert stop_distance == EXPECTED_STOP_DISTANCE, (stop_distance, EXPECTED_STOP_DISTANCE)
  assert returns == expected_returns, (returns, expected_returns)
  print("Theo following profile verified")


if __name__ == "__main__":
  main()
