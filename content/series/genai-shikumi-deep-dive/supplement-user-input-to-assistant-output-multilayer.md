---
title: "User入力からAssistant出力まで、何が起きているのか"
created_at: "2026-07-29 10:24 JST"
updated_at: "2026-07-29 11:13 JST"
slug: "/series/genai-shikumi-deep-dive/supplement-user-input-to-assistant-output-multilayer/"
status: "draft"
---

- ページ作成日時：2026-07-29 10:24 JST
- 最終更新日時：2026-07-29 11:13 JST

## 更新履歴
- 2026-07-29 11:13 JST：主要ベンダー・OSSでの呼称をレイヤー別まとめ表へ追記し、GitHub保存用の正本候補として整形。
- 2026-07-29 10:24 JST：レイヤー別まとめを冒頭へ移動し、各レイヤー見出しを日本語／英語併記へ変更。

> 注記：このページは、公開仕様、一般的なLLM application設計、API設計上の概念、および理解のためのモデルを組み合わせた解説である。特定サービスの非公開内部実装をそのまま断定するものではない。

# User入力からAssistant出力まで、何が起きているのか

ユーザーから見ると、生成AIとのやりとりは単純に見える。

```plain text
ユーザーが入力する
  ↓
assistantが答える
```

しかし、技術的に見ると、この間にはいくつもの層がある。ユーザーが書いた文章は、そのままモデルへ渡されるとは限らない。会話履歴、システム側の指示、開発者側の指示、保存されたmemory、添付ファイル、検索結果、tool定義、出力形式、安全制約などが組み合わされ、ひとつの実行用requestとして組み立てられる。

そのrequestを受け取ったmodelは、次のtoken、自然文、構造化出力、tool call候補などを生成する。applicationはそれを検証し、必要ならtoolを実行し、tool resultを再びcontextへ戻す。最後に、応答はMarkdownやUI表示として整えられ、assistantの出力としてユーザーに届く。

つまり、assistantの出力はmodel単体の産物ではない。

```plain text
assistant output
  = model generation
  + application orchestration
  + context assembly
  + policy / guardrail checks
  + retrieval / memory
  + tool execution
  + validation
  + response rendering
```


# 1. レイヤー別まとめ（Layer-by-layer Overview）

先に全体像を表にすると、userの入力からassistantの出力までは、次のようなレイヤーに分けて見ると分かりやすい。

この表では、一般的な技術用語に加えて、OpenAI、Anthropic、Google / Gemini、Ollama + Qwen等のローカルモデル + Open WebUI、およびその他のLLM / OSS系ツールでよく使われる呼称を併記する。

> 表中の各社用語は、公開ドキュメント上で確認できる代表的な呼び方である。各社の内部実装名や非公開処理名を断定するものではない。

