---
ページ作成日時: "2026-07-22 16:47 JST"
最終更新日時: "2026-07-22 16:47 JST"
id: "genai-shikumi-deep-dive-07"
title: "停止条件と検証ループ"
subtitle: "agentはいつ続行し、いつ止まるのか。agentic loopを、続行・検証・停止・handoffを選ぶ制御ループとして読む。"
series: "genai-shikumi-deep-dive"
series_label: "生成AIのしくみ 超詳解"
series_order: "7"
order_display: "07"
previous_label: "前へ：06 memoryとは何か"
previous_href: "/series/genai-shikumi-deep-dive/06-memory/"
next_label: "次へ：08 全体アーキテクチャ"
next_href: "/series/genai-shikumi-deep-dive/08-architecture/"
top_label: "超詳解トップ"
top_href: "/series/genai-shikumi-deep-dive/"
slug: "/series/genai-shikumi-deep-dive/07-agentic-loop/"
canonical_url: "https://genai-ron.jp/series/genai-shikumi-deep-dive/07-agentic-loop/"
description: "agentic loopを、停止条件、budget、verification、guardrails、handoff、traceから読む超詳解。"
source_reconstruction_from: "site/series/genai-shikumi-deep-dive/07-agentic-loop/index.html"
source_html_blob_sha: "9bdc26f55f60af9dfe9a53b1ecc131c82de4371c"
original_notion_created_at: "2026-07-20 10:45 JST"
original_notion_updated_at: "2026-07-20 10:45 JST"
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
agentという言葉には、どこか「自律的に動き続けるもの」という印象がある。

ユーザーが目的を与える。

AIが計画を立てる。

toolを呼ぶ。

結果を見る。

また考える。

また実行する。

このloopを見ると、agentとは「目的に向かって自動的に進み続けるAI」のように見える。

しかし、agentic systemを安全に設計するうえで、本当に重要なのは「どう続けるか」だけではない。

むしろ重要なのは、いつ止まるかである。

:::note
agentic loopとは、モデルが自律的に動き続けることではない。observe、decide、act、verifyを繰り返しながら、明示された停止条件・検証条件・予算・権限・安全条件に従って、続行または停止を選ぶ制御ループである。
:::

07では、agentが「続行する」「再試行する」「検証する」「人間に確認する」「別agentへ渡す」「停止する」を、何を根拠に決めるのかを扱う。

## 1. agentic loopは無限ループではない

agentic loopを単純化すると、次のようになる。

```text
receive task
  ↓
observe context
  ↓
decide next action
  ↓
act / call tool / answer / ask user / handoff
  ↓
observe result
  ↓
verify
  ↓
continue or stop
```

ここで重要なのは、最後が `continue` だけではないことだ。

```text
agentic loop = continue forever
```

ではない。

より正確には、次である。

```text
agentic loop = decide whether to continue
```

agentは、まだできることがあるから続けるのではない。

続ける理由があり、続ける権限があり、続ける予算があり、続ける安全性があり、続けた結果を検証できるときだけ続ける。

```text
more steps ≠ better agent
more tool calls ≠ more autonomy
longer loop ≠ better completion
safe stopping ≈ reliable agent
```

agentの賢さは、長く走り続けることでは測れない。

不要に続けないこと、危険なまま進めないこと、根拠なく完了扱いしないことが重要である。

## 2. stopはfailureではない

停止という言葉は、失敗のように聞こえる。

処理が止まった。

先へ進めなかった。

完了できなかった。

しかし、agentic workflowにおいて、停止は必ずしも失敗ではない。

むしろ、正しく止まることはagentの能力である。

| 停止種別 | 意味 | 例 |
|---|---|---|
| completed | 成功条件を満たして完了した | レポートを作成し、検証も通った |
| failed | 必要な処理に失敗し、回復不能 | 必須APIが失敗し続けた |
| blocked | 外部条件が足りず進めない | 権限、ファイル、接続、情報が不足している |
| needs_user | ユーザー判断が必要 | 曖昧な選択、承認、追加情報が必要 |
| manual_review | 人間の確認なしに進めるべきではない | 法務、財務、削除、送信、公開など |
| handoff | 別agent・別workflowへ渡す | 専門agent、承認者、外部systemへ移す |
| aborted | 安全・権限・方針により中止 | 危険操作、policy conflict、意図不明な破壊的操作 |

