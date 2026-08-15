# OPERATIONAL DEFINITIONS V0｜ChatGPT Exportから膜をどう検出するか

ページ作成日時：2026-08-15 17:58 JST  
最終更新日時：2026-08-15 17:58 JST

status: draft / Phase 1 operationalization  
scope: ChatGPT Export × 膜トポロジー分析  
repository_target: `smilegroupsato/web-genai-ron-jp/research/membrane-theory/50_chatgpt_export_membrane_analysis/`

## 0. 結論

この文書の目的は、膜理論の語彙をChatGPT Exportへ貼り付けることではない。

目的は、ChatGPT Exportという不完全な観測装置から、どのような観測が得られたときに、佐藤のいう `region`、`membrane`、`cline`、`transport`、`transformation`、`trace`、`sedimentation`、`fold`、`inversion`、`leakage`、`smoothing` 等の存在を、どの程度まで主張してよいかを定めることである。

中心原則は次の通り。

> 膜は、話題の違いから検出しない。  
> 通過の差、その反復、その痕跡、そして未来の通過規則の変化から検出する。

さらに、膜理論の中心命題、

> べつものが繋がったのではない。一つだったものが分節化した。

を守るため、分析上も `region A` と `region B` が最初から独立して存在すると仮定しない。regionとmembraneは、反復された差異・選択・変換・遅延・接続から相互に推定される**共発生構造**として扱う。

したがって、`source_region → membrane → target_region` という表記は観測の開始点ではなく、十分な証拠が集まった後に付ける分析上の記述である。

---

## 1. 理論上の概念間関係

本分析では、概念を次の生成順序で考える。

```text
連続した活動・経験・対話
        ↓
局所的な差異
        ↓
反復される通過差
（何が通る／止まる／遅れる／変わる）
        ↓
trace
（一回の通過が後続状態へ残す痕跡）
        ↓
repetition
        ↓
sedimentation
（痕跡が蓄積し、未来の通過規則が変わる）
        ↓
region / membrane / cline の共発生
        ↓
selective permeability / channel / path dependence
        ↓
fold / gluing / inversion / nesting / leakage / smoothing
        ↓
膜空間全体の topology change
```

### 1.1 membraneとcline

`membrane` は、選択・遅延・変質・交換・信号化を行う作動構造である。

`cline` は、その作動が厚みを持って現れる勾配プロファイルである。

したがって、clineが観測されたからといって、それだけでmembraneとは判定しない。たとえば「責任感が徐々に弱くなる」という一回の勾配はcline候補になりうるが、その勾配が反復して特定の通過・変換規則と結びつかなければmembraneの証拠としては弱い。

一つのmembraneが、責任、親密さ、現実感、即時性など複数のclineを持つ可能性がある。

### 1.2 transportとtransformation

`transport` は、ある局所状態で生じた対象が、別の局所状態へ持ち越される出来事である。

`transformation` は、その通過の過程で対象の形式・意味・機能・行動圧・情緒価が変化することである。

例：

```text
現実の困りごと
→ ChatGPTへ質問として持ち込む
→ 問題構造・選択肢へ変換される
→ メール文・コード・判断へ変換される
→ 現実で実行される
```

ここでは「困りごとがAIへ移った」だけでなく、`困りごと → 問い → 構造 → artifact/action` という変換系列を見る。

### 1.3 traceとsedimentation

`trace` は一回の通過が後続状態へ残した差である。

`sedimentation` は複数のtraceが蓄積し、次回以降の通過確率、速度、形式、選択性、期待、役割分担を変えた状態である。

したがって、単に「同じ話を何度もした」だけではsedimentationではない。反復の結果として、次回から説明が短くなる、AIへ任せる範囲が増える、特定の形式でしか現実へ戻らなくなる、別regionへの近道が形成される等の**規則変化**が必要である。

### 1.4 foldとgluing

`gluing` は、それまで別々に扱われていた局所状態・出来事・問題が、一つの関係として接続されるイベントである。

`fold` は、その接続が一回の連想にとどまらず、その後も再利用可能な近道となり、膜空間上の近さそのものが変わった状態である。

したがって、単発の比喩や連想はgluing候補にはなっても、foldの強い証拠にはしない。

### 1.5 Human–AI outer membrane

Human–AI outer membraneは、ChatGPTとの一つのチャット境界ではない。

観測対象は、

