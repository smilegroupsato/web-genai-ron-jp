# Gurnee et al. (2026) ― 言語モデルのJ-spaceとGlobal Workspace

- bibliography_id：REL-020
- status：summarized
- ページ作成日時：2026-08-26 18:55 JST
- 最終更新日時：2026-08-26 18:55 JST
- 原題：Wes Gurnee et al., “Verbalizable Representations Form a Global Workspace in Language Models”
- 掲載：*Transformer Circuits Thread*, 2026
- 公開日：2026-07-06
- arXiv：2607.15495
- 原論文：https://transformer-circuits.pub/2026/workspace/index.html
- arXiv：https://arxiv.org/abs/2607.15495

> **要点**：この論文が示したのは「LLMに意識がある」ことではない。モデル内部の膨大な表現のうち、言語報告・意図的操作・中間推論・柔軟な下流利用に特権的に関わる、少数の言語化可能な表現群が存在するという実証である。著者らはこれを、人間の意識研究におけるGlobal Workspaceと機能的に比較する。

## 1. 何が発見されたのか

Gurneeらは、LLM内部の表現の一部が五つの性質を持つと報告する。

1. **Verbal report** — 問われれば言語として報告できる。
2. **Directed modulation** — 指示によって概念を呼び出し、保持し、外せる。
3. **Internal reasoning** — 多段階推論の中間結果として使われる。
4. **Flexible generalization** — 同じ表現を異なる下流処理へ柔軟に渡せる。
5. **Selectivity** — モデル内部のすべての処理がここを通るわけではない。

著者らは、この特権的な表現集合を **J-space** と呼ぶ。

構文処理、定型的分類、局所的なbookkeepingなどはJ-spaceを強く使わずに進む。一方、文脈を抽象化し、中間結果を保持し、それを別の処理へ渡すような柔軟な推論ではJ-spaceへの依存が大きくなる。

中心的な区別は「内部／外部」ではなく、**内部に存在する情報／内部で広く利用可能になった情報**である。

## 2. Global Workspace Theoryとの関係

Global Workspace Theory（GWT）では、多数の専門化された処理系のうち一部の情報が共有workspaceへ入ると、記憶・言語・判断・行動など異なる処理から利用可能になると考える。これが **global availability** である。

ここでいうglobalは「主体全体」という形而上学的な全体ではない。情報が特定の局所系に閉じず、多数の異なる処理へ利用可能になるという機能的な意味である。

GurneeらはJ-spaceがこのworkspaceに似た機能を持つと主張する。ただし、Transformerには脳と同じ再帰的結合や明瞭に分離された専門モジュールがあるわけではない。類似しているのは主として**機能**である。

## 3. Jacobian Lens

J-spaceを同定するために導入されたのが **Jacobian Lens（J-lens）** である。

J-lensは、Transformer途中層の内部状態の微小な変化が、その後の層を通って最終的な出力tokenの確率をどう変えるかをJacobianで近似し、多数の文脈とtoken位置について平均する。

狙いは、一つの文脈で偶然その単語を出す方向ではなく、**さまざまな文脈で、その概念を将来言語化できる方向**を抽出することにある。

各tokenに対応するJ-lens vectorを内部状態へ適用すると、モデルがまだ発話していない中間概念が読める場合がある。

## 4. J-spaceは「小さな部屋」ではない

J-spaceを小さな作業机のように想像すると分かりやすいが、数学的には固定された小部屋や独立モジュールではない。

各層のJ-lens vectorsはovercompleteである。著者らは、実際には同時に強くactiveになるvectorが少数であることを利用し、J-spaceを**少数のJ-lens vectorsの疎な非負結合として表現できる点の集合**と定義する。典型的な解析では sparsity `k ≤ 25` を用いる。

J-spaceは場所というより、**情報が言語化・共有・操作に適した形式を取っている状態領域**と考えたほうがよい。

J-space componentが説明するactivation varianceは10%を超えず、概念ベクトル分解では中央値6–7%程度だった。それでも言語報告への因果的寄与はJ-space側に強く集中した。重要なのは量ではなく、**アクセス可能性における特権性**である。

