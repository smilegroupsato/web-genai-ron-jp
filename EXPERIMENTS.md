# EXPERIMENTS.md

Research Log for Repository Context

Version: 0.1

Status: Draft

Created: 2026-07-03 12:47 JST

Last Updated: 2026-07-04 15:40 JST

Repository: web-genai-ron-jp

Project: GENAI-RON（生成AI論）

---

## Purpose

EXPERIMENTS.md は、このRepositoryにおける実験・仮説・観察・検証を記録するための研究ノートである。

本書は、作業ログではない。

本書は、単なる更新履歴でもない。

本書は、AIと人間の協働開発において、

- 何を仮説とし、
- 何を試し、
- 何が起き、
- 何が分かり、
- 何がまだ分からないのか

を記録する場所である。

---

## Position of this document

このRepositoryには、複数の文書がある。

それぞれの責務は異なる。

- README.md  
  Repositoryの入口。

- CODEX.md  
  Engineering Charter。AIと人間がどう振る舞うか。

- CHAT_HISTORY.md  
  設計判断の履歴。なぜそう判断したか。

- AFTERHOURS.md  
  作業後の余韻、未整理の気付き、文化的記録。

- CHANGELOG.md  
  公開サイトおよびRepositoryの主要変更履歴。

- EXPERIMENTS.md  
  仮説、検証、観察、考察。

本書は、判断そのものを書く場所ではない。

判断が正しかったか、どのような効果を持ったかを観察する場所である。

---

## Core Research Question

このRepositoryにおける中心的な研究問いは、次の通りである。

> AIの内部記憶ではなく、Repository Contextによって、長期的なAI協働開発は成立するか。

ここでいう Repository Context とは、コードだけでなく、README、CODEX、CHAT_HISTORY、AFTERHOURS、CHANGELOG、PROJECT、DESIGN、STYLEGUIDE などの文書群を含む、Repository内に蓄積された外部知識基盤を指す。

---

## Working Hypothesis

現時点での仮説は次の通りである。

AIの長期的な協働能力は、AI内部の記憶だけに依存しなくてもよい。

むしろ、Repository内に設計思想、判断履歴、憲章、作業文化、変更履歴を蓄積することで、AIと人間の協働は安定しうる。

このときRepositoryは、単なるコード置き場ではなく、AI協働開発の外部記憶として機能する。

---

## Experiment Principles

本書で扱う実験は、厳密な自然科学実験ではない。

しかし、単なる感想でもない。

次の原則を守る。

1. 仮説を明示する。
2. 観察対象を明示する。
3. 実施前の状態を記録する。
4. 実施後の変化を記録する。
5. 成功だけでなく失敗も記録する。
6. 主観的な印象と観察可能な事実を区別する。
7. 後から都合よく歴史を書き換えない。

---

## Observation Points

Repository Context の効果を観察するために、次のような点を見る。

### 1. Instruction Following

Codex が指示をどの程度正確に実行するか。

観察例：

- 作業前に CODEX.md を読むか。
- 最新 main を pull するか。
- clean working tree を確認するか。
- force push を避けるか。
- 指定されたファイルのみを編集するか。
- 完了報告に必要項目を含めるか。

### 2. Scope Control

Codex が作業範囲を勝手に広げないか。

観察例：

- README修正依頼で他ファイルを不必要に変更しないか。
- 設計変更を独断で行わないか。
- 存在しない文書を存在するものとして書かないか。

### 3. Design Consistency

Codex がRepository全体の設計思想に沿って作業するか。

観察例：

- READMEを入口文書として扱えるか。
- CHANGELOGとの責務分離を理解できるか。
- CODEX.mdの価値観に沿った報告をするか。

### 4. Maintenance Quality

修正が長期的に保守しやすいか。

観察例：

- 重複した記述を増やさないか。
- 古い運用と現在の運用を整理できるか。
- 文書間の責務を明確にできるか。

### 5. Human Load

Human と ChatGPT の負担が減るか。

観察例：

- 指示の手戻りが減るか。
- 確認質問が減るか。
- 修正依頼の粒度が粗くても作業できるか。
- 完了報告からレビューしやすいか。

---

# Experiments

---

## Experiment 000 — Repository Context

Status: Active

Started: 2026-07-02

### Question

Repositoryは、AIと人間の長期協働における外部記憶として機能するか。

### Background