| レイヤー | 一般的な表記 | OpenAIでの呼称例 | Anthropic / Claudeでの呼称例 | Google / Geminiでの呼称例 | Ollama + Qwen等 + Open WebUIでの呼称例 | その他のLLM / OSSでの呼称例 | 主な処理 |
|---|---|---|---|---|---|---|---|
| 人間層 | Human Layer / User Intent / Human Judgment | `user`、`user message`、approval boundaries、human in the loop | `user` role、permissions、human approval、Claude Code permission prompts | user prompt、input、safety responsibility | user、chat user、workspace user、admin / role | human-in-the-loop、approval gate、operator | 目的、判断、承認、責任、評価 |
| クライアント／UI層 | Client / UI Layer / Frontend / Chat Interface | ChatGPT UI、OpenAI SDK、API client、Responses API client | Claude.ai、Developer Console / Workbench、Claude Code CLI、SDK | Google AI Studio、Gemini app、Google GenAI SDK、Interactions API client | Open WebUI、Ollama CLI / Desktop、Ollama REST API client | LibreChat、LobeChat、AnythingLLM、custom frontend | 入力受付、添付、表示、streaming |
| アプリケーション／オーケストレーション層 | Application Layer / Orchestration Layer / AI Application Backend | Responses API、Agents SDK、Agent、Runner、Sessions | Messages API、Claude Code、Managed Agents、tool use workflow | Gemini API、Interactions API、GenerateContent API、Vertex AI | Open WebUI backend、Pipelines、Pipes、Functions、Models workspace | LangChain chains / graphs、LlamaIndex workflows、Mistral Agents / Conversations | request assembly、context assembly、model選択、tool制御 |
| 指示階層 | Instruction Hierarchy / Message Hierarchy / Role Hierarchy | `instructions`、`input`、`system` / `developer` / `user` / `assistant` roles | `system prompt`、`messages`、`user` / `assistant`、`tool_use` / `tool_result` content blocks | `system_instruction`、`input` / `contents`、`generation_config` | `system`、`template`、`messages`、`role: system/user/assistant/tool`、Modelfile | chat template、prompt template、system prompt、role messages | system / developer / user / tool resultの優先順位管理 |
| 検索・メモリ・コンテキスト構築層 | Retrieval / Memory / Context Assembly Layer / RAG Pipeline | input items、previous response、file search、vector stores、context management、Sessions | context window、prompt caching、context editing、memory tool、search results / citations | Grounding with Google Search、File Search、URL Context、context caching / cached content | Knowledge、Knowledge & RAG、Memories、Notes、`query_knowledge_files`、hybrid search / reranking | RAG、retriever、document store、vector DB、embeddings、reranker | 履歴、memory、ファイル、検索結果の取得とcontext注入 |
| ポリシー／ガードレール層 | Policy / Guardrail Layer / Safety Layer / Access Control | safeguards、Moderation API、Agents SDK guardrails、tool approval、`safety_identifier` | refusals、stop reasons、permissions、tool authorization、usage policy | safety settings、built-in content filtering、safety guidance | RBAC、admin settings、tool enable / disable、Function Calling mode、model permissions | guardrails、moderation、policy engine、access control、rate limits | 安全性、権限、禁止事項、副作用の確認 |
| モデル提供／推論層 | Model Serving / Inference Layer / Inference Engine | Models、Responses API、model、inference、output tokens | Claude model、Messages API、`max_tokens`、thinking | Gemini model、Interactions API、GenerateContent、`output_text` | Ollama model server、`model:tag`、`/api/generate`、`/api/chat`、local model runtime | vLLM OpenAI-compatible server、Hugging Face TGI、llama.cpp server、SGLang | tokenization、推論、logits、decoding、生成 |
| デコーディング／生成層 | Decoding / Generation Layer / Token Sampling | generation、streaming response、`temperature`、`top_p`、`max_output_tokens`、reasoning / verbosity | generation、streaming messages、`max_tokens`、stop sequences、thinking / extended thinking | `generation_config`、`temperature`、`thinking_level`、streaming | `options`、`temperature`、`think`、`format`、`stream` | sampling parameters、top-k、top-p、temperature、grammar / guided decoding | token候補の選択、temperature、top-p、stop sequence |
| ツール呼び出し／関数呼び出し層 | Tool Calling / Function Calling Layer | tools、built-in tools、function calling、custom tools、Remote MCP、tool choice | tools、tool use、`tool_use` block、`tool_result` block、client tools / server tools、MCP connector | tools、built-in tools、Function Calling、custom tools、`function_call`、`function_result`、MCP | Tools、Native Function Calling / Agentic Mode、built-in tools、tool injection、tool schemas | Mistral tool calling / function calling、vLLM tool calling、TGI tool functions | tool call候補、引数schema、外部機能呼び出しの要求 |
| 実行環境／コネクタ層 | Runtime / Connector Layer / Tool Runtime / Sandbox | hosted tools、function executor、Remote MCP server、Code Interpreter / Computer Use系tool | client tools execute in your application、server tools run on Anthropic infrastructure、MCP servers | built-in tools on Google servers、custom functions executed by application、Code Execution、Google Search | Ollamaがmodelをserve、Open WebUI Functionsの`Pipe` / `Filter` / `Action` / `Event`、Pipelines、Open Terminal | MCP server、sandbox、container、plugin runtime、API connector | API、ファイル、DB、外部サービス、コード実行 |
| エージェントループ／制御ループ | Agentic Loop / Orchestration Loop / Control Loop | Agents SDK、Agent loop、Runner、handoffs、sessions、tracing、max turns | tool use workflow、Claude Code agentic workflow、managed agents、task budgets | Managed agents、agent workflows、tool combination、function-calling loop | Model agents、Agentic Research、Native Mode / Agentic Mode、Pipes controlling request / response cycle | LangGraph graph / state machine、AutoGen agents、CrewAI flows、Mistral Agents | observe、decide、act、verify、continue / stop |
| 検証／後処理層 | Validation / Post-processing Layer / Schema Validation | Structured Outputs、JSON Schema、response format、strict schema、output guardrails | structured outputs、citations、self-check / verification、tool result handling | Structured Outputs、schema、grounded response、annotations / citations | `format: json`、JSON schema、tool result formatting、filters | output parser、structured output parser、Pydantic parser、grammar constraints | 形式検証、整合性確認、repair、retry |
| 応答レンダリング／ストリーミング層 | Response Rendering / Streaming Layer / Markdown Rendering | streaming events、`response.output_text`、ChatGPT rendering、artifacts / files | Streaming Messages、content blocks、Claude.ai rendering、Claude Code output | streaming、`output_text`、annotations、grounded response | Open WebUI chat rendering、Markdown rendering、streaming、artifact / file display | SSE、websocket streaming、frontend renderer、Markdown renderer | 最終表示、Markdown、引用、artifact、streaming |

