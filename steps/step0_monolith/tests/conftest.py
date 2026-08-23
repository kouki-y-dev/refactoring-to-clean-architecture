"""steps/step0_monolith のテスト用 conftest."""

import sys
from pathlib import Path

# このステップの src/ を Python パスに追加する
# NOTE: pyproject.toml の pythonpath ではグローバル設定になり
#       ステップごとに異なる src/ を指定できないため、
#       各ステップの conftest.py で個別に設定する
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "src"),
)
