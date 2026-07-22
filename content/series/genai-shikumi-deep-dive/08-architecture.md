---
ページ作成日時: "2026-07-22 16:47 JST"
最終更新日時: "2026-07-22 16:47 JST"
id: "genai-shikumi-deep-dive-08"
title: "全体アーキテクチャ"
subtitle: "model / application / runtime / human の責任境界を組み直し、生成AIシステム全体を読む。"
series: "genai-shikumi-deep-dive"
series_label: "生成AIのしくみ 超詳解"
series_order: "8"
order_display: "08"
previous_label: "前へ：07 停止条件と検証ループ"
previous_href: "/series/genai-shikumi-deep-dive/07-agentic-loop/"
next_label: "次へ：主要概念マップ"
next_href: "/series/genai-shikumi-deep-dive/concept-map/"
top_label: "超詳解トップ"
top_href: "/series/genai-shikumi-deep-dive/"
slug: "/series/genai-shikumi-deep-dive/08-architecture/"
canonical_url: "https://genai-ron.jp/series/genai-shikumi-deep-dive/08-architecture/"
description: "生成AIシステムを、model、application、runtime、memory、tools、guardrails、human、auditの責任境界として読む超詳解。"
source_reconstruction_from: "site/series/genai-shikumi-deep-dive/08-architecture/index.html"
source_html_blob_sha: "029fd63228872cdf28a19d9d4f0b584869d8fde6"
original_notion_created_at: "2026-07-20 11:22 JST"
original_notion_updated_at: "2026-07-20 11:22 JST"
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
ここまで、生成AIのしくみをいくつかの部品に分けて見てきた。

01では、ユーザー入力がそのままモデルへ流れ込むのではなく、request objectとして組み立てられることを見た。

02では、system / developer / user / tool result などの指示階層を見た。

03では、context、memory、RAG、file input、context windowを扱った。

04では、tool callとapplication execution、そしてtool resultが再びcontextへ戻るloopを扱った。

05では、JSON Schema、Structured Outputs、parse、validate、repair、handoffを扱った。

06では、memoryを、保存・参照・注入・監査の仕組みとして見た。

07では、agentic loopを、停止条件、budget、verification、guardrails、handoff、traceとして扱った。

08では、これらを一枚の全体図に戻す。

中心にある問いは、これである。

:::note
生成AIシステムにおいて、model、application、runtime、tool、memory、humanは、それぞれ何を担当し、どこで責任境界が切られているのか。
:::

## 1. 生成AIシステムはmodelだけではない

日常的には、私たちはこう言う。

```text
AIが答えた
AIが検索した
AIがファイルを読んだ
AIがメールを書いた
AIがNotionにページを作った
AIがコードを直した
```

もちろん、日常語としてはこれでよい。

しかし、しくみとして見るなら、この言い方はかなり粗い。

モデルが直接Webを検索しているとは限らない。

モデルが直接ファイルシステムを読んでいるとは限らない。

モデルが直接メールを送っているとは限らない。

モデルが直接NotionやGoogle Driveを書き換えているとは限らない。

モデルが直接データベースや外部APIを操作しているとは限らない。

多くの場合、モデルがしているのは、次のような出力を生成することである。

```text
natural language answer
structured output
tool call request
reasoned next-step proposal
refusal
clarification request
handoff proposal
```

それを受け取ったapplicationが、構造を確認し、権限を確認し、toolを呼び、runtimeが実行し、結果を受け取り、必要なら再びmodelへ戻す。

つまり、外からは「AIがやった」ように見えることの多くは、実際には複数の層の協働である。

```text
"AI did it"
  = model generated something
  + application interpreted it
  + runtime executed something
  + tool returned a result
  + application verified or displayed it
  + human accepted, corrected, or approved it
```

「AIがやった」を分解しなければ、どこで失敗したのか分からない。

モデルが誤ったのか。

contextが足りなかったのか。

