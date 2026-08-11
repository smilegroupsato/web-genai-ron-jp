# genai-ron.jp v2 content salvage inventory

ページ作成日時：2026-07-27 09:22 JST
最終更新日時：2026-08-11 12:02 JST

## 1. Purpose and boundary

Issue #33 の Phase 1 として、v2 再構築前に失ってはいけない公開情報を記録する。これは削除許可リストではない。今回の調査では `site/**/*.html`、`site/assets/**/*.css`、`site/assets/**/*.js`、`site/downloads/**`、`content/**`、`publishing/**`、`scripts/**`、`.github/workflows/**`、`docs/site-ui-normalization-baseline.md` と Issue #27 / #32 / #33 を確認した。

調査時点の概数は次のとおり。

| 対象 | 数 | 判定 |
|---|---:|---|
| `site/**/*.html` | 102 | 公開生成物。ただし未抽出本文・URL・meta の移行元 |
| `content/**/*.md` | 22 | 正本候補。全公開ページは未収容 |
| `site/assets/**/*.css` | 10 | legacy公開実装。視覚同等性の参照元 |
| `site/assets/**/*.js` | 1 | legacy behavior。挙動と保存キーの参照元 |
| `site/downloads/**` の公開ファイル | 3 PDF | 維持対象 |
| SVG asset | 3 | favicon / OG / QR として維持対象 |

## 2. Source-of-truth status

### 残すべき正本

- `content/series/ai-dialogue-intro/*.md`（10ページ）
- `content/series/genai-shikumi-deep-dive/*.md`（12ページ）
- 各Markdownの本文、見出し、slug、description、series/order/navigation、意味ブロック、原稿由来日時
- `site/downloads/*.pdf` と `site/assets/favicon.svg`、`og.svg`、`qr-genai-shikumi.svg` の実体
- URL、シリーズ順序、研究・思想上の関係、本文内の参照リンク

`content/README.md` が規定する通り、`content/` は文章正本候補である。ただし抽出結果は公開本文とのsemantic parity確認が終わるまで確定正本に昇格させない。

### 移行元として参照すべきもの

- `site/**/*.html`：`content/` 未収容ページの本文、title、description、日時コメント、内部リンク、download link
- `site/assets/*.css`：現行の読み幅、タイポグラフィ、ページ固有表現を比較するbaseline
- `site/assets/theme.js`：appearance / text-size の保存・適用挙動
- `publishing/**`：structured publishing の既存設計、template、components、token、theme registry
- Git履歴：HTML内に明記されない作成・更新日時の「根拠候補」。推定値として自動採用しない

### v2生成後に破棄可能なもの

semantic parity、URL parity、asset/link検証、visual regression、rollback snapshotがすべて完了したページに限り、手書き公開HTMLとlegacy CSS/JSの実装は置換可能である。現時点では一括削除可能なファイルはない。

### まだ判断できないもの

- `site/article/*.html` と `site/article/state-change.html`：実ページへのlegacy alias。外部参照確認後にredirectへ置換できる可能性がある
- `site/article/state-change-lit-review/index.html`：移動案内。アクセス実績または外部参照確認が必要
- version付きCSS（`style.v5-6.css`、`style_article1.v5-6.css`）：同内容・旧参照の有無を確認後に判断
- `og.svg` が全ページ共通OG正本か、暫定placeholderか
- HTMLコメントにだけある日時が、どのシステムで記録された値か

## 3. Public URL and title inventory

URLは末尾スラッシュを含む現在の公開形をv2のroute contractとする。`.html` のlegacy URLと移動案内も、redirect方針が確定するまで維持する。

### Home, essays and notes

| URL | 現行title |
|---|---|
| `/` | GENAI-RON｜生成AI論 |
| `/essay/` | エッセイ｜GENAI-RON |
| `/essay/ai-era-authorship/` | 自分で作らない創作の時代に、主体はどこに残るのか｜GENAI-RON |
| `/essay/ai-only-generation/` | AIしか使わない世代は現れるか｜GENAI-RON |
| `/notes/` | 研究ノート｜GENAI-RON |
| `/notes/history-of-generative-ai/` | 生成AIの歴史｜多層年表｜GENAI-RON |
| `/notes/history-of-generative-ai/timeline.html` | 生成AIの歴史｜完全版年表｜GENAI-RON |
| `/notes/state-change-lit-review/` | LLMとの対話は人間の何を変えるのか――「状態変化」の先行研究レビュー｜GENAI-RON |
| `/notes/themes.html` | 関連テーマ｜GENAI-RON |
| `/notes/tool-discovery-layer/` | ChatGPTのツール発見レイヤーとユーザー指示の衝突｜GENAI-RON |

### Articles

