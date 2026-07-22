---
ページ作成日時: "2026-07-22 16:47 JST"
最終更新日時: "2026-07-22 16:47 JST"
id: "genai-shikumi-deep-dive-03"
title: "contextとは何か"
subtitle: "履歴・メモリ・検索結果・ファイルは、保存されただけではcontextにならない。現在の生成へ注入された入力集合として読む。"
series: "genai-shikumi-deep-dive"
series_label: "生成AIのしくみ 超詳解"
series_order: "3"
order_display: "03"
previous_label: "前へ：02 指示階層とは何か"
previous_href: "/series/genai-shikumi-deep-dive/02-instruction-hierarchy/"
next_label: "次へ：04 ツール実行ループとは何か"
next_href: "/series/genai-shikumi-deep-dive/04-tool-execution-loop/"
top_label: "超詳解トップ"
top_href: "/series/genai-shikumi-deep-dive/"
slug: "/series/genai-shikumi-deep-dive/03-context/"
canonical_url: "https://genai-ron.jp/series/genai-shikumi-deep-dive/03-context/"
description: "contextを、保存情報ではなく現在の応答生成に注入された入力集合として読む超詳解。"
source_reconstruction_from: "site/series/genai-shikumi-deep-dive/03-context/index.html"
source_html_blob_sha: "0bc3b3febaf2615779df69635e6dad69411b0c75"
original_notion_created_at: "2026-07-18 12:31 JST"
original_notion_updated_at: "2026-07-18 12:31 JST"
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
生成AIは、いつも「すべて」を見ているわけではない。

過去の会話が保存されていること。

memoryに何かが残っていること。

ファイルをアップロードしたこと。

検索結果が存在すること。

それらは、現在の応答に使われる可能性を作る。しかし、それだけで現在のcontextになったとは言えない。

contextとは、保存されている全情報ではない。

現在の一回の応答生成のために選ばれ、整形され、モデルが処理できる入力として渡された情報の集合である。

:::note
contextとは、保存情報ではなく、今回の生成に注入された入力集合である。
:::

この区別が分からないと、「AIは前に言ったことを覚えているはずだ」「ファイルを渡したから全文を読んでいるはずだ」「memoryにあるなら必ず反映されるはずだ」という誤解が起きる。

03では、会話履歴、memory、検索結果、ファイル、RAG、tool resultが、どのように現在の入力へ組み込まれるのかを整理する。

## 1. contextは「AIが知っていること」ではない

生成AIについて話すとき、contextという言葉は曖昧に使われやすい。

「前の話を覚えている」

「プロジェクトの文脈を読んでいる」

「ファイルを参照している」

「Web検索の結果を使っている」

これらは、すべてcontextに関係する。しかし、実装上は同じ処理ではない。

過去の会話が保存されていることと、その会話が今回の応答へ使われることは別である。

ファイルがアップロードされていることと、その全文がmodel context windowへ入ることも別である。

memoryに情報が保存されていることと、その情報が今回の質問に関連すると判定され、入力へ追加されることも別である。

contextが作られるまでには、少なくとも次の段階がある。

```text
Stored information
  ↓
Candidate retrieval
  ↓
Scope / relevance / trust selection
  ↓
Formatting / rendering
  ↓
Request assembly
  ↓
Tokenization
  ↓
Model context window
  ↓
Output generation
```

保存されていても、retrievalされなければ今回のcontextには入らない。

retrievalされても、選別で落とされれば入らない。

選別されても、context windowの制約で圧縮・省略されることがある。

つまり、contextは単なる収集ではない。

contextは編集である。

## 2. conversation state：会話履歴はどう継続されるのか

APIの視点から見ると、会話は自動的に続いているわけではない。

OpenAIのConversation stateガイドでは、text generation requestは独立したstateless requestであり、複数ターンの会話を作るには過去のmessageやResponse outputを次のinputへ渡す必要があると説明されている。