instruction placementが悪かったのか。

tool schemaが曖昧だったのか。

runtime executionが失敗したのか。

validationが弱かったのか。

human approvalが必要だったのか。

そもそも委任してはいけない判断だったのか。

全体アーキテクチャとは、この責任境界を見えるようにすることである。

## 2. 四つの大きな層

生成AIシステムは、まず大きく四つの層に分けられる。

| 層 | 主な責務 | 混同してはいけないこと |
|---|---|---|
| model | contextをもとに、自然文、構造化出力、tool call候補などを生成する | 外部世界を直接操作していると思い込む |
| application | request、instruction、context、memory、tool、validation、loopを編成する | modelの自然文応答をそのまま真実や完了扱いする |
| runtime | tool、API、connector、file system、database、sandboxなどを実行する | 実行成功をtask成功と同一視する |
| human | 目的、判断、承認、責任、評価、意味づけを担う | すべてを自動化できるとみなす |

この四層は、単純な上下関係ではない。

責務の違いである。

modelは、入力されたcontextから次の出力を生成する。

applicationは、何をcontextへ入れ、何をtoolとして許し、出力をどう扱うかを決める。

runtimeは、外部世界への接続を実行する。

humanは、目的、意味、責任、承認、評価を持つ。

```text
AI system ≠ model alone

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

この分担が曖昧になると、生成AIシステムは一気に危険になる。

モデルの限界をapplicationの設計で補うべきところを、モデルの賢さに丸投げしてしまう。

runtimeの副作用をhuman approvalで制御すべきところを、「AIが判断したから」で通してしまう。

検証すべきtool resultを、自然文の完了報告で置き換えてしまう。

全体設計の第一原則は、modelを神格化しないことではなく、modelを正しい場所に置くことである。

## 3. requestからresponseまでのpipeline

生成AIシステムをpipelineとして見ると、次のようになる。

```text
1. user intent
2. request assembly
3. instruction hierarchy placement
4. context selection
5. memory / retrieval injection
6. tool schema exposure
7. model invocation
8. output parsing
9. validation / refusal handling
10. tool execution or direct response
11. result observation
12. verification
13. loop decision
14. final response / artifact / handoff / stop
15. trace / audit / evaluation
```

これは単なる実装手順ではない。

責任境界の一覧である。

どの段階で何を確認するのか。

どの段階で人間へ返すのか。

どの段階でtoolを許可するのか。

どの段階で止めるのか。

どの段階を記録するのか。

それぞれを分けなければ、生成AIシステムは「なんとなく賢い黒箱」になる。

## 4. model layerの責務と限界

model layerの責務は、与えられたcontextから次の出力を生成することである。

ここでいう出力は、自然文だけではない。

```text
answer text
structured output
tool call candidate
classification
plan
refusal
clarification request
handoff proposal
```

modelは、入力されたcontextの中からパターンを見つけ、推論し、生成する。

文章を作る。

構造化されたJSONを作る。

toolを呼ぶべきだと判断し、tool call候補を出す。

質問が危険または不可能であれば拒否する。

情報が足りなければ確認を求める。

しかし、modelには限界がある。

```text
model output ≠ external fact
model output ≠ tool execution
model output ≠ permission
model output ≠ user approval
model output ≠ completed task
```

modelが「ファイルを作成しました」と言っても、本当にファイルが存在するとは限らない。

modelが「メールを送信しました」と言っても、実際に送信されたとは限らない。

modelが「この情報は正しいです」と言っても、それだけではsource of truthではない。

modelが「このtoolを使います」と言っても、使ってよいとは限らない。

```text
model says X happened ≠ X happened
```

modelは、source of truthではない。

modelは、memory storeでもない。

modelは、外部世界を直接操作する主体でもない。

modelは、責任主体でもない。

だから、model outputとapplication actionを分ける必要がある。

## 5. application layerの責務

application layerは、modelを呼び出すだけの薄い殻ではない。

むしろ、生成AIシステムの中核的な編成層である。

application layerは、少なくとも次を担う。

| 責務 | 内容 |
|---|---|
| request assembly | ユーザー入力、設定、履歴、添付、system / developer指示をrequestへ組み立てる |
| instruction placement | どの内容をsystem / developer / user / tool resultとして置くかを決める |
| context selection | 履歴、ファイル、検索結果、tool resultから今回入れるものを選ぶ |
| memory injection | 保存情報をそのまま使うのではなく、今回のtaskに有用な形で注入する |
| tool schema exposure | どのtoolをmodelに見せ、どのschemaで呼ばせるかを決める |
| output handling | model出力をparse / validate / retry / repair / refusal handlingする |
| loop orchestration | tool call、result observation、verification、continue / stopを制御する |
| UI / user control | 確認、承認、取り消し、編集、選択、表示を設計する |

application layerで重要なのは、「何をmodelに渡すか」と「modelから返ったものをどう扱うか」である。

```text
application decides:
  what the model sees
  what the model may call
  what counts as valid output
  what requires approval
  what should be retried
  what must stop
  what should be shown to the user
