# CHAT_HISTORY.md

Version: 1.0

Created: 2026-07-02 14:12 JST

Last Updated: 2026-07-03 15:38 JST

Repository:
web-genai-ron-jp

Project:
GENAI-RON（生成AI論）

Status:
Active

Purpose:
ChatGPT・Codex・人間が共有する設計判断の記録。
会話ログではなく、設計思想・判断理由・背景を保存する。

## Prologue

2026-07-02 は、本プロジェクト「生成AI論」が一つの転換点を迎えた日である。

この文書は、生成AIについて研究した結果だけから生まれたものではない。生成AIと共同で設計し、実装し、保守した結果として生まれたものである。

ChatGPT のチャット履歴は、永続的な知識ベースではない。Codex もまた、過去チャットを自由に読むことはできない。そのため、設計思想や判断理由を、AI が読める形でリポジトリへ保存する必要がある。

生成AI論は、生成AIについて研究するプロジェクトであると同時に、生成AIと協働する方法論を研究するプロジェクトへ発展した。CHAT_HISTORY.md は、その最初の方法論的成果である。

これはチャット履歴ではなく、設計判断を保存する文書である。ADR（Architecture Decision Record）の思想を、ChatGPT と Codex の協働開発へ応用する。

AI に内部記憶を増やすだけではなく、AI が読める形で世界を設計し、保存し、引き継ぐことが重要である。

ChatGPT は思考する。
Codex は実装する。
リポジトリは記憶する。

## Decision 001: Appearance Theme を全サイト共通仕様とする

Paper / Reading / Archive を、genai-ron.jp の標準テーマとする。

- Paper: 大学出版局・学術誌風の明るい紙面
- Reading: 夜の研究室のような暗色背景
- Archive: 古い紙・図書館資料のようなアーカイブ色

この切替は一部ページの装飾ではなく、サイト全体で共有される基本機能として扱う。

## Decision 002: 共通修正は theme.css へ集約する

Appearance Theme に関する共通修正は、原則として `site/assets/theme.css` へ集約する。

個別ページや個別 CSS に同じ処理を重複して書くのではなく、共通部品としてテーマ差分を管理する。ページ固有 CSS は、そのページ固有の構造や表現に集中させる。

## Decision 003: ChatGPT と Codex の役割を分離する

ChatGPT と Codex は、同じ目的に向かうが、役割を分けて扱う。

ChatGPT:
設計、UI、デザイン、文章、レビュー、実装指示を担当する。

Codex:
GitHub 編集、HTML/CSS/JavaScript 修正、リファクタリング、commit、push、確認を担当する。

この分離により、人間は設計判断と実装結果を往復しやすくなり、AI 間の役割も明確になる。

## Decision 004: GitHub Desktop を標準経路から外す

GitHub Desktop は通常運用の標準経路から外す。

通常運用は、次の流れとする。

ChatGPT → Codex → GitHub → GitHub Actions → 公開確認

これにより、編集、差分確認、commit、push、公開反映までの経路を明確にし、AI と人間が同じ前提で作業しやすくする。

## Decision 005: リポジトリを知識ベースとする

チャット履歴に依存せず、Markdown 文書として設計思想を外部化する。

リポジトリはソースコードだけでなく、設計判断、背景、運用方針を保存する場所として扱う。AI が次回以降に読むべき情報は、チャットの中ではなく、リポジトリ内の文書として残す。

## Decision 006: 標準文書群を整備する

genai-ron.jp では、少なくとも次の文書群を整備する。

- README.md
- PROJECT.md
- DESIGN.md
- STYLEGUIDE.md
- ARCHITECTURE.md
- CONTENT_POLICY.md
- CODEX.md
- CHAT_HISTORY.md
- CHANGELOG.md

これらは、サイト制作、思想、運用、AI 協働の知識を分散させず、読み継げる形で保存するための標準セットである。

## Decision 007: テンプレートリポジトリを作る

将来的に `web-project-template`（仮称）を作成する。

genai-ron.jp で成熟させた文書群、運用方針、AI 協働の流れを、他サイトでも再利用できる汎用テンプレートとして抽出する。

## Decision 008: CHAT_HISTORY.md は ADR に近い役割を持つ

CHAT_HISTORY.md は、会話保存ではなく、設計判断保存のための文書である。

ADR（Architecture Decision Record）に近い役割を持つが、対象はソフトウェア構造だけではない。ChatGPT、Codex、人間の協働方法、サイト運用、文書体系、公開プロセスも含めて記録する。

この文書は、追記・更新を原則とする。過去の Decision を書き換えて歴史を改変しない。設計変更は、新しい Decision として追加する。過去の判断が未熟だった場合でも、「当時そう判断した」という事実を残す。

## Open Questions

現時点で未確定の事項を、次に整理する。

- `CHAT_HISTORY.md` という名称を継続するか
- 将来的に `DECISIONS.md` / `DECISION_HISTORY.md` / `DESIGN_HISTORY.md` へ改名するか
- ADR 形式へ完全移行するか
- PROJECT.md の詳細構成をどうするか
- テンプレートリポジトリの名称を `web-project-template` とするか
- 各サイト共通文書の最終セットをどこまで固定するか
- GitHub Desktop を完全に使わないか、限定用途に残すか
- CHAT_HISTORY.md の更新粒度を、日単位、判断単位、リリース単位のどれに寄せるか
- Decision の採番、日付、状態管理をどの程度厳密にするか

## Future Directions

今後の予定を、次に整理する。

- CODEX.md 初版作成
- PROJECT.md 初版作成
- DESIGN.md / STYLEGUIDE.md / ARCHITECTURE.md 整備
- CONTENT_POLICY.md / CHANGELOG.md の位置づけ整理
- genai-ron.jp で文書群を成熟させる
- その後、汎用部分を `web-project-template` へ抽出する
- math-intuition.jp / yakushoron.jp へ横展開する
- ChatGPT、Codex、人間の協働手順を、他リポジトリでも再利用できる形へ整理する

## Resolution 001: PROJECT.md の位置づけと詳細構成を定義する

Status:
Adopted

Addressed question:
PROJECT.md の詳細構成をどうするか。

Outcome:
PROJECT.md を追加し、GENAI-RON全体の方向性、Project Stance、Project Layers、Current Focus、Roadmapを定義した。

PROJECT.md は、Repository Context の運用文書ではなく、GENAI-RON / 生成AI論プロジェクト全体の方向性、思想、現在の焦点、ロードマップを示す文書として定義した。

Repository Context は、GENAI-RON の主題そのものではなく、重要な実践的研究対象として PROJECT.md 内に位置付けた。

README.md、CODEX.md、CHANGELOG.md、EXPERIMENTS.md、AFTERHOURS.md などと内容が重複しすぎないように、PROJECT.md には文書運用の詳細や作業ログを置かない方針とした。

Open Questions や Backlog を新規の独立文書として増やすのではなく、現時点では問いの種類に応じて、CHAT_HISTORY.md、EXPERIMENTS.md、PROJECT.md などへ分担させる方針とした。

「生成AIのしくみ」シリーズは、研究成果そのものではなく、主に人間の理解を助ける学習・解説コンテンツとして位置付けた。

AI との対話が人間にも状態変化をもたらしうるという立場、AI 協働成果物の著者性・主体性に関する基本姿勢を、PROJECT.md に短く記載した。

この Resolution は、Open Questions にあった問いを消すものではない。当時の問いは履歴として残し、その後の処理として PROJECT.md の初版作成を記録する。
