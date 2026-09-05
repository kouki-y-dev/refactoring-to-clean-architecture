<h1 align="center">Refactoring to Clean Architecture</h1>

<p align="center">
  <a href="https://github.com/yama0308/refactoring-to-clean-architecture/actions/workflows/ci.yml"><img src="https://github.com/yama0308/refactoring-to-clean-architecture/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.14+-3776AB?logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv"></a>
  <a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white" alt="Pydantic"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://github.com/astral-sh/ty"><img src="https://img.shields.io/badge/type%20checker-ty-1f425f" alt="ty"></a>
  <a href="https://docs.pytest.org/"><img src="https://img.shields.io/badge/pytest-tested-0A9EDC?logo=pytest&logoColor=white" alt="pytest"></a>
  <a href="https://github.com/nat-n/poethepoet"><img src="https://img.shields.io/badge/task_runner-poethepoet-blueviolet" alt="Poe the Poet"></a>
  <a href="https://github.com/pre-commit/pre-commit"><img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="pre-commit"></a>
</p>

## Overview

Python でクリーンアーキテクチャを段階的に学ぶためのリファクタリング教材です。

## Problem Statement

アーキテクチャが何も導入されていないモノリシックなコードから出発し、層を1つずつ追加してリファクタリングしていきます。各ステップを独立したディレクトリとして保存し、変化を追えるようにしています。

シンプルな EC サイトの注文システムを題材に、以下の機能を段階的に実装・リファクタリングしていきます。

### Features

| 機能 | 説明 |
|------|------|
| 商品一覧の取得 | カタログから商品を一覧表示する |
| カートへの追加・削除 | ユーザーが商品をカートに追加・削除する |
| 注文確定 | 在庫チェック → 合計金額計算 → 注文作成 |
| 注文履歴の参照 | 過去の注文を確認する |

### Domain Rules

- 在庫が不足している場合、注文は確定できない
- 合計金額には消費税（10%）が加算される
- 注文が確定すると在庫が減少する

## Steps

各ステップは `steps/` ディレクトリ内に独立したディレクトリとして配置されています。

| Step | ディレクトリ | 概要 |
|------|-------------|------|
| 0 | `step0_monolith` | すべてが密結合したモノリシックなコード |
| 1 | `step1_separate_layers` | 関心の分離（ロジック・データアクセス・表示） |
| 2 | `step2_domain_model` | ドメインモデルの抽出 |
| 3 | `step3_repository` | Repository パターンの導入 |
| 4 | `step4_usecase` | ユースケース層の導入 |
| 5 | `step5_dependency_inversion` | 依存関係逆転の原則（DIP）の適用 |
| 6 | `step6_clean_architecture` | クリーンアーキテクチャの完成形 |
| 7 | `step7_over_engineering` | 過剰な抽象化（Input/Output Port, Gateway, DTO マッピング） |

> **Note**: 各ステップの詳細な解説は、対応する PR およびステップ内のドキュメントを参照してください。

## Getting Started

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
# 依存関係のインストール
uv sync

# pre-commit フックのインストール（任意）
uv run pre-commit install
```

## Testing

```bash
# 全ステップのテストを実行
uv run poe test

# 特定のステップのテストを実行
uv run poe test-step steps/step0_monolith/tests

# カバレッジレポート付きで実行
uv run poe test-cov
```

## Lint / Format

```bash
# lint
uv run poe lint

# format
uv run poe fmt

# lint + test
uv run poe check
```