当初、このRepositoryは公開サイト `genai-ron.jp` のHTML、CSS、JavaScriptを管理するための場所だった。

しかし運用の中で、Repositoryは単なるコード置き場ではなくなった。

README.md は入口となり、CHAT_HISTORY.md は設計判断の履歴となり、CODEX.md はEngineering Charterとなり、AFTERHOURS.md は文化的記録となった。

この変化により、Repositoryはコードだけでなく、設計思想、判断履歴、運用文化を保持する場所になった。

### Hypothesis

Repository内に十分な文書群を整備すれば、AIは過去のチャット文脈に依存しなくても、現在のRepository Contextを読んで、設計思想に沿った作業ができるようになる。

### Method

Repositoryに次の文書群を段階的に整備する。

- README.md
- CODEX.md
- CHAT_HISTORY.md
- AFTERHOURS.md
- CHANGELOG.md
- PROJECT.md
- DESIGN.md
- STYLEGUIDE.md
- ARCHITECTURE.md
- EXPERIMENTS.md

すべてを一度に整備するのではなく、実際の必要に応じて段階的に作成する。

各作業で、Codexがどの文書を読み、どのように判断し、どのように報告するかを観察する。

### Current Observations

2026-07-03時点で、次の文書が作成または整理された。

- CHAT_HISTORY.md
- CODEX.md
- AFTERHOURS.md
- README.md
- CHANGELOG.md
- EXPERIMENTS.md
- PROJECT.md

CODEX.md制定後、CodexはAFTERHOURS.md追加作業において、CODEX.mdを読んだことを報告した。

また、README.md整理作業においても、CODEX.mdを読んだうえで、古いzip運用の記述とサイト更新履歴の責務を整理した。

これは、CODEX.mdが少なくとも作業手順と報告様式に影響を与えた可能性を示している。

PROJECT.md作成後、CHAT_HISTORY.mdにあったPROJECT.mdの詳細構成に関する未解決の問いが、Resolutionとして処理された。

既存のOpen Questionを削除せず、後続のResolutionとして閉じる運用が試された。

これにより、Repository Context内の問いが放置されるのではなく、後続の文書作成や設計判断によって処理される可能性が観察された。

この運用は、今後のQuestion Closure Ruleの候補となる。

2026-07-04の議論で、Repository Context は、Webサイト保守パターンから、Repository Context Starter Kit / Repository Context Method へ抽象化され始めた。

これは、Repository Context が公開サイトだけでなく、業務システム、研究サイト、社内運用、データ処理、複数AIエージェントを含む将来プロジェクトにも適用される可能性を示している。

### Open Questions

- Codexは、明示的に「CODEX.mdを読め」と言われなくても読むようになるか。
- Repository Contextは、新しいチャット、新しいCodexセッション、新しい作業者にも引き継がれるか。
- 文書が増えたとき、どの文書を優先して読むべきか。
- Repository Contextが過剰になった場合、かえって混乱を生まないか。
- README.mdはどこまで簡潔であるべきか。
- Resolutionによって閉じられたOpen Questionを、どのように追跡・確認するべきか。

### Notes

このExperiment 000は、個別の作業結果ではなく、Repository Contextという考え方そのものを観察する基礎実験である。

---

## Experiment 001 — Engineering Charter Effect

Status: Active

Started: 2026-07-03

### Question

CODEX.md は、Codexの作業行動を変えるか。

### Background

2026-07-03 11:19 JST、CODEX.md が制定された。

CODEX.md は、単なる作業指示ではなく、Engineering Charterとして作成された。

そこには、Codexの役割、価値観、作業手順、Git運用、報告様式が記載されている。

### Hypothesis

CODEX.mdをRepository内に置くことで、Codexは個別プロンプトだけでなく、Repository内の憲章を参照して作業するようになる。

その結果、作業の一貫性、範囲管理、報告品質が向上する。

### Method

CODEX.md制定後に行われるCodex作業について、次の点を観察する。

- CODEX.mdを読むか。
- CODEX.mdの手順に従うか。
- force pushを避けるか。
- clean working treeを確認するか。
- 作業範囲を守るか。
- 完了報告が定型化されるか。
- 設計変更を独断で行わないか。

### Initial Observations

CODEX.md制定後、次の作業が行われた。

1. AFTERHOURS.md追加
2. README.md責務整理

いずれの作業でも、CodexはCODEX.mdを読んだことを報告した。