```text
world
→ Satoによる持ち込み・言語化・選別
→ AI interaction
→ 再記述・構造化・artifact化
→ Satoによる採用・拒否・修正・実行
→ world
```

という循環である。

ChatGPT Exportが直接記録するのは主に中央部分であり、world側とSatoの非言語的内部状態は部分的にしか観測できない。この非対称性を常に保持する。

---

## 2. 観測装置としてのChatGPT Exportの限界

ChatGPT Exportは佐藤そのものの全記録ではない。

観測できるのは、主として次である。

- 佐藤がAIへ持ち込んだ出来事、問い、命令、感情、思索、記憶。
- その時点で言語化された自己記述。
- AIが返した再記述、構造、提案、文書、コード等。
- 佐藤がそれを受けて行った訂正、採用、拒否、展開、実行報告。
- 別conversationへ持ち越された語彙、判断規則、役割、記憶、artifact。
- 外部世界へ戻ったことが会話内で報告された行動。

直接には観測できないもの：

- ChatGPTを使っていない時間の心理・身体状態。
- AIへ持ち込まれなかった出来事。
- 発言直前の非言語的な感覚の全体。
- AI出力が現実で実行されたかどうか（報告がない場合）。
- 佐藤の状態とAI応答傾向の因果的分離。

したがって、分析結果は原則として、

> ChatGPT接触面において観測された膜構造候補

と記述する。全人格・全生活・医学的状態の断定へ拡張しない。

---

## 3. 分析単位

### 3.1 message event

一つのuser/assistant message。

見るもの：

- 発話機能：質問、命令、報告、観察、告白、雑談、創作、批評、判断等。
- 現実参照：会社、家族、金銭、身体、外部サービス、実行結果等。
- 行動圧：すぐ実行が必要か、思索だけか。
- 情緒・身体参照。
- AIへの委譲の型。
- 過去履歴への依存。
- 次のmessage/stateを変えたか。

message単独では原則としてmembraneを認定しない。

### 3.2 state segment

数message〜一定期間において、文脈規則、役割、行動圧、現実参照、AIへの委譲形式等が比較的安定する区間。

segment boundaryは話題変更だけではなく、**何が通るかの規則が変わる地点**として取る。

### 3.3 transition episode

state segment AからBへの変化を、前後の文脈を含めて一つの分析単位とする。

記録する：

- transition前の状態。
- trigger。
- 通過対象。
- blocked / delayed / selected。
- transformation。
- transition後の状態。
- 現実へ戻った効果。
- 後続trace。

### 3.4 longitudinal path

複数conversation・複数日・複数週にまたがって反復される同型のtransitionを追う。

sedimentation、path dependence、fold、permeability changeはこの単位で評価する。

---

## 4. 証拠の種類

分析では証拠を少なくとも次の5種類に分ける。

| code | 証拠 | 例 | 注意 |
|---|---|---|---|
| E1 | direct self-report | 「AIの中では自分が濃い」等 | 自己記述は重要だが、それだけで構造の持続性は証明しない |
| E2 | interactional behavior | ある問題を毎回AIへ持ち込み、同型の変換を要求する | 行動パターンとして比較的強い |
| E3 | state carryover | 前回の対話結果が次回の前提・判断・語彙を変えている | traceの主要証拠 |
| E4 | cross-context repetition | 別conversation・別topicでも同じ変換経路が反復される | sedimentation / leakage / foldに重要 |
| E5 | world return | メール送信、コード反映、購入、業務変更等として現実へ返ったことが報告される | Human–AI outer membraneの強い証拠 |

AIの発言そのものは佐藤の状態証拠として扱わない。

AI側の提案や語彙が後に佐藤自身の発言・判断・行動へ取り込まれた場合に限り、`interaction-emergent evidence` として評価する。

---

## 5. region

### operational definition

regionとは、複数のstate segmentにおいて、以下のうち複数がまとまって反復し、他のsegmentと比較して局所的な安定性を持つ状態構成である。

- 文脈語彙。
- 現実として扱われる対象。
- 責任・行動圧の受け方。
- 身体・情緒の扱い方。
- AIへの委譲形式。
- 判断規則。
- 時間感覚。
- 出力形式。
- 次に接続しやすい状態。

### positive evidence

