- ページ作成日時：2026-06-02 17:07 JST
- 最終更新日時：2026-06-02 17:07 JST

# web-genai-ron-jp

Web管理｜生成AI論｜genai-ron.jp

## 0. このリポジトリの位置づけ

このリポジトリは、`genai-ron.jp` のWeb公開用ファイルを管理する正本リポジトリです。

Notionは内部ノート・研究原本・素材整理の場所として扱い、GitHubはWeb公開用ファイルの正本・履歴管理・自動公開の起点として扱います。

## 1. 公開フロー

```text
ChatGPTで文章作成・編集
↓
必要に応じてNotionに内部ノート化
↓
Web公開用HTML / CSS / 画像 / 静的ファイルを作成
↓
このGitHubリポジトリに保存・更新
↓
GitHub Actionsでロリポップ等へ自動アップロード
↓
Web公開
```

## 2. ディレクトリ構成

```text
/
  README.md
  site/
    index.html
    article/
    assets/
    downloads/
    sitemap.xml
    robots.txt
  .github/
    workflows/
      deploy.yml
```

## 3. 公開対象

`site/` 以下が公開サーバへアップロードされます。

現在の公開候補最新版：

```text
genai-ron_public_v5_7_inline_header_fix_2026-05-20.zip
```

位置づけ：

- 論考①：`article/state-change/` 配下に整理
- 論考②：`article/understanding-defense-action/` 配下に追加
- 論考別の色調整理済み
- ヘッダー修正版
- PDF同梱版

## 4. GitHub Actions

`.github/workflows/deploy.yml` により、`main` ブランチへのpush時に `site/` 以下を公開サーバへFTPSアップロードします。

初回は安全確認のため、`dry-run: true` 付きで設定します。dry-runが成功した後、本番反映時に `dry-run: true` を削除します。

## 5. GitHub Secrets

以下のRepository Secretsを使用します。

```text
FTP_SERVER
FTP_USERNAME
FTP_PASSWORD
SERVER_DIR
```

秘密情報はREADME、チャット本文、リポジトリ内ファイルには記載しません。

## 6. 更新ルール

- FTPで直接アップロードしない。
- `site/` 以下を更新し、GitHub Actionsで自動反映する。
- トップページ・論考一覧・ナビゲーション・sitemapも必要に応じて更新する。
- PDFや画像などのバイナリも公開対象として `site/` 以下に置く。
- 公開に向かない内部事情、未確定情報、個人情報、秘密情報は入れない。

## 7. 更新履歴

- 2026-06-02 17:07 JST：GitHub Actionsによる公開運用前提のREADMEへ更新。