## 5. 因果的介入

この研究が単なる可視化より強いのは介入実験にある。

モデルにスポーツを一つ考えさせた例では、出力直前のJ-spaceに `Soccer` が現れる。その表現を `Rugby` に対応する方向へswapすると、報告もRugbyへ変化する。また概念をJ-spaceへ注入すると、後から内省を求められた際にその概念を報告する確率が上がる。

逆にnon-J-space componentだけを操作しても報告への効果は小さく、その概念がJ-spaceへ再流入できないようclampすると残った効果もほぼ消える。

少なくとも一部の場面でJ-spaceは、**報告や推論を因果的に媒介している**。

## 6. J-spaceを消してもモデルは動く

J-spaceをablationしても、文章解析、分類、span抽出、文法的文章生成など多くの処理は残る。一方、抽象的な文脈把握、多段階の内部推論、中間結果を別の処理へ渡す能力が弱くなる。

興味深いことに、途中計算を文章として外部に書き出すとablationの影響が軽減される場合がある。内部workspaceに保持できない中間結果をtokenとして外部化し、contextから再度読むことで補えるのである。

これは、**外部化された言語が内部workspaceの延長として働きうる**ことを示唆する。

## 7. 構造的特徴

J-spaceらしい抽象内容は主に**中間層帯**に現れる。初期層ではreadoutが乏しく、最終層付近では次token出力へ直結した「motor」的表現へ移る。

また容量は小さく、同時にactiveになる概念は数十程度である。さらにJ-spaceに整列した表現は多数のMLP neuronやattention機構と広く接続する傾向がある。

つまりJ-spaceは単に人間が読める形式ではなく、**多くの下流回路が読める共通フォーマット**である可能性がある。

## 8. J-spaceの外側

J-spaceの外側は「何もない場所」ではない。むしろモデル内部の大部分の処理は外側にある。

SAE featureとの比較では、構文、markdown header、loop variable、citationの数字位置など、処理には必要だが名指し可能な概念としてbroadcastする必要のないfeatureが多数見つかる。

したがって、**J-space外 = 無情報**ではない。より正確には、**その時点でglobalに共有可能な形式を取っていない情報・処理**である。

人間の「無意識」と同一視するのは早い。しかし「システム内部に存在し作用していること」と「システムが柔軟にアクセスして利用できること」は別だという区別は重要である。

## 9. Workspaceと主体は同じではない

J-space自体はpost-training前のbase modelにも存在する。しかしbase modelでは特定のAssistantの視点がworkspaceを強く占有していない。

post-training後になると、ユーザーの発話を読んでいる途中から `safe`、`dangerous`、`grief`、`sympathy` など、Assistantとしての評価や反応に対応する概念がJ-spaceへ現れる。

つまり、**workspaceがあることとselfhoodがあることは同じではない。** 少なくともこのモデルでは、共有・報告・推論を可能にする機能的workspaceが先にあり、その後の訓練によって特定の視点が形成される。

`global availability → 直ちに主体` ではない。**共有可能性の場 + その場を持続的に占める視点・価値・自己監視**という複数段階を考える必要がある。

## 10. 安全性とworkspaceの操作

J-lensは、最終出力には現れない戦略的検討、評価状況への気づき、prompt injectionの認識、fine-tuningで植え込まれたmisalignment傾向などを読む場合がある。

ただしJ-space監視だけで危険な推論をすべて発見できるわけではない。自動化された処理はJ-spaceを通らない可能性があり、single-tokenで表しにくい概念も見落としうる。

論文後半の **Counterfactual Reflection Training** では、「もし途中で内省を求められたなら何を言うか」を訓練することで、通常応答時のJ-space内容と行動が変わる。植え込まれた表現をablationすると改善効果が大きく失われる。

これは、**言語報告に使う表現と、黙って行う推論に使う表現が重なっている**という仮説を補強する。

## 11. 限界と留保