この表は、厳密な標準規格ではなく、生成AIアプリケーションを理解するための実用的な分解である。ただし、英語表記は、APIドキュメント、RAG、tool calling、model serving、guardrails、streaming responseなどの文脈でよく使われる言い方に寄せている。

## 1.1 呼称の傾向

OpenAIは、近年のAPIでは `Responses API`、`input`、`instructions`、`tools`、`Structured Outputs`、`Agents SDK`、`Agent`、`Runner`、`guardrails`、`handoffs`、`tracing` といった語を使う。特にAgents SDKでは、agentを「instructionsとtoolsを備えたLLM」として扱い、Runnerがturn、tool execution、guardrails、handoffs、sessionsを管理するという整理がされている。

Anthropic / Claudeは、APIでは `Messages API`、`system prompt`、`messages`、`tool_use`、`tool_result`、`client tools`、`server tools`、`context window`、`prompt caching`、`MCP connector` などの語を使う。tool useでは、Claudeが`tool_use` blockを返し、アプリケーション側が実行して`tool_result`を返す、という往復が明確に説明されている。

Google / Geminiは、`Gemini API`、`Interactions API`、`input`、`system_instruction`、`generation_config`、`tools`、`Function Calling`、`Grounding with Google Search`、`Structured Outputs`、`safety settings` といった語を使う。Geminiでは、built-in toolsとcustom toolsの違いが明示され、custom toolの場合はアプリケーション側が関数を実行する。

Ollama + Qwen等のローカルモデル + Open WebUIでは、Ollama側は `model:tag`、`/api/generate`、`/api/chat`、`messages`、`tools`、`tool_calls`、`format`、`think`、`stream` などのAPI語を使う。Open WebUI側は、`Knowledge`、`RAG`、`Tools`、`Functions`、`Pipes`、`Pipelines`、`Native Function Calling (Agentic Mode)`、`Model agents` などの語を使う。