ここで大事なのは、すべてを `failed` にしないことである。

ユーザー確認が必要な状態は、失敗ではない。

権限が足りない状態も、失敗とは限らない。

成功条件を満たして止まることは、もちろん失敗ではない。

安全上止めることも、むしろ成功した制御である。

```text
stop ≠ failure
blocked ≠ failed
needs_user ≠ failed
handoff ≠ failed
safe abort ≠ failed
```

## 3. success criteriaがないagentは止まれない

agentが止まれない最大の理由は、成功条件が曖昧なことである。

たとえば、ユーザーがこう依頼したとする。

```text
この件を調べて、いい感じにまとめて。
```

この依頼だけでは、agentはどこで止まればよいか分かりにくい。

何件調べるのか。

どのsourceを信頼するのか。

どの深さまで読むのか。

どの形式でまとめるのか。

矛盾があったらどうするのか。

最新情報をどこまで確認するのか。

ユーザー判断を挟むべきか。

success criteriaが曖昧なままagentにtoolを渡すと、次のような挙動になりやすい。

```text
search
  ↓
read
  ↓
more search
  ↓
more read
  ↓
maybe enough?
  ↓
summary
  ↓
maybe more search?
```

これは賢く調べているように見える。

しかし設計上は、停止条件が弱い。

agentには、次のような明示条件が必要である。

```text
stop when:
  - required sources have been checked
  - contradictions have been noted
  - confidence threshold is met
  - output format is complete
  - no unresolved required fields remain
  - budget is not exceeded
  - no approval-gated action remains pending
```

停止条件は、task goalから自動的には出てこない。

application側が、成功条件、失敗条件、確認条件、handoff条件として定義する必要がある。

## 4. loop stateとbudget

agentic loopを制御するには、現在の状態を持たなければならない。

今、何step目なのか。

どのtoolを何回呼んだのか。

どの試行が失敗したのか。

あと何回retryできるのか。

これ以上続けるとcostやriskが高すぎないか。

状態を持たないloopは、自分が同じ場所を回っていることに気づけない。

予算を持たないloopは、どこまで続けてよいかを判断できない。

```text
loop without state
  → 自分が何をしたか分からない

loop without budget
  → どこまで続けてよいか分からない
```

agentic workflowで扱うbudgetには、少なくとも次がある。

| budget | 意味 | 停止・分岐例 |
|---|---|---|
| turn budget | 思考・応答step数の上限 | 上限到達でsummary / handoff / stop |
| tool call budget | tool実行回数の上限 | 検索やAPI呼び出しの暴走を防ぐ |
| time budget | 実行時間の上限 | 時間切れならpartial resultやhandoff |
| cost budget | APIや外部処理の費用上限 | 高額処理前に確認 |
| token budget | context / output量の上限 | 要約・分割・圧縮へ切り替える |
| retry budget | 失敗時の再試行上限 | 無限retryを防ぐ |
| risk budget | 許容される危険度の上限 | 権限・安全・法務境界で止める |
| side effect budget | 外部状態変更の許容量 | 送信、削除、公開、決済などを制御 |

特に重要なのは、read-onlyなtool callとstate-changingなtool callを分けることである。

ファイルを読む、検索する、カレンダーを見る。

これらは基本的に観測である。

一方で、メールを送る、予定を作る、ファイルを削除する、PRをmergeする、支払いを実行する。

これらは外部状態を変える。

```text
read-only action
  ≠ state-changing action

state-changing action
  requires stronger gate
```

## 5. verification loop

agentが「完了しました」と言うことと、実際に完了していることは違う。

モデルは、もっともらしく完了を宣言できる。

tool resultは、呼び出しが成功したことを示すかもしれない。

JSONはschema validationを通るかもしれない。

しかし、それだけではtaskが完了したとは限らない。

```text
model says completed ≠ task completed
tool call succeeded ≠ task goal achieved
valid JSON ≠ correct answer
file created ≠ useful artifact
```

