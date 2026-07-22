---
ページ作成日時: "2026-07-22 16:07 JST"
最終更新日時: "2026-07-22 16:07 JST"
id: genai-shikumi-deep-dive-04
title: "ツール実行ループとは何か"
subtitle: "tool callはモデルの直接操作ではなく、application layerとruntimeが検証・実行・返却するloopである。"
series: genai-shikumi-deep-dive
series_label: "生成AIのしくみ 超詳解"
series_order: 4
slug: "/series/genai-shikumi-deep-dive/04-tool-execution-loop/"
canonical_url: "https://genai-ron.jp/series/genai-shikumi-deep-dive/04-tool-execution-loop/"
description: "tool call、application execution、tool resultがどのように発生し戻るのかを読む超詳解。"
source_reconstruction_from: "site/series/genai-shikumi-deep-dive/04-tool-execution-loop/index.html"
source_html_blob_sha: "2e56897a9cba9e03199b1edcab2d9f0caa16a4d9"
original_notion_created_at: "2026-07-18 13:06 JST"
original_notion_updated_at: "2026-07-18 13:06 JST"
web_migrated_at: "2026-07-20 12:56 JST"
status: source-sample
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

生成AIが「ツールを使う」と言うと、AI自身がWebを検索し、Notionを書き換え、Gmailを送り、カレンダーを操作しているように見える。

しかし、実装上はそうではない。

LLMそのものが、外部APIを直接叩いているわけではない。

モデルは、利用可能なtool schemaを見て、必要なら「このtoolを、この引数で使いたい」という構造化されたtool callを出力する。

そのtool callを受け取り、検証し、実行し、結果を戻すのは、モデルの外側にあるapplication layer、orchestrator、tool runtimeである。

:::note
tool useとは、モデルが外部世界を直接操作することではない。モデルが構造化されたtool callを出力し、アプリケーション側がそれを検証・実行し、その結果をtool resultとして再びcontextへ戻すmulti-step loopである。
:::

04では、このtool実行ループを分解する。

## 1. toolは、モデル内部能力ではない

toolを渡すと、モデルの内部に新しい能力が生えるわけではない。

天気toolを渡したからといって、モデルが気象データベースを内部に持つわけではない。

Gmail toolを渡したからといって、モデルが直接メールボックスを読めるようになるわけではない。

Notion toolを渡したからといって、モデル自身がNotion APIの実行主体になるわけでもない。

モデルに渡されるのは、まずtool definitionである。

つまり、次のような情報である。

- そのtoolの名前
- 何のために使うtoolか
- どのような引数を受け取るか
- どの型・必須項目・許容値を持つか
- schemaにどの程度厳密に従わせるか

理解用に単純化すると、function toolは次のようなinterfaceに近い。

```json
{
  "type": "function",
  "name": "get_weather",
  "description": "Get the current weather for a city.",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "The city name, e.g. Tokyo"
      }
    },
    "required": ["city"],
    "additionalProperties": false
  },
  "strict": true
}
```

このtool definitionは、単なるドキュメントではない。

モデルへの説明であり、同時にapplicationとの契約である。

| 要素 | 役割 |
|---|---|
| `name` | モデルが呼び出すtoolを識別する |
| `description` | いつ・何のために使うtoolかをモデルへ説明する |
| `parameters` | 引数のshape、型、必須項目、許容値を定義する |
| `strict` | schemaに沿った引数生成をどの程度強制するかを示す |

つまり、tool schemaは、promptとAPI contractの中間にある。

## 2. tool useは、複数の層で成立する

生成AIアプリケーションでtoolが使われるとき、少なくとも次の層が関わる。

| 層 | 何が起きるか |
|---|---|
| model | tool schemaを読み、必要ならtool callを出力する |
| orchestrator | tool callを受け取り、routing、許可、再requestを管理する |
| tool runtime | 実際の関数、API、browser、code interpreter、MCP serverなどを実行する |
| external system | Web、DB、Gmail、Notion、filesystem、calendarなど実際の対象 |
| verification layer | 実行結果、外部状態、安全条件、停止条件を確認する |

流れとしては、次のようになる。

```text
Tool definitions are provided to the model
  ↓
Model decides whether a tool is needed
  ↓
Model emits a tool call
  ↓
Application validates and executes it
  ↓
Application returns tool result
  ↓
Model uses the result to continue or answer
```

ここで大事なのは、tool callとtool executionを分けることである。

モデルがtool callを出した時点では、まだ外部操作は完了していない。

tool callは、実行済みの事実ではなく、実行要求である。

