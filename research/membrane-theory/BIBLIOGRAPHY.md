# 膜理論 BIBLIOGRAPHY

- ページ作成日時：2026-08-05 20:20 JST
- 最終更新日時：2026-08-06 17:37 JST
- status：working bibliography / first 20 sources

この文書は、膜理論を概念研究・創作研究・領域横断ノートから、外部検討に耐える研究へ育てるための文献台帳である。

`CHARTER.md` で定めた「先行研究を20本以上読み、文献台帳を作る」という条件の実行場所として使う。

## 目的

この文献台帳の目的は、単に参考文献を集めることではない。

膜理論において重要なのは、各文献を次の4点で読み分けることである。

| 観点 | 問い |
|---|---|
| 既存研究 | その文献は、元の分野で何を主張しているか |
| 膜への接続 | その文献は、膜、境界、交換、自己、媒体、現実感をどう考える手がかりになるか |
| 限界 | その文献を膜理論へ接続するとき、どこに飛躍や無理があるか |
| 小説への接続 | その文献は、小説『膜』の構造、場面、文体、読者経験へどう変換できるか |

## 読書ステータス

| status | 意味 |
|---|---|
| `unread` | 未読。読む候補として登録した状態 |
| `reading` | 読書中。メモはあるが、まだ要約していない状態 |
| `read` | 読了済み。内容は把握したが、膜理論への接続は未整理 |
| `summarized` | 要約済み。文献単体としての整理がある状態 |
| `integrated` | 膜理論の定義、仕様、小説素材、論文構成へ反映済み |
| `queued` | 次に読む候補。読む必要が高いが、まだ読解メモ化していない状態 |

## 個別読解ノートの保存場所と命名規則

`BIBLIOGRAPHY.md` は文献台帳に限定し、長い読解ノートは1文献1ファイルで分離する。

保存場所：

- `research/membrane-theory/reading_notes/`

ファイル名：

- `{author-slug}_{publication-year}_{title-slug}.md`

命名ルール：

| 要素 | ルール | 例 |
|---|---|---|
| `author-slug` | 著者姓を小文字ASCIIで書く。2名は `singer-nicolson`、3名は `varela-thompson-rosch`、4名以上は原則 `paun-et-al` | `gorter-grendel` |
| `publication-year` | 文献の初出年または対象版の年を4桁で書く | `1925` |
| `title-slug` | タイトルを3〜8語程度に短縮し、小文字ASCII・ハイフン区切りにする | `bimolecular-layers-of-lipoids` |

例：

| 文献 | 読解ノートファイル |
|---|---|
| Gorter & Grendel (1925), "On Bimolecular Layers of Lipoids..." | `reading_notes/gorter-grendel_1925_bimolecular-layers-of-lipoids.md` |
| Singer & Nicolson (1972), "The Fluid Mosaic Model..." | `reading_notes/singer-nicolson_1972_fluid-mosaic-model.md` |
| Maturana & Varela (1980), *Autopoiesis and Cognition* | `reading_notes/maturana-varela_1980_autopoiesis-and-cognition.md` |
| Varela, Thompson & Rosch (1991), *The Embodied Mind* | `reading_notes/varela-thompson-rosch_1991_embodied-mind.md` |
| Paun, Rozenberg & Salomaa (2002), "A Guide to Membrane Computing" | `reading_notes/paun-rozenberg-salomaa_2002_guide-to-membrane-computing.md` |

台帳側には、個別読解ノートへのリンク、status、読了日、膜理論への接続の要点だけを残す。

## 現在の読解状況

佐藤がすでに読んだ、または読んでいる途中の文書と、次に読むべきと判断している文書をここで管理する。

