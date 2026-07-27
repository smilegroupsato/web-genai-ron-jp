# genai-ron.jp v2 rebuild plan

ページ作成日時：2026-07-27 09:22 JST
最終更新日時：2026-07-27 09:22 JST

## 1. Purpose

genai-ron.jpを、公開HTMLへ本文・構造・見た目・挙動を重ねる運用から、content-first publishing architectureへ移す。本文、URL、asset、シリーズ構造、確認可能なmetadataを保存し、HTMLを再現可能な生成物にする。

この文書は設計であり、公開HTML/CSS/JS、本文、deploy設定を変更しない。Visual World Systemの実装にも入らない。

## 2. Current problems

- 公開HTMLは102ページ、Markdown正本候補は22ファイルで、legacy本文の多くがHTMLにしかない。
- article / notes / 4シリーズでテンプレート世代、header、幅、controlsが混在する（Issue #27）。
- page、manuscript、Web migrationの日時が混在する（Issue #32）。
- CSSはbase、page family、volume、theme、version付きcopyが重なり、責務境界が弱い。
- `theme.js`がappearance、text size、control生成を担い、legacy DOMとの結合がある。
- minimal builder、structured preview builder、promotion fixture、複数validationが段階的に追加され、全サイトbuildの単一契約には未統合。
- `main` pushで`site/`全体をFTPS deployするため、公開生成とdeployの間にartifact固定・全route検証のgateがない。

## 3. Content-first principles

1. `content/`の原稿と明示metadataを正本にする。
2. `site/`はbuild artifactとし、手編集しない。
3. 移行中は、未抽出ページの`site/**/*.html`を唯一の移行元として保護する。
4. 本文抽出と文章編集を同じPRで行わない。
5. 不明metadataを推定しない。値、出所、確度を分ける。
6. 既存URLをroute contractとして固定する。
7. preview、semantic parity、link、visual、artifact diffを通過した生成物だけを公開する。

## 4. Target architecture

```text
content/                     manuscript + semantic blocks
content-data/                page/series/route metadata (or front matter by schema)
publishing/
  templates/                 document/page-type skeletons
  components/                shared semantic UI
  styles/
    tokens/
    base/
    typography/
    layout/
    components/
    page-types/
    themes/
  behaviors/                 opt-in runtime scripts
  themes/                    visual theme manifests
  assets/                    source assets and role manifests
scripts/                     deterministic build and migration tools
validation/                  schema, parity, links, assets, HTML, visual tests
dist/ or site/               immutable build output
.github/workflows/           validate, artifact, staging, deploy
```

物理名はscaffold PRで決める。既存`publishing/`のlogical ID、template/component分離、preview-only、fail-closed theme resolutionは継承候補である。

## 5. Page types

| Page type | Examples | Required relationships |
|---|---|---|
| `home` | `/` | primary collections |
| `collection-index` | `/article/`, `/notes/`, `/essay/` | child pages |
| `article-index` | `/article/state-change/` | chapters, bibliography, PDF |
| `article-chapter` | chapter HTML | parent, previous, next |
| `note` | notes detail/timeline | collection, references |
| `essay` | essay detail | collection |
| `series-index` | each series root | series order, children, downloads |
| `series-entry` | series chapters | parent, previous, next |
| `support` | concept-map, glossary, misconceptions, bibliography, flyer | owner collection |
| `redirect` | legacy aliases | destination, status policy |
| `utility` | sitemap, robots, manifest | build-derived configuration |
| `maintenance` | optional cutover page | archive access policy |

page typeはDOMを固定するものではなく、必要metadata、navigation、validationを定義する契約とする。

## 6. Metadata design

最低限のschema：

```yaml
id: stable-logical-id
route: /existing/public/path/
page_type: series-entry
title: current public title
description: current public description
canonical: /existing/public/path/
status: published
content_source: content/...
series:
  id: series-id
  order: 1
dates:
  page_created_at: null
  page_updated_at: null
  manuscript_created_at: null
  manuscript_updated_at: null
  web_migrated_at: null
aliases: []
downloads: []
assets: []
theme_id: default-academic
```

