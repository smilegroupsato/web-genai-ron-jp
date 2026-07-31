# コンテキストエンジニアリング・レビュー｜作業計画

- ページ作成日時：2026-07-31 08:00 JST
- 最終更新日時：2026-07-31 14:39 JST

## 現在地

対象論文：*A Survey of Context Engineering for Large Language Models*（arXiv:2507.13334v2）

完了済み：

- 論文全体の見取り図
- 第1章 Introduction
- 第2章 Related Work
- 基盤文書の初期整備
- 旧 `surveys/` 原稿の内容確認と新構成への統合
- レビュー作業サイクルの正式化

## 次の作業

第3章「Why Context Engineering?」を精読する。

最初に扱う範囲：

- 3.1 Definition of Context Engineering
- コンテキストエンジニアリングの形式的定義
- 組立関数 `C = A(c1, c2, ..., cn)` の意味
- プロンプトエンジニアリングとの境界
- 静的な指示文から動的な情報組立への転換

## 章レビュー予定

- `03_why_context_engineering.md`
- 以後は原論文の章構成に従って追加する

## 今後の優先順位

1. 第3章のレビューを完成させる。
2. 原論文の分類体系を章ごとに精読する。
3. 各章の読解に合わせて用語集・訳語方針・年表・概念地図・文献一覧を同期する。
4. 各作業単位の最後に `CHANGELOG.md` を更新する。

## 保留事項

- Grounding、Routing、Orchestration、Governance、Lifecycle の訳語確定
- 原論文の全参照文献をどの粒度で `bibliography.md` に収録するか
- 章レビュー完了後に論文横断の統合レビューを別途作成するか

## 運用

執筆基準・引用方針・評価軸・標準作業サイクルは `review-policy.md` を正本とする。本書には現在の進捗、次の作業、優先順位、保留事項だけを記載する。

## 更新履歴

- 2026-07-31 14:39 JST：編集方針を `review-policy.md` へ集約し、本書を進捗・次作業・保留事項の管理文書へ再編
- 2026-07-31 08:00 JST：初期執筆・読解方針を作成
