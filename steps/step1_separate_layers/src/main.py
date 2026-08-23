"""Entry point for Step 1.

アプリケーションの起動を担当するモジュール。
"""

import cli


def main() -> None:
    """アプリケーションを起動する."""
    cli.main_menu()


if __name__ == "__main__":
    main()