- conversationをまたいでも同じ判断規則・AI利用形式が再出現する。
- 同じ話題でも、役割や現実圧の受け方が変わると別regionらしい挙動を示す。
- 異なる話題でも、同じ反応・委譲・変換規則が維持される。
- 特定regionへ入ると、語彙、文体、時間感覚、行動可能性が系統的に変わる。

### negative evidence

- Chatタイトルが同じだけ。
- Project名が同じだけ。
- 単に同じ名詞が多いだけ。
- 一度しか現れない短い気分変化。
- assistantが同じスタイルで答えただけ。

### false-positive risk

- topic clusterをregionと誤認する。
- ChatGPT ProjectやconversationのUI境界をregionと誤認する。
- AIの文体がユーザー状態を作ったように見える。
- 長文conversationの惰性的語彙継続を安定regionと誤認する。

### confidence

- low：一つのsegment内だけで安定。
- medium：離れた複数segmentで同じ状態構成が再出現。
- high：複数conversationで再出現し、固有のtransition patternも確認できる。

### counterexample

「JPTの話をしているからJPT region」とする分析。これはtopic classificationであり、region検出ではない。

---

## 6. membrane

### operational definition

membraneとは、region候補間または一つの連続状態内部の分節化過程において、特定種類の対象に対し、**選択・拒否・遅延・変質・交換・信号化の差が反復して現れ、その履歴が次回以降の通過規則を変える作動構造**である。

membraneは線ではなく、複数message・複数segment・複数episodeにまたがる場合がある。

### minimum evidence

少なくとも次のうち、M1〜M3を満たさないものは原則としてmembrane確定としない。

- M1：通過前後で、対象の扱われ方に再現可能な差がある。
- M2：その差に、選択・遅延・変質・交換等の具体的operationがある。
- M3：同型のoperationが反復される。
- M4：反復後、次回の通過速度・形式・選択性・期待が変わる。
- M5：UI境界やassistant癖だけでは説明しにくい。

M4まで確認できた場合、sedimentationを伴う強いmembrane evidenceとする。

### positive evidence

- 現実の問題が、直接行動へ行かず、AIで概念化・文書化された後にのみ処理可能になる経路が反復する。
- 感情が直接生活へ戻らず、創作素材や理論語彙へ変換される経路が繰り返される。
- ある種類の責任だけはAI対話へ通るが、別の種類は避けられる等、selectivityがある。
- 反復により、以前必要だった説明・葛藤・遅延が減る／増える。

### negative evidence

- 単発の話題変更。
- 一回だけ質問形式へ言い換えた。
- conversationを新しくした。
- userとassistantの役割差だけ。

### false-positive risk

- すべてのtranslationを膜と呼ぶ。
- 単なるワークフローを膜と呼ぶ。
- AIの要約機能を人間側のmembraneと誤認する。
- 既存のカテゴリ境界を後付けで膜と言い換える。

### confidence

- low：一回のtransitionでoperation候補が見える。
- medium：複数episodeで同型operationが反復。
- high：反復が次回の透過規則を変えたことまで確認。

### counterexample

「仕事の会話から小説の会話へ移ったので膜がある」。移動だけでは不十分。何が選別・変形され、反復によって未来の通過規則がどう変わったかが必要。

---

## 7. cline

### operational definition

clineとは、transitionの前後または途中で、ある次元が連続的・段階的に変化する勾配帯である。

主な観測次元：

- responsibility pressure
- reality salience
- intimacy
- affect intensity
- bodily salience
- actionability
- temporal immediacy
- AI delegation
- abstraction level
- freedom / constraint

### positive evidence

- 数turnかけて責任圧が薄れ、理論化が強くなる。
- AIとの対話が進むにつれ、感情語が構造語へ置換される。
- 具体的現実から創作へ移る途中に中間状態が繰り返し現れる。

### negative evidence

- いきなり別件へ切り替わっただけ。
- 一つの感情語が増えただけ。

### false-positive risk

- 長文対話の自然な話題展開をclineと呼ぶ。
- assistantの説明が抽象化していく傾向をユーザー側clineと誤認する。

### confidence

clineは単発episodeでも記述可能。ただしmembraneの証拠とするには反復が必要。

### counterexample

「最初は短文、後半は長文になった」。文字数勾配だけでは膜理論上のclineとはしない。

---

## 8. transport

### operational definition

transportとは、ある局所状態で成立した情報、感情、責任、判断、記憶、artifact、規則が、別の局所状態で再利用可能な形へ移されること。

