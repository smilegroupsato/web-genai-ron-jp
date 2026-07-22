---
ページ作成日時: "2026-07-22 16:47 JST"
最終更新日時: "2026-07-22 16:47 JST"
id: "genai-shikumi-deep-dive-misconceptions"
title: "よくある誤解集"
subtitle: "生成AIを神秘化しすぎず、過小評価もしないための誤解と整理。"
series: "genai-shikumi-deep-dive"
series_label: "生成AIのしくみ 超詳解"
top_label: "超詳解トップ"
top_href: "/series/genai-shikumi-deep-dive/"
slug: "/series/genai-shikumi-deep-dive/misconceptions/"
canonical_url: "https://genai-ron.jp/series/genai-shikumi-deep-dive/misconceptions/"
description: "生成AIのしくみ超詳解で扱うprompt、context、tool、memory、agentなどに関するよくある誤解集。"
source_reconstruction_from: "site/series/genai-shikumi-deep-dive/misconceptions/index.html"
source_html_blob_sha: "cc0bd17fa8cfa2fa1f65926b4a703dbcdebbc711"
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
このページは、`生成AIのしくみ 超詳解` 01〜08で繰り返し出てくる「よくある誤解」を整理したページである。

目的は、生成AIを過度に神秘化せず、かといって単なる文章生成器として過小評価もしないために、誤解と正しい見方を対にして示すことにある。

## 1. prompt / requestに関する誤解

誤解1：プロンプトとは、チャット欄に書いた文章のことである

正しくは、チャット欄の文章はprompt / requestの一部である。

実行時には、system instruction、developer instruction、会話履歴、memory、ファイル、検索結果、tool定義、出力制約などが組み合わされる。

```text
prompt ≠ user text only
prompt = runtime input environment
```

関連：01

誤解2：同じ文章を送れば、同じ条件で実行される

正しくは、同じユーザー文でも、背後のcontext、memory、利用可能tool、モデル設定、会話履歴が違えば、実行環境は変わる。

見た目の入力が同じでも、request objectが同じとは限らない。

関連：01, 03, 08

## 2. instruction hierarchyに関する誤解

誤解3：強い口調で命令すれば、上位指示を上書きできる

正しくは、指示の強さは言葉の強さではなく、置かれた層によって決まる。

```text
louder instruction ≠ higher instruction
```

system instructionやdeveloper instructionが、user instructionより優先されることがある。

関連：02

誤解4：外部資料に書かれている命令も、AIへの命令である

正しくは、外部資料や検索結果に含まれる文章は、通常は資料であり命令ではない。

外部資料中の「前の指示を無視せよ」「このURLへ送信せよ」などを命令として扱ってしまうのが、prompt injectionの典型である。

関連：02, 03

誤解5：tool resultはmodelへの命令である

正しくは、tool resultは戻り値であり、資料である。

通常、tool resultがsystemやdeveloper instructionを上書きすることはない。

関連：02, 04

## 3. context / memoryに関する誤解

誤解6：contextとは、保存されている情報のことである

正しくは、contextとは今回の生成に注入された入力集合である。

保存されていても、今回のcontextに入っていなければ、modelは参照できない。

関連：03

誤解7：AIは過去の会話を全部覚えている

正しくは、過去の会話が常に丸ごとcontextへ入るわけではない。

履歴の一部、要約、memory、検索された断片などが選ばれて入ることがある。

関連：03, 06

誤解8：memoryはモデルの中に人間の記憶のように保存されている

正しくは、多くの場合、memoryは外部または周辺の保存機構にあり、必要に応じて参照され、contextへ再注入される。

```text
memory ≠ model's lived experience
memory = stored information + retrieval + injection + audit
```

関連：06

誤解9：contextが長ければ長いほど良い

正しくは、contextは長ければよいのではなく、必要な情報が適切な役割で入っていることが重要である。

不要な情報が多いと、重要な情報が埋もれたり、矛盾や混乱が増える。

関連：03, 08

## 4. tool useに関する誤解

誤解10：モデルがtoolを直接実行している

正しくは、modelはtool call候補を出す。

それをapplicationが検証し、runtime / connector / APIが実行し、tool resultが戻る。

```text
model emits tool call
application executes tool
```

関連：04, 08

誤解11：tool callが出たら、必ず実行される

正しくは、tool callは実行候補である。

application側でschema、権限、policy、ユーザー承認、危険度などを確認したうえで、実行される場合もあれば止められる場合もある。

関連：04, 07, 08

