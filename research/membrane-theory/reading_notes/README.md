# 膜理論 個別読解ノート

- ページ作成日時：2026-08-06 07:21 JST
- 最終更新日時：2026-08-06 17:37 JST
- status：reading note directory

このディレクトリは、膜理論の先行研究読解ノートを1文献1ファイルで保存する場所である。

`BIBLIOGRAPHY.md` は文献台帳として使い、長い読解メモ、引用、膜理論への接続、小説『膜』への変換メモはこのディレクトリに分離する。

## 保存場所

- `research/membrane-theory/reading_notes/`

## ファイル名

形式：

```text
{author-slug}_{publication-year}_{title-slug}.md
```

ルール：

| 要素 | ルール | 例 |
|---|---|---|
| `author-slug` | 著者姓を小文字ASCIIで書く。2名は `singer-nicolson`、3名は `varela-thompson-rosch`、4名以上は原則 `paun-et-al` | `gorter-grendel` |
| `publication-year` | 文献の初出年または対象版の年を4桁で書く | `1925` |
| `title-slug` | タイトルを3〜8語程度に短縮し、小文字ASCII・ハイフン区切りにする | `bimolecular-layers-of-lipoids` |

例：

| 文献 | ファイル名 |
|---|---|
| Gorter & Grendel (1925), "On Bimolecular Layers of Lipoids..." | `gorter-grendel_1925_bimolecular-layers-of-lipoids.md` |
| Singer & Nicolson (1972), "The Fluid Mosaic Model..." | `singer-nicolson_1972_fluid-mosaic-model.md` |
| Maturana & Varela (1980), *Autopoiesis and Cognition* | `maturana-varela_1980_autopoiesis-and-cognition.md` |
| Varela, Thompson & Rosch (1991), *The Embodied Mind* | `varela-thompson-rosch_1991_embodied-mind.md` |
| Paun, Rozenberg & Salomaa (2002), "A Guide to Membrane Computing" | `paun-rozenberg-salomaa_2002_guide-to-membrane-computing.md` |

## テンプレート

```markdown
# 文献名

- ページ作成日時：YYYY-MM-DD HH:MM JST
- 最終更新日時：YYYY-MM-DD HH:MM JST
- bibliography_id：
- status：reading

## 書誌情報

- 著者：
- 年：
- タイトル：
- 掲載誌 / 出版社：
- DOI / URL：

## 読む目的

## 要約

## 重要概念

## 膜理論への接続

## 小説『膜』への接続

## 限界・注意

## 次に読むべき文献

## 更新履歴

- YYYY-MM-DD HH:MM JST：初版作成。
```

## 読解ノート一覧

| bibliography_id | 読解ノート |
|---|---|
| BIB-001 | [`gorter-grendel_1925_bimolecular-layers-of-lipoids.md`](./gorter-grendel_1925_bimolecular-layers-of-lipoids.md) |
| BIB-002 | [`singer-nicolson_1972_fluid-mosaic-model.md`](./singer-nicolson_1972_fluid-mosaic-model.md) |
| BIB-003 | [`nicolson_2014_fluid-mosaic-model-after-40-years.md`](./nicolson_2014_fluid-mosaic-model-after-40-years.md) |
| BIB-004 | [`maturana-varela_1980_autopoiesis-and-cognition.md`](./maturana-varela_1980_autopoiesis-and-cognition.md) |
| BIB-011 | [`sierra_2009_depersonalization-neglected-syndrome.md`](./sierra_2009_depersonalization-neglected-syndrome.md) |
| BIB-012 | [`hunter-sierra-david_2004_epidemiology-depersonalisation-derealisation.md`](./hunter-sierra-david_2004_epidemiology-depersonalisation-derealisation.md) |

## 更新履歴

- 2026-08-06 17:37 JST：BIB-011 Sierra (2009) を登録し、既存の個別読解ノート一覧を同期。
- 2026-08-06 07:28 JST：BIB-001 Gorter and Grendel (1925) の個別読解ノートを登録。
- 2026-08-06 07:21 JST：初版作成。保存場所、命名規則、テンプレートを定義。