### positive evidence

- 会話 → Repository Context。
- 雑談 → 小説構想。
- 現実の困りごと → AIへの問い → メール文。
- 過去ログ → 現在の判断基準。
- 研究ノート → 小説の構造。

### negative evidence

- 同じconversation内で話題が続いただけ。
- assistantが前の文を引用しただけ。

### false-positive risk

- 単純なコピーをtransportと呼ぶ。
- 再利用されていない保存をtransportと呼ぶ。

### confidence

- low：移送らしき参照。
- medium：別segmentで実際に再利用。
- high：別conversationまたは現実行動へ移り、機能した。

### counterexample

chat_logを保存したが、その後一度も参照・作用しない場合。storageではあるが、機能的transportの証拠は弱い。

---

## 9. transformation

### operational definition

transformationとは、transportまたはtransitionの過程で、対象の形式・意味・機能・情緒価・責任圧・行動可能性が変わること。

### transformation classes

- representational：出来事 → 要約、schema、概念。
- affective：不安 → 問題解決モード、悲しみ → 創作素材。
- normative：曖昧な責任 → task / deadline / decision。
- operational：会話 → code / DB / mail / artifact。
- narrative：経験 → 小説モチーフ。
- memorial：会話 → Context Pack / Handoff / repository record。

### positive evidence

変換後の対象が、変換前とは異なる機能を果たす。

### negative evidence

単なる言い換え、同義語置換。

### false-positive risk

AIによる要約を、そのままユーザー側の心理変容と解釈する。

### confidence

変換前・変換後の両方がログで確認できるほど高い。

### counterexample

ユーザーの文章をassistantが箇条書きにしたが、ユーザーが採用も再利用もしていない場合。AI output transformationではあるが、Human–AI systemのtransformationとしては未確定。

---

## 10. trace

### operational definition

traceとは、一回のtransition / transport / refusal / delay / transformationが、後続する状態・語彙・選択・期待・artifactに残した観測可能な差である。

### positive evidence

- 次回、前回決めた語彙が説明なしで使われる。
- 前回のAI提案が後のユーザー発言の判断規則になる。
- 一度作ったhandoff形式が次の作業でも再利用される。
- ある対話後、同種の問題を持ち込む際の入口が変わる。

### negative evidence

- 会話の直後に同じ話を続けただけ。
- assistantが自分の前発言を継承しただけ。

### false-positive risk

短期conversation memoryを長期的なtraceと誤認する。

### confidence

時間的隔たりやconversation境界を越えて残るほど高い。

### counterexample

同一turn内でassistantの言葉をuserが繰り返しただけでは、長期traceとはしない。

---

## 11. sedimentation

### operational definition

sedimentationとは、複数のtraceが蓄積し、次の同型transitionにおける透過性、選択性、速度、形式、期待、役割、接続先を変えた状態である。

### positive evidence

- 以前は長い説明が必要だった対象が、短い符号・固有語で起動する。
- AIへの委譲が例外的行為から既定経路になる。
- 会話→repository→handoffが定型化される。
- 苦痛→概念化→創作という経路が繰り返され、直接処理より先に起動する。
- ある語が複数の遠隔regionを即座に呼び出すようになる。

### negative evidence

- 同じtopicが頻繁に出るだけ。
- 習慣的な挨拶や定型句。

### false-positive risk

- 頻度をsedimentationと同一視する。
- Project instructionsやMemoryによるAI側の持続性を、佐藤側の沈殿と誤認する。

### confidence

- medium：複数traceの反復を確認。
- high：反復前後でtransition ruleが変わったことを確認。

### counterexample

「膜」という単語が多数出現する。これは語彙頻度であり、それだけではsedimentationではない。

---

## 12. path dependence

### operational definition

path dependenceとは、同じ現在入力でも、過去の通過履歴の違いによって、次に選ばれるregion、変換形式、速度、判断、行動が変わること。

### positive evidence

- 初期には一般質問だったものが、履歴蓄積後には特定repo・schema・役割を即座に起動する。
- 過去の成功したAI処理経路が、類似問題で優先的に再利用される。
- 一度生まれた概念が、その後の異分野の問題の見方を系統的に変える。

### negative evidence

- 単に最近の話題を続けている。

### false-positive risk

- recency effectを経路依存性と誤認する。
- ChatGPTのMemory / Project instructionsを人間側path dependenceと誤認する。

