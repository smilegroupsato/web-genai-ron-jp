# Research Notes controlled publication v0

ページ作成日時：2026-08-04 16:22 JST
最終更新日時：2026-08-04 16:37 JST

## 目的

`content/notes/` の研究ノートを正本として扱い、対象を一つに限定した明示操作だけで `site/notes/` へ反映する。

## v0の対象

```text
content/notes/<slug>/index.md
  -> preview review
  -> site/notes/<slug>/index.html
```

`content/notes/index.md`、`themes.md`、`timeline.md`、複数ページの一括生成は対象外とする。

## preview

```bash
python scripts/build_notes_preview.py \
  --source content/notes/tool-discovery-layer/index.md \
  --preview-root _notes_build_preview
```

preview builderは`site/`へ書く引数を持たない。

## controlled promotion

previewと現行公開ページのsemantic parityを確認した後、対象sourceを一つだけ明示して実行する。

```bash
python scripts/promote_note.py \
  --source content/notes/tool-discovery-layer/index.md \
  --candidate-root _notes_promotion_candidate \
  --write-site
```

promotion scriptは出力先を引数で受け取らない。sourceのrouteとpath契約から、単一の`site/notes/<slug>/index.html`だけを決定する。

## PR Gate

`Validate Notes Publish`は次を検証する。

- 公開対象は一つだけ
- `site/`の他ファイルに差分がない
- 対応sourceが`content/notes/<slug>/index.md`に存在する
- 公開HTMLがsourceから再生成したcandidateとbyte-identical
- 既存公開ページからtitle、本文、見出し、リンク、目次の意味が欠落していない
- 管理メタデータが公開HTMLへ漏れていない
- desktop 1440px / mobile 390pxで必須領域、横overflow、console errorを検証する

## 更新履歴

- 2026-08-04 16:37 JST：初回controlled promotionに向け、対象route自動解決・既存note layout互換・desktop/mobile visual QAを必須gateへ追加。
- 2026-08-04 16:22 JST：研究ノートのpreview-only builder、明示promotion、PR validatorのv0契約を新規作成。
