# GENAI-RON Publishing Architecture

ページ作成日時：2026-07-22 22:50 JST  
最終更新日時：2026-07-22 22:50 JST

## Current State

```yaml
phase: publishing-structure-v0.1
gate: parallel-scaffold
status: in_progress
public_site_changed: false
site_output_changed: false
current_public_source: site/
article_source_candidate: content/
structured_preview_source: publishing/
```

この文書は、`genai-ron.jp` を、本文・誌面構造・共通部品・デザイン・表示機能・公開成果物に分離し、改稿や季節変更で壊れにくい出版基盤へ移行するためのArchitecture入口である。

現段階では、公開中の `site/` を置換しない。新構造を並行して作り、previewとdiffで同等性を確認してから段階的に昇格する。

## Source of Truthの階層

```text
content/
  記事本文と意味上のブロック

publishing/
  template、component、design token、theme metadata

scripts/
  contentとpublishingを結合するbuild / validate処理

site/
  公開サーバへ配信する生成物
```

原則：

- `content/` は文章正本候補。
- `publishing/` は出版構造・表示契約の正本候補。
- `site/` は公開成果物であり、長期的には再生成可能にする。
- 現在の移行中は、既存 `site/` にしかない意味や表示が残る可能性があるため、ページごとにdiff確認する。

## Target Structure

```text
/
  ARCHITECTURE.md
  content/
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
  scripts/
    build_content_pages.py
    build_structured_preview.py
  site/
```

この構造は物理pathを永久固定するためのものではない。外部から参照する契約は、できるだけlogical idとasset roleで表現する。

## Stable Contracts

早期に固定するのは次だけとする。

```yaml
content_contract:
  - id
  - title
  - slug
  - canonical_url
  - body_semantics

layout_contract:
  - layout_id
  - component_slots
  - required_metadata

component_contract:
  - component_id
  - semantic_role

visual_contract:
  - theme_id
  - collection_id
  - asset_role
  - text_contrast

build_contract:
  - preview_first
  - explicit_site_write
  - diff_before_publish
```

固定しすぎないもの：

- 物理ディレクトリの深さ
- template engine
- storage backend
- 画像形式
- variation数
- theme追加方法
- build toolの実装言語

## Layer Responsibilities

### content

含めるもの：

- title / subtitle
- headings
- paragraphs
- note / quote / phrase
- code / table
- references
- series metadata
- navigation metadata

含めないもの：

- global header
- site navigation
- CSS classの見た目指定
- JavaScript補正
- hero画像の物理path
- deploy設定

### templates

ページ全体のsemantic structureを持つ。

- `<head>`
- header / main / footerの配置
- hero slot
- article body slot
- article navigation slot
- theme id等のdocument-level state

### components

header、footer、hero、navigation、callout等を独立部品として保持する。同じHTML断片を複数templateへ手作業複製しない。

### design

色、余白、本文幅、文字サイズ、line-height、border等をtokenとして保持する。季節やtheme変更で本文DOMを変更しない。

### behaviors

文字サイズ、appearance、accordion等はdocument stateを切り替える。個別段落や見出しをJavaScriptで書き換えない。

### themes

themeは本文やtemplateそのものではなく、visual metadataとasset roleの組み合わせとする。

```yaml
theme_id: library-university-humanities-summer
collection_id: library-series
hero_asset_role: hero-main
text_contrast: dark
```

## Flexible Asset Resolution

templateが画像の物理pathを直接多数埋め込まないようにする。

```text
content / page metadata
        ↓ theme_id
publishing theme registry
        ↓ asset role
asset manifest or storage adapter
        ↓ resolved public path
site output
```

これにより、将来 `assets/hero/` から別directory、CDN、Drive原本＋Web derivative等へ移しても、記事本文を変更せずに済む。

## Migration Phases

### Phase 0｜content分離

`content/` から既存公開HTMLを再生成できるかをページ単位で確認する。

### Phase 1｜parallel publishing scaffold

`publishing/` とstructured preview builderを作る。公開 `site/` は変更しない。

### Phase 2｜semantic parity

現行builderとstructured previewの差分を確認する。

確認対象：

- title / metadata
- header / navigation
- headings / paragraphs
- code / table / note
- previous / next links
- mobile表示に必要なclass

### Phase 3｜component extraction

現行HTMLと同等性が確認できたcomponentから、共通header、footer、article layoutへ移す。

### Phase 4｜design token bridge

既存CSSを直ちに全面置換せず、現在の値をtokenへ対応づける。

### Phase 5｜theme preview

default themeとLibrary Seriesのtheme metadataを使い、heroと小さなaccentだけをpreviewで変更する。

### Phase 6｜controlled site generation

対象ページ群を限定し、explicitなwriteとdiff後にのみ `site/` へ反映する。

## Gates

```yaml
gate_before_main_merge:
  - structured preview builds successfully
  - no unresolved template placeholders
  - current site is not modified
  - default theme metadata resolves
  - one article diff is reviewed

gate_before_site_write:
  - semantic parity confirmed
  - header and navigation parity confirmed
  - mobile structure reviewed
  - rollback commit identified
  - target pages explicitly listed
gate_before_theme_release:
  - hero readability checked
  - mobile crop checked
  - no text baked into image
  - accessibility role decided
  - public asset storage verified
```

## Current Stop Conditions

次はまだ開始しない。

- `site/` 全体の一括再生成
- current builderの削除
- CSS / JavaScriptの全面置換
- 文字サイズ機能の再実装
- hero画像の本番導入
- physical asset pathの最終固定
- Library Seriesの本番採用

## Next First Action

`refactor/publishing-structure-v0.1` branchをdevboxへ取得し、`scripts/build_structured_preview.py` で04ページをpreview生成する。現行 `site/` および既存content builderのpreviewとの差分を確認する。

## 更新履歴

- 2026-07-22 22:50 JST：本文、出版構造、部品、design、theme、公開成果物を分離するparallel scaffoldのArchitectureとして新規作成。