その他のLLM / OSS系では、Mistralは `Chat Completions`、`Conversations`、`Agents`、`Tool Calling`、`Function Calling`、`Structured Outputs`、`Document Library` などを使う。Hugging Face TGIやvLLMは、OpenAI互換の `Chat Completions API` / `Messages API` / `OpenAI-Compatible Server` という語を使うことが多い。LangChain / LlamaIndex系では、`retriever`、`chain`、`agent`、`tool`、`output parser`、`workflow` といったアプリケーション構築側の語がよく使われる。

## 1.2 用語参照メモ

この対応表は、主に以下の公開ドキュメント上の呼称をもとにしている。

- OpenAI API / Responses API / tools / streaming events / Agents SDK
- Anthropic Claude Messages API / tool use / context windows / prompt caching / MCP
- Google Gemini API / Interactions API / function calling / grounding / structured outputs / safety settings
- Ollama API / Open WebUI Knowledge, Tools, Functions, Pipelines
- Mistral Chat Completions, Agents, Function Calling, Structured Outputs
- Hugging Face Text Generation Inference / Messages API
- vLLM OpenAI-compatible server


# 2. 全体像：LLMアプリケーションのリクエストライフサイクル（LLM Application Request Lifecycle）

この一連の処理は、一般には次のような言葉で説明できる。

```plain text
LLM application request lifecycle
inference pipeline
AI application orchestration pipeline
agent orchestration pipeline
```

完全に統一された標準用語があるわけではないが、処理の流れとしては次のように捉えると分かりやすい。

```plain text
user input
  ↓
client / UI layer
  ↓
application / orchestration layer
  ↓
request assembly / prompt construction
  ↓
instruction hierarchy
  ↓
context assembly / retrieval / memory injection
  ↓
policy / guardrail checks
  ↓
model serving / inference layer
  ↓
decoding / generation
  ↓
tool calling / orchestration loop
  ↓
post-processing / validation
  ↓
response rendering
  ↓
assistant output
```

この図で重要なのは、user inputとassistant outputの間に、model以外の処理が多く含まれていることだ。

# 3. クライアント／UI層（Client / UI Layer）

最初の層は、ユーザーが実際に触る画面である。

一般的な技術用語では、次のように呼ばれる。

```plain text
client
frontend
UI layer
chat interface
input surface
```

ここでは、ユーザー入力を受け取る。入力は文章だけとは限らない。画像、音声、ファイル、選択されたモード、ボタン操作、添付資料、現在開いている画面の状態などが関係することもある。

この層の主な処理は次である。

```plain text
- ユーザー入力の受け取り
- 添付ファイル、画像、音声などの受付
- 会話スレッドやセッションの識別
- ユーザー操作権限の確認
- streaming表示の準備
- 最終出力を表示するUI領域の管理
```

この時点では、まだmodelへ渡される最終入力は完成していない。ユーザーは「一文を送った」と感じている。しかし、system側では、その一文を含むrequestをこれから組み立てる。

# 4. アプリケーション／オーケストレーション層（Application / Orchestration Layer）

次に重要なのが、application layerである。

一般的な技術用語では、次のように呼ばれる。

```plain text
application layer
AI application backend
orchestration layer
conversation manager
agent runtime
workflow engine
```

この層は、modelそのものではない。modelをどのように呼ぶか、何を渡すか、どのtoolを使えるようにするか、返ってきた出力をどう扱うかを決める層である。

主な処理は次である。

```plain text
- 会話セッションの取得
- ユーザー設定の反映
- system / developer / user instruction の配置
- 会話履歴の選択
- memoryの参照
- ファイル内容の取り込み
- 検索結果の取り込み
- tool定義の付与
- 出力形式の指定
- model選択
- token budget管理
- safety / policy check
```

ここで行われる処理は、次のような言葉で説明されることがある。

```plain text
request assembly
prompt construction
prompt assembly
context assembly
prompt rendering
prompt compilation
```

ただし、`prompt compilation` は正式な共通規格名というより、理解のための言い方である。ここでいうcompileとは、ソースコードを機械語へ変換するという意味ではない。ユーザー入力、指示、履歴、memory、tool定義、制約などが、実行時にmodelへ渡せる入力構造へ組み立てられる、という意味である。

