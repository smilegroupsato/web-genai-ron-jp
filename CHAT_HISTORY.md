# CHAT_HISTORY.md

Version: 1.0

Created: 2026-07-02 14:12 JST

Last Updated: 2026-07-04 15:40 JST

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

## Decision 009: Repository ContextをStarter Kitへ抽象化する

Repository Context は、Webサイト保守のためだけの運用パターンではなくなった。

本プロジェクトで育った方法は、公開サイト、業務システム、社内運用、研究サイト、データ処理システム、そして ChatGPT、Codex、Claude、Gemini など複数のAIエージェントを用いる将来のプロジェクトにも応用しうる。

そのため、かつて仮称として置かれていた `web-project-template` は範囲が狭い。今後の抽象化の方向は、Repository Context Method、Repository Context Starter Kit、そして `repository-context-template` とする。

この変更は、Decision 007 を消すものではない。当時は `web-project-template` として発想されたが、その後の議論によって、より広い方法論へ拡張されたという履歴を残す。

## Decision 010: AGENTS.mdを実務入口、README.mdを入口、CHARTER.mdを思想参照先として整理する

`CODEX.md` は、web-genai-ron-jp において Engineering Charter として意味を持つ。しかし、将来の汎用テンプレートにおける標準ファイル名としては Codex 固有に寄りすぎている。

汎用的な Repository Context では、`README.md` を人間とAIの入口、`AGENTS.md` を実務上のAIエージェント指示入口として扱う。特にCodex向けには、OpenAI の AGENTS.md guidance に従う。

`CLAUDE.md` のようなエージェント固有のアダプタは、各ツールの公式仕様に従い、可能な場合は `AGENTS.md` を参照または取り込む形にする。

長い文化的・哲学的・協働原則は、`CHARTER.md` に置く。小さなプロジェクトでも、Repository Context の短い思想文は `README.md` または `AGENTS.md` の上部に置く。

Charter は、coding agent の職業倫理だけではない。チャット履歴だけに依存せず、人間と生成AIが長期協働するために、Repository Context をどう設計し、保存し、引き継ぐかという文化と方法論を含む。

## Decision 011: CHAT_HISTORY.md / decision-logの保守ルーチンを定義する

`CHAT_HISTORY.md` は raw chat log ではない。

これは、設計判断、Resolution、Open Question、文書責務変更、方法論の変化を記録する decision-log である。

今後、次のような場合は `CHAT_HISTORY.md` または対応する decision-log の更新対象とする。

- プロジェクトの方向性が変わった。
- 文書の責務が変わった。
- 新しい Open Question が生まれた。
- Open Question が Resolution によって処理された。
- AI / Human / agent workflow が変わった。
- 公式の agent 仕様が文書戦略を変えた。
- template-level methodology が変わった。
- 主要なRepository文書が追加または再定義された。

すべてのタスクの最後に、Repository Context impact check を行う。影響がある場合、対象文書を更新するか、少なくとも更新が推奨されることを報告する。

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
- web-genai-ron-jp に AGENTS.md を CODEX.md と並行して導入するか
- CODEX.md を将来的に CHARTER.md へ改名するか、または CHARTER.md で補完するか
- Repository Context impact check を prompt、PR template、CI warning のどれで担保するか
- とても小さなプロジェクトにおける最小限の文書セットは何か
- Claude、Gemini、Cursor、Windsurf、Devin、将来のAIエージェント向けアダプタをどう構成するか

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

## Resolution 002: web-project-templateをrepository-context-templateへ再定義する

Status:
Adopted

Addressed question:
テンプレートリポジトリの名称を `web-project-template` とするか。

Outcome:
`web-project-template` は、Repository Context Starter Kit / Repository Context Method の広がりを表すには狭い名称であると判断した。

今後の抽象化では、`repository-context-template` を有力な名称とし、Webサイトに限らず、業務システム、研究サイト、社内運用、データ処理、複数AIエージェントを使う将来プロジェクトへ展開可能な方法として扱う。

この Resolution は、Decision 007 の履歴を消さない。当時は `web-project-template` として構想され、その後、より広いRepository Context Methodへ拡張された。

## Resolution 003: CODEX.mdを汎用標準名ではなくプロジェクト固有憲章として位置付ける

Status:
Adopted

Addressed question:
各サイト共通文書の最終セットをどこまで固定するか。

Outcome:
`CODEX.md` は web-genai-ron-jp の Engineering Charter として維持する。ただし、汎用テンプレートにおける標準入口ファイル名にはしない。

汎用的なRepository Contextでは、`README.md` を入口、`AGENTS.md` を実務的なAI-agent instruction、`CHARTER.md` を長い文化的・哲学的原則の置き場として扱う方向へ整理した。

Claude Code などのエージェント固有ファイルは、それぞれの公式仕様に従う adapter として扱い、可能な範囲で `AGENTS.md` を参照する。

## Resolution 004: CHAT_HISTORY.mdの更新粒度をdecision-log triggerとして定義する

Status:
Adopted

Addressed question:
CHAT_HISTORY.md の更新粒度を、日単位、判断単位、リリース単位のどれに寄せるか。

Outcome:
`CHAT_HISTORY.md` は、すべてのチャットやすべてのcommitを記録する文書ではない。

更新粒度は、Decision、Resolution、Open Question、文書責務変更、agent workflow変更、template-level methodology変更などの decision-log trigger に寄せる。

日単位の感想や余韻は AFTERHOURS.md、変更履歴は CHANGELOG.md、仮説と観察は EXPERIMENTS.md に分担する。