| ID | status | 文書 | 位置づけ | 次アクション |
|---|---|---|---|---|
| CUR-001 | reading | [`2026.07.25_01_human_cognitive_models_to_llm_mapping.md`](./2026.07.25_01_human_cognitive_models_to_llm_mapping.md) | 人間の認知モデルとLLMを接続する文書。膜理論のAI/認知接続に関わる | Wang et al. (2024) SPP論文読解として、要約と膜理論への接続を追記する |
| CUR-002 | reading | [`research/membrane-theory/papers/a-guide-to-membrane-computing/`](./papers/a-guide-to-membrane-computing/) | 膜計算 / P systems 読解プロジェクト。形式理論としての膜を扱う | 読解済み章を整理し、膜理論に使える点と使わない点を分ける |
| CUR-003 | reading | [`2026.07.27_01_doukisugitewaikenai_prologue_joucho_connection_disconnection.md`](./2026.07.27_01_doukisugitewaikenai_prologue_joucho_connection_disconnection.md) | 千葉雅也『動きすぎてはいけない』プロローグ読解。情緒、接続、切断に関わる | 「動きすぎないこと」と膜の調整作用を接続する |
| NEXT-001 | queued | [`2026.08.01_03_membrane_prior_research_map.md`](./2026.08.01_03_membrane_prior_research_map.md) | 先行研究マップ。20本読解の分野バランスを調整する入口 | 第1期20本との対応表を作る |
| NEXT-002 | queued | [`2026.08.01_04_membrane_literary_reference_books.md`](./2026.08.01_04_membrane_literary_reference_books.md) | 文学・技法参照棚。小説『膜』側の読書地図 | 第1期20本の文学枠と接続する |

## 最初に読む核5本

まずこの5本を優先する。

| 順 | ID | 文献 | 理由 |
|---:|---|---|---|
| 1 | BIB-002 | Singer & Nicolson, 1972 | 膜を固定壁ではなく、流動する場として読むための基礎 |
| 2 | BIB-004 | Maturana & Varela, 1980 | 境界が自己を成立させる、という生命システム論の核 |
| 3 | BIB-005 | Varela, Thompson & Rosch, 1991 | 身体、認知、経験を切り離さず扱うための基礎 |
| 4 | BIB-006 | Merleau-Ponty, 1945 | 世界に触れる身体、知覚、現実感を考えるための基礎 |
| 5 | BIB-010 | Sass & Parnas, 2003 | 自己境界・自己感の異常作動を考えるための基礎 |

この5本で、物質的な膜、生命を作る境界、身体化された認知、世界に触れる身体、自己境界の異常作動が揃う。

## 第1期 20本文献