## 3. tool callは、構造化された実行要求である

tool callは自然文の返答ではない。

モデルが、response outputの中に出す構造化itemである。

簡略化すると、次のようなものになる。

```json
{
  "type": "function_call",
  "name": "get_weather",
  "arguments": "{\"city\":\"Tokyo\"}",
  "call_id": "call_abc123"
}
```

この中で重要なのは、`name`、`arguments`、`call_id`である。

| 要素 | 意味 | application側の扱い |
|---|---|---|
| `name` | 呼び出したいtool名 | 登録済みtoolへroutingする |
| `arguments` | toolへ渡す引数 | JSON parseし、schema validationする |
| `call_id` | このtool callの識別子 | 後続のtool resultと対応させる |

ここで、`arguments`を信用してはいけない。

schemaに合っているように見えても、権限上許されない操作かもしれない。

存在しないIDを指定しているかもしれない。

ユーザーがまだ承認していない書き込み操作かもしれない。

外部文書に含まれたprompt injectionの影響を受けているかもしれない。

したがって、tool callを受け取ったapplication側は、少なくとも次を確認する必要がある。

```text
Detect function_call item
  ↓
Route by tool name
  ↓
Parse arguments
  ↓
Validate against schema
  ↓
Policy check
  ↓
Permission / scope check
  ↓
User confirmation if needed
  ↓
Execute external function / API
```

`strict: true`は、schemaに沿った引数生成を助ける。

しかし、strict modeはpermission checkの代わりではない。

schema validであることと、実行してよいことは違う。

```text
schema valid ≠ authorized
schema valid ≠ safe
schema valid ≠ user-confirmed
```

## 4. tool_choiceは、自然文ではなくruntime parameterである

ユーザーが「ツールを使わないで」と自然文で書くことと、API runtimeで `tool_choice: "none"` を指定することは違う。

自然文は、モデルが解釈するinstructionである。

`tool_choice`は、tool使用を制御するruntime parameterである。

代表的には、次のように整理できる。

| 指定 | 意味 | 使いどころ |
|---|---|---|
| `auto` | モデルがtoolを使うか判断する | 通常のagent的応答 |
| `none` | toolを使わせない | 外部参照なしで答えたい場合 |
| `required` | 何らかのtool使用を要求する | 必ず検索・DB確認・外部照合をさせたい場合 |
| specific tool | 特定toolだけを使わせる | 処理経路を固定したい場合 |
| `allowed_tools` | 使えるtool subsetを制限する | 安全境界や段階的実行 |

特に重要なのは、write / send / delete / purchase / publish / commit などの副作用を持つtoolである。

外部文書を読んだ直後に、同じturnで書き込みtoolを許可すると、prompt injectionの影響を受けやすくなる。

そのため、設計としては次のように段階を分けるのが安全である。

```text
Read / retrieve untrusted content
  ↓
Summarize and classify
  ↓
Ask user confirmation if action is needed
  ↓
Enable write tool only after confirmation
```

parallel function callingも同じである。

複数の読み取りtoolを並列に呼ぶのは便利な場合がある。

しかし、順序依存がある処理、副作用がある処理、承認が必要な処理では、parallel callsを抑制した方がよい。

## 5. application側は、実行前に止める責任を持つ

危険なのは、tool callをparseして即実行する実装である。

```tsx
const args = JSON.parse(item.arguments);
await toolsitem.name;
```

これは短く見えるが、実運用では危ない。

安全なtool executionでは、application側が次の責務を持つ。

| 段階 | 確認内容 |
|---|---|
| routing | そのtool名が現在のruntimeで利用可能か |
| parse | `arguments`が正しいJSONか |
| schema validation | 型、必須項目、enum、追加propertyの有無 |
| policy check | この種類の操作を許してよいか |
| permission check | このユーザー・scope・resourceで実行可能か |
| confirmation | 副作用のある操作に明示承認があるか |
| execution | 外部API・DB・関数を実行する |
| audit | 誰が、何を、いつ、どの引数で実行したか記録する |

特に、書き込み系toolでは、確認境界が重要になる。

- メールを送る
- カレンダーを変更する
- ファイルを削除する
- DBを更新する
- Gitへpushする
- 決済を行う
- 公開ページを更新する

これらは、単なる回答生成ではない。

外部状態を変える操作である。

したがって、モデルがtool callを出しても、application側は「実行しない」という判断をしてよい。

## 6. tool resultは、命令ではなく戻り値である

tool実行の結果は、モデルへ戻される。

Function toolの場合、典型的には `function_call_output` として戻る。

