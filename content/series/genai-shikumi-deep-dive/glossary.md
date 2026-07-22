---
ページ作成日時: "2026-07-22 16:47 JST"
最終更新日時: "2026-07-22 16:47 JST"
id: "genai-shikumi-deep-dive-glossary"
title: "用語集"
subtitle: "このシリーズ内で使う主要用語の作業定義。"
series: "genai-shikumi-deep-dive"
series_label: "生成AIのしくみ 超詳解"
top_label: "超詳解トップ"
top_href: "/series/genai-shikumi-deep-dive/"
slug: "/series/genai-shikumi-deep-dive/glossary/"
canonical_url: "https://genai-ron.jp/series/genai-shikumi-deep-dive/glossary/"
description: "生成AIのしくみ超詳解で使うrequest、prompt、context、tool、memory、agentなどの用語集。"
source_reconstruction_from: "site/series/genai-shikumi-deep-dive/glossary/index.html"
source_html_blob_sha: "40662695ddfdb578804eb4f39aea1960e3d9aa15"
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
このページは、`生成AIのしくみ 超詳解` 01〜08で使う主要用語を整理した用語集である。

定義は、厳密な標準仕様というより、このシリーズ内での使い方を明確にするための作業定義である。

## 1. request / prompt 系

| 用語 | 定義 | 関連回 |
|---|---|---|
| prompt | 狭義にはユーザーが入力する文。広義には、実行時にmodelへ渡される入力環境全体。 | 01 |
| prompt compilation | ユーザー入力、指示、履歴、memory、ファイル、tool定義などが、実行時に入力構造へ組み立てられる過程。 | 01 |
| request object | applicationがmodelへ送る構造化された依頼。instructions、input、tools、settingsなどを含みうる。 | 01 |
| input | 今回modelに処理させる対象。ユーザー文、添付、画像、ファイル内容、会話履歴などを含みうる。 | 01 |
| instructions | modelの振る舞いを制御するために置かれる指示。system、developer、userなど層によって効力が異なる。 | 01, 02 |

## 2. instruction hierarchy 系

| 用語 | 定義 | 関連回 |
|---|---|---|
| instruction hierarchy | 指示の優先順位構造。system、developer、user、tool resultなどの層を区別する考え方。 | 02 |
| system instruction | 最上位に近いシステム側の指示。モデルの基本的な振る舞い、禁止事項、安全条件などを定める。 | 02 |
| developer instruction | アプリケーションや開発者が設定する動作方針。ユーザー指示より上位に置かれることがある。 | 02 |
| user instruction | ユーザーが与える依頼や希望。重要だが、system / developer instructionを上書きできるとは限らない。 | 02 |
| tool result | tool実行後にapplicationからmodelへ返される結果。資料・戻り値であり、通常は命令ではない。 | 02, 04 |
| prompt injection | 外部資料や検索結果の中の命令文が、本来の資料ではなく指示として扱われてしまう境界事故。 | 02, 03 |

## 3. context / memory / retrieval 系

| 用語 | 定義 | 関連回 |
|---|---|---|
| context | 今回の生成に注入された入力集合。履歴、memory、検索結果、ファイル、tool resultなどを含みうる。 | 03 |
| context window | modelが一度の生成で参照できる入力量の枠。大きくても無限ではない。 | 03 |
| conversation history | 過去の会話内容。すべてが常にcontextへ入るとは限らない。 | 03 |
| memory | 保存されたユーザー情報や設定など。必要に応じて参照され、contextへ注入される。 | 03, 06 |
| personalization | ユーザーの好み、過去の作業、制約などを反映して応答を調整すること。 | 06 |
| retrieval | 外部情報や文書から、今回のtaskに関連する情報を探して取り出すこと。 | 03, 06 |
| RAG | Retrieval-Augmented Generation。検索・取得した情報をcontextへ入れて生成する構成。 | 03 |
| file input | ユーザーが添付したファイルや、接続先から取得されたファイル内容。 | 03 |
| source of truth | 正本・信頼できる原本。model出力やtool resultは、それだけではsource of truthとは限らない。 | 03, 08 |

## 4. tool / runtime 系

