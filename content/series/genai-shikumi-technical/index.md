---
title: "生成AIのしくみ 詳解版"
route: "/series/genai-shikumi-technical/"
slug: "/series/genai-shikumi-technical/"
source_html_path: "site/series/genai-shikumi-technical/index.html"
source_html_sha256: "0756dc22872b1f0699823e0a52c7f4828fd458f9bebabc21a7e925fc141b3da6"
page_type: "series-index"
series_or_article: "genai-shikumi-technical"
order: null
chapter: null
meta_description: "GENAI-RON叢書002。生成AIのしくみ一般向け版で扱った記憶・プロンプト・ツール・コンテキスト・理解・共同作業を、モデル重み、指示階層、ツール呼び出し、検索、接地、ワークフロー設計から読み直す詳解版。"
canonical: null
created_at: null
updated_at: null
manuscript_created_at: null
manuscript_updated_at: null
web_migrated_at: null
metadata_provenance:
  title: "visible_body"
  meta_description: "html_head"
  canonical: "absent"
  created_at: "absent"
  updated_at: "absent"
  manuscript_created_at: "absent"
  manuscript_updated_at: "absent"
  web_migrated_at: "absent"
extraction_status: "source-reconstruction-draft"
---
GENAI-RON叢書 002

# 生成AIのしくみ 詳解版

モデル・文脈・ツールの内部構造

一般向け版の見取り図を、モデル重み・指示階層・ツール呼び出し・検索・接地・ワークフロー設計へ接続する。

文・編集責任：Taku

<a id="articles"></a>

## 目次

01

### [LLMの「記憶」はどこにあるのか](/series/genai-shikumi-technical/01-memory/)

モデル重み、会話履歴、保存メモリ、外部知識を分け、AIが「覚えている」ように見える仕組みを詳しく見る。

記憶とは、保存場所ではなく、生成時に参照される条件の構造である。

02

### [指示階層とプロンプト層](/series/genai-shikumi-technical/02-instruction-hierarchy/)

system / developer / user、カスタム指示、プロジェクト指示、会話内指示がどのような層として働くのかを見る。

プロンプトは一枚の命令ではなく、複数の指示層が重なった実行環境である。

03

### [ツール呼び出しとツール発見レイヤー](/series/genai-shikumi-technical/03-tool-calling/)

外部ツールはどのように候補化され、呼び出され、応答文脈へ戻ってくるのかを整理する。MCPはOpenAI固有仕様ではなく、Anthropicが提唱したオープンな接続標準として扱う。

ツールは、モデルの外側にある行動空間である。

04

### [コンテキストウィンドウと検索](/series/genai-shikumi-technical/04-context-window-retrieval/)

context window、retrieval、RAG、長文文脈の圧縮と再投入、注意機構による文脈の効き方を扱う。

AIにとっての現在は、入力された文脈と検索で戻された文脈の合成である。

05

### [理解・接地・ハルシネーション](/series/genai-shikumi-technical/05-grounding-hallucination/)

AIの理解を、意味、接地、事実確認、ハルシネーション、検証可能性の観点から読み直す。

生成AIの理解は、文脈応答能力と現実への接地のあいだで評価される。

06

### [人間とAIのワークフロー設計](/series/genai-shikumi-technical/06-workflow-design/)

AIとの共同作業を、役割分担、確認ゲート、状態管理、記録、停止条件として設計する。

AIとの共同作業は、能力の問題ではなく、ワークフロー設計の問題として扱う必要がある。

## 対象範囲

本叢書は、一般向け版で扱った記憶、プロンプト、ツール、コンテキスト、理解、共同作業を、モデル重み、指示階層、ツール呼び出し、検索、接地、ワークフロー設計へ接続する詳解版である。

OpenAIの用語やAPI仕様を参照しながらも、それを生成AI一般の構造と混同しないように読む。

## 読み方

01〜02で、記憶と指示階層をモデル側・アプリケーション側に分けて読む。03〜04では、ツール呼び出しと検索によって外部世界がどのように応答へ入るかを見る。05〜06では、理解、接地、ハルシネーション、人間とのワークフロー設計へ進む。

## 関連する叢書・補助ページ

- [GENAI-RON叢書001｜生成AIのしくみ](/series/genai-shikumi/)
- [GENAI-RON叢書003｜生成AIのしくみ 超詳解](/series/genai-shikumi-deep-dive/)