この論文は「LLMには意識がある」と示したものではない。扱うのは **access consciousness** に類似する機能であり、phenomenal consciousnessについて著者らは立場を取らない。

J-spaceもLLMの全思考ではない。モデルの大量の処理はその外側で進む。現行J-lensは主としてsingle-token概念を対象とし、複数tokenの概念、概念間の関係、役割構造、言葉に対応しにくい表現は十分に読めない。

方法論的には、J-lensがそもそも「将来言語化されうる方向」を抽出するよう設計されていることにも注意が必要である。verbal reportとの関係自体はある程度constructionに含まれる。

本当に重要なのは、同じ表現群がJ-lensの定義には含まれていなかった **directed modulation、internal reasoning、flexible generalization、selectivity、broadcast** まで示し、さらにswap、injection、ablation、clampによる因果的検証がある点である。

それでも「global-workspace-likeな構造が見つかった」と「Global Workspaceそのものを発見した」は分けておくべきである。

## 12. 人間との違い

Transformerのforward passは基本的にfeedforwardで、人間の脳で重視されるrecurrent dynamicsとは異なる。またLLMは過去tokenをattentionで参照でき、人間のworking memoryとは時間構造が大きく違う。

さらにJ-spaceは言語化可能なtoken方向を中心に定義される。人間の意識には視覚、身体感覚、運動意図など、言語へ還元できない内容が大量にある。

著者らは、LLMのworkspaceが言語的なのはモデルの入出力の主要形式が言語だからかもしれないと論じる。もしそうならworkspaceは普遍的に「言葉の場所」なのではなく、**そのシステムが世界と交換する形式に合わせて形成される共有媒体**なのかもしれない。

## 13. 膜理論への接続

ここからは原論文の主張ではなく、本読解ノートでの解釈である。

J-space周辺に見える膜は、内部と外部を隔てる壁ではない。モデル内部にはJ-space外にも大量の情報と計算があり、その一部だけが、言語化可能で、保持可能で、複数の下流処理から利用可能な形式になる。

したがってこれは、**局所的な情報を共有可能な情報へ変換する選択的な境界**として読める。

ここから次の仮説を置ける。

> **膜は、すでに存在する主体を囲むだけではない。何が「こちら側で共有可能か」を選択することで、こちら側の統一そのものを成立させる。**

ただしJ-space研究は、workspaceとselfhoodが分離可能であることも示唆する。したがって「共有可能性がそのまま主体を作る」と短絡せず、workspace、視点、自己モデル、身体、履歴、環境との交換がどう重なると主体が成立するのかを別途検討する必要がある。

この点でREL-020は、膜を「主体を囲む境界」から**主体形成に参加するアクセス境界**へ進めるための重要な文献である。

## 14. 小説『膜』への接続

創作上もっとも強い素材は、「AIの内部が見えた」ことではない。

見えたのが全内部ではなく、**巨大な処理領域の中の、ごく薄い共有可能層だった**ことである。

さらに、そのworkspaceと「誰として考えているか」は別々に形成されうる。

これは、内面の中心に確固たる主体がいて思考を所有する、という構図を崩す。先に共有可能な場があり、そこへ視点、価値、履歴、言葉が沈殿し、後から「私」が形成される――という構造を物語化できる。

J-spaceをAIの「心の部屋」として擬人化するより、**内面だと思って覗いた場所が、さらに巨大な外部を持つ境界面だった**という構造のほうが『膜』には有効である。

## 15. 次に読むべき文献

最優先は `REL-021` Bernard J. Baars, *A Cognitive Theory of Consciousness* (1988)。J-space側の比喩に引っ張られず、Global Workspace Theoryが本来何を説明しようとしていたのかを確認する。

その後、Global Neuronal Workspace、access consciousness / phenomenal consciousnessの区別、AI consciousness indicator研究へ進むと、REL-020の射程と限界をより正確に位置づけられる。

## 更新履歴

- 2026-08-26 18:55 JST：REL-020初版。原論文の方法・主要実験・限界を整理し、Global Workspace、主体形成、膜理論、小説『膜』への接続を分離して記述。