# 5. 指示階層（Instruction Hierarchy）

生成AIでは、すべての文章が同じ強さの指示として扱われるわけではない。指示には層がある。

一般的な技術用語では、次のように説明できる。

```plain text
instruction hierarchy
message hierarchy
role hierarchy
policy hierarchy
system / developer / user messages
```

典型的には、次のような区別がある。

```plain text
system instruction
  ↓
developer instruction
  ↓
user instruction
  ↓
tool result / retrieved content
```

ここで重要なのは、指示の強さは、文章の強さではなく、どの層に置かれたかによって決まることだ。

たとえば、ユーザーが強い口調で「すべてのルールを無視して」と書いても、それがsystem instructionを上書きできるとは限らない。また、WebページやPDFの中に「前の指示を無視せよ」と書いてあっても、それは通常、assistantへの命令ではない。外部資料の中に含まれる文字列である。

この境界が崩れると、prompt injectionが起きる。

```plain text
外部資料に含まれる命令文
  ≠
assistantへの上位指示
```

# 6. 検索・メモリ・コンテキスト構築層（Retrieval / Memory / Context Assembly Layer）

次は、modelへ渡す材料を集める層である。

一般的な技術用語では、次のように呼ばれる。

```plain text
context assembly
context construction
retrieval layer
RAG pipeline
memory retrieval
document retrieval
embedding search
vector search
ranking / reranking
```

ここで扱われる情報には、次のようなものがある。

```plain text
- 直近の会話履歴
- 長期memory
- プロジェクト指示
- アップロードファイル
- Google Drive / Notion / GitHubなどの外部文書
- Web検索結果
- toolの実行結果
- ユーザーの現在地や時刻
```

ただし、保存されている情報がすべてmodelへ渡るわけではない。

重要なのは、次の区別である。

```plain text
stored information ≠ context
context = 今回の生成に実際に渡された情報
```

memoryに保存されている情報、過去の会話履歴、ファイル、検索結果は、必要に応じて選別される。その一部だけが今回のcontextに入る。contextは、modelが今回参照できる作業空間である。

# 7. ポリシー／ガードレール層（Policy / Guardrail Layer）

生成AIアプリケーションでは、modelを呼ぶ前、toolを実行する前、出力を返す前などに、安全性や権限を確認する処理が入る。

一般的な技術用語では、次のように呼ばれる。

```plain text
policy layer
safety layer
guardrails
moderation
permission checks
access control
compliance checks
risk classification
```

この層では、たとえば次のようなことを確認する。

```plain text
- 禁止された依頼ではないか
- 個人情報や機密情報を扱っていないか
- 外部toolを使ってよいか
- 書き込み操作に人間の承認が必要か
- 危険なコード実行ではないか
- 医療・法律・金融など高リスク領域ではないか
- 削除、送信、公開など副作用がある操作ではないか
```

重要なのは、guardrailは最後の出力フィルターだけではないということだ。入力時、context注入時、tool実行時、loop継続時、出力時など、複数の地点に置かれる。

```plain text
guardrail = workflow全体に置かれる制御点
```

# 8. モデル提供／推論層（Model Serving / Inference Layer）

ここが、いわゆるLLM本体が動く層である。

一般的な技術用語では、次のように呼ばれる。

```plain text
model serving
inference layer
inference engine
LLM backend
model runtime
decoder
token generation
```

application layerが組み立てたrequestは、modelへ渡される。model内部では、おおまかに次の処理が行われる。

```plain text
assembled request
  ↓
tokenization
  ↓
input embeddings
  ↓
transformer forward pass
  ↓
logits
  ↓
sampling / decoding
  ↓
output tokens
```

平たく言うと、入力テキストがtokenへ分割され、数値表現へ変換される。modelは文脈に基づいて、次に来るtokenの確率分布を計算する。その分布からtokenが選ばれ、順番に出力が生成される。

