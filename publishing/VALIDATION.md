# Publishing Structure Validation

ページ作成日時：2026-07-23 07:56 JST  
最終更新日時：2026-07-23 07:56 JST

## Current State

```yaml
phase: parallel-structured-publishing
status: validated-preview-only
gate: semantic-parity-all-content-pages
branch: refactor/publishing-structure-v0.1
pull_request: 2
public_site_changed: false
site_write_enabled: false
```

## Completed Gates

- structured builderのPython構文検証
- `--write-site` 非搭載の確認
- `content/` 全ページのcurrent builder / structured builder生成
- 全生成ページのtitle / h2 / article text / article links一致確認
- global header / footerの存在確認
- unresolved template placeholderの不在確認
- Library Series runtime variant解決確認
- unregistered theme idのfail-closed確認
- branch上で`site/`がmainから変更されていないことの確認
- structured preview artifactの生成・一時保存

## Theme Resolution Verified

```yaml
theme_id: library-university-humanities-summer
collection: library-series
base_theme: university-humanities
season: summer
hero_variant: image-background
text_contrast: dark
asset_role: hero-main
asset_status: unresolved
production_enabled: false
```

画像実体が存在しない状態では`asset_status: unresolved`かつ`production_enabled: false`を維持する。

## Current Boundary

まだ行わないこと：

- PR #2のmerge
- structured builderから`site/`への書き込み
- Library Series画像の本番参照
- current builderの廃止
- public CSS / JavaScriptの置換
- 公開サイトのtheme切替

## Next Gate

1. structured preview artifactを視覚確認する
2. header / hero / body / footer / mobile相当幅を確認する
3. default themeが現行表示を壊さないことを確認する
4. Library Seriesは画像なしのmetadata-only previewとして確認する
5. merge前の責務境界レビューを行う

## 更新履歴

- 2026-07-23 07:56 JST：全contentページのsemantic parityとLibrary Series runtime metadata解決のCI成功を記録。