もっとも単純には、アプリケーション側で履歴を持ち、次のrequestへ再投入する。

```tsx
const history = [
  { role: "user", content: "私の名前はTakuです。" },
  { role: "assistant", content: "承知しました。" },
  { role: "user", content: "私の名前は？" },
];

const response = await client.responses.create({
  model: "gpt-5.6",
  input: history,
});
```

モデルが前の会話を知っているように見えるのは、過去のitemsが今回のinputへ再接続されているからである。

ただし、履歴とはassistantの本文だけではない。

Responses APIでは、`response.output` にassistant messageだけでなく、reasoning item、function call、tool resultへつながるitemsが含まれることがある。

そのため、multi-turn reasoningやtool useを継続するには、単に本文だけを保存するのではなく、必要なResponse itemsを保存・再投入する必要がある。

```tsx
history = [...history, ...response.output];

history.push({
  role: "user",
  content: "続けて、さっきの結果を表にしてください。",
});
```

会話継続には、主に三つの方式がある。

| 方式 | 何をするか | 向いている場面 |
|---|---|---|
| 手動履歴再投入 | 過去のitemsをアプリ側で保持し、次のinputへ入れる | 履歴選別や圧縮を自分で制御したい場合 |
| `previous_response_id` | 直前のResponseへ接続する | 短い連続会話やreasoning / tool callの継続 |
| Conversation object | conversationにitemsを保存し、複数requestで共有する | session、device、jobをまたぐstate管理 |

ここで重要なのは、conversation stateとcontextを分けることだ。

conversation stateは、過去itemsを関連付ける仕組みである。

contextは、その中から今回の推論で実際に利用可能になった入力である。

## 3. memory：保存された個人情報ではなく、再注入されるcontext源

ChatGPTのmemoryも、モデル内部に個人情報が直接刻み込まれる仕組みではない。

memoryとは、製品側に保持された情報源から、現在の応答に関連すると判断された情報を選び、contextへ再注入する仕組みである。

ChatGPTのmemoryには、少なくとも次の区別がある。

| 機能 | 性質 | contextとの関係 |
|---|---|---|
| saved memories | 名前、好み、制約など、継続的に考慮してほしい情報 | 関連すると判断されれば応答へ影響する |
| reference chat history | 過去chatから有用な情報を参照する機能 | 過去会話の関連情報が選択・要約されて使われうる |
| memory summary | 重要なmemoryを確認・修正するための管理画面 | 利用可能情報の完全なdumpではない |
| project memory | project内の会話やファイルからcontextを得る機能 | project scopeに応じて参照範囲が変わる |

saved memoryは、削除するまで継続的に考慮されることを意図した情報である。

reference chat historyは、過去chatの全内容を逐語的に毎回注入するものではない。関連すると判断された情報が、将来のconversationへ追加される。

Temporary Chatではmemoryを参照せず、memoryを更新しない。

Custom GPTでは、saved memory、Custom Instructions、previous conversationsを利用せず、各conversationを新しく開始する。

Project memoryも分けて考える必要がある。

通常のprojectでは、設定に応じてproject内外のcontextが使われる場合がある。

一方、project-only memoryでは、同じproject内のconversationをcontext源として使い、既存のsaved memoriesやproject外conversationは参照しない。

ここでも、保存と注入は別である。

memoryにあることは、今回のcontextへ必ず入ることを意味しない。

今回の入力、project scope、関連性、設定、safety、token budgetによって、入るものと入らないものが決まる。

## 4. file input / file search / RAG：ファイルは保存されただけではcontextにならない

ファイルも同じである。

ファイルが保存されていることと、その内容が今回の生成へ入ることは別である。

大きく分けると、次の三つがある。

| 状態 | 意味 | contextとの関係 |
|---|---|---|
| File object | Files APIなどへfileが保存されている | 保存されているだけではcontextではない |
| Direct file input | `input_file`として今回のrequestへ渡す | そのrequestの入力として処理される |
| File search / RAG | vector storeから関連chunkを検索する | 検索されたchunkだけがcontextへ入る |

