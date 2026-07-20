# GENAI-RON / 生成AI論

Repository: `web-genai-ron-jp`

Public Site: <https://genai-ron.jp/>

Last Updated: 2026-07-20 12:12 JST

## Overview

このRepositoryは、公開サイト `genai-ron.jp` のWeb公開用ファイルと、サイトを継続的に保守するための文書群を管理する正本Repositoryです。

対象は、HTML / CSS / JavaScript / 画像 / PDF / sitemap などの公開ファイルと、AI・人間が共有する設計思想、運用方針、判断履歴です。

README.md は作業ログではありません。初めてこのRepositoryを読む人間・AIが、現在の運用と主要文書の位置づけを理解するための入口です。

## Public Site

公開サイトは `genai-ron.jp` です。

公開対象は原則として `site/` 以下の管理ファイルです。`main` ブランチへのpushを起点に、GitHub Actions が `site/` 以下を公開サーバへアップロードします。

現在の原本はGitHub repositoryです。過去には、ChatGPTでzipパッケージを作成し、Google Driveに原本として保存し、公開候補最新版として扱う運用がありました。現在の標準運用では、zipファイルを公開候補最新版として扱いません。

公開・保守の基準は、GitHub上の管理ファイル、commit履歴、GitHub Actionsの実行結果です。

## Repository Role

このRepositoryは、単なるコード置き場ではありません。

`genai-ron.jp` の公開サイト、設計思想、文書体系、運用知識を保持するRepository Contextです。

ChatGPT、Codex、人間が同じ前提で協働するため、設計判断や文化的記録はチャット履歴だけに置かず、Markdown文書としてRepository内に保存します。

## Current Workflow

標準運用フローは次のとおりです。

```text
ChatGPT / Codex
↓
GitHub repository
↓
GitHub Actions
↓
Public site: genai-ron.jp
```

Notionは内部ノート、研究原本、素材整理の場所として扱います。GitHubはWeb公開用ファイルの正本、履歴管理、自動公開の起点として扱います。

FTPで直接アップロードする運用は標準経路ではありません。

## Repository Structure

```text
/
  README.md
  CODEX.md
  CHAT_HISTORY.md
  AFTERHOURS.md
  site/
    index.html
    article/
    essay/
    notes/
    series/
      genai-shikumi/
      genai-shikumi-technical/
      genai-shikumi-deep-dive/
    assets/
    downloads/
    sitemap.xml
    robots.txt
  .github/
    workflows/
      deploy.yml
```

## Documents

主要文書の役割は次のとおりです。存在しない文書は、今後整備予定として扱います。

| Document | Status | Role |
| --- | --- | --- |
| `README.md` | Active | Repositoryの入口。現在の運用と文書案内。 |
| `CODEX.md` | Active | Engineering Charter。Codexを含む実装者の文化、価値観、行動規範。 |
| `CHAT_HISTORY.md` | Active | 設計判断の履歴。会話ログではなくArchitecture Decision History。 |
| `AFTERHOURS.md` | Active | 作業後の余韻、未整理の気付き、文化的記録。 |
| `CHANGELOG.md` | Planned | Repositoryおよび公開サイトの主要変更履歴。 |
| `PROJECT.md` | Planned | 現在位置、ロードマップ、優先順位。 |
| `DESIGN.md` | Planned | デザイン思想。 |
| `STYLEGUIDE.md` | Planned | 文体、UI、HTML、CSS、命名規則。 |
| `ARCHITECTURE.md` | Planned | ディレクトリ構造、共通部品、サイト構造。 |
| `CONTENT_POLICY.md` | Planned | 公開方針、著者表記、コンテンツ判断。 |
| `EXPERIMENTS.md` | Planned | 仮説、検証、観察、考察。 |

サイトやコンテンツの変更履歴は、将来的に `CHANGELOG.md` へ分離します。README.md には、サイト更新履歴ではなく、README自身の責務変更や主要文書追加の履歴だけを残します。

## Deployment

`.github/workflows/deploy.yml` により、`main` ブランチへのpush時に `site/` 以下を公開サーバへFTPSアップロードします。

GitHub Actionsでは、次のRepository Secretsを使用します。

```text
FTP_SERVER
FTP_USERNAME
FTP_PASSWORD
SERVER_DIR
```

秘密情報はREADME、チャット本文、リポジトリ内ファイルには記載しません。

## Maintenance Notes

作業開始前には、目的に応じてRepository内の文書を読んでください。Codexが作業する場合は、まず `CODEX.md` を確認します。

通常作業では、最新 `main` をpullし、未コミット変更がないことを確認してから編集します。未コミット変更がある場合は作業を停止して報告します。

通常の commit / push を使用します。force push は使用しません。

公開対象は `site/` 以下です。トップページ、一覧ページ、ナビゲーション、sitemap、PDFや画像などの公開ファイルも必要に応じて整合させます。

公開に向かない内部事情、未確定情報、個人情報、秘密情報はRepositoryへ入れません。

## README History

- 2026-07-20 12:12 JST: Repository Structure に `series/genai-shikumi-deep-dive/` を明記。生成AIのしくみ超詳解シリーズ公開に合わせてREADMEの現行構成を更新。
- 2026-07-03 12:04 JST: README.md をRepository Contextへの入口として再定義。古いzip原本管理の記述を現在のGitHub中心運用へ整理し、サイト更新履歴をREADMEの責務から外した。
- 2026-06-02 17:07 JST: GitHub Actionsによる公開運用前提のREADMEへ更新。