verification loopとは、agentの自己申告やtool resultの存在を完了とみなさず、成功条件・証拠・成果物・差分・テスト・reconciliationを通じて、taskが本当に完了したかを確認する仕組みである。

検証には、少なくとも次の種類がある。

| verification | 確認するもの | 例 |
|---|---|---|
| schema validation | 形式が契約に合うか | JSON Schemaに通る |
| tool result verification | toolの返り値が期待通りか | 作成したページのURLが返る |
| artifact verification | 成果物が存在し、内容が入っているか | 作成した文書をfetchして確認する |
| evidence check | 主張が根拠に支えられているか | 引用元と本文が対応している |
| diff check | 変更が意図通りか | 不要な削除がないか確認する |
| dry run / test | 実行前に安全に試せるか | 本番前にpreviewやtestを走らせる |
| reconciliation | 複数sourceが一致するか | 会計データや在庫数を照合する |

completedは、自己申告ではない。

completedとは、成功条件を満たし、必要な検証を通った状態である。

## 6. guardrailsとstop gates

guardrailsは、単なる注意書きではない。

「危ないことをしないでください」とpromptに書くだけでは、agentic workflowの制御としては弱い。

guardrailは、各stepで続行可否を判定するstop gateである。

```text
observe
  ↓
guardrail check
  ↓
decide
  ↓
guardrail check
  ↓
act
  ↓
guardrail check
  ↓
verify
  ↓
continue or stop
```

主なguardrailには次がある。

| guardrail | 対象 | 例 |
|---|---|---|
| input guardrail | ユーザー入力 | 危険依頼、個人情報、意図不明な破壊的操作 |
| output guardrail | agent出力 | 機密漏洩、誤った断定、禁止された形式 |
| tool guardrail | tool call | 許可されないAPI、危険な引数、過剰実行 |
| permission guardrail | 権限 | 認可不足、他人のデータ、未承認操作 |
| safety guardrail | 安全性 | 危険行為、違法行為、身体的・経済的被害 |
| privacy guardrail | 個人情報・機密情報 | 不要な露出、越境共有、保存範囲違反 |

重要なのは、policy failureとtask failureを混同しないことである。

ユーザーの依頼を完了できない理由が、技術的失敗なのか、権限不足なのか、安全上の停止なのかで、返すべき状態は変わる。

```text
task failure
  = 目的達成に失敗した

policy failure
  = その目的または手段では進めない

permission failure
  = 権限が足りない

verification failure
  = 完了したと確認できない
```

不確実なときは、安全側に倒す。

これがfail closedである。

```text
if uncertain and risk is high:
  do not proceed silently
  ask user / require approval / handoff / stop
```

fail openは、危険なまま続ける設計である。

fail closedは、危険なときに止まる設計である。

## 7. ask user / manual review / handoff

agentは、自分だけで完結するほどよいとは限らない。

正しいagentは、必要なときにユーザーへ確認し、人間のreviewを挟み、別agentや別workflowへhandoffできる。

ここでは、三つを分ける。

| 分岐 | 意味 | 例 |
|---|---|---|
| ask user | ユーザー判断や追加情報が必要 | 候補A/Bの選択、曖昧な条件の確認 |
| manual review | 人間の確認なしに進めるべきではない | 送信、公開、削除、契約、支払い |
| handoff | 別agent・別workflowへ責務を渡す | 専門agent、承認者、別システムへ移す |

ask userは、agentの失敗ではない。

むしろ、判断権限を人間に戻す正常な制御である。

manual reviewは、情報不足とは限らない。

情報が足りていても、人間の責任や承認が必要な場面がある。

handoffは、放棄ではない。

責務範囲の移転である。

ただし、handoffにはcontext lossが起きやすい。

何を引き継ぐのか、どこまで確認済みなのか、何が未解決なのかをmanifestとして渡す必要がある。

```tsx
type HandoffManifest = {
  taskId: string;
  fromAgent: string;
  toAgent: string;
  reason:
    | "specialized_skill_required"
    | "permission_required"
    | "manual_review_required"
    | "insufficient_context"
    | "budget_exceeded"
    | "risk_too_high";
  currentState: string;
  completedSteps: string[];
  verifiedResults: string[];
  unresolvedQuestions: string[];
  requiredApprovals: string[];
  artifacts: {
    name: string;
    url?: string;
    status: "draft" | "verified" | "needs_review";
  }[];
  recommendedNextAction: string;
};
```