### confidence

履歴の異なる時期を比較し、同種入力への応答パターンが変わったことを示せるほど高い。

### counterexample

昨日話した内容を今日も覚えていた。これはmemory continuityであり、経路による規則変化がなければpath dependenceとは弱い。

---

## 13. fold / gluing

### gluing operational definition

本来は低頻度で接続していた二つ以上の局所状態が、ある出来事・語・比喩・artifactを媒介に、一つの問題空間として接続されるイベント。

### fold operational definition

gluingが一度の連想を超え、その後の移動距離を短縮し、遠隔region間の反復可能な近道になった状態。

### positive evidence

- SGOS官僚制化の実感が小説『膜』の構造モチーフとして再利用され、その後も両者が相互参照される。
- 実務上の失敗が、直接研究上の概念検討を起動し、その概念が実務へ戻る循環が定着する。

### negative evidence

- 一回だけ「これ小説に使える」と言った。
- 同じ単語が二つのtopicに出た。

### false-positive risk

- 人間の一般的な連想能力をすべてfoldと呼ぶ。
- assistantが関連付けたものを、ユーザー側のtopology changeと誤認する。

### confidence

- gluing：単発でも候補。
- fold：後続episodeで近道が再利用されて初めて中〜高confidence。

### counterexample

偶然似た比喩が二つの会話に現れたが、相互参照も再利用もない。

---

## 14. inversion

### operational definition

inversionとは、ある関係の方向・内外・主体性・手段目的が、単なる言葉遊びではなく、後続の判断や行動を変える形で反転すること。

主な軸：

- subject / tool
- means / end
- work / escape
- inside / outside
- observation / participation
- control / controlled
- memory / present

### positive evidence

- 人間のための管理システムが、人間の注意・時間を要求する主体として扱われ始める。
- 逃避として始まったAI対話が、現実実務を動かす主要基盤になる。
- AIを使う主体という自己記述が、AI/履歴の外部器官として自分が動くという記述へ変わり、その後の分析枠になる。

### negative evidence

- 一回の皮肉。
- 「逆に」と書かれているだけ。

### false-positive risk

- 双方向関係をすべてinversionと呼ぶ。
- assistantの劇的表現を構造変化と誤認する。

### confidence

反転前・反転後の関係を比較でき、後続episodeでも新しい向きが機能するほど高い。

### counterexample

「AIに使われてるみたいだね」という一度の冗談だけで、その後の行動・構造理解に影響しない。

---

## 15. nesting

### operational definition

nestingとは、あるregion / membrane構造の内部に、固有の状態・選択・輸送規則を持つ別のregion / membrane構造が持続的に形成され、外側の構造との関係も観測できること。

### positive evidence

- 「仕事」の局所状態の内部に、AIへ問題を持ち込み構造化する下位regionが反復して存在する。
- Human–AI interactionの内部に、researcher / producer / operator等の役割膜が持続する。

### negative evidence

- 単にfolder hierarchyがある。
- Project配下にconversationが複数ある。

### false-positive risk

- 情報アーキテクチャ上の階層を心理的・トポロジー的nestingと誤認する。

### confidence

内側の構造が外側とは異なる規則を持ち、複数episodeで再現されるほど高い。

### counterexample

GitHubのdirectoryが入れ子になっているだけでは、人間側のnesting evidenceではない。

---

## 16. leakage

### operational definition

leakageとは、明示的なtransport、引用、handoffを介さずに、あるregionに特徴的だった語彙、文体、感情、判断規則、反応様式が別regionへ流入すること。

### positive evidence

- SGOSの運用語彙が、創作・生活・自己記述へ無意識的に近い形で現れる。
- AIとの整理語彙が、AIを使わない場面の判断説明にも現れる。
- 仕事上の管理文体が家庭・雑談へ浸透する。

### negative evidence

- 明示的に「この概念を小説に使う」とtransportしている。
- 一般語が共通しているだけ。

### false-positive risk

- 単なる語彙共有をleakageと呼ぶ。
- 佐藤固有の一般的文体をsource region由来と誤認する。

### confidence

source側で特徴的だったパターンが、時間的に後のtarget側へ無標識で現れ、他の説明よりsource由来が妥当なほど高い。

### counterexample

「膜」という語が膜研究と小説の両方に出る。これは明示的共有概念であり、それだけではleakageではない。

