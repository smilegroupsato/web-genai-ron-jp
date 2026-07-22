---
ページ作成日時: "2026-07-22 16:47 JST"
最終更新日時: "2026-07-22 16:47 JST"
id: "genai-shikumi-deep-dive-05"
title: "構造化出力とは何か"
subtitle: "JSON、schema、validation、repair、handoffを、applicationが受け取れる契約として読む。"
series: "genai-shikumi-deep-dive"
series_label: "生成AIのしくみ 超詳解"
series_order: "5"
order_display: "05"
previous_label: "前へ：04 ツール実行ループとは何か"
previous_href: "/series/genai-shikumi-deep-dive/04-tool-execution-loop/"
next_label: "次へ：06 memoryとは何か"
next_href: "/series/genai-shikumi-deep-dive/06-memory/"
top_label: "超詳解トップ"
top_href: "/series/genai-shikumi-deep-dive/"
slug: "/series/genai-shikumi-deep-dive/05-structured-output/"
canonical_url: "https://genai-ron.jp/series/genai-shikumi-deep-dive/05-structured-output/"
description: "構造化出力を、JSONらしい文字列ではなく、schemaとvalidationを含むapplication contractとして読む超詳解。"
source_reconstruction_from: "site/series/genai-shikumi-deep-dive/05-structured-output/index.html"
source_html_blob_sha: "3f059939ebf9376ad7572fb8a96d672093421441"
original_notion_created_at: "2026-07-18 14:34 JST"
original_notion_updated_at: "2026-07-18 14:34 JST"
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
生成AIに「JSONで返して」と頼むことは、いまでは珍しくない。

問い合わせ分類、議事録のaction item抽出、見積依頼の項目整理、UI表示用データ生成、次のworkflowへのhandoff。

人間が読む文章ではなく、アプリケーションが処理できる形で返してほしい場面は多い。

しかし、「JSONで返して」と「安全にアプリケーションへ渡せる」は違う。

JSONらしく見える文字列が返ってきても、それがparseできるとは限らない。

parseできても、期待したschemaに合っているとは限らない。

schemaに合っていても、業務上そのまま使ってよいとは限らない。

:::note
構造化出力とは、モデルに「きれいなJSONを書いてもらうこと」ではない。applicationが受け取れる契約をschemaとして定義し、モデル出力をその契約に沿わせ、parse / validate / refusal / retry / repair / handoffまで含めて管理することである。
:::

05では、この構造化出力を分解する。

## 1. 「JSONで返す」は、まだ出発点でしかない

たとえば、問い合わせ分類をAIに依頼するとする。

```text
次の問い合わせを分類して、JSONで返してください。
```

返ってくるものは、次のような形かもしれない。

```json
{
  "category": "billing",
  "priority": "high",
  "needs_reply": true
}
```

見た目としては十分に扱いやすい。

しかし、application側から見ると、確認すべきことは多い。

- JSONとしてparseできるか
- 想定したkeyが存在するか
- valueの型が正しいか
- enumの範囲に収まっているか
- 不要なkeyが混ざっていないか
- null、空文字、unknownの扱いが決まっているか
- 業務上、その値を使ってよいか
- safety refusalや不完全回答を区別できるか

つまり、段階はこう分かれる。

```text
JSON-looking text ≠ valid JSON
valid JSON ≠ schema-valid data
schema-valid data ≠ business-valid decision
business-valid decision ≠ safe action
```

自然文なら、人間が曖昧さを補える。

「これは請求関連で、かなり急ぎです。返信が必要です」と書かれていれば、人間は意味を取れる。

しかし、DB保存、Slack通知、担当者割り当て、CRM更新、次のtool callへの入力に使うなら、機械が安定して読める構造が必要になる。

## 2. JSON syntax、schema adherence、business validationは違う

JSON syntaxとは、文字列がJSONとしてparseできることである。

これは、最低限の構文チェックである。

たとえば、これはvalid JSONである。

```json
{
  "priority": "urgent"
}
```

しかし、applicationが期待するpriorityが `low` / `medium` / `high` の三択だった場合、`urgent` はschema上は不正である。

