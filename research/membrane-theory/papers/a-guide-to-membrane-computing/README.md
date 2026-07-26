---
ページ作成日時: "2026-07-27 08:57 JST"
最終更新日時: "2026-07-27 08:57 JST"
---

# 『A Guide to Membrane Computing』読解プロジェクト

## 位置づけ

Gheorghe Păun と Grzegorz Rozenberg による論文「A Guide to Membrane Computing」を、単なる紹介ではなく、SGOSで育ちつつある「膜」の考え方に対する計算機科学上の先行研究として読む。

本ディレクトリは、原著の章別読解、用語整理、SGOSとの比較、そこから生まれる独自研究上の問いを保存する文献読解層である。

独自理論として確立した内容は、将来 `research/membrane-theory/` 直下の別文書へ昇格させる。原著の説明と佐藤側の解釈を混同しない。

## 原著情報

- Gheorghe Păun, Grzegorz Rozenberg
- “A Guide to Membrane Computing”
- *Theoretical Computer Science*, 287 (2002), pp. 73–100
- DOI: 10.1016/S0304-3975(02)00136-6
- 分野：Natural Computing / Membrane Computing / P systems

## 読解方針

各章について、次を分けて記録する。

1. 原著の内容に沿った日本語訳・再構成
2. 用語と形式モデルの説明
3. SGOSの膜、Communication、Handoff、Context Syncとの比較
4. 一致点だけでなく非対応・誤読の危険
5. 生成AI時代に拡張できる研究仮説
6. 佐藤の所感・追加の問い

P systemsの「膜」を、そのままSGOSの膜と同一視しない。P systemsは計算モデルであり、SGOSの膜は人間・AI・文脈・組織・世界の接触境界を含む、現時点ではより広い概念である。

## ファイル一覧

- `2026.07.27_01_chapter_01_introduction.md` — 第1章 Introduction
- `2026.07.27_02_glossary.md` — 読解用語集
- `2026.07.27_03_sgos_comparison_notes.md` — 章横断のSGOS比較ノート

以後、原著の章ごとに連番ファイルを追加する。

## 現在地

- 第1章：初回読解・日本語化・SGOS比較まで完了
- 第2章以降：未着手
- 原著の図表：必要な章で個別に読解する
- 独自の「SGOS膜理論」：文献読解と混同しない形で漸進的に抽出する

## 更新履歴

- 2026-07-27 08:57 JST：読解プロジェクトを開始し、目的、配置、読解方針、初期ファイル構成を定義。