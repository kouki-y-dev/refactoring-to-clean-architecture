# Refactoring to Clean Architecture

Python でクリーンアーキテクチャを段階的に学ぶためのリファクタリング教材です。

アーキテクチャが何も導入されていないモノリシックなコードから出発し、層を1つずつ追加してリファクタリングしていきます。各ステップを独立したディレクトリとして保存し、変化を追えるようにしています。

## 題材：EC サイトの注文システム

シンプルな EC サイトの注文システムを題材に、以下の機能を段階的に実装・リファクタリングしていきます。

### 機能一覧

| 機能 | 説明 |
|------|------|
| 商品一覧の取得 | カタログから商品を一覧表示する |
| カートへの追加・削除 | ユーザーが商品をカートに追加・削除する |
| 注文確定 | 在庫チェック → 合計金額計算 → 注文作成 |
| 注文履歴の参照 | 過去の注文を確認する |

### ドメインルール（例）

- 在庫が不足している場合、注文は確定できない
- 合計金額には消費税（10%）が加算される
- 注文が確定すると在庫が減少する

## ステップ一覧

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

> **Note**: 各ステップの詳細な解説は、対応する PR およびステップ内のドキュメントを参照してください。

## 開発環境のセットアップ

### 前提条件

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

### セットアップ

```bash
# 依存関係のインストール
uv sync

# pre-commit フックのインストール（任意）
uv run pre-commit install
```

## テストの実行

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