逆に、次の出力は人間には意味が分かるが、JSONとしては壊れている。

```json
{
  "priority": high,
  "needs_reply": yes
}
```

`high` も `yes` も文字列としてquoteされていないため、JSON parserは失敗する。

さらに、schema上正しくても、業務上使えない場合がある。

たとえば、`customer_id` が文字列として正しく存在していても、そのIDが実在しない、権限のない顧客である、すでに退会済みである、ということはありうる。

| 段階 | 見るもの | 失敗例 |
|---|---|---|
| JSON syntax | JSONとしてparseできるか | quote漏れ、末尾comma、Markdown fence混入 |
| schema adherence | 期待した構造に合うか | required欠落、型違い、enum外、余計なproperty |
| business validation | 業務ルール上使えるか | 存在しないID、期限切れstatus、不許可action |

構造化出力を設計するとは、この三段階を混ぜないことである。

## 3. JSON Schemaはapplication contractである

JSON Schemaは、AIの出力形式を整えるための飾りではない。

モデル、validator、workflowのあいだに置かれるapplication contractである。

簡単な問い合わせ分類schemaは、たとえば次のように書ける。

```json
{
  "type": "object",
  "properties": {
    "category": {
      "type": "string",
      "enum": ["billing", "technical", "sales", "other"]
    },
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high"]
    },
    "needs_reply": {
      "type": "boolean"
    }
  },
  "required": ["category", "priority", "needs_reply"],
  "additionalProperties": false
}
```

ここで重要なのは、次の要素である。

| 要素 | 役割 |
|---|---|
| `type` | object、array、string、number、integer、boolean、nullなどの型を定義する |
| `properties` | objectが持つkeyと、そのvalueの型を定義する |
| `required` | 必ず存在すべきfieldを定義する |
| `enum` | 許可される値を限定する |
| `additionalProperties: false` | 想定外のkeyを拒否する |
| `items` | arrayの要素型を定義する |

`additionalProperties: false` は特に重要である。

余計なkeyを許すと、モデルが説明文や提案、confidenceのようなfieldを勝手に足すことがある。

それ自体が悪いわけではないが、application contractとして受け取るなら、想定外のfieldは失敗として扱った方がよい。

## 4. null、unknown、empty、not applicableを分ける

構造化出力では、「値がない」を雑に扱うと壊れやすい。

たとえば、問い合わせから希望日時を抽出するschemaを考える。

```json
{
  "type": "object",
  "properties": {
    "preferred_date": {
      "type": ["string", "null"]
    },
    "preferred_date_status": {
      "type": "string",
      "enum": ["present", "unknown", "not_applicable", "withheld"]
    }
  },
  "required": ["preferred_date", "preferred_date_status"],
  "additionalProperties": false
}
```

ここでは、単に `preferred_date: null` とするだけではなく、なぜnullなのかをstatusで分けている。

| 状態 | 意味 |
|---|---|
| `present` | 値が抽出できた |
| `unknown` | 入力からは分からない |
| `not_applicable` | このcaseでは該当しない |
| `withheld` | 安全上または権限上、出さない |

空文字、null、unknown、該当なし、拒否は同じではない。

この区別は、後続workflowの分岐に直結する。

## 5. JSON modeとStructured Outputs

JSON modeとStructured Outputsは似て見えるが、目的が違う。

JSON modeは、valid JSONを出しやすくする方向の仕組みである。

一方、Structured Outputsは、開発者が定義したJSON Schemaに出力を沿わせるための仕組みである。

```text
JSON mode:
  valid JSONを出すことを助ける

Structured Outputs:
  指定したJSON Schemaに合う出力を得るための仕組み
```

たとえばJSON modeでは、JSONとしてparse可能な出力は期待できる。

しかし、`category` が `money_problem` になったり、`priority` が `urgent` になったり、`needs_reply` が文字列の `"yes"` になったりする可能性は残る。

Structured Outputsでは、schemaを指定することで、こうした構造上のずれを減らす、または避けることを狙う。