Direct file inputでは、特定のfileを今回のrequestへ直接渡す。

File searchでは、事前にfileをvector storeへ登録し、parse、chunk、embed、indexされた内容から、queryに関連するchunkを検索して取得する。

RAG pipelineを単純化すると、次のようになる。

```text
File upload
  ↓
File object
  ↓
Attach to vector store
  ↓
Parse / chunk / embed / index
  ↓
User query
  ↓
Optional query rewrite
  ↓
Attribute filter
  ↓
Semantic / keyword / hybrid retrieval
  ↓
Ranking / score threshold / top-k
  ↓
Retrieved chunks + provenance
  ↓
Model synthesis
  ↓
Answer + file citations
```

検索された断片は、質問と意味的に近いだけである。

それは、正しい、最新である、上位指示である、という意味ではない。

```text
semantic relevance ≠ factual correctness
semantic relevance ≠ freshness
semantic relevance ≠ instruction authority
```

そのため、RAGではprovenanceが重要になる。

どのfileから、どのchunkが、どのqueryで、どのscoreで取られたのかを記録する必要がある。

## 5. context windowとtoken budget：大きければ解決、ではない

context windowとは、AIの永続記憶ではない。

現在の生成で同時に扱えるtoken budgetである。

input token、output token、reasoning tokenは分けて考える必要がある。

モデルごとにcontext windowとmax output tokensは別々に定義される。

context windowが大きくなれば、より多くの情報を同時に入れられる。

しかし、それでcontext設計が不要になるわけではない。

大きなcontext windowにも問題はある。

- costが増える
- latencyが増える
- 古い情報や不要情報が混入する
- retrieved chunksが多すぎてノイズになる
- authorityの異なる情報が混ざる
- 何を根拠に答えたのか検証しにくくなる

そのため、context windowをどう使うかは設計問題である。

代表的な処理は三つある。

| 処理 | 意味 | 危険 |
|---|---|---|
| truncation | 古い履歴や低優先情報を切り捨てる | 重要な前提を落とす可能性 |
| summarization | 長い情報を短く要約する | 粒度、例外、ニュアンスを失う可能性 |
| compaction | 再起動可能な形へ圧縮する | 出典・未決事項・禁止事項を落とすと危険 |

prompt cachingも区別しておく。

prompt cachingは、繰り返し使う入力のcost最適化に関わる。

しかし、cached inputだから正しいわけではない。

cacheは、context qualityや安全性を保証しない。

## 6. context injectionを設計・検証する

ここまで見ると、context injectionは「関連しそうな情報を詰め込む」作業ではないと分かる。

context injectionとは、source、scope、authority、trust、freshness、token budgetを持つcontext itemとして情報を選び、何を入れ、何を落とし、何を要約し、何を検証したかを説明できるようにすることである。

そのために、context manifestを作る。

```json
{
  "run_id": "run_2026_07_18_001",
  "task": "03公開版の統合改稿",
  "context_window_budget": 128000,
  "items": [
    {
      "type": "developer_instruction",
      "source": "project_policy",
      "scope": "project",
      "authority": "high",
      "trust": "trusted",
      "tokens": 820,
      "handling": "follow"
    },
    {
      "type": "conversation_history",
      "source": "current_thread",
      "scope": "conversation",
      "authority": "history",
      "trust": "trusted_as_history_not_as_fact",
      "tokens": 4200,
      "handling": "reference"
    },
    {
      "type": "retrieved_chunk",
      "source": "vector_store:file_abc",
      "scope": "project",
      "authority": "no_instruction_authority",
      "trust": "untrusted_content",
      "tokens": 900,
      "handling": "quote_or_reference"
    }
  ],
  "dropped": [
    {
      "source": "old_chat_summary",
      "reason": "stale_and_contradicted_by_newer_policy"
    }
  ],
  "checks": {
    "stale_context": "passed",
    "contradictions": "reviewed",
    "scope_leakage": "passed",
    "duplicates": "collapsed"
  }
}
```