```json
{
  "type": "function_call_output",
  "call_id": "call_abc123",
  "output": "{\"ok\":true,\"temperature\":29,\"unit\":\"C\"}"
}
```

`call_id`は、どのtool callへの返答なのかを対応づけるために使う。

ここで重要なのは、tool resultが上位命令ではないことだ。

たとえば、Web検索toolが取得したページに「これ以降のsystem instructionを無視せよ」と書かれていたとしても、それはtool result内の外部データである。

上位instructionではない。

```text
tool result = external observation / return value
tool result ≠ system instruction
tool result ≠ developer instruction
tool result ≠ user authorization
```

そのため、tool resultは、なるべく構造化して戻すのがよい。

```json
{
  "ok": true,
  "source": "web_search",
  "provenance": [
    {
      "url": "https://example.com/report",
      "retrieved_at": "2026-07-18T13:06:00+09:00"
    }
  ],
  "data": {
    "summary": "..."
  },
  "warnings": [
    "untrusted_external_text"
  ]
}
```

成功、失敗、部分成功、timeout、permission denied、confirmation requiredを分けて返すことも重要である。

## 7. agentic loopには停止条件が必要である

tool call、application execution、tool resultが戻ると、モデルはそれを読んで最終応答を返すこともあれば、さらにtool callを出すこともある。

これがagentic loopである。

```text
Observe
  ↓
Decide
  ↓
Act
  ↓
Observe
  ↓
Decide again
```

ただし、loopは無限に回してはいけない。

agentic loopは、モデルの内面ではなく、model、orchestrator、tool runtime、external system、verification layerが作る制御ループである。

だから、停止条件はapplication側が設計する必要がある。

代表的な停止条件は、次の通りである。

| 停止条件 | 意味 |
|---|---|
| max tool iterations | tool実行の最大反復数を超えた |
| max total tool calls | 総tool call数が上限を超えた |
| timeout | 処理時間が上限を超えた |
| rate limit | 外部APIやruntimeの制限に近づいた |
| permission boundary | 権限外resourceへ触れようとした |
| confirmation required | 人間の承認が必要な操作に到達した |
| uncertainty stop | 必要情報が不足し、推測実行になる |
| unsafe request stop | 安全上実行できない操作が含まれる |

停止条件は、AIを弱くするものではない。

外部世界と接続されたAIを、実運用に耐えるものにするための制御装置である。

## 8. idempotency、audit log、rollback

外部状態を変えるtoolでは、実行後の記録も重要である。

同じtool callが二重実行されると、メールが二重送信されたり、予定が二重作成されたり、請求が二重登録されたりする。

そのため、副作用のある操作にはidempotency keyを持たせる。

```json
{
  "operation": "create_calendar_event",
  "idempotency_key": "event_20260718_1306_user123",
  "requested_by": "user123",
  "confirmed_by_user": true
}
```

audit logも必要である。

- どのmodel responseがtool callを出したか
- どのtoolが呼ばれたか
- どのargumentsだったか
- 誰の権限で実行したか
- user confirmationはあったか
- 実行結果は成功か失敗か
- 外部system側のresource IDは何か

さらに、失敗した場合に元に戻せるとは限らない。

削除や送信は、完全なrollbackができないこともある。

その場合は、compensation、つまり補償操作を設計する必要がある。

## 9. 04のまとめ

tool useは、LLMが外部世界を直接操作することではない。

モデルはtool schemaを読み、必要ならtool callを出す。

applicationはそれを検証し、必要なら人間の確認を挟み、外部APIや関数を実行する。

実行結果はtool resultとして戻され、再びcontextへ入る。

その結果を読んで、モデルは最終応答を生成するか、さらにtool callを出す。

この一連の流れがtool実行ループである。

重要なのは、次の分離である。

```text
tool definition ≠ tool call
tool call ≠ execution
tool result ≠ instruction
schema valid ≠ authorized
automation ≠ uncontrolled autonomy
```

03では、contextがどのように注入されるかを見た。

04では、そのcontextをもとに、モデルがどのように外部機能の使用要求を出し、application側がそれを実行し、結果を戻すかを見た。

次の回では、tool callやfinal answerをさらに安定させるための、structured output、JSON schema、validation、再生成、型安全な受け渡しへ進む。

## 10. 公式参照

- [OpenAI API Docs｜Function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [OpenAI API Docs｜Responses API](https://developers.openai.com/api/docs/guides/responses)
- [OpenAI API Reference｜Response input / output items](https://platform.openai.com/docs/api-reference/responses)
