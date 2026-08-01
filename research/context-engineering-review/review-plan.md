# コンテキストエンジニアリング・レビュー｜作業計画

- ページ作成日時：2026-07-31 08:00 JST
- 最終更新日時：2026-08-01 14:54 JST

## 現在地

対象論文：*A Survey of Context Engineering for Large Language Models*（arXiv:2507.13334v2）

完了済み：

- 論文全体の見取り図
- 第1章 Introduction
- 第2章 Related Work
- 第3章 Why Context Engineering?
- 第1章・第2章への引用形式導入と訳語統一
- 章横断ノートの作成
- 基盤文書の初期整備
- 旧 `surveys/` 原稿の内容確認と新構成への統合
- レビュー作業サイクルの正式化

## 次の作業

第4章「Foundational Components」を精読する。

最初に扱う範囲：

- 4.1 Context Retrieval and Generation
- 4.1.1 Prompt Engineering and Context Generation
- 4.1.2 External Knowledge Retrieval
- 4.1.3 Dynamic Context Assembly

特に、検索・生成・組立が同じ下位分類に置かれている妥当性と、組立関数の実装上の意味を検討する。

## 章レビュー予定

- `04_foundational_components.md`
- 必要に応じて第4章を節単位に分けるが、ファイル数は最小限に保つ

## 今後の優先順位

1. 第4章のレビューを完成させる。
2. 原論文の分類体系を章ごとに精読する。
3. 各章の読解に合わせて用語集・訳語方針・年表・概念地図・文献一覧を同期する。
4. 各作業単位の最後に `CHANGELOG.md` を更新する。

## 保留事項

- Grounding、Routing、Orchestration、Governance、Lifecycle の訳語確定
- 原論文の全参照文献をどの粒度で `bibliography.md` に収録するか
- 章レビュー完了後に論文横断の統合レビューを別途作成するか
- 数式をWeb公開時にどの記法で表示するか（Markdown、LaTeX、MathJax等）

## 運用

執筆基準・引用方針・評価軸・標準作業サイクルは `review-policy.md` を正本とする。本書には現在の進捗、次の作業、優先順位、保留事項だけを記載する。

## 更新履歴

- 2026-08-01 14:54 JST：第3章完了を反映し、次の対象を第4章へ更新
- 2026-07-31 14:39 JST：編集方針を `review-policy.md` へ集約し、本書を進捗・次作業・保留事項の管理文書へ再編
- 2026-07-31 08:00 JST：初期執筆・読解方針を作成
