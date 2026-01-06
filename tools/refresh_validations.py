from __future__ import annotations

from pathlib import Path
from tools.create_templates import refresh_validations


if __name__ == "__main__":
    refresh_validations(Path("input"))
    print("Validations refreshed.")