```

同じmodelでも、application設計が違えば、まったく違うシステムになる。

安全なapplicationは、model outputをそのまま外部世界へ流さない。

一度受け取り、構造を確認し、権限を確認し、必要なら検証し、人間へ戻し、traceを残す。

## 6. runtime / tool layerの責務

runtime / tool layerは、生成AIシステムにおける外部世界への実行境界である。

toolは、単なる「能力追加」ではない。

境界である。

```text
tool = capability + permission boundary + side effect boundary + audit boundary
```

runtime / tool layerには、次のようなものが含まれる。

- hosted tools
- local runtime tools
- connectors
- external APIs
- file system
- database
- browser / computer control
- sandbox
- code interpreter
- workflow engine
- job queue

modelがtool call候補を出す。

applicationがschemaと権限を確認する。

runtimeが実際に実行する。

tool resultが返る。

applicationがそれを観測し、検証し、必要なら再びmodelへ渡す。

```text
model emits tool call candidate
  ↓
application validates and authorizes
  ↓
runtime executes
  ↓
tool result returns
  ↓
application verifies
  ↓
model receives result as context
```

ここで重要なのは、execution resultはtruthそのものではないということだ。

APIが200を返したからといって、taskが成功したとは限らない。

ファイル作成toolが成功したからといって、中身が正しいとは限らない。

検索toolが結果を返したからといって、十分な調査ができたとは限らない。

DB更新が成功したからといって、正しいレコードを更新したとは限らない。

```text
execution succeeded ≠ task succeeded
result returned ≠ result verified
side effect occurred ≠ user intended it
```

runtime / tool layerでは、permission、credential、side effect、sandbox、auditが重要になる。

特に、外部状態を変える操作では、read-only actionとstate-changing actionを分けなければならない。

```text
read-only action
  ≠ state-changing action

state-changing action
  requires stronger gate
```

メール送信、公開、削除、上書き、支払い、契約、PR merge、DB更新などは、強いgateが必要になる。

toolは便利さの入口であると同時に、事故の入口でもある。

## 7. memory / retrieval layerの位置

memoryやretrievalは、modelそのものではない。

多くの場合、保存された情報や外部知識を候補として取り出し、applicationが選別し、contextへ注入する層である。

```text
stored memory
  ↓
retrieval candidate
  ↓
application selection
  ↓
context injection
  ↓