| 用語 | 定義 | 関連回 |
|---|---|---|
| tool | modelが呼び出し候補として使える外部機能。検索、コード実行、Notion更新、Gmail操作など。 | 04, 08 |
| tool call | modelが出力する、特定toolを呼ぶための構造化された要求。実行そのものではない。 | 04 |
| tool schema | toolに渡せる引数や形式を定義したもの。modelに対する行動空間の定義でもある。 | 04, 05 |
| application execution | application側がtool callを検証し、実際にtoolやAPIを実行すること。 | 04 |
| runtime | tool、API、file system、database、sandboxなどが実際に動く実行環境。 | 04, 08 |
| connector | Notion、Gmail、Google Drive、GitHubなど外部サービスと接続する機能。 | 04, 08 |
| side effect | 外部世界に変更を加える作用。ファイル更新、メール送信、予定作成、削除など。 | 07, 08 |
| credential | 外部サービスやAPIへアクセスするための認証情報。tool権限と密接に関係する。 | 08 |
| sandbox | 実行を隔離する環境。コード実行やファイル操作の影響範囲を制限する。 | 08 |

## 5. structured output 系

| 用語 | 定義 | 関連回 |
|---|---|---|
| structured output | 自然文ではなく、JSONなどapplicationが解釈できる形式で出されるmodel output。 | 05 |
| JSON Schema | JSON出力の構造、型、必須項目、制約などを定義するschema。 | 05 |
| schema | 出力やtool引数の構造的な契約。modelとapplicationの境界に置かれる。 | 05 |
| parse | model outputをapplicationが読める構造へ変換すること。 | 05 |
| validation | 出力がschemaや業務条件を満たしているか検査すること。 | 05, 07 |
| retry | 失敗時に同じtaskを再試行すること。無制限に行うべきではない。 | 05, 07 |
| repair | 不完全または不正な出力を、schemaや条件に合わせて修復すること。 | 05 |
| refusal | 安全・権限・方針上、modelまたはsystemが依頼を拒否すること。 | 05, 07 |
| output contract | 出力が満たすべき構造・意味・検証条件の契約。 | 05, 08 |

## 6. agentic loop / control 系

| 用語 | 定義 | 関連回 |
|---|---|---|
| agent | goalに向けて、model、tools、context、loop controlを組み合わせて進行するsystem構成。 | 07, 08 |
| agentic loop | observe、decide、act、verifyを繰り返し、続行・停止・handoffなどを選ぶ制御ループ。 | 07 |
| loop state | agent runの現在状態。試行回数、tool結果、未解決事項、検証状態などを含む。 | 07 |
| budget | turn数、tool call数、時間、cost、token、retry、risk、side effectなどの上限。 | 07 |
| stop condition | agentが止まるべき条件。完了、失敗、確認待ち、権限不足、安全停止など。 | 07 |
| verification | taskが成功条件を満たしたか確認すること。modelの自己申告だけでは不十分。 | 07 |
| guardrail | 危険、権限、形式、安全、privacyなどの境界を検出・制御する仕組み。 | 07, 08 |
| stop gate | 続行、修復、再試行、確認、manual review、handoff、abortを選ぶ判断点。 | 07 |
| handoff | 別agent、別workflow、人間、別systemへ状態付きで処理を渡すこと。 | 07 |
| manual review | 人間による確認・承認へ回すこと。送信、公開、削除、契約などで重要になる。 | 07 |
| trace | agentic loopの実行記録。何を見て、何を判断し、何を実行し、なぜ止まったかを残す。 | 07, 08 |
| audit | traceをもとに、実行が妥当だったか後から検証すること。 | 07, 08 |
| evaluation | agentやworkflowの品質を継続的に測ること。最終回答だけでなくloop全体を見る。 | 07, 08 |

## 7. architecture / responsibility 系

| 用語 | 定義 | 関連回 |
|---|---|---|
| model layer | contextをもとに自然文、構造化出力、tool call候補などを生成する層。 | 08 |
| application layer | request、instruction、context、tool、validation、loop、UIを編成する層。 | 08 |
| runtime / tool layer | 外部API、file system、database、sandbox、connectorなどを実行する層。 | 08 |
| human layer | 目的、判断、承認、責任、評価、委任境界を担う層。 | 08 |
| accountability | 結果に対して責任を引き受けること。modelではなく人間・組織・運用主体が持つ。 | 08 |
| delegation boundary | どこまでをAIに任せ、どこから人間や別systemへ渡すかの境界。 | 08 |
| failure boundary | 失敗がどの層で起きたかを切り分ける境界。model、context、tool、runtime、humanなど。 | 08 |
| manifest | context、tool、memory、loop、auditなどの状態や構成を明示する記録。 | 07, 08 |

## 8. この用語集の使い方

この用語集は、以下の用途で使う。

- 01〜08本文中の概念の再確認
- 公開版の注釈・脚注の素材
- 図解版のラベル
- よくある誤解集の整理
- 実務設計チェックリストの語彙統一
- 09以降を作る場合の前提語彙

用語は今後、本文の改稿や公開後の反応に応じて更新してよい。
