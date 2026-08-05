# 膜理論 INDEX

- ページ作成日時：2026-08-05 17:17 JST
- 最終更新日時：2026-08-05 17:34 JST
- status：working index / classification ledger

この文書は、`research/membrane-theory/` に蓄積された文書を、研究・創作・原文ログの工程別に読み分けるための索引である。

現時点ではファイル移動を行わず、まず「どの文書がどの棚に属するか」をここで管理する。将来ディレクトリを分割する場合、このINDEXを移動台帳として使う。

## これは研究と言えるか

結論として、これは研究と言える。

ただし、現時点での性格は、査読論文型の完成された学術研究ではなく、**小説『膜』を成立させるための領域横断的な概念研究**である。

研究と呼べる理由は、次の条件をすでに満たし始めているためである。

| 条件 | 現状 |
|---|---|
| 問いがある | 「膜とは何か」「現実感・自己感・AI対話履歴・身体状態をどう接続して読むか」という問いがある |
| 用語を定義している | 膜、region、cline、入れ子、漏出、平坦化、交換装置などの作業定義がある |
| 先行研究を確認しようとしている | 生物学、精神医学、現象学、薬理学、AI研究、膜計算などへの参照地図がある |
| 自分の仮説を分けている | 既存概念と、佐藤の膜理論上の仮説を混同しない方針がある |
| 創作への変換先がある | 小説『膜』の技法、場面、情緒、構造へ接続している |

一方で、今後さらに研究として強くするには、各ノートで次の区別を保つ必要がある。

| 区別 | 注意点 |
|---|---|
| 既存研究 | 出典・用語・分野内での意味を確認する |
| 作業仮説 | 「膜理論ではこう読む」と明示する |
| 観測記録 | 佐藤の経験・対話・感覚として記録する |
| 小説素材 | 真偽ではなく、場面・語り・構造へ変換する |

したがって、この領域の名前は「膜理論研究ノート」または「小説『膜』制作資料室」がよい。短く言えば、**研究が小説のエンジンになっている場所**である。

## 推奨棚

| 仮想棚 | 役割 | 置くもの |
|---|---|---|
| `00_manifest/` | 中心命題と入口 | README、定義、読む順番、中心仮説 |
| `10_theory/` | 佐藤の膜理論 | 人間の膜、異常作動、トポロジー、A2A、交換装置 |
| `20_research/` | 先行研究 | 膜計算、生物学、精神医学、現象学、薬理学、AI研究 |
| `30_literature/` | 文学・技法 | 参考作品、読書ノート、小説技法 |
| `40_observations/` | 観測記録 | 情緒、身体感覚、離人感、生活上の実感、対話から出た洞察 |
| `50_fiction/` | 小説『膜』本体 | 書き出し、場面草稿、人物、プロット |
| `90_chat_logs/` | 原文ログ | 全文転記、未加工の会話記録 |

## 最初に読む順番

全体像をつかむ場合は、この順番で読む。

1. [`README.md`](./README.md)
   - 中心命題、暫定定義、現在の作品タイトル。
2. [`CHARTER.md`](./CHARTER.md)
   - 研究とは何か、完成された学術研究とは何か、膜理論をどこまで育てるか。
3. [`2026.08.03_06_membrane_space_topology_spec_v0.md`](./2026.08.03_06_membrane_space_topology_spec_v0.md)
   - 膜空間の基本仕様。現時点の理論的な骨格。
4. [`2026.08.01_03_membrane_prior_research_map.md`](./2026.08.01_03_membrane_prior_research_map.md)
   - 思い込みだけで進めないための先行研究マップ。
5. [`2026.08.01_01_human_membranes_concept_note.md`](./2026.08.01_01_human_membranes_concept_note.md)
   - 人間の膜を、生物学的膜、認知的膜、人称の膜、時間の膜、内面分節として整理した文書。
6. [`2026.08.01_02_membrane_abnormal_operations.md`](./2026.08.01_02_membrane_abnormal_operations.md)
   - 離人感、現実感喪失、解離、依存などを膜の異常作動として読む文書。
7. [`2026.08.03_05_membrane_joucho_first_response.md`](./2026.08.03_05_membrane_joucho_first_response.md)
   - 膜の情緒、比喩としての膜、定義の厳密さに関する入口。
8. [`2026.08.01_04_membrane_literary_reference_books.md`](./2026.08.01_04_membrane_literary_reference_books.md)
   - 小説化のための文学・技法参照棚。

原文の空気や生成過程を確認したい場合だけ、`chat_logs/` を読む。

## 文書分類台帳