- ISO 8601とtimezoneを保存し、表示形式はtemplateに委ねる。
- `null`を許容し、不明値をGit履歴から自動生成しない。
- `updated_at`はbuild時刻にしない。本文またはmetadataに意味のある変更があった時刻とする。
- canonicalはroute manifestから生成し、HTMLごとの手書きを避ける。
- 公開表示する日時の組合せはIssue #32の別PRで決定する。

## 7. CSS layers

読み込み順と責務を固定する。

1. `tokens`: color、space、type scale、measure、z-index
2. `base`: reset、element defaults、accessibility
3. `typography`: prose、code、table、reference
4. `layout`: shell、header、main grid、reading measure
5. `components`: navigation、cards、reading preferences、footer
6. `page-types`: article/series/index等の構成差
7. `themes`: token overrideのみを基本とする
8. `visual-world`: 将来のopt-in layer。今回対象外

`publishing/design/tokens.css`と`components.css`はsource候補、`site/publishing/design/*`は生成copyとする。`style-genai-shikumi.css`、`style-codex-volume.css`、`theme.css`等はvisual parityの参照元であり、v2へそのまま集約コピーしない。

## 8. Behavior scripts and themes

- behaviorはcomponent単位で明示opt-inし、全ページへDOMを自動mountしない。
- reading preferenceの状態key、初期値、keyboard、no-JS挙動を契約化する。
- `theme.js`のlegacy adapter依存を段階的に外す。
- themeはlogical IDとasset roleで参照し、物理pathをtemplateへ埋め込まない。
- 未登録theme、未解決必須asset、未解決placeholderはbuild failureとする。
- theme変更で本文DOMやcontent schemaを変えない。

## 9. Assets

- source assetとgenerated assetを分離する。
- asset manifestにlogical ID、role、source path、output path、media type、dimensions、hash、license/credit（必要な場合）を持つ。
- favicon、OG、QR、PDFは既存公開pathを維持する。
- responsive derivativeやOG derivativeは元assetから再生成可能にする。
- orphanとmissing referenceをvalidationで検出する。
- PDFは本文から独立したimmutable public assetとしてhashを比較する。

## 10. Build, validation and deployment

buildは同じcommitとtoolchainから同じartifactを作る。推奨pipeline：

1. schema / front matter validation
2. content render
3. route collision / alias validation
4. HTML semantic validation
5. internal link / fragment / download / asset validation
6. current-vs-v2 text parity report
7. representative desktop/mobile visual regression
8. sitemap / robots / manifest generation
9. immutable artifact作成とmanifest/hash保存
10. staging deploy、smoke test、承認後productionへ同一artifactをpromote

現行の`deploy.yml`は`main` push時に`site/`をFTPS転送する。v2ではbuildをdeploy job内で暗黙実行せず、検証済みartifactをdeployする。切替PRまで現行workflowは変更しない。

## 11. Existing URL policy

- salvage inventoryの全URLをroute fixture化し、原則200を維持する。
- legacy aliasは直接削除せず、同一内容生成または明示redirectへ移行する。
- redirect statusはhosting能力を確認して決める。meta refreshだけを恒久策にしない。
- slash / `.html` / relative canonicalの違いを正規化する場合も、旧入口を残す。
- sitemapのURL集合と内部link graphをcutover前後で比較する。

## 12. Classification of current implementation

| Current item | Classification | v2 handling |
|---|---|---|
| `content/**` | 正本候補 | parity確認後に正本化 |
| `site/**/*.html` | 生成物 + 未抽出本文の移行元 | 今回保持。移行完了ページから再生成 |
| `style-genai-shikumi.css` | legacy page-family CSS | visual reference、後に置換可能 |
| `style-codex-volume.css` | legacy volume CSS | visual reference、後にpage type/themeへ分解 |
| `theme.css` | legacy appearance CSS | token/theme挙動を参照して置換 |
| `theme.js` | legacy behavior | state contractを参照してcomponent behaviorへ分離 |
| `publishing/design/tokens.css` | v2 source候補 | naming/a11y監査後に採用 |
| `publishing/design/components.css` | v2 source候補 | component境界監査後に採用 |
| `site/publishing/**` | 公開copy | build outputへ統合 |
| `scripts/build_content_pages.py` | migration proof | full builderへ統合後に廃止判断 |
| `scripts/build_structured_preview.py` | architecture proof | v2 builderの基礎候補 |
| validators/workflows | gate資産 | route/schema/full-site用へ統合 |

