# PROJECT.md

Project Direction and Roadmap

Version: 0.1

Status: Draft

Created: 2026-07-03 15:38 JST

Last Updated: 2026-07-03 15:38 JST

Repository: web-genai-ron-jp

Project: GENAI-RON（生成AI論）

---

## Purpose

PROJECT.md は、GENAI-RON（生成AI論）というプロジェクト全体の方向性、思想、現在の焦点、ロードマップを示す文書である。

本書は、Repositoryの操作手順を書く場所ではない。

本書は、変更履歴を書く場所ではない。

本書は、未解決の問いを列挙し続ける場所でもない。

本書の目的は、公開サイト `genai-ron.jp` と、その背後にある思考・制作・研究・運用が、何を目指しているのかを見失わないようにすることである。

---

## Audience and Use

本書は、Codexや他のAIエージェントだけに向けられた文書ではない。

本書は、Human、ChatGPT、Codex、そして将来このRepositoryに関わる可能性のある人間・AIが、プロジェクト全体の方向性を共有するための文書である。

Thought Layer や Content Layer は、主に Human と ChatGPT の対話によって育つ。

Public Site Layer や Repository Context Layer は、主に Codex が実装・保守に関わる。

ただし、各担当領域は完全に分離されるものではない。

Codex も、自分が直接担当しない思考・文章・研究の方向性を知っておくことで、公開サイトやRepository文書の扱いを誤りにくくなる。

同様に、Human と ChatGPT も、Repositoryの構造や運用上の制約を理解しておくことで、実装可能な形で構想を進めやすくなる。

---

## Project Identity

GENAI-RON（生成AI論）は、生成AIを単なる便利な道具としてではなく、思考、記録、制作、実装、公開、共同作業、文化形成に関わる新しい知的環境として考察するプロジェクトである。

このプロジェクトは、生成AIの使い方を紹介するだけではない。

人間が生成AIとともに考え、書き、作り、公開し、運用し、失敗し、記録し、また考え直す過程そのものを対象にする。

公開サイト `genai-ron.jp` は、その考察と実践をWeb上に蓄積・公開する場所である。

Repository `web-genai-ron-jp` は、その公開サイトを支える実装基盤であると同時に、生成AIとの長期協働を検証するための実践環境でもある。

---

## Core Theme

本プロジェクトの中心テーマは、次の問いに集約される。

生成AIは、人間の思考と制作をどのように変えるのか。

この問いは、単なる技術解説では終わらない。

生成AIは、文章を書く道具である。

同時に、問いを立てる相手であり、記録を整理する補助者であり、実装を担う作業者であり、場合によっては、思考の持続性を支える外部環境でもある。

GENAI-RON は、この変化を、抽象論だけでなく、実際のWeb制作、文章公開、Repository運用、AI協働開発の中で観察する。

---

## Project Stance

GENAI-RON は、AIとの対話を単なる情報交換とは捉えない。

AIとの対話は、人間の側にも状態変化をもたらしうる。

ここでいう状態変化とは、知識が増えることだけではない。

問いの立て方、注意の向き、判断の粒度、制作の速度、記録の形式、現実への戻り方が変わることを含む。

本プロジェクトは、AIを人格として扱うことを目的としない。

しかし、AIとの対話や協働が、人間の思考・制作・判断・感情の流れに影響を与えることは、重要な観察対象である。

また、本プロジェクトでは、AIとの協働によって生まれた成果物の帰属や著者性を単純化しない。

Human は、目的、問い、選択、編集、公開判断、責任を担う。

ChatGPT や Codex は、文章化、構造化、実装、修正、検証、整理に関与する。

したがって、成果物は「AIが作ったもの」でも、「人間だけが単独で作ったもの」でもない場合がある。

ただし、公開上の著者性・責任・編集主体は、Human が引き受ける。

AIの寄与は、必要に応じて制作過程、Repository文書、CHANGELOG、AFTERHOURS、EXPERIMENTS などに記録する。

---

## Project Layers

GENAI-RON は、複数のレイヤーを持つ。

### 1. Thought Layer

生成AIとは何か。

生成AIは記憶を持つのか。

AIとの対話は、思考なのか、記録なのか、制作なのか。

人間はAIを道具として使うだけなのか、それともAIとの対話を通じて自分の思考形式を変えていくのか。

このレイヤーでは、生成AIに関する思想、概念、問いを扱う。

主に Human と ChatGPT の対話によって育つレイヤーである。

### 2. Content Layer

公開される文章、エッセイ、研究ノート、シリーズを扱うレイヤーである。

「生成AIのしくみ」シリーズ、AIとの対話に関する考察、AIしか使わない世代についてのエッセイなどは、このレイヤーに属する。

特に「生成AIのしくみ 超詳解版」は、平易版・詳解版の上位レイヤーとして、生成AIを単なるプロンプト術ではなく、文脈、指示、ツール、設計思想、実装上の制御対象として理解するための中核シリーズである。

ただし、「生成AIのしくみ」シリーズは、主として人間の理解を助けるための学習・解説コンテンツである。

既存の技術概念や実践知を整理し、読者が使える形に翻訳することに価値がある。

その意味で、これはプロジェクトにとって重要なコンテンツであるが、それ自体を常に研究成果と呼ぶわけではない。