model invocation
```

memoryが存在することと、今回の応答に使われることは違う。

検索結果が存在することと、信頼できる根拠になることも違う。

ファイルが添付されていることと、context windowに十分入ることも違う。

memory / retrieval layerでは、次を記録する必要がある。

```text
what was retrieved
why it was retrieved
what was injected
what was omitted
what authority it has
whether the user can inspect or correct it
```

memoryは便利である。

しかし、memoryの注入が見えないと、ユーザーは「なぜその前提で答えたのか」を検証できない。

だからmemoryは、単なるpersonalizationではなく、監査可能なcontext sourceとして扱う必要がある。

## 8. human layerの責務

human layerは、AIシステムの外側にある飾りではない。

システム構成要素である。

人間は、次を担う。

| 責務 | 内容 |
|---|---|
| goal setting | 何を達成したいのかを決める |
| judgment | 複数の選択肢から、意味や文脈に照らして判断する |
| approval | 送信、公開、削除、課金、契約などを承認する |
| value choice | 何を優先し、何を避けるかを決める |
| accountability | 結果に対する責任を引き受ける |
| evaluation | 成果物がよいか、正しいか、使えるかを評価する |
| delegation boundary | AIに任せる範囲と任せない範囲を決める |

human-in-the-loopは、単に確認ボタンを置くことではない。

人間が判断できるだけのcontextを返す必要がある。

```text
bad approval:
  "実行してよいですか？"

good approval:
  action: 何をするか
  target: どこに対して行うか
  consequence: 何が変わるか
  reversibility: 元に戻せるか
  evidence: 何を根拠にしているか
  alternatives: 他の選択肢はあるか
```

人間をloopに入れるなら、人間が判断できる形で情報を渡さなければならない。

## 9. manifestとして設計する

生成AIシステムを安全に設計するには、暗黙の状態を減らし、manifestとして見える形にする必要がある。

少なくとも、次のmanifestが有用である。

| manifest | 記録するもの |
|---|---|
| request manifest | 今回のtask、user intent、制約、成功条件 |
| instruction manifest | system / developer / user / tool result の配置 |
| context manifest | どの履歴、file、search result、tool resultをcontextに入れたか |
| memory manifest | どのmemoryを参照し、注入し、除外したか |
| tool manifest | 利用可能tool、権限、schema、side effect分類 |
| output contract | 期待する出力形式、schema、validation条件 |
| loop trace | 各stepで何を観測し、何を判断し、何を実行したか |
| audit log | 承認、外部書き込み、失敗、停止、handoffの記録 |

manifestは、開発者向けの内部資料だけではない。

AIシステムを後から説明し、検証し、改善するための足場である。

```text
no manifest → invisible state
invisible state → unverifiable behavior
unverifiable behavior → untrustworthy system
```

## 10. failure boundary

生成AIシステムでは、失敗を一種類にまとめてはいけない。

```text
model failure
context failure
instruction failure
schema failure
validation failure
runtime failure
permission failure
verification failure
approval failure
evaluation failure
```

これらは、すべて違う。

modelが誤ったのか。

contextに必要情報がなかったのか。

外部文書中の命令をinstructionとして扱ってしまったのか。

JSON schemaが曖昧だったのか。

parseやvalidationが弱かったのか。

tool実行が失敗したのか。

権限がなかったのか。

実行結果を確認しなかったのか。

人間の承認が必要だったのに省略したのか。

成果物の評価基準がなかったのか。

failure boundaryを切ることは、責任逃れではない。

改善可能性を作ることである。

```text
wrong answer
  → maybe model / context / instruction / retrieval failure

bad action
  → maybe application / runtime / permission / approval failure

unverified completion
  → maybe validation / verification / audit failure
