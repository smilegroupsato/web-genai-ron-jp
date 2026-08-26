---
id: "v2-publication-lane-test"
title: "新規文書公開レーン v0 テスト"
subtitle: "新しい content 文書を、公開領域へ書き込まずに二つの builder で検証する。"
series: "publication-lane-fixtures"
series_label: "公開レーン検証"
series_order: "0"
order_display: "v0"
slug: "/fixtures/v2-publication-lane-test/"
canonical_url: "https://genai-ron.jp/fixtures/v2-publication-lane-test/"
description: "preview-only の新規文書公開レーンを検証するための fixture。"
theme_id: "default-academic"
status: "preview-only-fixture"
page_created_at: "2026-08-04 14:06 JST"
last_updated_at: "2026-08-04 14:06 JST"
exclude_from_public_body:
  - "更新履歴"
  - "作業履歴"
  - "内部TODO"
  - "変換ログ"
rendering_contract:
  note: "semantic block. Web側でblockquote, callout, accordion等へ変換してよい。"
  phrase: "semantic phrase/code block. Web側で article-phrase 相当へ変換してよい。"
  table: "content table. Web側で responsive table へ変換してよい。"
  references: "公式参照。タイトル文字列を通常リンクにする。"
---
この文書は、新規 content 文書を公開領域へ書き込まずに preview 生成できることを確認するための fixture である。

## 検証する境界

二つの builder は、同じ Markdown を明示的に入力として受け取り、それぞれ独立した preview を生成する。

:::note
この fixture の生成先は preview ディレクトリに限定し、site ディレクトリは変更しない。
:::

## 検証する意味要素

- タイトルと見出し
- 本文と注記
- コードブロックと表
- 参照リンク
- 標準 Markdown の強調と引用

**強調表示**は strong 要素として描画する。

> 標準 Markdown の引用は blockquote 要素として描画する。

```text
content fixture -> current preview
content fixture -> structured preview
current preview == structured preview (semantic parity)
```

| 検証対象 | 期待結果 |
|---|---|
| current preview | 明示した fixture だけを生成する |
| structured preview | 明示した fixture だけを生成する |
| semantic parity | 本文の意味要素が一致する |

公開レーンの設計方針は [content source の説明](../README.md) を参照する。