ただし、Structured Outputsを使えばapplication validationが不要になるわけではない。

schemaは出力形式の契約である。

業務上の正しさ、権限、安全な実行許可までは、application側で確認する。

## 6. response schemaとtool arguments schemaは違う

04では、function toolのarguments schemaを扱った。

05で扱うresponse schemaは、それと似ているが、目的が違う。

| schema | 何を制約するか | 主な用途 |
|---|---|---|
| function tool arguments schema | モデルがtool callで出すarguments | 外部関数を安全に呼ぶため |
| response schema | モデルがユーザーまたはapplicationへ返すfinal output | 分類、抽出、UI生成、DB保存、workflow handoff |

前者は「何を実行したいか」を制約する。

後者は「何を返すか」を制約する。

```text
tool arguments schema:
  actの入口を制約する

response schema:
  observe / decide の結果をapplicationへ渡す出口を制約する
```

この区別がないと、構造化出力とtool callingが混ざってしまう。

## 7. Structured Outputsとstrict mode

Structured Outputsでは、モデルの最終応答をJSON Schemaに沿った形で受け取る。

概念的には、次のような構成になる。

```json
{
  "text": {
    "format": {
      "type": "json_schema",
      "name": "support_ticket_classification",
      "description": "Classify a support ticket for workflow routing.",
      "schema": {
        "type": "object",
        "properties": {
          "category": {
            "type": "string",
            "enum": ["billing", "technical", "sales", "other"]
          },
          "priority": {
            "type": "string",
            "enum": ["low", "medium", "high"]
          },
          "needs_reply": {
            "type": "boolean"
          }
        },
        "required": ["category", "priority", "needs_reply"],
        "additionalProperties": false
      },
      "strict": true
    }
  }
}
```

`strict: true` は、schema adherenceを強める。

しかし、それは安全保証ではない。

```text
strict schema adherence ≠ factual correctness
strict schema adherence ≠ business validity
strict schema adherence ≠ authorization
strict schema adherence ≠ safe action
```

たとえば、schema上は `priority: "high"` が正しくても、本当にhighなのかは別問題である。

`customer_id` がstringとして正しくても、そのcustomerが実在するかはDBで確認する必要がある。

`action: "refund"` がenum内でも、返金してよいかは権限と業務ルールで確認する必要がある。

また、安全上回答できない場合には、schemaに沿った通常出力ではなくrefusal branchが返ることがある。

これを「壊れたJSON」として修復しようとしてはいけない。

refusalは別branchとして扱う。

## 8. parse / validate / branch

構造化出力のapplication側処理は、次のように考える。

```text
Receive model response
  ↓
Check refusal / safety branch
  ↓
Parse JSON
  ↓
Validate against JSON Schema
  ↓
Validate against business rules
  ↓
Normalize to domain model
  ↓
Branch workflow
  ↓
Log result
```

ここで大事なのは、model outputを即DB保存しないことである。

まずparseする。

次にschema validationを行う。

そのうえでbusiness validationを行う。

失敗の種類によって、進む先は違う。

| 失敗 | 意味 | 次の処理 |
|---|---|---|
| parse error | JSONとして読めない | repairまたはretry |
| schema validation error | 構造契約に合わない | retryまたはfailure branch |
| business validation error | 業務上使えない | human review、clarification、停止 |
| refusal | 安全上、通常回答ではない | safety branch |
| incomplete | 情報不足 | 追加質問、tool再実行、保留 |

構造化出力は、成功だけでなく、失敗を正しく分岐させるための設計である。

## 9. repair / retry / regenerate

repair、retry、regenerateは同じではない。

| 処理 | 意味 | 向いている失敗 |
|---|---|---|
| repair | 既存出力を修復する | 軽微なJSON構文エラー、Markdown fence除去 |
| retry | 同じ入力で再生成する | schema違反、required欠落、enum外 |
| regenerate | promptやcontextを調整して再生成する | semantic mismatch、schema設計との不整合 |
| clarify | ユーザーへ追加質問する | 入力情報不足、曖昧な意図 |
| human review | 人間確認へ送る | 業務判断、権限判断、リスク判断 |
| stop | 処理を止める | safety refusal、危険操作、retry上限超過 |

