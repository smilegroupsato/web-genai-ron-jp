# Site UI normalization baseline｜header / width / reading controls

ページ作成日時：2026-07-25 09:49 JST  
最終更新日時：2026-07-25 09:49 JST

## 0. Purpose

この文書は、genai-ron.jp の公開ページ群について、緊急復旧後に残っている UI / layout の不統一を安全に正規化するための基準である。

対象Issue: #27 `Site UI normalization｜header / width / reading controls`

この文書は実装PRではなく、以後の小分けPRで壊さないための baseline として扱う。

---

## 1. Current state summary

2026-07-24 に site-wide appearance / reading controls 関連の変更が既存ページへ広く干渉し、一部ページで表示崩れが発生した。

緊急対応として、以下はmerge済み。

- PR #25: `site/assets/theme.css` の site-wide controls block をrevert
- PR #26: `theme.js` の appearance 適用を `.reading-preferences` がある structured publishing pages に限定

これにより大きな表示崩れは止まったが、次の不統一が残っている。

- ヘッダーがページ群ごとに異なる
- 目次ページと本文ページの幅・余白が異なる
- 表示モード / 文字サイズUIの有無がシリーズ・ページ単位で混在している
- 001 / 002 / 003 / AI対話入門が、同じサイト内で別世代テンプレートとして見えている

---

## 2. Public observation snapshot

### `/`

- 大きな表示崩れは確認されていない
- 表示モード調整ボタンなし
- 文字サイズ調整ボタンなし

### `/series/genai-shikumi/`

- 目次ページ、本文ページとも調整ボタンなし
- 目次ページと本文ページの幅が異なる

### `/series/genai-shikumi-technical/`

- 目次ページ、本文ページとも調整ボタンなし
- 本文ページの幅が目次ページと異なる
- 本文ページには目次ページに適用されているCSSが適用されていないように見える

### `/series/genai-shikumi-deep-dive/`

- 目次ページには調整ボタンなし
- 本文ページは 04 / 07 / 08 にのみ調整ボタンあり
- structured移行済みページと未移行ページが混在している

### `/series/ai-dialogue-intro/`

- 目次、本文とも調整ボタンあり
- structured publishing pages として `.reading-preferences` を保持

---

## 3. Baseline principles

### 3.1 First principle: no site-wide automatic UI mount

旧ページ全体へ、表示モード / 文字サイズUIを自動mountしない。

禁止すること:

- `theme.js` で全ページに `data-appearance` を付ける
- `.appearance-switcher` を全ページの `body` 末尾へ自動追加する
- site-wide CSSで既存ページのヘッダー・本文幅・カード背景を横断的に上書きする

許可すること:

- `.reading-preferences` を明示的に持つ structured publishing pages のみ表示設定UIを有効化する
- 旧ページへ表示設定UIを戻す場合は、ページ群単位で明示的に opt-in する

### 3.2 Second principle: layout before controls

表示モード / 文字サイズUIを戻す前に、ヘッダーと本文幅を安定化する。

順序:

1. ヘッダー方針
2. 目次 / 本文幅の方針
3. 003 structured混在の扱い
4. 表示設定UIの再導入可否

### 3.3 Third principle: no large batch style rewrite

複数シリーズを一括でCSS修正しない。

PRは以下のように分割する。

- PR-A: header / layout baseline documentation
- PR-B: 001 / 002 width normalization
- PR-C: 003 mixed-state policy / migration path
- PR-D: reading controls policy and implementation

### 3.4 Fourth principle: public check target must be explicit

各PRには、公開確認対象URLを必ず書く。

最低限確認するURL:

- `/`
- `/series/genai-shikumi/`
- `/series/genai-shikumi/01-memory/`
- `/series/genai-shikumi-technical/`
- `/series/genai-shikumi-technical/01-memory/`
- `/series/genai-shikumi-deep-dive/`
- `/series/genai-shikumi-deep-dive/04-context/`
- `/series/genai-shikumi-deep-dive/07-workflow/`
- `/series/genai-shikumi-deep-dive/08-context-design/`
- `/series/ai-dialogue-intro/`
- `/series/ai-dialogue-intro/01-start-talking/`

---

## 4. Header normalization policy draft

### Goal

同一サイト内で、最低限以下が揃って見えること。

- ブランド表示
- サイト内ナビの並び
- シリーズ内ナビの位置づけ
- ヘッダー高さ / 余白 / 境界線

### Current issue

- 001/002/003の叢書トップは `codex-volume` 系の見た目を持つ
- 001/002本文は通常の `series-page` 寄り
- AI対話入門は structured publishing template 由来
- そのためシリーズ移動時に、別サイトへ移動したように見える

### Draft policy

- site-wide brand: `GENAI-RON / 生成AI論`
- top-level nav: `目録 / 論考 / 研究ノート / 叢書001 / 叢書002 / 叢書003`
- series-specific nav: structured pages のみ必要最小限に追加
- headerの装飾色はシリーズ色を許可するが、構造は揃える

---

## 5. Width normalization policy draft

### Goal

同一シリーズ内では、目次ページと本文ページの読み幅が急に変わらないこと。

### Draft policy

- 目次トップ: 広めの一覧幅を許可
- 本文ページ: 読みやすい本文幅を優先
- ただし、ヘッダー・hero・main containerの左右位置は揃える
- 目次だけ `1120px`、本文だけ極端に狭い/広い状態を避ける

### Candidate implementation direction

- 001/002本文に、明示的な series body class を追加する
  - `codex-volume codex-001` or `codex-volume codex-002`
- ただし、本文そのものの読み幅は広げすぎない
- `series-main` と `article.note-box` の責務を分ける
  - container alignment
  - reading width

---

## 6. Reading controls policy draft

### Current safe state

PR #26 後、表示設定UIは `.reading-preferences` が存在する structured publishing pages のみに限定されている。

### Do not do

- legacy pages にJSで自動追加しない
- `body > .appearance-switcher` をsite-wide fixed表示しない
- 旧ページの本文幅調整と同時に表示設定UIを戻さない

### Candidate policy

- Phase 1: AI対話入門のみ維持
- Phase 2: 003 structured移行済みページで維持
- Phase 3: 001/002をstructured化または明示opt-inした後に再導入

---

## 7. PR sequence

### PR-A: baseline documentation

This document.

Scope:

- docs only
- no public CSS / JS / HTML changes

### PR-B: width normalization for 001 / 002

Scope:

- 001/002のトップと本文のcontainer alignment
- 表示設定UIは触らない

### PR-C: deep dive mixed-state handling

Scope:

- 003の04/07/08と未移行ページの差を記録
- structured migration継続か、暫定統一CSSかを判断

### PR-D: reading controls reintroduction policy

Scope:

- 表示モード / 文字サイズUIの対象ページを明示
- 自動mount禁止
- structured / opt-in方式のみ

---

## 8. Acceptance checklist for future PRs

- [ ] 変更対象ページを列挙した
- [ ] 非対象ページに影響しない理由を書いた
- [ ] 公開確認URLを書いた
- [ ] `theme.js` のsite-wide mountを復活させていない
- [ ] `theme.css` でsite-wide controls blockを復活させていない
- [ ] 本文内容を変更していない
- [ ] rollback方法を書いた

---

## 更新履歴

- 2026-07-25 09:49 JST：Issue #27に基づき、UI正規化のbaseline文書を作成。
