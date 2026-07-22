# GENAI-RON Publishing Layer

ページ作成日時：2026-07-22 22:50 JST  
最終更新日時：2026-07-23 08:44 JST

## Purpose

`publishing/` は、`content/` の文章資産を、公開可能な誌面へ変換するための構造・部品・visual metadata・表示機能の配置契約を保持する。

```text
content/     = 何を伝えるか
publishing/  = どういう誌面構造と視覚・表示契約で出すか
site/        = 実際に配信される生成物
```

## Current Status

```yaml
phase: v0.1-parallel-scaffold
status: semantic-and-visual-qa-passed
writes_to_site: false
public_deploy_effect: none
```

現段階のstructured builderはpreview専用である。`site/` へ書き込む機能は持たせない。

## Structure

```text
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
```

## Responsibilities

### site.yml

logical idと物理pathを結ぶ最小registry。将来pathが変わっても、contentやtemplateの大量変更を避けるための入口。

### templates

document全体のsemantic structure。componentの中身を複製せず、slotとして受け取る。

### components

複数ページで共有するHTML断片。header、reading preferences、footer等を独立部品として保持する。

表示設定をheader、article、footerのいずれかへ埋め込まず、専用componentとして配置する。これにより、文字調整やappearance変更がheader構造を巻き込むことを防ぐ。

### design

CSS tokenとcomponent styleのsource。現行public CSSを直ちに全面置換しない。既存値との対応を確認しながらpreviewでbridgeする。

### behaviors

表示設定、accordion等のruntime責務を保持する層。

`reading-preferences-adapter.js` は移行用であり、現行`site/assets/theme.js`が生成するcontrolを専用slotへ移す。最終形では、appearance / reading preference責務そのものをlegacy runtimeから分離する。

### themes

visual themeのlogical metadata。画像の物理保存先を唯一の識別手段にしない。

### VALIDATION.md

semantic parity、visual QA、発見した失敗、停止条件、次のGateを保持する。

## Rules

- content本文へglobal UIを入れない。
- templateへ季節固有の画像pathを直接固定しない。
- componentへ記事固有本文を入れない。
- theme変更で本文DOM構造を変えない。
- 表示設定をbody直下へ未管理のまま追加しない。
- previewを経ず `site/` を変更しない。
- unresolved placeholderがある場合はbuildを失敗させる。
- 未登録theme IDはbuildを失敗させる。
- asset未解決themeは`production_enabled: false`を維持する。
- default themeは現行表示との同等性確認を優先する。

## Flexible Naming

物理pathは変更可能だが、logical idとroleは安定させる。

```yaml
layout_id: article-v1
component_id: reading-preferences-v1
theme_id: default-academic
collection_id: library-series
asset_role: hero-main
```

## Build and Validation Path

```text
content Markdown
  ↓ scripts/build_structured_preview.py
publishing template + components + theme id
  ↓
_structured_build_preview/
  ↓ semantic validator + Chromium visual QA
preview artifact / report / screenshots
```

既存の `scripts/build_content_pages.py` と `site/` は、このv0.1では置換しない。

## Completed Gate

- 全contentページのsemantic parity
- desktop 1440px / mobile 390pxのvisual QA
- document-level horizontal overflowなし
- Library Series metadata-only preview
- unregistered themeのfail-closed
- reading preferencesの専用component配置
- `site/`差分なし

## Next Promotion Gate

次のbranchで1ページだけをpromotion fixtureとして扱い、次を確認する。

- structured outputと現行site HTMLのdiff説明
- visual QA再実行
- target pageの明示
- rollback commitの明示
- explicit site writeが対象外へ波及しないこと

これらが揃うまでstructured builderへ`--write-site`を追加しない。

## 更新履歴

- 2026-07-23 08:44 JST：semantic / visual QA完了。reading-preferences component、component CSS、legacy runtime adapter、validation記録を反映。
- 2026-07-22 22:50 JST：parallel publishing layerの責務、構造、停止条件を新規定義。