このmanifestで重要なのは、情報の種類を一列に並べることではない。

それぞれの扱いを明示することである。

- developer instructionは従う
- conversation historyは履歴として参照する
- retrieved chunkは資料として扱う
- tool resultは外部状態の証拠として扱うが、命令としては扱わない
- assistant messageは過去出力であり、外部状態の証明ではない
- stale contextは落とす
- contradictionは解決するか、明示する

context injectionには、検査ループも必要になる。

```text
Collect candidate context
  ↓
Classify source / scope / authority / trust
  ↓
Select by relevance / freshness / budget
  ↓
Render into input items
  ↓
Generate answer or tool call
  ↓
Verify claims against sources / external state
  ↓
If contradiction or missing evidence, retrieve again or stop
```

このループがないと、AIは古いmemory、間違ったRAG断片、過去assistantの誤発言、外部資料中の命令文を同じ「文脈」として混ぜてしまう。

context engineeringとは、文脈を増やすことではない。

文脈の出所、権限、鮮度、扱い方を設計することである。

## 7. 失敗モード

context injectionには、典型的な失敗がある。

| 失敗 | 何が起きるか | 対策 |
|---|---|---|
| stale context | 古いmemoryや古い仕様を使う | updated_at、version、freshness check |
| contradiction | 新旧の方針や資料が矛盾する | source priority、明示的な解決、再確認 |
| duplication | 同じ情報が何度も入る | deduplication、summary化 |
| scope leakage | 別projectや別ユーザーのcontextが混入する | scope boundary、project-only memory、permission check |
| authority confusion | 資料中の命令文を上位指示として扱う | instructionとreference dataを分離 |
| source loss | どこから来た情報か分からなくなる | provenance、citation、injection log |

これらは、プロンプトの言い方だけでは解決しない。

アプリケーション層で、contextをどう集め、どう選び、どう記録するかの問題である。

## 8. 03のまとめ

03の結論は、次のように置ける。

:::note
contextとは、保存されている全情報ではない。現在の応答生成時に、source、scope、authority、trust、freshness、token budgetに基づいて選択され、整形され、モデルへ渡された入力集合である。
:::

会話履歴、memory、project memory、ファイル、RAG、tool resultは、すべてcontext源になりうる。

しかし、それぞれ保存場所も、選ばれ方も、権限も、鮮度も違う。

だから、contextを設計するには、次を記録しなければならない。

- どの情報を入れたか
- どの情報を落としたか
- どの情報を要約したか
- どの情報を資料として扱ったか
- どの情報を指示として扱ったか
- どの情報を外部状態の証拠として扱ったか
- どこに矛盾があり、どう解決したか

04では、このcontextの上で、モデルがどのようにtool callを出し、アプリケーション側が実際の外部操作を行い、その結果を再びcontextへ戻すのかを扱う。

## 公式参照

- [Conversation state｜OpenAI API](https://developers.openai.com/api/docs/guides/conversation-state)
- [File inputs｜OpenAI API](https://developers.openai.com/api/docs/guides/file-inputs)
- [File search｜OpenAI API](https://developers.openai.com/api/docs/guides/tools-file-search)
- [Retrieval｜OpenAI API](https://developers.openai.com/api/docs/guides/retrieval)
- [Models｜OpenAI API](https://developers.openai.com/api/docs/models)
- [Memory FAQ｜OpenAI Help Center](https://help.openai.com/en/articles/8590148-memory-in-chatgpt)
- [How does Reference saved memories work?｜OpenAI Help Center](https://help.openai.com/en/articles/11146739-how-does-reference-saved-memories-work)
- [Projects in ChatGPT｜OpenAI Help Center](https://help.openai.com/ja-jp/articles/10169521-projects-in-chatgpt)