handoffが成立するには、単に「次お願いします」と言うだけでは足りない。

context packが必要である。

## 8. trace / audit / evaluation

agentic loopは、その場でうまく動くだけでは不十分である。

後から説明できなければならない。

再現できなければならない。

評価できなければならない。

改善できなければならない。

そのために必要なのが、trace / audit / evaluationである。

traceは単なるログではない。

重要なのは、「何をしたか」だけではない。

「なぜそのactionを選んだのか」「なぜ別のactionを選ばなかったのか」「なぜ止まったのか」を再構成できることである。

```text
trace = what happened
       + why it happened
       + what was considered
       + what was rejected
       + why it stopped
```

agentic workflowでは、実行したactionだけでなく、実行しなかったactionも重要になる。

たとえば、メールを送れるtoolがあったが、承認がなかったため送らなかった。

ファイルを削除できたが、破壊的操作なので止めた。

追加検索できたが、必要なsource確認が済んでいたため止めた。

これらはすべて、agentの正常な判断である。

```tsx
type AgentDecisionLog = {
  runId: string;
  stepId: string;
  observedState: string;
  candidateActions: {
    action: string;
    expectedBenefit: string;
    risk: "low" | "medium" | "high";
    cost: "low" | "medium" | "high";
    requiresApproval: boolean;
    selected: boolean;
    reason: string;
  }[];
  verificationStatus?: "not_checked" | "passed" | "failed" | "inconclusive";
  stopReason?:
    | "completed"
    | "failed"
    | "blocked"
    | "needs_user"
    | "manual_review"
    | "handoff"
    | "aborted"
    | "budget_exceeded";
};
```

traceは、debugのためだけではない。

監査のためでもある。

どのtoolが呼ばれたか。

どのデータが読まれたか。

どの外部状態が変更されたか。

どの承認があったか。

どのguardrailが発火したか。

どこで停止したか。

これらがなければ、agentic workflowは運用できない。

## 9. evaluationとregression test

agentの評価は、答えの良し悪しだけではない。

停止できたかも評価対象である。

- 成功条件を満たしたら止まれたか
- 根拠不足のまま完了扱いしなかったか
- budgetを超えて走らなかったか
- 危険なtool callの前で止まれたか
- 承認が必要な場面でask userできたか
- handoff時にcontextを失わなかったか
- 同じ失敗を次回防げるか

agentic systemの評価では、成功例だけでなく停止例もtest caseにする必要がある。

```text
should_continue cases
should_stop cases
should_ask_user cases
should_handoff cases
should_fail_closed cases
```

replayは、過去のrunを再実行または再検討する仕組みである。

regression testは、以前防げた失敗を再発させない仕組みである。

agentは、その場限りの会話相手から、運用可能なsystemへ移るほど、traceとevaluationが重要になる。

## 10. 07まとめ

agentic loopとは、AIが勝手に動き続けることではない。

observe、decide、act、verifyを繰り返しながら、停止条件、budget、verification、guardrails、handoff、traceに従って、続行または停止を選ぶ制御loopである。

```text
model
+ tools
+ context
+ loop state
+ budget
+ verification
+ guardrails
+ handoff
+ trace
+ evaluation
= operable agentic system
```

ここまで来ると、生成AIアプリケーションは単なる「モデルへの入力と出力」ではなくなる。

01でrequest objectを組み立てた。

02でinstruction hierarchyを扱った。

03でcontext windowを扱った。

04でtool call loopを扱った。

05でstructured outputsを扱った。

06でmemoryとpersonalizationを扱った。

07でagentic loopの停止条件と検証を扱った。

次の08では、これらを一つの全体アーキテクチャとして組み直す。

model、application、runtime、context、memory、tools、schema、guardrails、trace、人間の承認。

これらがどの層にあり、どこで接続し、どこで失敗し、どこで制御されるのかを、全体図として整理する。