| URL group | 現行title / 構成 |
|---|---|
| `/article/` | 論考一覧｜GENAI-RON |
| `/article/state-change/` | 生成AIとの対話における状態変化とその一回性・不可逆性について |
| `/article/state-change/chapter-01.html` … `chapter-16.html` | 第1章「先行研究の予備的配置」から第16章「結論：生成AIとの対話は不可逆な履歴生成である」 |
| `/article/state-change/bibliography.html` | ビブリオグラフィー｜生成AI論 |
| `/article/understanding-defense-action/` | 理解・防御壁・行動｜GENAI-RON |
| `/article/understanding-defense-action/chapter-00.html` … `chapter-12.html` | 第0章「序論」から第12章「結論｜理解を行動へ沈めるために」 |
| `/article/understanding-defense-action/bibliography.html` | ビブリオグラフィー｜GENAI-RON |
| `/article/chapter-01.html` … `chapter-16.html`、`/article/bibliography.html`、`/article/state-change.html` | state-change配下を指すlegacy alias |
| `/article/state-change-lit-review/` | `/notes/state-change-lit-review/` への移動案内 |

記事章の各titleと本文は各HTMLから抽出し、章単位で照合する。alias側の同一本文を独立正本として複製しない。

### Series 001 — genai-shikumi

| URL | 現行title |
|---|---|
| `/series/genai-shikumi/` | GENAI-RON叢書001｜生成AIのしくみ｜AIと付き合うための8つの視点 |
| `/series/genai-shikumi/01-memory/` | 生成AIのしくみ 01｜ChatGPTの「記憶」はどこにあるのか｜GENAI-RON |
| `/series/genai-shikumi/02-prompt/` | 生成AIのしくみ 02｜プロンプトは命令なのか、環境なのか｜GENAI-RON |
| `/series/genai-shikumi/03-tools/` | 生成AIのしくみ 03｜なぜAIは余計なツールを呼びに行くのか｜GENAI-RON |
| `/series/genai-shikumi/04-context/` | 生成AIのしくみ 04｜コンテキストとは何か｜GENAI-RON |
| `/series/genai-shikumi/05-forgetting/` | 生成AIのしくみ 05｜AIの忘却とは何か｜GENAI-RON |
| `/series/genai-shikumi/06-understanding/` | 生成AIのしくみ 06｜AIは理解しているのか｜GENAI-RON |
| `/series/genai-shikumi/07-workflow/` | 生成AIのしくみ 07｜AIとの共同作業はなぜ失敗するのか｜GENAI-RON |
| `/series/genai-shikumi/08-context-design/` | 生成AIのしくみ 08｜AIを使うとは、文脈を設計することである｜GENAI-RON |
| `/series/genai-shikumi/flyer/` | A4チラシ｜GENAI-RON叢書001｜生成AIのしくみ |

### Series 002 — genai-shikumi-technical

| URL | 現行title |
|---|---|
| `/series/genai-shikumi-technical/` | GENAI-RON叢書002｜生成AIのしくみ 詳解版｜モデル・文脈・ツールの内部構造 |
| `/series/genai-shikumi-technical/01-memory/` | 詳解版｜生成AIのしくみ 01｜LLMの「記憶」はどこにあるのか｜GENAI-RON |
| `/series/genai-shikumi-technical/02-instruction-hierarchy/` | 詳解版｜生成AIのしくみ 02｜指示階層とプロンプト層｜GENAI-RON |
| `/series/genai-shikumi-technical/03-tool-calling/` | 詳解版｜生成AIのしくみ 03｜ツール呼び出しとツール発見レイヤー｜GENAI-RON |
| `/series/genai-shikumi-technical/04-context-window-retrieval/` | 詳解版｜生成AIのしくみ 04｜コンテキストウィンドウと検索｜GENAI-RON |
| `/series/genai-shikumi-technical/05-grounding-hallucination/` | 詳解版｜生成AIのしくみ 05｜理解・接地・ハルシネーション｜GENAI-RON |
| `/series/genai-shikumi-technical/06-workflow-design/` | 詳解版｜生成AIのしくみ 06｜人間とAIのワークフロー設計｜GENAI-RON |

### Series 003 — genai-shikumi-deep-dive

| URL | 現行title |
|---|---|
| `/series/genai-shikumi-deep-dive/` | GENAI-RON叢書003｜生成AIのしくみ 超詳解 |
| `/series/genai-shikumi-deep-dive/01-prompt-compilation/` … `/08-architecture/` | 生成AIのしくみ 超詳解 01 … 08｜GENAI-RON |
| `/series/genai-shikumi-deep-dive/concept-map/` | 生成AIのしくみ 超詳解｜主要概念マップ |
| `/series/genai-shikumi-deep-dive/glossary/` | 生成AIのしくみ 超詳解｜用語集 |
| `/series/genai-shikumi-deep-dive/misconceptions/` | 生成AIのしくみ 超詳解｜よくある誤解集｜GENAI-RON |