| ID | status | 領域 | 文献 | 読む目的 | 膜理論への接続 |
|---|---|---|---|---|---|
| BIB-001 | summarized | 生物膜 | E. Gorter and F. Grendel, "On Bimolecular Layers of Lipoids on the Chromocytes of the Blood", 1925. | 膜を物質的構造として扱う出発点を確認する | 膜を比喩化する前に、膜がどのような科学的対象として成立したかを確認する |
| BIB-002 | summarized | 生物膜 | S. J. Singer and G. L. Nicolson, "The Fluid Mosaic Model of the Structure of Cell Membranes", 1972. | 生物膜モデルの古典を読む | 膜を固定された壁ではなく、流動し、分布し、機能する場として扱う |
| BIB-003 | summarized | 生物膜 | G. L. Nicolson, "The Fluid-Mosaic Model of Membrane Structure: Still Relevant to Understanding the Structure, Function and Dynamics of Biological Membranes after More than 40 Years", 2014. | 流動モザイクモデルの更新点を確認する | 古典モデルをそのまま借りず、膜モデルの更新可能性を保持する |
| BIB-004 | summarized | オートポイエーシス | Humberto R. Maturana and Francisco J. Varela, *Autopoiesis and Cognition: The Realization of the Living*, 1980. | 生命、境界、自己生成の関係を読む | 膜を「自己を囲うもの」ではなく「自己を作る作動」として考える |
| BIB-005 | unread | 身体化認知 | Francisco J. Varela, Evan Thompson, and Eleanor Rosch, *The Embodied Mind: Cognitive Science and Human Experience*, 1991. | 身体、認知、経験の接続を読む | AI対話、身体状態、現実感を同じ交換系の中で扱う |
| BIB-006 | unread | 現象学 | Maurice Merleau-Ponty, *Phenomenologie de la perception*, 1945. | 知覚と身体が世界をどう開くかを読む | 膜を「世界に触れる/触れすぎない」身体的条件として読む |
| BIB-007 | unread | 現象学・精神医学 | Thomas Fuchs, *Ecology of the Brain: The Phenomenology and Biology of the Embodied Mind*, 2018. | 脳、身体、環境を一つの循環系として読む | 心を脳内だけに閉じず、身体-環境の膜的循環として扱う |
| BIB-008 | unread | 拡張認知 | Andy Clark and David J. Chalmers, "The Extended Mind", 1998. | 心が身体外の道具や環境へ拡張する論点を読む | AI対話履歴を、外部化された認知・記憶・自己調整として扱う |
| BIB-009 | unread | 比喩論 | George Lakoff and Mark Johnson, *Metaphors We Live By*, 1980. | 比喩が単なる装飾でなく思考を組織する仕組みを読む | 「膜」を曖昧な比喩ではなく、概念装置として管理する |
| BIB-010 | unread | 精神病理学 | Louis A. Sass and Josef Parnas, "Schizophrenia, Consciousness, and the Self", 2003. | 自己感、自己境界、経験の変質を読む | 離人感・現実感喪失・解離を、自己境界の膜的異常として考える |
| BIB-011 | summarized | 離人感 | Mauricio Sierra, *Depersonalization: A New Look at a Neglected Syndrome*, 2009. | DPDRを臨床・神経心理学的に読む | 現実感の薄れ、自己との距離、感情の平坦化を膜の透過性として読む |
| BIB-012 | summarized | 離人感レビュー | Elaine C. Hunter, Mauricio Sierra, and Anthony S. David, "The Epidemiology of Depersonalisation and Derealisation: A Systematic Review", 2004. | DPDRの発生頻度、定義、臨床的位置づけを確認する | 体験的実感と医学的事実を分けるための足場にする |
| BIB-013 | unread | システム論 | Niklas Luhmann, *Soziale Systeme: Grundriss einer allgemeinen Theorie*, 1984. | システムが境界によって成立する考え方を読む | 社会、組織、AI対話、SGOSを境界作動として見る |
| BIB-014 | unread | 個体化論 | Gilbert Simondon, *L'individuation a la lumiere des notions de forme et d'information*, 1958/2005. | 個体を完成物でなく生成過程として読む | 膜を、既存主体を包むものではなく主体を分節生成する条件として扱う |
| BIB-015 | unread | 哲学・文学理論 | Gilles Deleuze and Felix Guattari, *Mille plateaux*, 1980. | リゾーム、生成変化、多層性を読む | 膜空間を、中心を持たない多層・多方向の構造として扱う |
| BIB-016 | unread | HCI・状況論 | Lucy A. Suchman, *Plans and Situated Actions: The Problem of Human-Machine Communication*, 1987. | 人間-機械関係を状況的行為として読む | AIとの対話を、命令実行ではなく状況内の相互調整として扱う |
| BIB-017 | unread | ポストヒューマン論 | N. Katherine Hayles, *How We Became Posthuman: Virtual Bodies in Cybernetics, Literature, and Informatics*, 1999. | 情報、身体、人間の境界変化を読む | Human-AI Systemを、人間の喪失ではなく境界再編として読む |
| BIB-018 | unread | メディア哲学 | Mark B. N. Hansen, *New Philosophy for New Media*, 2004. | メディアと身体感覚の接続を読む | AI対話やインターフェースを、身体感覚を変える膜として読む |
| BIB-019 | unread | 小説理論 | Brian McHale, *Postmodernist Fiction*, 1987. | 世界が多重化する小説技法を読む | 膜を説明せず、世界の重なりとして読者に発生させる技法を探す |
| BIB-020 | unread | 小説実例 | Thomas Pynchon, *Gravity's Rainbow*, 1973. | 陰謀、欲望、技術、歴史が絡み合う読書体験を読む | 膜そのものを語らず、読者側に膜的ネットワークを発生させる実例として読む |

## 進行中・関連文献

第1期20本とは別に、すでに読み始めている文献や、膜理論との接続が強い文献をここに置く。