また、最新mainのpull、clean working tree確認、force push未使用、commit ID、push完了を報告した。

これは、CODEX.mdがCodex作業の儀式的・手続き的枠組みとして機能し始めたことを示す。

PROJECT.md追加作業において、CodexはPROJECT.mdを追加し、CHAT_HISTORY.mdへResolutionを追記した。

同時に、指示された範囲を守り、CHANGELOG.mdは変更しなかった。

これは、CODEX.mdの「作業範囲を勝手に広げない」「設計変更を独断で行わない」という方針に沿った挙動である。

一方で、CHANGELOG.mdへの追記が必要になりうる主要変更であることを、自律的に提案するところまでは行かなかった。

この観察は、CodexがScope Controlには成功したが、Cross-document Maintenanceの自律性にはまだ課題があることを示す可能性がある。

2026-07-04の議論では、CODEX.md はこのRepositoryでは有効に機能したが、汎用テンプレートでは AGENTS.md と README.md、必要に応じて CHARTER.md を組み合わせる方がよい可能性が観察された。

また、Cross-document Maintenance は暗黙の期待ではなく、明示的な実験対象として扱う必要があることが確認された。

### Evaluation Criteria

成功の兆候：

- Codexが作業開始前にRepository文書を読む。
- 作業範囲を守る。
- 完了報告が安定する。
- 不要な設計変更をしない。
- 既存文書の責務を尊重する。
- Human / ChatGPT のレビュー負担が減る。

失敗の兆候：

- CODEX.mdを読まない。
- 指示されていないファイルを変更する。
- READMEにサイト更新履歴を書き続ける。
- CHANGELOGやCHAT_HISTORYとの責務を混同する。
- 報告が不十分になる。
- Repository Contextが読まれず、個別プロンプトだけで作業される。

### Open Questions

- Codexは、毎回明示的にCODEX.mdを読む必要があるか。
- CODEX.mdは長すぎないか。
- CODEX.mdに具体的手順を書きすぎると、憲章ではなくマニュアルにならないか。
- Engineering Charterは、PROJECT.mdやSTYLEGUIDE.mdとどう役割分担すべきか。
- Version 1.1では何を追加し、何を削るべきか。
- 主要文書を追加・変更した場合、CodexはCHANGELOG.md更新の必要性を自律的に提案できるか。
- 作業範囲を守ることと、関連文書更新を提案することは、どのように両立できるか。

---

## Experiment 002 — README as Repository Entry Point

Status: Draft

Started: 2026-07-03

### Question

README.md は、Repository Contextへの入口として機能するか。

### Background

以前のREADME.mdには、古いzip原本管理やサイト更新履歴が含まれていた。

しかし、Repository運用がGitHub中心へ移行したことで、README.mdの責務は変わった。

README.mdは、作業ログではなく、Repositoryの入口として再定義された。

### Hypothesis

README.mdを簡潔な入口文書として整理することで、Human、ChatGPT、Codexはいずれも、Repository全体の構造と文書群の役割を把握しやすくなる。

### Method

README.mdから、次のものを整理する。

- 古いzip最新版の記述
- サイト更新履歴
- READMEの責務外の詳細情報

そのうえで、README.mdには次の情報を残す。

- Repository概要
- 公開サイト概要
- 現在の運用フロー
- 主要文書への案内
- 作業開始前の読み順

### Initial Observations

2026-07-03、README.mdはRepositoryの入口として再定義された。

古いzip最新版の記述は整理され、現在の原本はGitHub repositoryであることが明記された。

サイト更新履歴はREADMEから外され、将来的にCHANGELOG.mdへ分離する方針となった。

### Open Questions

- README.mdはどの程度までRepository思想を説明すべきか。
- README.mdからPROJECT.mdへの導線は必要か。
- README.mdが長くなりすぎた場合、どこで切り分けるべきか。
- AIに読ませるREADMEと、人間に読ませるREADMEは同一でよいか。

---

## Experiment 003 — CHAT_HISTORY Auto-Maintenance Trigger

Status: Active

Started: 2026-07-04

### Question

Repository Context は、人間が毎回思い出さなくても、CHAT_HISTORY.md / decision-log の更新必要性を検出し、保守できるか。

### Background

2026-07-04の議論で、CHAT_HISTORY.md が July 4 の Repository Context Starter Kit、multi-agent document structure、Charter positioning、decision-log maintenance automation の議論をまだ反映していないことが分かった。