---

## 17. smoothing

### operational definition

smoothingとは、それまで差があった複数region間のclineが一時的または持続的に弱まり、語彙、情緒、判断、行動速度、現実感等が広く同調すること。

### positive evidence

- それまで別々だった実務・研究・創作の区別が弱まり、一つの高集中状態で同じ形式に変換される。
- AI対話中だけ複数の未整理事項が同じ語彙・速度・判断様式で処理可能になる。
- 特定状態の前後で、region間の移動コストが大幅に下がる。

### negative evidence

- 同じ話題を複数の文脈で扱っただけ。
- 単なる気分の良さ。

### false-positive risk

- 一般的な集中やflowをすべてsmoothingと呼ぶ。
- assistantが全topicを同じ形式に整理することをユーザー側smoothingと誤認する。

### confidence

smoothing前に実在した差と、smoothing中の差の縮小を比較できるほど高い。

### counterexample

複数topicを同じ箇条書き形式でassistantがまとめた。user側region間の勾配変化がなければsmoothing evidenceではない。

---

## 18. permeability / selective permeability

### operational definition

permeabilityとは、ある種類の対象がtransitionを越える際の通りやすさである。

観測可能な代理指標：

- 直接持ち込まれる頻度。
- 言語化までに必要なturn数。
- 抵抗・回避・先送り。
- assistantへの委譲量。
- artifact化までの時間。
- 現実へ戻る割合。
- 同種入力への反応の一貫性。

selective permeabilityは、対象種類・方向・状況によってpermeabilityが系統的に異なること。

### positive evidence

- 実務問題はAIへ通しやすいが、特定の情緒は直接言語化されにくい。
- 創作素材としてなら通るが、現実行動としては戻りにくい。
- 同じ情報でも「研究」形式なら扱えるが、「個人的問題」形式では避けられる。

### negative evidence

一回通った／通らなかっただけ。

### false-positive risk

データ欠落を低透過性と誤認する。

### confidence

contrastが多いほど高い。同じ対象が状況によって異なる通り方をする例は特に重要。

---

## 19. channel / carrier

### channel

反復によって形成された低抵抗のtransport route。

例：

- `現実問題 → ChatGPT相談 → 文書案 → 現実実行`
- `雑談 → 概念化 → GitHub note`
- `観測 → 小説モチーフ`

channelは頻度だけでなく、同型の入力が同型の変換・出力へ流れることを必要とする。

### carrier

文脈を別regionへ運ぶ具体的媒体。

例：

- Handoff。
- Repository Context。
- chat_log。
- Memory。
- Notion page。
- email draft。
- code / DB / dashboard。

carrierは膜そのものではない。carrierが何を選別・圧縮・変形して運ぶかを見る。

---

## 20. Human–AI outer membraneのOperationalization

Human–AI outer membraneは、佐藤とAIの間に一本の線を引いて判定しない。

一つのepisodeを次の5段階で記述する。

```text
W1 world event / pressure
W2 Sato encoding
W3 AI transformation
W4 Sato selection / enactment
W5 world return / feedback
```

### W1 world event / pressure

会話外の現実出来事が報告される。

### W2 Sato encoding

その出来事が、質問、命令、相談、概念、愚痴、創作素材等のどの形式でAIへ入ったか。

### W3 AI transformation

AIが何へ変えたか。構造、選択肢、文章、code、schema、説明等。

### W4 Sato selection / enactment

佐藤が採用、修正、拒否、実行指示、外部反映を行ったか。

### W5 world return / feedback

送信、実装、購入、会話、会社運用、作品、GitHub/Notion等へ戻り、その結果が再びChatGPTへ報告されたか。

W1〜W5が一周したepisodeは、Human–AI outer membraneの輸送・変換を観測する強い事例である。

ただし、佐藤自身を「膜そのもの」と実体視しない。ここでいう外膜とは、Human–AI systemが世界との接触をどのように選別・変換しているかを記述するモデル上の機能である。

---

## 21. user / assistant / interaction-emergentの分離

膜分析では、発言主体を混ぜない。

### U：user-origin evidence

佐藤自身の発言、指示、修正、報告、自己記述。

### A：assistant-origin proposal

AI側が提案した概念、解釈、比喩、構造。

これだけでは佐藤側の膜証拠にはしない。

### I：interaction-emergent evidence