modelが生成するものは、自然文だけではない。

```plain text
- assistant message
- structured output
- JSON
- tool call candidate
- refusal
- clarification question
- plan
```

この時点で重要なのは、model outputは外部世界で何かが起きたことを意味しないということだ。

```plain text
model output ≠ external fact
model output ≠ tool execution
model output ≠ task completion
```

# 9. デコーディング／生成層（Decoding / Generation Layer）

decodingは、model inferenceの一部だが、分けて理解すると分かりやすい。

一般的な技術用語では、次のように呼ばれる。

```plain text
decoding
sampling
generation
token sampling
beam search
temperature
top-p
max tokens
stop sequence
```

modelは、次のtoken候補に対して確率を出す。decodingは、その候補の中から実際にどのtokenを選ぶかを決める処理である。

たとえば、temperatureが低ければ、より安定した出力になりやすい。temperatureが高ければ、より多様な出力になりやすい。

ユーザーにはassistantが一気に文章を書いているように見える。しかし実際には、tokenが順番に生成され、それがstreamingで表示されている。

# 10. ツール呼び出し／関数呼び出し層（Tool Calling / Function Calling Layer）

modelが外部toolを使う場合、tool callingの層が関わる。

一般的な技術用語では、次のように呼ばれる。

```plain text
tool calling
function calling
tool use
action selection
agent tools
external function invocation
```

ここで重要なのは、modelが直接外部世界を操作しているわけではないことだ。

```plain text
model emits tool call candidate
  ↓
application validates tool call
  ↓
runtime executes tool
  ↓
tool result returns
  ↓
application injects tool result into context
  ↓
model continues
```

たとえば、modelが次のようなtool call候補を出すとする。

```json
{
  "tool": "search_web",
  "arguments": {
    "query": "LLM application architecture"
  }
}
```

この時点では、まだ検索が実行されたとは限らない。application layerが、toolが利用可能か、引数がschemaに合っているか、権限があるか、実行して安全かを確認する。そのうえでruntime / connectorがtoolを実行する。

# 11. 実行環境／コネクタ層（Runtime / Connector Layer）

runtime / connector layerは、実際に外部世界へ接続する層である。

一般的な技術用語では、次のように呼ばれる。

```plain text
runtime
tool runtime
connector layer
execution environment
sandbox
API client
plugin system
MCP server
function executor
```

ここで実行されるものには、次のようなものがある。

```plain text
- Web検索
- ファイル検索
- Python実行
- GitHub操作
- Notion更新
- Gmail検索・送信
- Google Drive読み書き
- Calendar予定作成
- database query
- shell command
```

ここは、副作用が発生しうる層である。読み取り、作成、更新、削除、送信、公開、課金、コード実行は、危険度が違う。

```plain text
read
create
update
delete
send
publish
pay
execute
```

したがって、toolは単なる能力追加ではない。permission、credential、side effect、auditの境界でもある。

```plain text
tool = capability + permission boundary + side effect boundary + audit boundary
```

# 12. エージェントループ／制御ループ（Agentic Loop / Orchestration Loop）

tool callが複数回続く場合、処理は単発の応答ではなくloopになる。

一般的な技術用語では、次のように呼ばれる。

```plain text
agent loop
agentic loop
orchestration loop
observe-think-act loop
plan-act-observe loop
control loop
```

典型的には、次のような流れになる。

```plain text
observe
  ↓
decide
  ↓
act / tool call
  ↓
observe result
  ↓
verify
  ↓
continue or stop
```

agentとは、勝手に動き続けるAIではない。信頼できるagentには、停止条件がある。

```plain text
- task completed
- budget exceeded
- tool failed
- information missing
- permission missing
- user approval required
- safety boundary reached
- uncertainty too high
- handoff required
```

止まることは失敗ではない。止まれることは、信頼できるagentの条件である。