これは、Repository Context が有効に働き始めている一方で、decision-log 自体の保守ルーチンが未定義であることを示している。

### Hypothesis

AGENTS.md / CODEX.md の完了プロトコルに Repository Context impact check を含め、さらに PR / CI warning によって主要文書変更と decision-log / CHANGELOG / EXPERIMENTS 更新の不一致を検出できれば、CHAT_HISTORY.md / decision-log の陳腐化は減る。

ただし、最初は failure ではなく warning として扱うべきである。

### Method

1. CODEX.md に completion-report requirement と Repository Context impact check を追加する。
2. CHAT_HISTORY.md に July 4 の Decision / Resolution / Open Question を追記する。
3. Codex に、主要な文書作業の完了時に CHAT_HISTORY.md、EXPERIMENTS.md、CHANGELOG.md、PROJECT.md の更新要否を報告させる。
4. 将来的には、README.md、AGENTS.md、PROJECT.md、CHARTER.md、CODEX.md、docs/、主要Repository Context文書が変更されたとき、CHAT_HISTORY.md / decision-log / CHANGELOG.md / EXPERIMENTS.md の更新がない場合に warning を出す script または CI を検討する。
5. その検出は、まず warning-only とし、commit failure にはしない。

### Observation Points

- Codex は Repository Context impact を識別できるか。
- Codex は正しい文書を更新できるか。
- Codex は不要なファイル変更を避けられるか。
- Codex は Decision、Experiment、Changelog の責務を区別できるか。
- Human のレビュー負担は減るか、増えるか。

### Initial Observations

この実験は、CHAT_HISTORY.md がすでに July 4 の議論に対して遅れ始めていたという観察から始まった。

今回の更新では、CHAT_HISTORY.md、EXPERIMENTS.md、CHANGELOG.md、CODEX.md を明示的に対象化し、Repository Context impact check そのものを記録対象にした。

### Open Questions

- Repository Context impact check は、prompt、PR template、CI warning のどこに置くのが最も自然か。
- warning-only のまま十分に機能するか。
- 自動検出が過剰になると、Human / ChatGPT / Codex の負担を増やさないか。
- 小規模プロジェクトでも同じ仕組みが必要か。

### Notes

このExperiment 003は、CHAT_HISTORY.mdを完全自動更新することを直ちに目指すものではない。

まずは、人間が忘れがちなRepository Context影響確認を、Codexの完了プロトコルに組み込めるかを観察する。

---

## Future Experiments

今後、次のような実験を行う可能性がある。

### Experiment — PROJECT.md as Roadmap

PROJECT.mdを整備することで、Codexが現在の優先順位とロードマップを理解できるか。

### Experiment — CHANGELOG.md as Public History

CHANGELOG.mdを作成することで、公開サイトの変更履歴とRepository文書の変更履歴を適切に分離できるか。

### Experiment — STYLEGUIDE.md as Design Consistency Layer

STYLEGUIDE.mdを整備することで、HTML、CSS、UI、文章表現の一貫性が保たれるか。

### Experiment — New Chat Transfer

新しいChatGPTチャットでRepository文書だけを参照した場合、どの程度まで文脈を復元できるか。

### Experiment — New Codex Session Transfer

新しいCodexセッションでREADME.mdとCODEX.mdを読ませた場合、どの程度まで設計思想に沿った作業ができるか。

### Experiment — Repository Context Overload

文書が増えすぎた場合、AIが読むべき文書を選べなくなるか。

---

## Log Format

今後、新しい実験を追加する場合は、原則として次の形式を使う。

---

## Experiment XXX — Title

Status: Draft / Active / Paused / Completed

Started: YYYY-MM-DD

Ended: YYYY-MM-DD

### Question

何を問う実験か。

### Background

なぜこの実験が必要か。

### Hypothesis

どのような結果を予想しているか。

### Method

何をどのように試すか。

### Observations

実際に何が起きたか。

### Evaluation

仮説は支持されたか。

### Open Questions

何がまだ分からないか。

### Notes

その他の補足。

---

## Notes

EXPERIMENTS.md は、正しさを急がない。

ここに書かれることは、途中経過でよい。

失敗も記録する。

違和感も記録する。

仮説が間違っていた場合は、修正する。

重要なのは、あとから都合よく成功物語にしないことである。

Repository remembers.