| ID | status | 文献 | 位置づけ |
|---|---|---|---|
| REL-001 | reading | Gheorghe Paun, Grzegorz Rozenberg, and Arto Salomaa, "A Guide to Membrane Computing", 2002. | 形式理論としての膜。P systems読解プロジェクトの中心文献。`CUR-002` と対応 |

## 個別読解ノートテンプレート

各文献を読んだら、`reading_notes/` に以下の形式で1ファイルを作る。

```markdown
# 文献名

- bibliography_id：
- status：
- 読了日：
- 要約：
- 重要概念：
- 膜理論への接続：
- 小説『膜』への接続：
- 限界・注意：
- 次に読むべき文献：
```

## 個別読解ノート

長い読解ノートはここに追記せず、`reading_notes/` 配下に1文献1ファイルで保存する。

| ID | 読解ノート |
|---|---|
| BIB-001 | [`reading_notes/gorter-grendel_1925_bimolecular-layers-of-lipoids.md`](./reading_notes/gorter-grendel_1925_bimolecular-layers-of-lipoids.md) |
| BIB-002 | [`reading_notes/singer-nicolson_1972_fluid-mosaic-model.md`](./reading_notes/singer-nicolson_1972_fluid-mosaic-model.md) |
| BIB-003 | [`reading_notes/nicolson_2014_fluid-mosaic-model-after-40-years.md`](./reading_notes/nicolson_2014_fluid-mosaic-model-after-40-years.md)（Simons and Ikonen 1997 / Lingwood and Simons 2010 補遺あり） |
| BIB-004 | [`reading_notes/maturana-varela_1980_autopoiesis-and-cognition.md`](./reading_notes/maturana-varela_1980_autopoiesis-and-cognition.md) |
| BIB-011 | [`reading_notes/sierra_2009_depersonalization-neglected-syndrome.md`](./reading_notes/sierra_2009_depersonalization-neglected-syndrome.md) |
| BIB-012 | [`reading_notes/hunter-sierra-david_2004_epidemiology-depersonalisation-derealisation.md`](./reading_notes/hunter-sierra-david_2004_epidemiology-depersonalisation-derealisation.md) |
| REL-001 | `reading_notes/paun-rozenberg-salomaa_2002_guide-to-membrane-computing.md` |

## 更新履歴

- 2026-08-06 17:37 JST：BIB-011 Sierra (2009) の読解ノートを作成し、statusをsummarizedへ更新。
- 2026-08-06 17:12 JST：BIB-012 Hunter, Sierra, and David (2004) の読解ノートを作成し、statusをsummarizedへ更新。
- 2026-08-06 10:06 JST：BIB-004 Maturana and Varela (1980) の読解ノートを作成し、statusをsummarizedへ更新。
- 2026-08-06 09:43 JST：BIB-003読解ノートに、Simons and Ikonen (1997) / Lingwood and Simons (2010) の脂質ラフト補遺を追加。
- 2026-08-06 09:29 JST：BIB-003 Nicolson (2014) の読解ノートを作成し、statusをsummarizedへ更新。
- 2026-08-06 08:07 JST：BIB-002 Singer and Nicolson (1972) の読解ノートを作成し、statusをsummarizedへ更新。
- 2026-08-06 07:28 JST：BIB-001読解メモを個別読解ノートへ分離し、台帳側はリンク管理に変更。
- 2026-08-06 07:21 JST：読解ノートを1文献1ファイルで保存する方針を追加し、保存場所と命名規則を定義。
- 2026-08-05 22:27 JST：BIB-001 Gorter and Grendel (1925) の読解メモを追加し、statusをsummarizedへ更新。
- 2026-08-05 21:53 JST：research/spp-human-to-llm-mapping-20260805の統合に合わせ、CUR-001の所在未確認注記を解消。
- 2026-08-05 21:16 JST：現在の読解状況を追加。読了/読中文書3件、次に読む候補2件を登録。
- 2026-08-05 20:20 JST：初版作成。第1期20本文献、核5本、読書ステータス、読書メモテンプレートを追加。