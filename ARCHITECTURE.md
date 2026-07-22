# GENAI-RON Publishing Architecture

ページ作成日時：2026-07-22 22:50 JST  
最終更新日時：2026-07-23 08:44 JST

## Current State

```yaml
phase: publishing-structure-v0.1
status: validated-scaffold
completed_gate: semantic-and-visual-parity
public_site_changed: false
site_output_changed: false
current_public_source: site/
article_source_candidate: content/
structured_publishing_source: publishing/
structured_site_write_enabled: false
```

この文書は、`genai-ron.jp` を、本文・誌面構造・共通部品・デザイン・表示機能・theme・公開成果物に分離し、改稿や季節変更で壊れにくい出版基盤へ移行するためのArchitecture入口である。

現段階では、公開中の `site/` を置換しない。新構造を並行して作り、semantic parityとvisual QAを確認した後、対象ページを限定して段階的に昇格する。

## Source of Truthの階層

```text
content/
  記事本文と意味上のブロック

publishing/
  template、component、design token、behavior、theme metadata

scripts/
  contentとpublishingを結合するbuild / validate / visual QA

site/
  公開サーバへ配信する生成物
```

原則：

- `content/` は文章正本候補。
- `publishing/` は出版構造・表示契約の正本候補。
- `site/` は公開成果物であり、長期的には再生成可能にする。
- 移行中は、既存 `site/` とlegacy runtimeにしかない意味や表示が残る可能性があるため、ページ単位で検証する。

## Target Structure

```text
/
  ARCHITECTURE.md
  content/
  publishing/
    README.md
    VALIDATION.md
    site.yml
    templates/
      article.html
    components/
      site-header.html
      reading-preferences.html
      site-footer.html
    design/
      tokens.css
      components.css
    behaviors/
      reading-preferences-adapter.js
    themes/
      default.yml
      library-series.yml
  scripts/
    build_content_pages.py
    build_structured_preview.py
    validate_structured_preview.py
    capture_structured_preview.js
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

behavior_contract:
  - document_state
  - mount_region
  - persistence_key
  - no_unmanaged_body_child

visual_contract:
  - theme_id
  - collection_id
  - asset_role
  - text_contrast
  - production_enabled

build_contract:
  - preview_first
  - explicit_site_write
  - diff_before_publish
  - fail_on_unresolved_reference
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
- headings / paragraphs
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
- reading preferences slot
- hero slot
- article body slot
- article navigation slot
- theme id等のdocument-level state

### components

header、reading preferences、footer、hero、navigation、callout等を独立部品として保持する。同じHTML断片を複数templateへ手作業複製しない。

表示設定はheaderやarticleへ直接埋め込まず、専用componentに置く。文字調整機能の変更がheaderや本文構造を巻き込まないことを優先する。

### design

色、余白、本文幅、文字サイズ、line-height、border等をtokenとして保持する。季節やtheme変更で本文DOMを変更しない。

componentの配置と見た目は`components.css`へ分離し、article本文用CSSと混同しない。

### behaviors

文字サイズ、appearance、accordion等はdocument stateを切り替える。個別段落や見出しをJavaScriptで書き換えない。

現行`site/assets/theme.js`は複数責務を持つlegacy runtimeである。v0.1では、生成されたappearance switcherを専用slotへ移すadapterを置いた。最終形では次を分離する。

```text
reading preferences
content enhancement
syntax highlighting
Notion export repair
```

### themes

themeは本文やtemplateそのものではなく、visual metadataとasset roleの組み合わせとする。

```yaml
theme_id: library-university-humanities-summer
collection_id: library-series
base_theme: university-humanities
season: summer
hero_asset_role: hero-main
text_contrast: dark
asset_status: unresolved
production_enabled: false
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

## Validation Model

### Semantic validation

全`content/`ページについて、current builderとstructured builderの次を比較する。

- title
- h2 headings
- article text
- article links
- header / footerの存在
- unresolved placeholder

### Visual validation

Chromiumで次を描画する。

- desktop 1440px
- mobile 390px
- default academic theme
- Library Series metadata-only theme

確認対象：

- header
- reading preferences
- hero
- article
- footer
- document-level horizontal overflow
- runtime controlのmount先

初回visual QAでは、appearance switcherがbody直下、footer後へ未整形で漏出する問題を発見した。専用componentとadapterで回復し、CIで再発を検知する。

## Migration Phases

### Phase 0｜content分離

`content/` から既存公開HTMLを再生成できるかをページ単位で確認する。

### Phase 1｜parallel publishing scaffold

`publishing/` とstructured preview builderを作る。公開 `site/` は変更しない。

### Phase 2｜semantic parity

全contentページの意味上の一致を自動検証する。完了済み。

### Phase 3｜component extraction and visual QA

共通header、footer、reading preferences、article layoutを分離し、desktop / mobileで確認する。v0.1対象は完了済み。

### Phase 4｜design token bridge

既存CSSを直ちに全面置換せず、現在の値をtokenへ対応づける。previewで開始済み。

### Phase 5｜theme preview

default themeとLibrary Seriesのtheme metadataを使い、heroと小さなaccentだけをpreviewで変更する。画像実体は未解決。

### Phase 6｜controlled site generation

対象ページを1件に限定し、explicitなwrite、diff、visual QA、rollback確認後にのみ `site/` へ反映する。

## Gates

```yaml
gate_before_scaffold_merge:
  - structured preview builds successfully
  - no unresolved template placeholders
  - all content pages pass semantic parity
  - desktop and mobile visual QA pass
  - runtime controls stay in managed component regions
  - current site is not modified

gate_before_site_write:
  - target page explicitly listed
  - current site diff explained
  - header and navigation parity confirmed
  - mobile structure reviewed
  - rollback commit identified
  - write path cannot affect non-target pages

gate_before_theme_release:
  - hero readability checked
  - mobile crop checked
  - no text baked into image
  - accessibility role decided
  - public asset storage verified
  - asset checksum and provenance recorded
```

## Current Stop Conditions

次はまだ開始しない。

- `site/` 全体の一括再生成
- current builderの削除
- public CSS / JavaScriptの全面置換
- appearance / text-size runtimeの全面再実装
- hero画像の本番導入
- physical asset pathの最終固定
- Library Seriesの本番採用

## Next First Action

scaffoldをmainへmergeした後、別branchで04ページをpromotion fixtureとして選定する。structured builderに一般的な`--write-site`を追加せず、対象pathを固定したdry-run / explicit write / rollbackの最小設計から始める。

## 更新履歴

- 2026-07-23 08:44 JST：全content semantic parityとdesktop/mobile visual QA完了。reading-preferences component、legacy runtime adapter、再発検知GateをArchitectureへ反映。
- 2026-07-22 22:50 JST：本文、出版構造、部品、design、theme、公開成果物を分離するparallel scaffoldのArchitectureとして新規作成。