```

「AIが間違えた」だけでは改善できない。

どの層で何が起きたかを分ける必要がある。

## 11. 01〜07の統合

ここまでの各回を、08の全体図に対応させると次のようになる。

| 回 | 扱ったもの | 全体アーキテクチャ上の位置 |
|---|---|---|
| 01 | request object | user intentをapplicationがrequestへ組み立てる |
| 02 | instruction hierarchy | system / developer / user / tool result の権限境界 |
| 03 | context | 履歴、memory、file、RAG、tool resultの入力集合 |
| 04 | tool execution loop | model output、application validation、runtime execution、tool result |
| 05 | structured output | output contract、schema、parse、validate、repair、handoff |
| 06 | memory | 保存、参照、注入、personalization、監査 |
| 07 | agentic loop | 停止条件、budget、verification、guardrails、handoff、trace |
| 08 | architecture | model / application / runtime / human の責任境界 |

このシリーズで一貫していたのは、「生成AIはモデル単体ではなく、入力・指示・context・tool・memory・runtime・humanを含むシステムである」という見方である。

## 12. 設計原則

最後に、生成AIシステムの設計原則として整理する。

- modelを単独の主体として扱わない。
- user inputをそのままmodel inputとみなさない。
- instruction hierarchyを明示する。
- contextは保存情報ではなく、今回注入された入力集合として扱う。
- tool callは実行候補であり、application側で検証する。
- structured outputは、schema、parse、validate、repairまで含めて設計する。
- memoryは便利なpersonalizationではなく、監査可能なcontext sourceとして扱う。
- agentic loopは、続ける能力ではなく、止まる能力として設計する。
- human approvalは形式的なボタンではなく、判断可能なcontextとセットで置く。
- traceとauditを残し、後から説明・再現・評価できるようにする。

この10項目は、技術的な細部というより、AIシステムを「信頼できる協働相手」にするための条件である。

## 13. OpenAI Agents SDKとの対応

OpenAI Agents SDKでは、Agentはinstructionsやtoolsを備えたLLMとして説明され、handoffs、guardrails、structured outputsなどもAgentに関連するprimitiveとして扱われる。また、Agent + Runnerにより、turns、tool execution、guardrails、handoffs、sessionsなどをSDK側で管理できる。さらにtracingは、LLM生成、tool call、handoff、guardrailなど、agent run中のeventsを記録する仕組みとして説明されている。

このシリーズの整理に引き寄せるなら、対応は次のように読める。

```text
Agent / model
  → model layer

Runner / orchestration
  → application loop layer

tools / connectors
  → runtime / tool layer

guardrails / handoffs / tracing
  → control and audit layer

sessions / context management
  → memory / context layer

human approval / review
  → human layer
```

ただし、これは特定SDKの説明をそのまま一般理論にするという意味ではない。

重要なのは、どのframeworkを使うかではなく、責任境界を消さないことである。

## 14. 結論

生成AIシステムとは、modelだけで成立するものではない。

modelは、入力されたcontextから次の出力を生成する。

applicationは、request、instruction、context、memory、tool、validation、loopを組み立てる。

runtimeは、実際のtool、API、file system、database、network、sandboxを扱う。

memory / retrieval layerは、保存情報や外部知識を候補として取り出し、contextへ注入する。

guardrailsは、許可・禁止・確認・停止を判定する。

humanは、目的、判断、承認、責任、評価を担う。

audit trailは、それらの振る舞いを後から説明可能にする。

```text
model
  + application
  + runtime
  + memory
  + tools
  + guardrails
  + human
  + audit
  = AI system
```

「AIがやった」と見える出来事は、実際には複数層の協働である。

だから、生成AIを理解するとは、モデルの中身だけを理解することではない。

モデルの周囲にある、request、instruction、context、tool、memory、runtime、human、auditの配置を理解することでもある。

そして、AIを安全に使うとは、AIを信じることではない。

どの層が何をしているかを見えるようにし、どこで確認し、どこで止め、どこで人間が判断するかを設計することである。

この全体像を持つと、生成AIは単なるチャット画面ではなくなる。

それは、modelとapplicationとruntimeとhumanが協働する、新しい実行環境として見えてくる。

参考

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [OpenAI Agents SDK｜Agents](https://openai.github.io/openai-agents-python/agents/)
- [OpenAI Agents SDK｜Running agents](https://openai.github.io/openai-agents-python/running_agents/)
- [OpenAI Agents SDK｜Tracing](https://openai.github.io/openai-agents-python/tracing/)
