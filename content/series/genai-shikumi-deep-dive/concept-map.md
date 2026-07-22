---
ページ作成日時: "2026-07-22 16:47 JST"
最終更新日時: "2026-07-22 16:47 JST"
id: "genai-shikumi-deep-dive-concept-map"
title: "主要概念マップ"
subtitle: "01〜08を、一つの概念体系として見渡すための地図。"
series: "genai-shikumi-deep-dive"
series_label: "生成AIのしくみ 超詳解"
top_label: "超詳解トップ"
top_href: "/series/genai-shikumi-deep-dive/"
slug: "/series/genai-shikumi-deep-dive/concept-map/"
canonical_url: "https://genai-ron.jp/series/genai-shikumi-deep-dive/concept-map/"
description: "生成AIのしくみ超詳解 01〜08の主要概念を、関係図と境界として整理する補助資料。"
source_reconstruction_from: "site/series/genai-shikumi-deep-dive/concept-map/index.html"
source_html_blob_sha: "e35531e040de990695d640006a22a437098683ea"
original_notion_created_at: "2026-07-20 11:42 JST"
original_notion_updated_at: "2026-07-20 11:42 JST"
web_migrated_at: "2026-07-20 12:56 JST"
status: "source-reconstruction-draft"
exclude_from_public_body:
  - "更新履歴"
  - "作業履歴"
  - "内部TODO"
  - "変換ログ"
rendering_contract:
  note: "semantic block. Web側でblockquote, callout, accordion等へ変換してよい。"
  phrase: "semantic phrase/code block. Web側で article-phrase 相当へ変換してよい。"
  table: "content table. Web側で responsive table へ変換してよい。"
  references: "公式参照。タイトル文字列を通常リンクにする。"
---
このページは、`生成AIのしくみ 超詳解` 01〜08を、個別記事ではなく一つの概念体系として見渡すための主要概念マップである。

目的は、各回で扱った概念を、単なる用語一覧ではなく、互いにどう接続しているかが分かる形にすることにある。

## 1. 全体の骨格

このシリーズは、ユーザーが一文を送ってから、生成AIシステムが何を組み立て、何を参照し、何を実行し、どこで止まるかを分解してきた。

最も大きな流れは、次である。

```text
user intent
  ↓
request assembly
  ↓
instruction hierarchy
  ↓
context assembly
  ↓
model invocation
  ↓
model output
  ↓
structured output / tool call candidate
  ↓
application validation
  ↓
runtime / tool execution
  ↓
tool result
  ↓
verification
  ↓
continue / stop / ask user / handoff
  ↓
trace / audit / evaluation
```

この流れの中で、生成AIはモデル単体ではなく、次の複合システムとして現れる。

```text
AI system =
  model
  + application orchestration
  + context assembly
  + tool runtime
  + memory / retrieval
  + validation / verification
  + guardrails
  + human judgment
  + audit trail
```

## 2. 8つの概念クラスター

| クラスター | 中心概念 | 対応する回 | 一文でいうと |
|---|---|---|---|
| request | prompt compilation / request object | 01 | ユーザー文はそのままモデルへ渡るのではなく、実行時に入力環境として組み立てられる。 |
| instruction | system / developer / user / tool result | 02 | 指示の強さは言葉の強さではなく、置かれた層によって決まる。 |
| context | history / memory / retrieval / file / tool result | 03 | contextとは保存情報ではなく、今回の生成に注入された入力集合である。 |
| tool loop | tool call / application execution / tool result | 04 | modelはtoolを直接実行せず、applicationが検証・実行し、結果をcontextへ戻す。 |
| output contract | JSON Schema / validation / repair | 05 | 構造化出力とは、モデル出力とapplicationの間の契約である。 |
| memory | 保存 / 参照 / personalization / audit | 06 | memoryはモデルの体験ではなく、保存情報を選別しcontextへ再注入する仕組みである。 |
| agentic control | stop condition / budget / verification / handoff | 07 | agentic loopは動き続ける仕組みではなく、続行か停止かを選ぶ制御ループである。 |
| architecture | model / application / runtime / human | 08 | 生成AIシステムとは、責任境界を持つ複数層の協働である。 |

## 3. 主要概念の関係図

