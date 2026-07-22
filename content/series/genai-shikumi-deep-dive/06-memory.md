---
ページ作成日時: "2026-07-22 16:47 JST"
最終更新日時: "2026-07-22 16:47 JST"
id: "genai-shikumi-deep-dive-06"
title: "memoryとは何か"
subtitle: "memoryを、モデル内部の体験ではなく、保存・参照・personalization・context injection・監査の仕組みとして読む。"
series: "genai-shikumi-deep-dive"
series_label: "生成AIのしくみ 超詳解"
series_order: "6"
order_display: "06"
previous_label: "前へ：05 構造化出力とは何か"
previous_href: "/series/genai-shikumi-deep-dive/05-structured-output/"
next_label: "次へ：07 停止条件と検証ループ"
next_href: "/series/genai-shikumi-deep-dive/07-agentic-loop/"
top_label: "超詳解トップ"
top_href: "/series/genai-shikumi-deep-dive/"
slug: "/series/genai-shikumi-deep-dive/06-memory/"
canonical_url: "https://genai-ron.jp/series/genai-shikumi-deep-dive/06-memory/"
description: "memoryを、保存情報の参照・選別・再注入・監査の仕組みとして読む超詳解。"
source_reconstruction_from: "site/series/genai-shikumi-deep-dive/06-memory/index.html"
source_html_blob_sha: "7a88035b8b694ffd30f42c2fd78bb6d4274873ca"
original_notion_created_at: "2026-07-19 09:36 JST"
original_notion_updated_at: "2026-07-19 09:36 JST"
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
生成AIを使い続けていると、ある瞬間から「覚えている」という感覚が生まれる。

前に話した好みを踏まえてくれる。

家族構成や仕事上の役割を前提にする。

進行中のプロジェクトを続きから扱う。

文体や関心領域に合わせて応答する。

しかし、この現象をそのまま「AIの中に人間のような記憶がある」と理解すると、仕組みを見誤る。

:::note
memoryとは、モデル内部に体験が蓄積されることではない。過去の会話、保存情報、設定、ファイル、接続アプリなどから、現在の応答に有用だと判断された情報が選別され、contextとして再注入される仕組みである。
:::

06では、memoryを保存・参照・personalization・injection・監査という複数の層に分解する。

## 1. 「覚えている」は、一つの処理ではない

ユーザーから見ると、AIが過去の情報を踏まえて答えたとき、「覚えていた」と感じる。

しかし、application側では少なくとも次の段階がある。

```text
stored
  ↓ maybe
retrieved
  ↓ maybe
selected
  ↓ maybe
injected
  ↓ maybe
used in generation
```

情報がどこかに保存されていることと、今回検索されたことは違う。

検索候補に上がったことと、実際にcontextへ入ったことも違う。

contextへ入ったことと、最終応答で採用されたことも違う。

```text
stored somewhere ≠ currently injected
currently injected ≠ necessarily trusted
remembered ≠ authoritative
memory hint ≠ current user instruction
```

したがって、「AIは覚えているか」という問いは、本当は次の問いへ分解される。

- どこに保存されたのか
- どのsourceから来たのか
- どのscopeで使えるのか
- 今回retrievalされたのか
- contextへ注入されたのか
- 現在の指示と衝突しなかったか
- 応答に実際に使われたのか

## 2. model weightsとruntime context

memoryを理解するには、model weightsとruntime contextを分ける必要がある。

| 層 | 意味 | ユーザーから見た印象 |
|---|---|---|
| model weights | 学習済みモデルの重み。通常の会話ごとに個人向けに書き換わるものではない | AIの基礎知識・言語能力 |
| runtime context | 今回の応答時にモデルへ渡される入力集合 | 今この応答でAIが見ている材料 |
| saved memory | ユーザーや会話について保存された情報 | AIが覚えているように見える情報 |
| memory injection | 保存情報を今回のcontextへ入れる処理 | 前の話を踏まえて答える現象 |

通常の会話でmemoryが効くことは、モデルそのものがその場で再学習されたことを意味しない。

より近い理解は次である。

```text
過去会話・保存情報・設定・ファイル・接続アプリ
  ↓
保存・要約・検索・選別
  ↓
現在のrequestに関係する情報を抽出
  ↓
今回のcontextへ注入
  ↓
モデルがそのcontextを入力として生成
```

memoryは、モデル内部の体験ではなく、再注入可能なcontext sourceである。

## 3. saved memory、reference chat history、custom instructions

長期的なpersonalizationを支えるsourceは一つではない。

saved memory

saved memoryは、ユーザーについて継続的に使う価値があると判断された情報である。

例：

- 名前
- 食事上の制約
- よく使う文体
- 継続中の仕事上の役割
- 明示的に覚えておいてほしいと依頼された事項

saved memoryは、小さな恒常contextに近い。

reference chat history

reference chat historyは、過去の会話そのもの、またはそこから抽出された関連情報を、現在の会話へ参照する仕組みである。