retryを万能視してはいけない。

同じ失敗が続く場合、schemaが現実の入力に合っていない、必要なcontextが足りない、あるいはモデルに任せてはいけない判断をさせている可能性がある。

そのため、retryには上限とlogが必要である。

```tsx
 type StructuredOutputRetryLog = {
  attempt: number;
  failureType:
    | "parse_error"
    | "schema_validation_error"
    | "business_validation_error"
    | "refusal"
    | "incomplete"
    | "semantic_mismatch";
  actionTaken:
    | "deterministic_repair"
    | "llm_repair"
    | "retry"
    | "regenerate"
    | "clarify_user"
    | "rerun_tool"
    | "human_review"
    | "stop";
  reason: string;
  timestamp: string;
};
```

失敗した出力を捨てるだけでは、改善できない。

何が失敗し、どの修復を試し、なぜ止めたのかを記録することで、workflowは検証可能になる。

## 10. 型安全なapplication handoff

最終的にapplicationが欲しいのは、単なるJSONではない。

validated outputを、業務上使えるdomain objectへ変換することである。

TypeScriptならZod、PythonならPydanticのようなruntime validation layerを置くことが多い。

```tsx
const TicketClassification = z.object({
  category: z.enum(["billing", "technical", "sales", "other"]),
  priority: z.enum(["low", "medium", "high"]),
  needsReply: z.boolean(),
  confidence: z.number().min(0).max(1),
  evidence: z.array(z.string())
});
```

ここで重要なのは、schema-validなJSONをそのままDB保存しないことである。

通常は、次のような変換を挟む。

```text
schema-valid JSON
  ↓
runtime validation
  ↓
normalization
  ↓
domain model
  ↓
workflow handoff
```

domain modelには、値そのものだけでなく、周辺情報も持たせる。

- schema version
- model name / version
- prompt version
- validation status
- confidence
- provenance
- retry count
- human review status
- created_at
- audit_id

たとえば、handoff manifestは次のように設計できる。

```tsx
 type StructuredOutputHandoffManifest = {
  schemaName: string;
  schemaVersion: string;
  model: string;
  promptVersion?: string;
  outputStatus:
    | "valid"
    | "repaired"
    | "retried_valid"
    | "needs_human_review"
    | "rejected";
  validation: {
    jsonParsed: boolean;
    schemaValid: boolean;
    businessValid: boolean;
    errors?: string[];
  };
  provenance: {
    inputSources: string[];
    toolResults?: string[];
    generatedAt: string;
  };
  retryCount: number;
  handoffAllowed: boolean;
  nextWorkflow?: string;
};
```

このmanifestがあることで、後続のworkflowは「AIがそう言ったから」ではなく、「どのschemaで、どの検証を通過し、どの状態で渡されたか」を見て処理できる。

## 11. 05のまとめ

構造化出力は、きれいなJSONを書かせるテクニックではない。

それは、生成AIをapplication workflowへ接続するための境界設計である。

JSON syntax、schema adherence、business validation、safety refusal、retry、repair、typed handoffを分けて扱うことで、AI出力は初めて後続処理に渡せる。

05の結論は、次のようにまとめられる。

```text
Prompt asks for structured output
  ↓
Model generates JSON-like or schema-constrained output
  ↓
Application checks refusal
  ↓
Application parses JSON
  ↓
Application validates schema
  ↓
Application validates business rules
  ↓
Application repairs / retries / stops if needed
  ↓
Application converts to domain model
  ↓
Application hands off to workflow
```

つまり、構造化出力とは、出力形式の問題であると同時に、責任境界の問題である。

モデルは構造を生成する。

applicationは、それを検査し、解釈し、必要なら止める。

この境界を設計して初めて、生成AIは「文章を返す存在」から、「workflowに参加できる部品」になる。

## 公式参照

- OpenAI API Reference：Responses API / text.format / json_schema / strict
- OpenAI Structured Outputs guide