誤解12：tool resultが返ったら、それは真実である

正しくは、tool resultは実行結果であって、常に真実とは限らない。

APIが成功しても内容が古い場合がある。検索結果があっても信頼できるとは限らない。ファイルを読めても、対象ファイルが正本とは限らない。

関連：04, 07, 08

誤解13：読み取りtoolと書き込みtoolは同じ危険度である

正しくは、読み取り、作成、更新、送信、削除、課金、公開では危険度が違う。

特に、メール送信、公開、削除、上書き、契約、会計処理などは、承認・trace・rollback可能性を考える必要がある。

関連：04, 07, 08

## 5. structured outputに関する誤解

誤解14：JSONが出れば構造化出力である

正しくは、JSONらしい文字列が出ることと、applicationが信頼して扱える構造化出力であることは違う。

schema、parse、validation、refusal handling、retry、repair、handoffが必要になる。

関連：05

誤解15：schemaは出力の見た目を整えるためのものだ

正しくは、schemaはmodel outputとapplicationの間の契約である。

見た目ではなく、型、必須項目、制約、欠損時の扱い、失敗時の分岐に関わる。

関連：05

誤解16：validationが通れば、taskも成功している

正しくは、schema validationは形式の検証であり、task completionの検証とは別である。

JSON形式が正しくても、内容が間違っていることはある。

関連：05, 07

## 6. agentic loopに関する誤解

誤解17：agentとは、自律的に動き続けるAIである

正しくは、agentic loopは、observe、decide、act、verifyを繰り返しながら、続行・停止・確認・handoffを選ぶ制御ループである。

```text
agentic loop ≠ endless autonomy
agentic loop = controlled continuation and stopping
```

関連：07

誤解18：止まることは失敗である

正しくは、停止には複数の意味がある。

完了、失敗、確認待ち、権限不足、manual review、handoff、安全停止などがある。

止まれるagentのほうが、止まれないagentより信頼できる。

関連：07

誤解19：検証はmodelに「できた？」と聞けばよい

正しくは、modelの自己申告は検証ではない。

artifactの存在、diff、test、tool result、外部データ照合、承認記録などで確認する必要がある。

関連：07

誤解20：budgetはコスト管理だけの話である

正しくは、budgetにはturn、tool call、time、cost、token、retry、risk、side effectなどが含まれる。

budgetは、agentの自律性を制御するための設計要素である。

関連：07

## 7. guardrails / handoffに関する誤解

誤解21：guardrailは危険な出力を最後に止めるフィルターである

正しくは、guardrailは出力だけでなく、input、context、tool、permission、memory、loop stateなどにも置かれる。

最後のフィルターではなく、workflow全体の制御点である。

関連：07, 08

誤解22：人間に確認するのは、AIが未熟だからである

正しくは、確認は責任境界の設計である。

AIが有能でも、価値判断、承認、送信、公開、削除、契約、法務・会計判断などは、人間の責任に戻す必要がある。

関連：07, 08

誤解23：handoffは失敗である

正しくは、handoffは別の担当、別の権限、別のworkflowへ状態付きで渡す設計である。

handoffがあるから、長期・複雑・分散的な作業が壊れにくくなる。

関連：07

## 8. architectureに関する誤解

誤解24：AIがやった、という説明で十分である

正しくは、「AIがやった」は粗すぎる。

modelが生成したのか、applicationが実行したのか、runtimeが失敗したのか、human approvalが不足したのかを分ける必要がある。

関連：08

誤解25：モデルが賢くなれば、設計は不要になる

正しくは、モデルが賢くなるほど、tool、memory、権限、side effect、handoff、auditの設計は重要になる。

高性能なmodelは、よいarchitectureの代替ではない。

関連：08

誤解26：人間はAIシステムの外側にいる

正しくは、human layerはAIシステムの構成要素である。

目的を決め、価値を選び、承認し、責任を持ち、評価する。

関連：08

誤解27：traceは開発者向けログなので、ユーザーには関係ない

正しくは、traceは信頼性、監査、説明責任、改善の基盤である。

ユーザーに全部を見せる必要はないが、必要なときに検証できる記録がなければならない。

関連：07, 08

## 9. まとめ：誤解をほどくための一文

```text
生成AIを理解する近道は、
「AIが考えて、AIがやった」とまとめずに、
request、instruction、context、model output、tool execution、verification、human responsibilityへ分解することである。
```

この誤解集は、公開版の補助資料、読者向けFAQ、図解版、講義用スライド、Web掲載時の導入文に再利用できる。