すべての過去会話を毎回そのまま読み込むことではない。

現在のrequestに関係する情報が選ばれる。

custom instructions

custom instructionsは、ユーザーが明示的に設定した恒常的な指示である。

たとえば、

```text
日本語で答える。
文章は簡潔にする。
技術用語は必要に応じて説明する。
```

これは「過去にこうだった」というmemory claimではなく、「今後こう応答してほしい」というinstructionである。

| source | 主な内容 | 性質 |
|---|---|---|
| saved memory | ユーザーの好み・条件・継続情報 | 保存されたcontext |
| reference chat history | 過去会話から得られる関連情報 | 検索・再構成されるcontext |
| custom instructions | 恒常的な応答方針 | 明示的instruction |
| current user message | 今回の依頼 | 現在の明示的instruction |

これらをすべて「記憶」と呼ぶと、権限と更新方法が見えなくなる。

## 4. personalizationとはcontext selectionである

personalizationは、ユーザー専用モデルを作ることではない。

:::note
personalizationとは、現在のrequestに対して、どの記憶、履歴、設定、ファイル、プロジェクト文脈を選び、どの強さでcontextへ入れるかを決めることである。
:::

personalizationに使われうるsignalには次がある。

- 文体の好み
- 関心領域
- 生活条件
- 継続中のプロジェクト
- 過去に選んだ方針
- ファイルや接続アプリ内の情報
- 現在所属しているproject / workspace

しかし、personalizationは強ければよいわけではない。

```text
more personalization ≠ better answer
relevant personalization ≈ better answer
```

旅行相談で過去の犬連れ条件を使うことは有用かもしれない。

一方、技術文書の設計で家族情報を持ち出すことは不要である。

personalizationは、量ではなくscopeとrelevanceの問題である。

## 5. memory injectionとcontext window

保存されているmemoryが、毎回すべてcontextへ入るわけではない。

context windowには限りがある。

また、現在の依頼に関係しない情報を大量に入れると、重要な指示や根拠を圧迫する。

memory injectionでは、概念的に次の判断が必要になる。

```text
candidate memory
  ↓ relevance check
  ↓ scope check
  ↓ freshness check
  ↓ conflict check
  ↓ sensitivity check
  ↓ context budget check
  ↓ placement decision
  ↓ injected context
```

relevance

現在のrequestに関係するか。

scope

account全体、workspace、project、chat、taskのどの範囲で使える情報か。

freshness

今も正しいか。最後に確認されたのはいつか。

conflict

現在のuser instructionや、新しい事実と衝突していないか。

sensitivity

その情報を今回の応答へ露出してよいか。

placement

単なる参考contextとして入れるのか、明示的な制約として扱うのか。

memory injectionは、情報追加ではなく、情報の選別と配置である。

## 6. memoryはinstruction hierarchyを上書きしない

過去のmemoryに次があるとする。

```text
ユーザーは短い回答を好む。
```

しかし、現在のuser messageが次なら、現在の指示を優先する。

```text
今回は詳しく長めに説明して。
```

memoryは重要なcontextであっても、現在の明示的依頼を自動的に上書きする命令ではない。

同様に、過去のproject情報があるからといって、現在の依頼を必ずそのprojectとして扱うべきではない。

```text
memory relevance ≠ instruction authority
past preference ≠ current command
continuity hint ≠ confirmed scope
```

## 7. memoryの失敗モード

memoryの失敗は、単なる「記憶違い」だけではない。

stale memory

以前は正しかったが、現在は古い。

例：

- 以前の勤務先
- 終了済みproject
- 古い住所
- 変更済みの好み

wrong memory

最初から誤っている、または誤推論から作られた。

over-personalization

関係の薄いmemoryを使いすぎる。

ユーザーを過去の自己像に固定する。

under-personalization

既に共有済みの重要条件を無視し、毎回同じ説明や確認を求める。

sensitive memory

健康、家族、政治、宗教、財務、位置情報などを不必要に露出する。

contradictory memory

複数のmemoryが矛盾している。

false continuity

本当は続きではないのに、過去projectの続きだと断定する。

```text
relevant memory ≈ better personalization
stale memory ≠ useful memory
sensitive memory ≠ freely reusable memory
stored context ≠ confirmed continuity
```

## 8. 削除と無効化は同じではない

memoryを扱うときは、次を分ける必要がある。

- memory機能をオフにする
- saved memoryを削除する
- 元chatを削除する
- archived chatを削除する
- fileを削除する
- connected appを切断する
- Temporary Chatを使う

保存済みmemoryとchat historyは別管理される場合がある。

そのため、chatを削除しただけでは、そこから作られたsaved memoryが残ることがある。

逆に、saved memoryを削除しても、過去chat内の記述そのものは残る場合がある。

```text
delete chat ≠ delete every derived memory
delete saved memory ≠ erase past chat text
turn off memory ≠ delete all source data
```

