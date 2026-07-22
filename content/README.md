---
ページ作成日時: "2026-07-22 16:07 JST"
最終更新日時: "2026-07-22 16:07 JST"
---

# genai-ron.jp content source

この `content/` ディレクトリは、`genai-ron.jp` に公開する文章そのものを、公開HTML・CSS・JavaScript・ヘッダー・ナビゲーションなどのサイト実装から分離して保存するための場所である。

## 目的

`site/` は公開配信用の生成物・実装物を含む。将来、CSS、JavaScript、テンプレート、ヘッダー、ナビゲーション、文字サイズ切替などが壊れたり、全面的に作り直しになったりしても、文章本体を失わないようにする。

`content/` は、サイトが壊れたときに、文章資産から再構築できることを目的とする。

## 責務分離

```text
content/
  = 文章正本、意味上のブロック、最低限メタデータ

site/
  = 公開HTML、CSS、JavaScript、ナビゲーション、配信物
```

## content/ に含めるもの

- タイトル
- サブタイトル
- 本文
- 見出し構造
- 注記、引用、phrase、コード、表などの意味上のブロック
- 公式参照・参考資料
- slug、canonical URL、series情報など最低限のメタデータ
- 公開本文から除外すべき項目の指定

## content/ に含めないもの

- グローバルヘッダー
- メニュー
- フッター
- 文字サイズ切替
- appearance switcher
- CSSの見た目指定
- JavaScript補正
- 公開HTML固有のラッパー構造
- 作業履歴、内部TODO、変換ログ

## 基本方針

生成済みHTMLを唯一の原稿にしない。Notion exportも唯一の正本にしない。

正本は、公開文章を、特定のCMSや現在のHTML構造に依存しない形式で保存したものとする。

## 初期状態

まずは `content/series/genai-shikumi-deep-dive/04-tool-execution-loop.md` を復元サンプルとして作成し、そこから公開HTMLを再生成できるかを確認する。
