#!/usr/bin/env python3
"""Dependency-free regression check for Theo's capped acceleration profile."""

import ast
from pathlib import Path


ROOT = Path(__file__).parents[1]
PLANNER = ROOT / "openpilot/selfdrive/controls/lib/longitudinal_planner.py"
INTERFACES = ROOT / "opendbc_repo/opendbc/car/interfaces.py"
HONDA_VALUES = ROOT / "opendbc_repo/opendbc/car/honda/values.py"
SAFETY = ROOT / "opendbc_repo/opendbc/safety/modes/honda.h"

EXPECTED_CRUISE_MAX = [2.0, 1.8, 1.2, 0.9]
EXPECTED_SAFETY_CEILING = 2.0


def assignment_value(path: Path, name: str, class_name: str | None = None):
  tree = ast.parse(path.read_text())
  body = tree.body
  if class_name is not None:
    cls = next(node for node in body if isinstance(node, ast.ClassDef) and node.name == class_name)
    body = cls.body

  for node in body:
    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
      return ast.literal_eval(node.value)
  raise AssertionError(f"{name} not found in {path}")


def main() -> None:
  cruise_max = assignment_value(PLANNER, "A_CRUISE_MAX_VALS")
  global_max = assignment_value(INTERFACES, "ACCEL_MAX")
  honda_bosch_max = assignment_value(HONDA_VALUES, "BOSCH_ACCEL_MAX", "CarControllerParams")
  safety_source = SAFETY.read_text()

  assert cruise_max == EXPECTED_CRUISE_MAX, (cruise_max, EXPECTED_CRUISE_MAX)
  assert global_max == EXPECTED_SAFETY_CEILING, global_max
  assert honda_bosch_max == EXPECTED_SAFETY_CEILING, honda_bosch_max
  assert ".max_accel = 200" in safety_source
  assert ".max_gas = 2000" in safety_source
  print("Theo capped acceleration profile verified")


if __name__ == "__main__":
  main()
