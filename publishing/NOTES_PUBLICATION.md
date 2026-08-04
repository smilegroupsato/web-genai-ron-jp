# Research Notes controlled publication v0.2

ページ作成日時：2026-08-04 16:22 JST
最終更新日時：2026-08-04 18:16 JST

## 目的

`content/notes/` の研究ノートを正本として扱い、対象を一つに限定した明示操作だけで `site/notes/` へ反映する。

## v0.2の対象

```text
content/notes/<slug>/index.md
  -> preview review
  -> site/notes/<slug>/index.html

content/notes/history-of-generative-ai/timeline.md
  -> preview review
  -> site/notes/history-of-generative-ai/timeline.html
```

`content/notes/index.md`、`themes.md`、複数ページの一括生成は対象外とする。nested `.html` routeは、現時点では完全版年表のみを明示許可する。

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

builderは、Markdownのsection先頭に`Research Group A`等または`Theoretical Lines`のラベルと続く見出しがある場合、既存の`period`構造として保持する。`references` sectionの最初の番号付きリストは`source-list`として保持する。

明示section anchorがない概要型noteは、CONTENTSのページ内リンクとh2の数が一致する場合に限り、順番からanchorを復元する。`turning-points`と`layers`は、既存のカード構造を保つ。

完全版年表は、`PERIODS`目次、5期の順序、5層ラベル、出典sectionが全て一致する場合に限り、`period`・`timeline-card`・`badge`構造を再生成する。

## 更新履歴

- 2026-08-04 18:16 JST：完全版年表のnested route、5期・5層・イベントカードの再生成とCI検証をv0.2として追加。
- 2026-08-04 18:06 JST：概要型noteの目次・見出し順からのanchor復元と、転換点／5層カードの構造保持を追加。
- 2026-08-04 17:57 JST：長文研究ノートの既存表現を保つため、研究群区切りと参考文献リストの構造保持を追加。
- 2026-08-04 16:40 JST：既存のseries controlled-writeとpublishing structure gateから、notes公開差分を専用gateへ明示委譲。
- 2026-08-04 16:37 JST：初回controlled promotionに向け、対象route自動解決・既存note layout互換・desktop/mobile visual QAを必須gateへ追加。
- 2026-08-04 16:22 JST：研究ノートのpreview-only builder、明示promotion、PR validatorのv0契約を新規作成。
