# 状態変化論考｜AI可読性・参照構造の保守

ページ作成日時：2026-11-08 14:25 JST  
最終更新日時：2026-11-08 14:25 JST

対象：`site/article/state-change/` のトップ・16章・文献（18ページ）と対応する `content/` のメタデータ。本文の改稿・出版基盤の昇格は行わない。

## 観測と変更

- 公開GETで全18ページが200。main `054e6135e20df02019a3483f0f9d56db6707543b` のHTMLとバイト一致。
- 目次のTopリンクが全ページで二重の `state-change/` へ解決される。計36箇所を `./` に訂正。
- 文献末尾の関連テーマが `/article/notes/themes.html`（404）を指す。実在する `/notes/themes.html`（200）へ訂正。
- 全18ページへ各自のHTTPS canonicalを設定。章をすべて論考トップへcanonical化しない。
- トップで既に公開されている著者表記「Taku」を全章・文献の可視ヘッダーとauthor metaへ反映。
- 既存の節番号・文字見出しを使い、194個のh2へ固定ID（section-0、section-a等。目次はcontents）を追加。本文・見出しの文言は維持。
- トップのdescription／og:descriptionの途切れを、可視要旨に合わせて完結。

## 正本と再生成

`content/` は引き続き `source-reconstruction-draft`。canonical・author・要旨・文献末尾のリンクを同期する。`source_html_sha256` は抽出時点の来歴なので変更しない。文献の書誌、未検証DOI、論考公開日を推定で修正しない。

既存ビルダーは今回のauthor/canonical metadataを全面的には消費していない。構造化出版への移行や全文再生成を完了したとは扱わない。将来の昇格時には本保守処理とリンク・本文保持の検証を必ず再実行する。

```bash
python scripts/maintain_state_change_metadata.py          # 差分が必要なら失敗
python scripts/maintain_state_change_metadata.py --write  # 固定36ファイルのみ更新
python scripts/test_state_change_maintenance.py
```

## 検証契約

通常の新規出版gateはこの既存論考を登録対象として扱っていないため、限定保守gateへ委譲する。対象外のファイル、本文改稿、canonicalの外部置換、元から存在しないページは拒否する。既存baseに定義済み変換を適用した文字列と、変更後の全36ファイルを一致検証する。対象ディレクトリを無条件に許可する仕組みではない。

CIは18ページ×390/1440pxで著者・canonical・見出しID・目次のTopリンク・横はみ出しを検証し、代表ページの画像を保存する。これらはAIの読解精度・引用率・検索順位の改善を測るものではない。

HTTP→HTTPSリダイレクト、著者プロフィール、文献の精査・DOIリンク化、論考と章の構造化データ、全文版は後続候補。robotsには取得禁止がなく、XMLサイトマップに全18 URLがあるため今回は変更しない。

## 記録正本

[横断作業・思想・診断レポート](https://github.com/smilegroupsato/web-smilecompany-llc/tree/main/docs/projects/ai-readable-publishing)。本書は実装の保守記録であり、会話の逐語録ではない。

Repository Context impact: yes。本文正本・出版構造移行の方針は維持し、再生成時の検証契約を追加。CHAT_HISTORY / EXPERIMENTS / CHANGELOGへの重複転記はせず本書・PR・横断レポートを参照する。Force push used: no。

## 更新履歴

- 2026-11-08 14:25 JST：公開状態の観測、限定修正、本文保持・参照検証、再生成時の注意を記録。
