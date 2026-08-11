---
title: "生成AIのしくみ 超詳解"
route: "/series/genai-shikumi-deep-dive/"
slug: "/series/genai-shikumi-deep-dive/"
source_html_path: "site/series/genai-shikumi-deep-dive/index.html"
source_html_sha256: "642af712d8bff7de92b6e687ba67a0ae11adaf72b9dfe134bde9c5236b679a05"
page_type: "series-index"
series_or_article: "genai-shikumi-deep-dive"
order: null
chapter: null
meta_description: "GENAI-RON叢書003。生成AIを、request、instruction、context、tool、schema、memory、agentic loop、architectureの組み合わせとして理解するための超詳解シリーズ。"
canonical: null
created_at: "2026-07-20 11:30 JST"
updated_at: "2026-07-20 11:30 JST"
manuscript_created_at: null
manuscript_updated_at: null
web_migrated_at: "2026-07-20 12:56 JST"
metadata_provenance:
  title: "visible_body"
  meta_description: "html_head"
  canonical: "absent"
  created_at: "html_comment"
  updated_at: "html_comment"
  manuscript_created_at: "absent"
  manuscript_updated_at: "absent"
  web_migrated_at: "html_comment"
extraction_status: "source-reconstruction-draft"
---
GENAI-RON叢書 003

# 生成AIのしくみ 超詳解

実行構造と責任境界

ユーザーが一文を送ってから、生成AIシステムは何を組み立て、何を参照し、何を実行し、どこで止まり、誰が責任を持つのか。

文・編集責任：Taku

<a id="articles"></a>

## 目次

01

### [プロンプトは実行時にどうコンパイルされるのか](/series/genai-shikumi-deep-dive/01-prompt-compilation/)

ユーザーがチャット欄に書いた文章だけがpromptではない。上位指示、履歴、memory、ファイル、検索結果、tool定義が、実行時に入力環境として組み立てられる。

promptとは、ユーザー文だけではなく、実行時に組み立てられた入力環境である。

02

### [指示階層とは何か](/series/genai-shikumi-deep-dive/02-instruction-hierarchy/)

system、developer、user、tool resultの権限構造を分け、prompt injectionを「資料と指示の境界事故」として理解する。

指示の強さは、言葉の強さではなく、置かれた層によって決まる。

03

### [contextとは何か](/series/genai-shikumi-deep-dive/03-context/)

履歴、memory、retrieval、file input、tool resultが、今回の生成にどのように注入されるのかを見る。

contextとは、保存情報そのものではなく、今回の生成に入った入力集合である。

04

### [ツール実行ループとは何か](/series/genai-shikumi-deep-dive/04-tool-execution-loop/)

modelがtool callを出し、applicationが検証・実行し、tool resultをcontextへ戻す流れを見る。

modelはtoolを直接実行しない。外部世界への接続はapplication層で起きる。

05

### [構造化出力とは何か](/series/genai-shikumi-deep-dive/05-structured-output/)

JSON、schema、parse、validate、refusal、retry、repair、handoffまで含む、applicationとの契約として扱う。

構造化出力とは、きれいなJSONではなく、生成AIシステムとの契約である。

06

### [memoryとは何か](/series/genai-shikumi-deep-dive/06-memory/)

保存された情報が選別され、現在のcontextへ再注入される仕組みとしてmemoryを読む。

memoryとは、モデル内部の体験ではなく、保存・選別・再注入の仕組みである。

07

### [停止条件と検証ループ](/series/genai-shikumi-deep-dive/07-agentic-loop/)

agentic loopを、停止条件、budget、verification、guardrails、handoff、traceによって制御されるloopとして見る。

agentは動き続けるものではなく、止まり、検証し、引き継ぐように設計される。

08

### [全体アーキテクチャ](/series/genai-shikumi-deep-dive/08-architecture/)

model、application、runtime、memory、tools、guardrails、human、auditの責任境界として全体を統合する。

生成AIシステムはmodelだけでは成立しない。責任境界を持つ全体設計である。

## 対象範囲

本叢書は、生成AIを「なんとなく賢いチャットボット」としてではなく、request、instruction、context、tool、schema、memory、agentic loop、architectureの組み合わせとして理解するための超詳解シリーズである。

中心にある問いは、ユーザーが一文を送ってから、生成AIシステムは何を組み立て、何を参照し、何を実行し、どこで止まり、誰が責任を持つのか、である。

## 読み方

01〜05では、単発の応答がどのように組み立てられるかを見る。06では、過去情報がどのように保存・参照・注入されるかを見る。07では、agentがなぜ止まり、検証し、handoffする必要があるかを見る。08では、これらをmodel / application / runtime / humanの責任分担として統合する。

```
01 request / prompt compilation
  ↓
02 instruction hierarchy
  ↓
03 context / memory / retrieval / files
  ↓
04 tool call / tool result / execution loop
  ↓
05 structured output / schema / validation
  ↓
06 memory / personalization / audit
  ↓
07 agentic loop / stop conditions / verification
  ↓
08 full architecture / responsibility boundary
```

## テーマ別の逆引き

### prompt / requestを理解したい

[01](/series/genai-shikumi-deep-dive/01-prompt-compilation/)、[02](/series/genai-shikumi-deep-dive/02-instruction-hierarchy/)、[03](/series/genai-shikumi-deep-dive/03-context/) を読む。

### tool useを理解したい

[04](/series/genai-shikumi-deep-dive/04-tool-execution-loop/)、[05](/series/genai-shikumi-deep-dive/05-structured-output/)、[07](/series/genai-shikumi-deep-dive/07-agentic-loop/)、[08](/series/genai-shikumi-deep-dive/08-architecture/) を読む。

### memory / personalizationを理解したい

[03](/series/genai-shikumi-deep-dive/03-context/)、[06](/series/genai-shikumi-deep-dive/06-memory/)、[08](/series/genai-shikumi-deep-dive/08-architecture/) を読む。

## 関連する叢書・補助ページ

- [GENAI-RON叢書001｜生成AIのしくみ](/series/genai-shikumi/)
- [GENAI-RON叢書002｜生成AIのしくみ 詳解版](/series/genai-shikumi-technical/)
- [概念マップ](/series/genai-shikumi-deep-dive/concept-map/)
- [用語集](/series/genai-shikumi-deep-dive/glossary/)
- [誤解されやすい点](/series/genai-shikumi-deep-dive/misconceptions/)
