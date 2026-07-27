# genai-ron.jp v2 route / salvage manifest policy

ページ作成日時：2026-07-27 09:55 JST
最終更新日時：2026-07-27 09:55 JST

## Purpose

`site/**/*.html`の現在状態を、v2移行で比較可能なmachine-readable snapshotにする。manifestは本文の新しい正本ではなく、route、実装依存、content source対応、metadata出所、link/asset関係を救出するための台帳である。

## Files

- `data/site-routes.manifest.json`：preserve対象routeとsource HTMLの小さなroute contract
- `data/site-content-salvage.manifest.json`：各ページのsalvage detail
- `scripts/build_site_manifest.py`：現行HTMLとMarkdownから両manifestを再現
- `scripts/validate_site_manifest.py`：存在、重複、status、download等を検証

## Extraction rules

- routeは`site/`相対pathから決定する。`index.html`はdirectory route、その他は`.html`を維持する。
- title、description、canonical、body class、CSS/JS、linkはHTMLにある値だけを記録する。
- content sourceは同一series/slugに実在するMarkdownだけを対応付ける。
- 日時はvisible body、HTML comment、Markdown front matterを別々に検索する。
- 日時が見つからない場合、known flagは`false`、valueは`null`、locationは`absent`とする。
- Git日時、file mtime、build時刻から日時を推定しない。
- internal linkは同一siteへ解決できるlinkだけを記録し、外部linkは含めない。
- CSS/JS、download、その他assetは別配列へ分類する。

## Status policy

### `content_source_status`

- `content_source_exists`：対応するMarkdownが実在
- `html_only`：対応Markdownがなく、通常公開ページとして見える
- `alias`：canonicalが別routeを指すlegacy入口
- `redirect_notice`：移動案内ページ
- `unknown`：自動分類不能

### `salvage_status`

- `done`：抽出とparity reviewが完了（初回manifestでは自動付与しない）
- `needs_extraction`：HTMLからcontent sourceへの救出が必要
- `needs_parity_check`：content sourceはあるが公開HTMLとの確認が必要
- `alias_review`：alias/移動案内として維持方法の判断が必要
- `unknown`：人間による分類が必要

## Rebuild and validation

```bash
python3 scripts/build_site_manifest.py
python3 scripts/build_site_manifest.py --check
python3 scripts/validate_site_manifest.py
```

`--check`はcommitted JSONが現在のHTML/Markdownから生成した結果と一致するかを確認する。validatorはJSON parseに加え、source HTML、content source、downloadの存在、preserve routeの一意性、salvage status、2 manifest間のroute集合一致を検証する。

## Change control

- 公開HTMLを変更するPRではmanifest差分を明示する。
- titleや日時をmanifestだけで修正しない。sourceと根拠を先に直す。
- `preserve_route: false`への変更やroute削除は、redirect/cutover方針と人間reviewを必要とする。
- `done`への昇格はsemantic parityの証跡を必要とする。

## 更新履歴

- 2026-07-27 09:55 JST：初回route / salvage manifestの抽出・分類・検証規則を定義。