## 13. Phased migration and proposed PRs

各PRは小さくし、公開変更PRでは対象URL、rollback、公開確認を必ず明記する。

### PR 1 — Add machine-readable route and salvage manifests

- 目的：102ページのURL、title、description、canonical、source、asset/linkを機械台帳化
- 変更対象：inventory data、schema、read-only extractor、tests
- 触らないもの：本文、`site/`、CSS/JS、deploy
- rollback：追加manifest/scriptをrevert
- 公開確認：なし。現行site差分ゼロとinventory completenessをCI確認
- 関連Issue：#33、#32

### PR 2 — Salvage legacy article and note content

- 目的：`content/`未収容本文を意味保持で抽出
- 変更対象：content sources、provenance metadata、parity fixtures
- 触らないもの：公開HTML、文章表現、styles、deploy
- rollback：追加content sourceをrevert
- 公開確認：現行HTMLとのnormalized text/link parity report
- 関連Issue：#33

### PR 3 — Normalize metadata schema

- 目的：5種類の日時、canonical、description、aliasesを明示
- 変更対象：schema、known values、validation、policy doc
- 触らないもの：公開日時表示、本文
- rollback：schema/metadata commitをrevert
- 公開確認：previewでmeta差分をレビュー
- 関連Issue：#32、#33

### PR 4 — Scaffold unified v2 build

- 目的：page types、templates、components、style layers、route outputを統合
- 変更対象：`publishing/`、builder、preview output、tests
- 触らないもの：`site/`、deploy、Visual World System
- rollback：scaffoldをrevert
- 公開確認：preview artifactのみ
- 関連Issue：#33、#27

### PR 5 — Add full-site parity and link gates

- 目的：text、route、link、asset、HTML、visualのcutover gateを作る
- 変更対象：validation、fixtures、CI
- 触らないもの：公開site
- rollback：workflow/validatorをrevert
- 公開確認：代表URLのpreview screenshotsと全route report
- 関連Issue：#33、#27、#32

### PR 6 — Build v2 staging artifact

- 目的：全ページをstagingで生成・レビュー
- 変更対象：generated staging artifact/config（production deploy外）
- 触らないもの：production `site/`、main deploy
- rollback：staging deployment/versionを戻す
- 公開確認：全route smoke、代表visual、PDF/hash、404 scan
- 関連Issue：#33

### PR 7 — Cut over to v2

- 目的：検証済みartifactへ一括切替
- 変更対象：`site/`生成物、artifact deploy path/workflow
- 触らないもの：本文の編集、Visual World System
- rollback：直前production artifactを再deployし、cutover commitをrevert
- 公開確認：route fixture全件、homepage、各page type、downloads、sitemap、controls
- 関連Issue：#33、#27、#32

### PR 8 — Retire legacy implementation

- 目的：利用されないbuilder/CSS/JS/alias copyを削除
- 変更対象：到達不能と証明されたlegacy files
- 触らないもの：content、public URL、assets
- rollback：削除commitをrevert
- 公開確認：artifact hashとroute/link regression
- 関連Issue：#33

## 14. Exit criteria

- 全公開ページが正本sourceへ紐づく。
- route、title、description、canonical、metadata provenance、link、assetが台帳化される。
- `site/`を空から再生成できる。
- 現行本文とsemantic parityがある。
-既存URL、download、sitemapが維持される。
- stagingとproductionが同一artifactを使う。
- rollbackがリハーサル済みである。

## 更新履歴

- 2026-07-27 09:22 JST：Issue #33の初回v2 architecture planを作成。