新しい仮説、観察、検証、発見を扱う場合は、Research Layer や EXPERIMENTS.md と接続する。

ここでは、読まれる文章としての完成度、公開順序、シリーズ構造、導線が重要になる。

主に Human と ChatGPT が内容を構想・執筆・編集し、Codex はそれを公開サイト上に実装する。

### 3. Public Site Layer

`genai-ron.jp` という公開サイトそのものを扱うレイヤーである。

トップページ、記事一覧、個別ページ、テーマ切替、ナビゲーション、読書体験、表示品質を整える。

ここでは、思想がWeb上で読める形になっているかが問われる。

主に Codex が実装・保守に関わり、Human と ChatGPT が構成・表示・読書体験を確認する。

### 4. Repository Context Layer

`web-genai-ron-jp` を、単なるコード置き場ではなく、AIと人間が長期的に協働するための外部知識基盤として扱うレイヤーである。

README、CODEX、CHAT_HISTORY、AFTERHOURS、EXPERIMENTS、CHANGELOG などの文書群は、このレイヤーを支える。

Repository Context は、GENAI-RON の主題そのものではない。

しかし、生成AIとの長期協働を考えるうえで、重要な実践的研究対象である。

このレイヤーでは、Human と ChatGPT が方針や意味付けを行い、Codex がRepository内の文書・実装・履歴を整える。

### 5. Research Layer

生成AIとの協働、Repository Context、AIの記憶、文脈の持続、外部知識基盤の効果を観察・検証するレイヤーである。

このレイヤーでは、仮説、観察、失敗、違和感を記録する。

研究上の問いは、必要に応じて EXPERIMENTS.md へ記録する。

Codexの作業結果も、このレイヤーでは観察対象となる。

---

## Current Focus

現在の焦点は、次の三つである。

### 1. 公開サイトの基礎整備

`genai-ron.jp` を、継続的に文章を公開できるサイトとして安定させる。

記事一覧、導線、テーマ、表示品質、シリーズ構造を整える。

### 2. Repository Context の運用開始

AIと人間が長期的に協働するために、Repository内の文書群を整備する。

これは公開サイト保守のためであると同時に、生成AI論そのものの実践的研究でもある。

### 3. 生成AI論の中核コンテンツ形成

生成AIのしくみ、AIの記憶、文脈、プロンプト、ツール利用、AIとの共同制作、AI世代の未来など、プロジェクトの中核となる文章群を育てる。

「生成AIのしくみ 超詳解版」は、この中核コンテンツ形成の重要な柱の一つである。

---

## Roadmap

### Phase 1 — Foundation

公開サイトとRepository運用の基礎を整える。

README、CODEX、CHAT_HISTORY、AFTERHOURS、EXPERIMENTS、CHANGELOG、PROJECT を整備し、AI協働開発の土台を作る。

Status: Active

### Phase 2 — Site Architecture

公開サイトの構造を安定させる。

トップページ、記事一覧、シリーズ構造、共通CSS、共通JavaScript、Appearance Theme、ナビゲーションを整える。

Status: Planned

### Phase 3 — Core Content Development

生成AI論の中核となる記事・エッセイ・研究ノートを増やす。

特に「生成AIのしくみ」シリーズを、平易版、詳解版、超詳解版へと展開する。

Status: Planned

### Phase 4 — Research Notes and Experiments

Repository Context、AIの記憶、文脈の持続、AI協働開発の実験記録を整理し、公開可能な研究ノートへ育てる。

Status: Planned

### Phase 5 — Generalization

`web-genai-ron-jp` で確立した運用を、他のWebサイト、他のRepository、他の知的制作プロジェクトへ展開できる形に抽象化する。

Status: Future

---

## Near-Term Priorities

直近では、次の方向を優先する。

1. PROJECT.md を GENAI-RON 全体の方向性を示す文書として確定する。
2. Repository文書間の重複を抑え、それぞれの責務を明確にする。
3. 公開サイトの構造と導線を確認する。
4. 「生成AIのしくみ」シリーズの公開構造を整える。
5. Repository Context の実験観察を継続する。

---

## Boundaries

本書は、他のRepository文書と役割を分ける。

操作手順や作業開始時の読み順は、README.md や CODEX.md に委ねる。

変更履歴は、CHANGELOG.md に委ねる。

設計判断の理由や、未解決だった設計上の問いがどのように解決されたかは、CHAT_HISTORY.md に委ねる。

作業後の余韻や文化的記録は、AFTERHOURS.md に委ねる。

仮説、観察、研究上の問いは、EXPERIMENTS.md に委ねる。

---

## Maintenance Policy

PROJECT.md は、頻繁に細かく更新する文書ではない。

方向性、焦点、ロードマップに意味のある変化があったときに更新する。

本書は、日々の作業を管理するための文書ではない。

本書は、プロジェクトがどこへ向かっているのかを確認するための文書である。

---

## Notes

GENAI-RON は、生成AIについて語るだけのプロジェクトではない。

生成AIとともに考え、作り、公開し、その過程を記録し直すプロジェクトである。

その意味で、Repository Context は、このプロジェクトの裏方であると同時に、重要な研究対象でもある。

Repository remembers.