| 現ファイル | 仮想棚 | 位置づけ |
|---|---|---|
| [`README.md`](./README.md) | `00_manifest/` | 膜理論領域の入口。中心命題、暫定定義、記録方針を置く |
| [`INDEX.md`](./INDEX.md) | `00_manifest/` | 文書分類台帳。読む順番と仮想棚を管理する |
| [`CHARTER.md`](./CHARTER.md) | `00_manifest/` | 膜理論を研究として扱うための憲章。研究の条件と学術研究への到達条件を定める |
| [`2026.08.03_06_membrane_space_topology_spec_v0.md`](./2026.08.03_06_membrane_space_topology_spec_v0.md) | `10_theory/` | 膜空間トポロジー仕様 v0。理論の骨格 |
| [`2026.08.01_01_human_membranes_concept_note.md`](./2026.08.01_01_human_membranes_concept_note.md) | `10_theory/` | 人間の膜の層を整理した概念ノート |
| [`2026.08.01_02_membrane_abnormal_operations.md`](./2026.08.01_02_membrane_abnormal_operations.md) | `10_theory/` | 離人感、現実感喪失、解離、依存などの異常作動一覧 |
| [`2026.07.27_01_human_outer_membrane_and_internal_a2a.md`](./2026.07.27_01_human_outer_membrane_and_internal_a2a.md) | `10_theory/` | 人間外膜モデル、内部膜型A2A、膜誘導型主体性の統合ノート |
| [`2026.07.27_02_human_outer_membrane_model_notion_full.md`](./2026.07.27_02_human_outer_membrane_model_notion_full.md) | `10_theory/` / `90_chat_logs/` | Notion全文移行版。正本性が高いが、原文素材も多い |
| [`2026.08.01_03_membrane_prior_research_map.md`](./2026.08.01_03_membrane_prior_research_map.md) | `20_research/` | 先行研究マップ。研究化の足場 |
| [`papers/a-guide-to-membrane-computing/README.md`](./papers/a-guide-to-membrane-computing/README.md) | `20_research/` | 膜計算読解プロジェクトの入口 |
| [`papers/a-guide-to-membrane-computing/2026.07.27_01_chapter_01_introduction.md`](./papers/a-guide-to-membrane-computing/2026.07.27_01_chapter_01_introduction.md) | `20_research/` | 膜計算 第1章読解 |
| [`papers/a-guide-to-membrane-computing/2026.07.27_02_glossary.md`](./papers/a-guide-to-membrane-computing/2026.07.27_02_glossary.md) | `20_research/` | 膜計算読解用語集 |
| [`papers/a-guide-to-membrane-computing/2026.07.27_03_sgos_comparison_notes.md`](./papers/a-guide-to-membrane-computing/2026.07.27_03_sgos_comparison_notes.md) | `20_research/` / `10_theory/` | P systems とSGOS膜構想の比較ノート |
| [`papers/a-guide-to-membrane-computing/2026.07.28_04_chapter_02_bio_membranes.md`](./papers/a-guide-to-membrane-computing/2026.07.28_04_chapter_02_bio_membranes.md) | `20_research/` | 生体膜章の読解 |
| [`papers/a-guide-to-membrane-computing/2026.07.28_05_chapter_03_basic_model.md`](./papers/a-guide-to-membrane-computing/2026.07.28_05_chapter_03_basic_model.md) | `20_research/` | P systems 基本モデル章の読解 |
| [`2026.07.27_01_doukisugitewaikenai_prologue_joucho_connection_disconnection.md`](./2026.07.27_01_doukisugitewaikenai_prologue_joucho_connection_disconnection.md) | `30_literature/` / `40_observations/` | 千葉雅也読書ノート。情緒、接続、切断への接続 |
| [`2026.08.01_04_membrane_literary_reference_books.md`](./2026.08.01_04_membrane_literary_reference_books.md) | `30_literature/` | 小説『膜』参考書籍一覧 |
| [`2026.08.03_05_membrane_joucho_first_response.md`](./2026.08.03_05_membrane_joucho_first_response.md) | `40_observations/` / `10_theory/` | 膜の情緒、比喩としての膜、定義の厳密さ |
| [`chat_logs/2026-07-27_membrane_chat.md`](./chat_logs/2026-07-27_membrane_chat.md) | `90_chat_logs/` | 初期の膜研究チャット全文記録 |
| [`chat_logs/2026-07-28_morning_scene_and_reading.md`](./chat_logs/2026-07-28_morning_scene_and_reading.md) | `50_fiction/` / `90_chat_logs/` | 朝の場面と読解。小説素材として扱う |
| [`chat_logs/2026-07-28_opening-reading.md`](./chat_logs/2026-07-28_opening-reading.md) | `50_fiction/` / `90_chat_logs/` | 書き出し読解。小説素材として扱う |
| [`chat_logs/2026-07-28_projectization_discomfort.md`](./chat_logs/2026-07-28_projectization_discomfort.md) | `40_observations/` / `90_chat_logs/` | プロジェクト化への違和感。研究態度の重要メモ |
| [`chat_logs/2026.07.27_01_a2a_full_transcript.md`](./chat_logs/2026.07.27_01_a2a_full_transcript.md) | `90_chat_logs/` | A2A原文対話録 |
| [`chat_logs/2026.08.01_01_human_membranes_and_abnormal_exchange_full_transcript.md`](./chat_logs/2026.08.01_01_human_membranes_and_abnormal_exchange_full_transcript.md) | `90_chat_logs/` | 人間の膜と精神交換の異常作動に関する全文記録 |
| [`chat_logs/2026.08.03_01_membrane_topology_conversation.md`](./chat_logs/2026.08.03_01_membrane_topology_conversation.md) | `90_chat_logs/` | 膜空間トポロジーの対話記録 |

## 整理ルール

- READMEには、中心命題、暫定定義、読むべき入口だけを置く。
- INDEXには、分類、読む順番、移動候補、棚割りを置く。
- 概念ノートでは、既存研究、作業仮説、観測記録、小説素材を混ぜたままにしない。
- chat_logsは原則として原文保存に徹し、理論化は別ノートで行う。
- 先行研究ノートでは、出典にある概念と、膜理論による読み替えを明示的に分ける。
- 小説草稿は、理論を説明する場所ではなく、膜が読者の側に発生する場として扱う。

## 次の一手

1. `50_fiction/` 相当の小説草稿・断章を、今後は `works/maku/` とどう分担するか決める。
2. `20_research/` 相当の先行研究について、1分野1文書の読解台帳を作る。
3. `10_theory/` 相当の文書から、重複する定義を `README.md` とトポロジー仕様へ集約する。

## 更新履歴

- 2026-08-05 17:34 JST：CHARTER.mdを追加し、読む順番と分類台帳に登録。
- 2026-08-05 17:17 JST：初版作成。膜理論文書群を仮想棚ごとに分類し、研究としての位置づけを整理。