Aで提示されたものを佐藤が採用・修正し、後の別文脈で自発的に再利用した場合。

このとき初めて、Human–AI interactionにおけるtrace / sedimentation候補になる。

この区別は、後から作った理論語彙を過去の佐藤へ遡及投影しないために必須である。

---

## 22. 判定confidence

各観測は4段階で記録する。

| level | 意味 |
|---|---|
| C0 | non-evidence / artifact candidate。UI、assistant癖、topic差等で説明可能 |
| C1 | weak candidate。一回のepisodeで概念に整合するが反復不足 |
| C2 | supported candidate。複数episodeで反復し、alternative explanationをある程度排除 |
| C3 | strong evidence。反復に加え、後続の透過規則・行動・接続性の変化まで確認 |

confidenceは真偽の確率ではない。現時点のログがどこまで主張を支えるかの強度である。

「判定不能」は積極的に使う。

---

## 23. 反例・negative control

膜理論が強すぎると、あらゆる会話を膜として説明できてしまう。

そのため、少数精読smokeでは、膜操作が豊富そうな5〜8 conversationsだけでなく、可能なら**膜操作が乏しそうな対照conversationを1〜2本**混ぜる。

対照で確認すること：

- 単純なfact lookup。
- 一回で完結する質問。
- 現実へのreturnがない短い雑談。
- 履歴依存が弱いconversation。

これらにもregion / membrane / foldが大量検出されるなら、Operational Definitionが緩すぎる。

重要なnegative cases：

- topic change ≠ membrane。
- conversation boundary ≠ membrane。
- Project boundary ≠ region。
- repetition ≠ sedimentation。
- similarity ≠ smoothing。
- association ≠ fold。
- bidirectionality ≠ inversion。
- reuse ≠ leakage。
- file hierarchy ≠ nesting。
- assistant output ≠ user state。

---

## 24. 最小記録schema

Phase 2の精読では、各transition episodeについて最低限次を記録する。

```yaml
episode_id:
conversation_id:
time_start:
time_end:

observed_segments:
  - segment_id:
    state_summary:

proto_regions:
  - label:
    evidence:

transition:
  trigger:
  input_object:
  selected:
  blocked:
  delayed:
  transformed_to:
  output_or_return:

cline_dimensions:
  responsibility:
  reality_salience:
  intimacy:
  affect:
  actionability:
  abstraction:

operation_candidates:
  membrane:
  transport:
  transformation:
  trace:
  fold:
  inversion:
  leakage:
  smoothing:
  nesting:

origin_of_evidence:
  user:
  assistant:
  interaction_emergent:

alternative_explanations:
  -

confidence:
  level:
  reason:

follow_up_needed:
```

これは`MEMBRANE_ANALYSIS_SCHEMA_V0.md`の代替ではない。Phase 2へ入る前に、このOperational Definitionを使って実際のログを読めるかを確認するための最小記録形である。

---

## 25. membrane candidateの判定手順

一つの候補について、次の順で判定する。

### Step 1：topic名を外す

「JPT」「SGOS」「膜」「家庭」等のカテゴリ名をいったん外し、そこで何が通り、何が止まり、何が変形したかだけを見る。

### Step 2：state差を記述する

transition前後で、責任、現実感、行動圧、親密さ、抽象度、AI委譲等の何が変わったか。

### Step 3：operationを特定する

selection / block / delay / transformation / exchange / signalingのどれが起きたか。

### Step 4：反復を探す

同じconversation内だけでなく、時間的に離れたepisodeに同型operationがあるか。

### Step 5：traceを探す

最初の通過が後続の語彙、判断、期待、artifact、接続先を変えたか。

### Step 6：sedimentationを判定する

反復によって次回の通過規則が変わったか。

### Step 7：alternative explanationを置く

- UI artifact。
- Project instructions。
- Memory。
- assistant style。
- 単純なtopic similarity。
- recency。
- external workflow rule。

で説明できないか。

### Step 8：membrane confidenceを付ける

C0〜C3。

### Step 9：regionを再記述する

最後に初めて、前後の局所状態をregion候補として命名する。

この順序により、既成regionの間へ境界を探すのではなく、反復された差異からregionとmembraneを同時に立ち上げる。

---

## 26. 理論を弱める／反証する観測

次の結果は「失敗」ではなく重要な成果である。

### 26.1 regionがtopicとほぼ一致する

