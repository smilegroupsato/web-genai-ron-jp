# Publishing Structure Validation

ページ作成日時：2026-07-23 07:56 JST  
最終更新日時：2026-07-23 08:44 JST

## Current State

```yaml
phase: parallel-structured-publishing
status: visual-qa-passed-preview-only
gate: semantic-and-visual-parity
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
- Chromiumによるdesktop 1440px / mobile 390pxの描画確認
- header / reading preferences / hero / article / footerの領域確認
- document-level horizontal overflowなし
- default theme / Library Series metadata-only themeの双方でvisual QA成功
- 表示切替UIをbody直下から専用reading-preferences componentへ隔離

## Visual QA Result

```yaml
cases:
  - default-desktop
  - default-mobile
  - library-desktop
  - library-mobile
required_regions:
  - header
  - reading-preferences
  - hero
  - article
  - footer
document_horizontal_overflow: false
console_errors: none
appearance_buttons:
  count: 3
  mounted_in_dedicated_slot: true
  direct_body_child: false
```

初回visual QAでは、現行`theme.js`が生成する`Paper / Reading / Archive`のswitcherがbody直下、footer後へ未整形のまま現れることを確認した。

structured publishing側では、次を追加して配置責務を分離した。

- `publishing/components/reading-preferences.html`
- `publishing/design/components.css`
- `publishing/behaviors/reading-preferences-adapter.js`

adapterは現行runtimeが生成したcontrolを専用slotへ移す移行措置である。将来は`theme.js`からappearance / reading preference責務自体を分離する。

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

## Observed Non-blocking Detail

mobileの横幅では、情報量の多いtableは内部横スクロールを許容する。document全体は390pxを超えていない。

これは現行CSSとの互換挙動であり、今回のpublishing scaffold mergeを妨げない。tableのmobile表現改善は、構造化基盤とは別の誌面改稿として扱う。

## Current Boundary

まだ行わないこと：

- structured builderから`site/`への書き込み
- Library Series画像の本番参照
- current builderの廃止
- public CSS / JavaScriptの置換
- 公開サイトのtheme切替
- appearance / text-size runtimeの全面置換

## Next Gate

1. PR #2の責務境界と変更ファイルを最終確認する
2. scaffoldのみをmainへmergeする
3. merge後も`site/`差分がないことを再確認する
4. 次のbranchで、1ページだけをstructured builderから生成するpromotion fixtureを設計する

## 更新履歴

- 2026-07-23 08:44 JST：desktop / mobile visual QA成功、表示切替UIのbody直下漏出を検出・専用componentへ隔離。tableのmobile内部スクロールを非blockerとして分離。
- 2026-07-23 07:56 JST：全contentページのsemantic parityとLibrary Series runtime metadata解決のCI成功を記録。