```text
User
  └─ has intent / goal
      ↓
Application
  ├─ assembles request
  ├─ places instructions
  ├─ selects context
  ├─ exposes tools
  ├─ validates outputs
  ├─ controls loop
  └─ records trace
      ↓
Model
  ├─ reads context
  ├─ generates answer
  ├─ emits structured output
  ├─ proposes tool call
  ├─ refuses
  └─ asks clarification
      ↓
Runtime / Tools
  ├─ search
  ├─ file read/write
  ├─ API call
  ├─ database operation
  ├─ connector action
  └─ sandbox execution
      ↓
Application
  ├─ observes result
  ├─ verifies progress
  ├─ retries / repairs
  ├─ asks user
  ├─ hands off
  └─ stops
      ↓
Human
  ├─ sets goal
  ├─ approves
  ├─ judges value
  ├─ accepts responsibility
  └─ evaluates result
```

## 4. 混同しやすい境界

| 混同 | 正しくは | 関連回 |
|---|---|---|
| prompt = チャット欄の文章 | prompt / requestは、実行時に組み立てられる入力環境である。 | 01 |
| 強い言葉 = 強い指示 | 指示の強さは、どのrole / layerに置かれたかで決まる。 | 02 |
| context = 保存済み情報 | contextは、今回の生成に入った情報である。 | 03 |
| tool call = tool実行 | tool callは実行候補であり、実行するのはapplication / runtimeである。 | 04 |
| JSONが出た = 構造化出力成功 | schemaに沿ってparse / validateされて初めて扱える。 | 05 |
| memory = モデル内部の記憶 | 多くの場合、外部保存された情報の参照・注入である。 | 06 |
| agent = 自律的に動き続けるAI | agentic loopは停止条件・budget・verificationで制御される。 | 07 |
| AIがやった = modelがやった | model、application、runtime、humanの協働として分解する必要がある。 | 08 |

## 5. 01〜08の概念接続

01から02へ

01で扱ったrequest objectは、ただ情報を集めるだけではない。

その中に入る情報には、system、developer、user、tool resultなどの層がある。

そのため、01の「組み立て」は、02の「指示階層」と直結する。

02から03へ

指示階層が分かると、外部資料や検索結果を命令として扱ってはいけない理由が見える。

これが03のcontext理解につながる。

contextに入ったからといって、その情報が上位命令になるわけではない。

03から04へ

tool resultもcontextの一部である。

ただし、それはモデルが直接外部世界を見たという意味ではない。

04では、tool callがapplicationで実行され、その結果がtool resultとしてcontextへ戻るloopを見る。

04から05へ

tool callは、自然文ではなく構造化された出力である。

だから、schema、validation、retry、repairが必要になる。

04のtool call理解は、05の構造化出力理解へつながる。

05から06へ

schema化できるのは出力だけではない。

memoryの保存・参照・注入にも、何を保存し、いつ使い、どう監査するかという構造が必要である。

05の契約という考え方は、06のmemory governanceにつながる。

06から07へ

memoryやretrievalがあると、agentは長い文脈の中で行動できるように見える。

しかし、長く動けることと、安全に止まれることは別である。

06の持続性は、07の停止条件と検証ループを必要とする。

07から08へ

agentic loopを制御するには、modelだけでなくapplication、runtime、human、auditの責任境界が必要になる。

07のcontrol loopは、08の全体アーキテクチャへ統合される。

## 6. 中心命題一覧

| 回 | 中心命題 |
|---|---|
| 01 | プロンプトとは、ユーザーが書いた文章そのものではなく、実行時に組み立てられる入力環境である。 |
| 02 | 指示の強さは、言葉の強さではなく、置かれた層によって決まる。 |
| 03 | contextとは、保存情報ではなく、今回の生成に注入された入力集合である。 |
| 04 | tool useとは、モデルが外部世界を直接操作することではなく、tool callとtool resultをapplicationが仲介するloopである。 |
| 05 | 構造化出力とは、モデルとapplicationの間にschemaという契約を置くことである。 |
| 06 | memoryとは、人間の記憶のような体験ではなく、保存情報の参照・選別・注入・監査の仕組みである。 |
| 07 | agentic loopとは、自律的に動き続ける仕組みではなく、続行・検証・停止・handoffを選ぶ制御ループである。 |
| 08 | 生成AIシステムとは、model、application、runtime、humanの責任境界を持つ複合システムである。 |

## 7. この概念マップの使い方

このページは、次の用途で使う。

- 01〜08を読み返すときの地図
- 用語集を作るときの分類軸
- よくある誤解集の整理軸
- 図解版を作るときの下図
- Web公開時のシリーズ導入
- 09以降を設計するときの土台

特に重要なのは、次の一文である。

```text
生成AIを理解するとは、modelの賢さを語ることだけではなく、
request、instruction、context、tool、schema、memory、loop、human responsibilityの境界を読むことである。
```
