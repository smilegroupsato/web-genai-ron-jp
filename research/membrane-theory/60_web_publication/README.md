# 膜理論 Web公開化作業

- ページ作成日時：2026-08-26 12:39 JST
- 最終更新日時：2026-08-26 12:39 JST
- status：working / publication planning

このディレクトリは、`research/membrane-theory/` に蓄積された研究資料を、genai-ron.jp 上の公開版「膜」へ編集・選定・実装するための作業専用領域である。

## 役割

ここでは次を管理する。

- 公開対象・非公開対象の棚卸し
- source archive と public edition の分離
- 公開版 v0.1 の情報設計
- 原稿化・再編集が必要な文書の判定
- `content/` への昇格候補と公開順序
- route / index / theme / visual QA を含む実装計画

## 原則

`research/membrane-theory/` は研究・観測・原文の source archive として保持する。

Web公開版は source archive の単純なミラーにしない。公開すると単独で意味が通る内容だけを、新規の public edition として編集する。

```text
research/membrane-theory/
  source archive / research canon
          ↓ 選定・再編集
research/membrane-theory/60_web_publication/
  公開候補台帳 / 編集方針 / 実装計画
          ↓ publication candidate
content/
  公開Markdown正本
          ↓ existing publication lane
site/
  公開HTML
```

特に以下は原則としてそのまま公開しない。

- `40_observations/` の個人的観測記録
- ASC / CDS風 self-test
- `90_chat_logs/` の全文対話録
- 個人的・臨床的・生活上の生データ
- 小説の未公開原稿、人物設定、scene board
- 内部分析仕様、実装用schema、作業ログ

## v0.1の狙い

公開版 v0.1 は「小説の資料置場」ではなく、**生命・自己・世界・AIのあいだにある膜を考える公開研究ノート**として成立させる。

最初の入口では、次の三つを読者に示す。

1. 膜とは何か。
2. なぜ生物学・現象学・精神病理・文学・AIを横断して読むのか。
3. 既存研究と佐藤独自の作業仮説をどう区別しているのか。

## 文書

- [`2026.08.26_01_public_v0.1_inventory.md`](./2026.08.26_01_public_v0.1_inventory.md)
  - 現行資料の公開適性を A / B / C に分類した棚卸し。
- [`2026.08.26_02_public_v0.1_implementation_plan.md`](./2026.08.26_02_public_v0.1_implementation_plan.md)
  - 公開版 v0.1 の情報設計、制作順、publication laneへの接続、完成条件。

## 判定記号

| 判定 | 意味 |
|---|---|
| A | 軽微な編集または公開版への転記で掲載可能 |
| B | 内容は公開価値があるが、public editionとして再構成が必要 |
| C | v0.1では内部資料のまま保持 |

## 更新履歴

- 2026-08-26 12:39 JST：Web公開化作業専用領域を新設し、役割・原則・v0.1の狙いを定義。