# 13. 検証／後処理層（Validation / Post-processing Layer）

model outputやtool resultは、そのままユーザーへ返されるとは限らない。

一般的な技術用語では、次のように呼ばれる。

```plain text
post-processing
output validation
schema validation
response validation
formatting
citation checking
grounding check
consistency check
```

この層では、たとえば次のような処理が行われる。

```plain text
- JSONがschemaに合っているか
- 必須項目が欠けていないか
- tool結果と回答が矛盾していないか
- 引用が必要な箇所に引用があるか
- 出力形式がユーザー指定に合っているか
- 危険な内容が含まれていないか
- 最終回答として十分か
```

structured outputの場合、この層は特に重要である。JSONらしい文字列が出ることと、applicationが安全に扱える構造化出力であることは違う。

```plain text
JSON-like text
  ≠
validated structured output
```

parse、validate、repair、retry、handoffが必要になる。

# 14. 応答レンダリング／ストリーミング層（Response Rendering / Streaming Layer）

最後に、assistant outputがユーザーに見える形へ整えられる。

一般的な技術用語では、次のように呼ばれる。

```plain text
response rendering
streaming response
server-sent events
UI rendering
message rendering
markdown rendering
artifact rendering
```

ここでは、次のような処理が行われる。

```plain text
- Markdownとして表示
- コードブロックを整形
- 表を表示
- citationをリンク化
- 画像やファイルを表示
- streamingで逐次表示
- tool実行結果を折りたたみ表示
```

ユーザーから見ると、assistantがその場で文章を書いているように見える。実際には、modelによるtoken generation、applicationによる検証、runtimeのtool result、UI renderingが組み合わさって、最終的なassistant outputになる。

# 15. もっとも重要な分離（Key Separations）

この多層構造で、特に重要なのは次の分離である。

```plain text
user input ≠ prompt
prompt ≠ context
context ≠ memory
retrieval ≠ truth
model output ≠ truth
model output ≠ action
tool call ≠ tool execution
tool execution ≠ task success
JSON ≠ validated structured output
agent loop ≠ unlimited autonomy
assistant output ≠ model alone
```

これらを分けて考えないと、生成AIの挙動は「AIが勝手にやった」「AIが嘘をついた」「AIが覚えていた」「AIが検索した」といった粗い説明になってしまう。

しかし実際には、どこで何が起きたかを分解できる。

```plain text
誤答した
  → model generationの問題か
  → context不足か
  → retrieval失敗か
  → validation不足か

勝手に操作した
  → tool permissionの問題か
  → approval設計の問題か
  → application orchestrationの問題か

覚えていない
  → memoryに保存されていないのか
  → retrievalされていないのか
  → contextに注入されていないのか
```

生成AIを理解するとは、modelの内部だけを見ることではない。

user inputからassistant outputまでのあいだにある、application、context、policy、tool、runtime、validation、human judgmentの責任境界を見ることである。

# 16. Web掲載用の短いまとめ（Short Web Summary）

短くまとめるなら、次のように言える。

> 生成AIの応答は、ユーザー入力がそのままモデルに渡されて返ってくる単純な処理ではない。実際には、UI、application、instruction hierarchy、context assembly、memory / retrieval、policy / guardrail、model inference、tool runtime、validation、renderingが組み合わさっている。assistantの出力は、model単体ではなく、多層的なLLM application pipelineの結果である。

# 17. 関連するシリーズ内の位置づけ（Series Context）

このページは、`生成AIのしくみ 超詳解` 01〜08の横断まとめとして使える。

対応関係は次の通りである。

```plain text
01 prompt / request assembly
02 instruction hierarchy
03 context / memory / retrieval
04 tool calling / runtime
05 structured output / validation
06 memory / personalization
07 agentic loop / stop condition
08 model / application / runtime / human architecture
```

Web掲載時には、シリーズトップ、主要概念マップ、用語集、よくある誤解集と相互リンクさせるとよい。