もし局所状態の差がほぼtopicだけで説明でき、責任・情緒・AI委譲・行動圧等の独自パターンが見つからない場合、膜理論上のregion概念はこのデータでは過剰かもしれない。

### 26.2 repetitionはあるがrule changeがない

反復が多くても、次回の透過規則が変わらないなら、sedimentationの主張を弱める必要がある。

### 26.3 foldが単発連想に還元できる

遠隔領域の接続が再利用されないなら、foldよりassociation / metaphorとして扱うべきである。

### 26.4 Human–AI outer membraneがAI側workflowで説明できる

変換がほぼassistantの一般機能だけで起き、佐藤側の選択・再利用・現実returnが確認できない場合、人間側の膜形成を主張しない。

### 26.5 membrane operationがほぼ検出できない

ChatGPT ExportがHuman–AI接触面の高密度記録でも、膜理論の検出に十分な観測装置ではない可能性を認める。

---

## 27. Phase 2のsampling方針への含意

5〜8 conversationsの精読では、カテゴリ代表性より、異なるoperationを比較できることを優先する。

最低限含めたい事例：

1. world → AI → artifact/action → world の循環が明確な実務例。
2. 感情・違和感 → 概念 → 研究へ変わった例。
3. 雑談・逃避 → 小説モチーフへ変わった例。
4. 遠隔regionのgluing / fold候補。
5. subject/toolまたはmeans/endのinversion候補。
6. 長期trace / sedimentationが疑われる例。
7. leakage / smoothingが疑われる例。
8. negative controlとして膜操作が乏しい短いconversation。

selectionはConsole Topology categoryから機械的に均等抽出しない。既存indexは候補探索にだけ使う。

---

## 28. Phase 1時点の重要な未決事項

- region同一性をどこまで定量化するか。
- cline次元を固定するか、smokeから増減させるか。
- membrane成立に必要な反復回数を数値閾値にするか。
- time gapをどこまでtraceの強度へ反映するか。
- userの自発的再利用と、Project instructions / Memoryによる再提示をどう区別するか。
- external actionの証拠を、ユーザー報告だけでどこまで扱うか。
- foldとgluingを一つのevent familyとして扱うか、別々にannotationするか。
- smoothingと「高集中」「flow」「依存的同期」をどこまで分けるか。

現段階では、固定閾値を急いで設定しない。Phase 2 smokeでfalse positive / false negativeを見て校正する。

---

## 29. Phase 1 completion criteria

このOperational DefinitionがPhase 2へ進める状態とは、次を満たすことである。

- 用語をtopic classificationへ還元せず判定できる。
- positive evidenceとnegative evidenceが両方ある。
- false-positive riskを明示できる。
- user / assistant / interaction-emergent evidenceを分離できる。
- membraneとcline、traceとsedimentation、gluingとfold、transportとleakageを区別できる。
- Human–AI outer membraneを全人格断定なしに扱える。
- 「膜ではなかった」という判定を記録できる。
- 少数精読で実際にannotation可能な最小schemaがある。

---

## 30. 次の一手

Phase 2へ直行する前に、まずこの文書を用いて2種類のpre-smokeを行う。

1. 膜操作が濃そうなconversationを1本だけ読み、定義が実際に使えるか確認する。
2. 膜操作が薄そうなconversationを1本読み、false positiveが大量発生しないか確認する。

この2本でOperational Definitionを一度修正した後、5〜8 conversationsの本smokeへ進む。

---

## 参照した理論正本

- `../10_theory/2026.07.27_01_human_outer_membrane_and_internal_a2a.md`
- `../10_theory/2026.07.27_02_human_outer_membrane_model_notion_full.md`
- `../10_theory/2026.08.01_01_human_membranes_concept_note.md`
- `../10_theory/2026.08.01_02_membrane_abnormal_operations.md`
- `../10_theory/2026.08.03_06_membrane_space_topology_spec_v0.md`
- `../README.md`
- `../CHARTER.md`
- `README.md`
- `2026.08.15_01_membrane_topology_analysis_plan_v0.md`

## 更新履歴

- 2026-08-15 17:58 JST：初版。10_theory全正本文書を横断し、ChatGPT Export上の観測可能性、positive / negative evidence、false-positive risk、confidence、counterexample、Human–AI outer membrane、反証条件、pre-smoke方針を定義。