HTMLのconcept-map / glossaryの`<title>`には項目名が欠けているため、v2移行時に現行値を無言で「修正」せず、metadata正規化PRで判断する。

### AI dialogue intro

| URL | 現行title |
|---|---|
| `/series/ai-dialogue-intro/` | 生成AIと話すと、考えが見えてくる 目次｜GENAI-RON |
| `/series/ai-dialogue-intro/introduction/` | 生成AIと話すと、考えが見えてくる はじめに｜GENAI-RON |
| `/series/ai-dialogue-intro/01-start-talking/` … `/07-living-with-ai/` | 生成AIと話すと、考えが見えてくる 第1章 … 第7章｜GENAI-RON |
| `/series/ai-dialogue-intro/afterword/` | 生成AIと話すと、考えが見えてくる おわりに｜GENAI-RON |

## 4. Metadata inventory

- meta descriptionは102 HTML中83ページで確認。空欄・欠落ページでは現行本文から新規生成せず、`unknown`として編集判断へ回す。
- canonical linkは21ページで確認。legacy article aliasの相対canonical 19件と、notes 2件が中心。canonicalがないページでも現在のURLをroute contractとして維持する。
- Markdown正本候補はslug / title / description / series情報を持つ。deep-diveはページ作成・更新日時も持つ。
- HTMLコメントにはNotion原稿作成日時、Notion原稿最終更新日時、Web移植日時が存在するページがある。essayには単一日時だけのコメントもある。
- 「ページ作成日時」「最終更新日時」「原稿作成日時」「原稿最終更新日時」「Web移植日時」は別フィールドとし、値が確認できない場合は空欄にする。Git commit日時から推定補完しない。
- Issue #32に従い、公開表示項目の決定は別PRとし、このPRでは値の存在と出所だけを記録する。

推奨する移行台帳の列：

`route`, `page_type`, `title`, `description`, `canonical`, `content_source`, `source_status`, `page_created_at`, `page_updated_at`, `manuscript_created_at`, `manuscript_updated_at`, `web_migrated_at`, `series_id`, `order`, `aliases`, `internal_links`, `download_links`, `asset_refs`, `verification_status`, `evidence`.

## 5. Static assets and downloads

| Path | Role | Size | Handling |
|---|---|---:|---|
| `site/assets/favicon.svg` | favicon | 186 B | pathと内容を維持 |
| `site/assets/og.svg` | default OG | 424 B |参照ページを記録し維持 |
| `site/assets/qr-genai-shikumi.svg` | 叢書001 QR | 9,571 B | flyerとの関係を維持 |
| `site/downloads/ai-dialogue-intro-flyer.pdf` | AI対話入門 flyer | 16,958,898 B | URL・bytes・linkを維持 |
| `site/downloads/genai-ron_01_state-change_2026-05-20.pdf` | 論考①PDF | 520,214 B | URL・bytes・linkを維持 |
| `site/downloads/genai-ron_02_understanding-defense-action_2026-05-20.pdf` | 論考②PDF | 397,785 B | URL・bytes・linkを維持 |

cutover前に全assetへSHA-256 manifestを作り、生成先で一致を検証する。CSS/JSはstatic assetではなくlegacy implementationとして別管理する。

## 6. Links to preserve

- 全HTMLから`href` / `src`を抽出し、内部route graph、alias、fragment、download、asset参照を機械台帳化する。
- root-relative、directory-relative、`.html`相対linkが混在するため、v2 build時に解決後URLで検証する。
- download linkはHTTP 200、Content-Type、Content-Length、SHA-256をcutover前後で比較する。
- sitemap、robots、manifestも公開契約として比較する。
- 外部リンク切れは本文変更と分離し、移行時に勝手に差し替えない。

## 7. Salvage gates

各ページを「救出済み」にできる条件：

1. 本文・見出し・表・引用・コード・リンクのsemantic parityがある。
2. title / description / canonical /日時の出所が記録されている。
3. 現行URLとaliasがroute manifestにある。
4. 参照assetとdownloadが存在しhash一致する。
5. 前後ページ、index、breadcrumb相当のシリーズ関係が維持される。
6. reviewerが公開HTMLとcontent sourceを照合する。

## 更新履歴

- 2026-08-11 12:02 JST：`/notes/themes.html`の現行titleを「関連テーマ｜GENAI-RON」へ更新。
- 2026-07-27 09:22 JST：Issue #27 / #32 / #33と指定ディレクトリを調査し、初回salvage inventoryを作成。
