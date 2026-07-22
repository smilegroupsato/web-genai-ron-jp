# GENAI-RON Publishing Layer

ページ作成日時：2026-07-22 22:50 JST  
最終更新日時：2026-07-22 22:50 JST

## Purpose

`publishing/` は、`content/` の文章資産を、公開可能な誌面へ変換するための構造・部品・visual metadataを保持する。

```text
content/     = 何を伝えるか
publishing/  = どういう誌面構造と視覚契約で出すか
site/        = 実際に配信される生成物
```

## Current Status

```yaml
phase: v0.1-parallel-scaffold
status: experimental
writes_to_site: false
public_deploy_effect: none
```

現段階のstructured builderはpreview専用である。`site/` へ書き込む機能は持たせない。

## Structure

```text
publishing/
  README.md
  site.yml
  templates/
    article.html
  components/
    site-header.html
    site-footer.html
  design/
    tokens.css
  themes/
    default.yml
    library-series.yml
```

## Responsibilities

### site.yml

logical idと物理pathを結ぶ最小registry。将来pathが変わっても、contentやtemplateの大量変更を避けるための入口。

### templates

document全体のsemantic structure。componentの中身を複製せず、slotとして受け取る。

### components

複数ページで共有するHTML断片。header、footer等を最初の対象とする。

### design

CSS tokenのsource案。現行CSSへ直ちにimportしない。既存値との対応を確認してからbridgeする。

### themes

visual themeのlogical metadata。画像の物理保存先を唯一の識別手段にしない。

## Rules

- content本文へglobal UIを入れない。
- templateへ季節固有の画像pathを直接固定しない。
- componentへ記事固有本文を入れない。
- theme変更でDOM構造を変えない。
- previewを経ず `site/` を変更しない。
- unresolved placeholderがある場合はbuildを失敗させる。
- default themeは現行表示との同等性確認を優先する。

## Flexible Naming

物理pathは変更可能だが、logical idとroleは安定させる。

```yaml
layout_id: article-v1
component_id: site-header-v1
theme_id: default-academic
collection_id: library-series
asset_role: hero-main
```

## Build Path

```text
content Markdown
  ↓ scripts/build_structured_preview.py
publishing template + components + theme id
  ↓
_structured_build_preview/
```

既存の `scripts/build_content_pages.py` と `site/` は、このv0.1では置換しない。

## Promotion Gate

1ページで次を確認した後に、structured builderを標準builderへ統合するか判断する。

- article bodyの意味が一致
- header / footer / navが一致
- metadataが一致
- class contractが維持される
- 差分理由を説明できる
- `site/` を変更していない

## 更新履歴

- 2026-07-22 22:50 JST：parallel publishing layerの責務、構造、停止条件を新規定義。