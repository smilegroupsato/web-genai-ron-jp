# CHANGELOG.md

Public Site and Repository Change History

Version: 0.1

Status: Draft

Created: 2026-07-03 13:11 JST

Last Updated: 2026-07-03 13:11 JST

Repository: web-genai-ron-jp

Project: GENAI-RON（生成AI論）

---

## Purpose

CHANGELOG.md は、公開サイトおよびRepositoryにおける主要な変更を記録するための文書である。

本書は、すべてのcommitを列挙するための作業ログではない。

本書は、README.md に置かれていたサイト更新履歴を分離し、公開サイト・Repository構成・運用上の重要な変更を時系列で記録する場所である。

---

## Principles

CHANGELOG.md には、次のような変更を記録する。

- 公開サイトに新しいページやエッセイを追加した。
- 公開サイトの表示、テーマ、導線、構造を変更した。
- Repositoryの主要文書を追加または大きく整理した。
- 公開・保守の運用フローを変更した。
- GitHub Actions、デプロイ、共通CSS、共通JavaScriptなど、サイト全体に影響する仕組みを変更した。

CHANGELOG.md には、次のものを原則として記録しない。

- 細かい誤字修正。
- 個別作業の全commit。
- 設計判断の詳細な理由。
- 作業後の感想や会話の余韻。
- 未検証の仮説。

---

## Format

変更履歴は、新しいものを上に並べる。

各日付の下では、必要に応じて次の分類を使う。

- Added
- Changed
- Fixed
- Removed
- Notes

厳密なリリース番号よりも、日付と意味の分かりやすさを優先する。

---

# Changes

---

## 2026-07-03 — Repository Context Foundation

### Added

- CODEX.md を追加。Engineering Charter Version 1.0 として、AI協働開発における価値観、役割、作業手順、Git運用、報告様式を定義した。
- AFTERHOURS.md を追加。作業後の余韻、未整理の気付き、文化的記録を残す場所として定義した。
- EXPERIMENTS.md を追加。Repository Context に関する仮説・観察・検証を記録する研究ノートとして定義した。

### Changed

- README.md をRepositoryの入口として再定義した。
- README.md から古いzip原本管理の記述を整理し、現在の原本はGitHub repositoryであることを明記した。
- README.md からサイト更新履歴を外し、今後はCHANGELOG.mdへ分離する方針とした。

### Notes

この日は、Engineering Charter Version 1.0 の制定日であり、Repository Context を実運用へ移した日である。

この日以降、Codex作業はCODEX.mdを参照し、Repository内の文書群をRepository Contextとして扱う。

関連commit：

- CODEX.md: 24b77cf94ec52cd46f4ba46f4a84edd885f161d8
- AFTERHOURS.md: 2ea34e6deb7497fc9483b3f8b3ca974646c030c3
- README.md: deabc6f39b82e4145c1f376addc3181bbfd0eb73
- EXPERIMENTS.md: d1b2d458422c1c9de227203502b30cfe3a58eb50

---

## 2026-07-02 — Draft Day

### Added

- CHAT_HISTORY.md を追加。設計判断の履歴を記録する文書として整備を開始した。

### Changed

- Webサイト保守における標準運用を、ChatGPTでzipを作成してDriveへ保存する方式から、GitHub repositoryを原本とする方式へ移行する方針に整理した。
- ChatGPT、Codex、GitHub、GitHub Actions、公開サイトの役割分担を整理した。
- Repositoryを、単なるコード置き場ではなく、AIと人間が長期協働するための外部知識基盤として捉える Repository Context の考え方を明確化した。

### Fixed

- Appearance Theme のサイト全体への適用範囲を整理した。
- ArticleページにおけるAppearance Themeの表示面を修正した。
- エッセイ「AIしか使わない世代は現れるか」のAppearance Theme関連の不足を修正した。
- エッセイ一覧から「AIしか使わない世代は現れるか」への導線を修正した。

### Notes

この日は、CODEX.md制定前の起草日である。

後に AFTERHOURS.md Entry 001 では、この日を Draft Day として記録した。

関連commit：

- CHAT_HISTORY.md: 9b097f8138dc33c8516f6c52c0a5023996740888
- Sitewide appearance theme coverage: d386c47
- Article appearance theme surfaces: 1399c5b46bbdcc6e5c6be14cfa763cf12b774116
- AI-only essay appearance assets: 6afacb0
- Essay index title link: 2b24ff83a71193059b8faa72c35b6ed4aaa2cbc6

---

## Earlier History — Before Repository-Centered Operation

### Notes

このRepository以前、公開サイト管理は主に次のような流れで行われていた。

ChatGPTで公開用zipパッケージを作成し、Google Driveに原本として保存し、そこから公開作業へ進む。

この運用は、初期段階では有効だった。

しかし、現在の標準運用では、GitHub repositoryが原本であり、公開・保守はGitHubを中心に行う。

過去のzipファイルは歴史的な参照物であり、現在の公開候補最新版ではない。

---

## Notes

CHANGELOG.md は、Repositoryの変化を後から追えるようにするための文書である。

ただし、本書は歴史を美化するための文書ではない。

変更がうまくいかなかった場合も、必要に応じて記録する。

Repository remembers.