削除は、sourceごとの状態を確認する必要がある。

## 9. Temporary Chatは「すべてのcontextを消す」機能ではない

Temporary Chatは、personalization用memoryへアクセスせず、新しいmemoryも作らないための会話モードである。

ただし、custom instructionsが有効なら従うことがあり、安全性やセキュリティ目的の限定的contextが使われる場合もある。

したがって、Temporary Chatを「完全な無文脈状態」と理解するのは正確ではない。

```text
Temporary Chat:
  no personalization memory access
  no new personalization memory creation
  but current message / system rules / enabled custom instructions remain
```

## 10. memoryを設計・監査する

memoryを安全に使うには、内容だけでなくmetadataを持つ必要がある。

```tsx
type MemoryManifest = {
  id: string;
  subject: string;
  claim: string;
  sourceType:
    | "explicit_user_request"
    | "inferred_from_chat"
    | "file"
    | "connected_app"
    | "custom_instruction"
    | "human_entry";
  sourceRef?: string;
  scope: "account" | "workspace" | "project" | "chat" | "task";
  confidence: "low" | "medium" | "high";
  sensitivity: "normal" | "sensitive" | "restricted";
  createdAt: string;
  lastConfirmedAt?: string;
  expiresAt?: string;
  retentionStatus: "active" | "expired" | "superseded" | "deleted";
  consentStatus: "explicit" | "implicit" | "not_required" | "revoked";
};
```

最低限、次が追跡できるべきである。

- claim：何を覚えているのか
- provenance：どこから来たのか
- scope：どこで使えるのか
- freshness：いつ確認されたのか
- confidence：どの程度確かか
- sensitivity：露出してよいか
- retention：いつまで持つか
- deletion status：削除済みか
- consent：ユーザーの同意状態

## 11. memory audit log

memoryは保存だけでなく、使用履歴も監査対象になる。

```tsx
type MemoryAuditEvent = {
  eventId: string;
  memoryId: string;
  eventType:
    | "created"
    | "updated"
    | "retrieved"
    | "injected"
    | "used"
    | "suppressed"
    | "corrected"
    | "deleted";
  reason: string;
  requestId?: string;
  occurredAt: string;
};
```

重要なのは、「何を覚えているか」だけではない。

- なぜ今回使ったのか
- どのsourceから来たのか
- どのmemoryを使わなかったのか
- 衝突をどう解決したのか
- stale判定をしたか
- sensitive情報を抑制したか

これらが分かることで、personalizationは検証可能になる。

## 12. memoryを使わず停止すべき条件

memoryに不確実性がある場合、applicationは無理に連続性を作るべきではない。

```text
memory candidate
  ↓
source known?
  ├─ no → do not rely
  └─ yes
       ↓
scope matches?
  ├─ no → suppress
  └─ yes
       ↓
fresh enough?
  ├─ no → ask / verify
  └─ yes
       ↓
conflict exists?
  ├─ yes → prefer current explicit information
  └─ no
       ↓
sensitive?
  ├─ yes → minimize / confirm
  └─ no → inject
```

停止・確認すべき典型例は次である。

- sourceが不明
- 古さが重大な結果に影響する
- 複数memoryが矛盾する
- 現在のuser instructionと衝突する
- sensitive情報を露出する必要がある
- project scopeが確定できない
- memoryを根拠に外部操作しようとしている

memoryは、確認を省略するための権限ではない。

## 13. 06のまとめ

- memoryはmodel weightsそのものではない
- memoryは再注入可能なcontext sourceである
- saved memory、reference chat history、custom instructionsは別物である
- personalizationはcontext selectionとinjectionで起きる
- 保存されていることと、今回使われたことは違う
- memoryは現在の明示的instructionを上書きしない
- stale / wrong / sensitive / contradictory memoryは失敗モードである
- 削除、無効化、chat削除、file削除は分けて考える
- memory manifestとaudit logでprovenanceを追跡する
- 不確実なmemoryは、使わずに停止・確認する

:::note
記憶を設計するとは、AIに何を覚えさせるかを決めることではない。何を、どの根拠で、どの範囲に、いつまで保持し、どの条件で再注入し、どう訂正・削除・監査できるようにするかを決めることである。
:::

次回07では、この停止と確認をさらに一般化し、agentic systemがいつ続行し、いつretryし、いつ人間へ返し、いつ止まるべきかを扱う。

## 参考資料

- [OpenAI Memory FAQ](https://help.openai.com/en/articles/8590148-memory-in-chatgpt)
- [How does Reference saved memories work?](https://help.openai.com/en/articles/11146739-how-does-reference-saved-memories-work)
- [Temporary Chat FAQ](https://help.openai.com/en/articles/8914046-temporary-chat-faq)
- [Chat and File Retention Policies in ChatGPT](https://help.openai.com/en/articles/8983778-chat-and-file-retention-policies-in-chatgpt)

参照確認日：2026-07-19 JST
