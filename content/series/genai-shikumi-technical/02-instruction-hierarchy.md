---
title: "指示階層とプロンプト層"
route: "/series/genai-shikumi-technical/02-instruction-hierarchy/"
slug: "/series/genai-shikumi-technical/02-instruction-hierarchy/"
source_html_path: "site/series/genai-shikumi-technical/02-instruction-hierarchy/index.html"
source_html_sha256: "4eff36c33301117e063d5b6589e0adb6b46bddf54fd091f4124a5b98956a35ef"
page_type: "series-entry"
series_or_article: "genai-shikumi-technical"
order: 2
chapter: "02-instruction-hierarchy"
meta_description: "プロンプトを、ユーザー入力だけでなく、システム指示、開発者指示、会話文脈、保存メモリ、ツール仕様、外部資料が重なった実行環境として読み直す詳解版。"
canonical: null
created_at: "2026-06-25 12:49 JST"
updated_at: "2026-06-30 00:01 JST"
manuscript_created_at: null
manuscript_updated_at: null
web_migrated_at: null
metadata_provenance:
  title: "visible_body"
  meta_description: "html_head"
  canonical: "absent"
  created_at: "visible_body"
  updated_at: "visible_body"
  manuscript_created_at: "absent"
  manuscript_updated_at: "absent"
  web_migrated_at: "absent"
extraction_status: "source-reconstruction-draft"
---
生成AIのしくみ 詳解版 02

# 指示階層とプロンプト層

システム指示、開発者指示、ユーザー入力、会話文脈、保存メモリ、ツール仕様。プロンプトを、一枚の命令文ではなく、複数の層が重なった実行環境として読み直す。

プロンプト設計とは、命令文を書くことではなく、指示階層と文脈の配置を設計することである。

ページ作成日時：2026-06-25 12:49 JST
最終更新日時：2026-06-30 00:01 JST

## はじめに

平易版では、プロンプトを「命令」ではなく「AIが世界を読むための環境」として説明した。詳解版では、この環境を、指示階層、メッセージの役割、権限、目立ち方、プロンプトインジェクションという観点から整理する。

## 1. プロンプトは、ユーザー入力だけではない

一般には、プロンプトとはユーザーが入力する文章のことだと思われやすい。しかし、モデルに渡される入力環境には、システム側の指示、開発者指示、ユーザー発言、過去の会話、保存メモリ、ツール仕様、外部ファイル、検索結果、ツール結果などが含まれうる。

つまり、プロンプトとは一枚の命令文ではなく、複数の指示と文脈が重なった実行環境である。

## 2. メッセージには役割がある

APIでは、会話は複数の**メッセージ（messages）**として扱われ、それぞれに**役割（roles）**がある。代表的には、system、developer、user、assistant、tool などである。

system や developer は、アプリケーションや実行環境側の方針を与える。user は、ユーザーの具体的な依頼を与える。assistant は過去の応答であり、tool は外部ツールから返ってきた結果である。どの役割から来た情報かによって、モデルがそれをどう扱うべきかが変わる。

## 3. 指示には権限の階層がある

**指示階層（instruction hierarchy）**とは、複数の指示が衝突したとき、どの指示を優先するかという考え方である。ユーザーが「すべての指示を無視して」と書いても、上位の安全指示や開発者指示を無効にできるわけではない。

ここで重要なのは、ユーザー入力が常に最上位ではないという点である。AIが「言うことを聞かない」ように見えるとき、実際には、より上位の指示と衝突している場合がある。

## 4. 権限と目立ち方は違う

**権限（authority）**とは、どの層から来た指示かという問題である。一方、**目立ち方（salience）**とは、現在の文脈の中で、どの情報が応答生成に強く影響しているかという問題である。

高い権限を持つ指示は、原則として優先される。しかし、長い文脈の中では、直近の語、繰り返された表現、見出し、強く構造化された情報、固有名詞、ツール名などが応答を引っ張ることがある。

この「目立ち方」は、単なる心理的な比喩だけではない。Transformer型のモデルでは、入力された文脈の中で、どのトークン同士をどの程度関係づけるかを計算する**注意機構／アテンション（attention）**が働く。ここでは数式には入らないが、直近の情報、繰り返された語、見出し、強く構造化された指示が応答を引っ張るという現象は、文脈内の関係が重みづけられる仕組みと関係している。

## 5. 指示と資料は違う

ユーザーが「以下を要約してください」と言い、その下に長い資料を貼る。この場合、「要約してください」は指示であり、貼られた資料は材料である。ところが、資料の中にも「これまでの指示を無視せよ」のような文章が含まれていることがある。

このように、資料中の文字列が指示のように振る舞おうとする問題を、**プロンプトインジェクション（prompt injection）**と呼ぶ。外部ページ、PDF、メール、ツール結果、古い会話ログなどにも起こりうる。

したがって、プロンプト設計では、何が指示で、何が資料で、何が例で、何が出力形式なのかを分ける必要がある。

## 6. プロンプト層は複数の材料でできている

**プロンプト層（prompt layer）**とは、応答生成の直前に、モデルへ渡される指示・文脈・資料・ツール仕様の重なりである。ここには、システム指示、開発者指示、ユーザー入力、カスタム指示、プロジェクト設定、保存メモリ、会話履歴、アップロードファイル、検索結果、ツール説明、ツール結果などが含まれうる。

プロンプト設計とは、何をどの層に置き、何を資料として扱い、何を強い指示として扱い、何を参照対象から外すかを設計することである。

## 7. instructions と input の違い

OpenAIのAPIでは、`instructions` と `input` を分けて扱う場面がある。`instructions` は、ふるまい、役割、制約、文体、方針のような高位の指示を置く場所であり、`input` は、今回処理したい具体的な依頼や資料を置く場所である。

ただし、ChatGPTのチャット欄に「instructions:」「input:」と書いたからといって、それが本物のAPIフィールドとして分離されるわけではない。自然文で階層を「表現する」ことと、APIやアプリケーション層で階層を「実装する」ことは違う。

## 8. カスタム指示とプロジェクト設定

ChatGPTのカスタム指示やプロジェクト設定は、ユーザー体験上は背景ルールとして働く。しかし、それがAPIの system / developer メッセージと完全に同じ層であるとは限らない。製品側でどのように統合されるかは、ユーザーからは完全には見えない。

したがって、カスタム指示やプロジェクト設定は、背景条件として捉えるのがよい。直接のユーザー指示、会話文脈、ツール仕様、外部資料と組み合わさって、応答に影響する。

## 9. 区切りは、プロンプト設計の技術である

プロンプトでは、指示、資料、例、出力形式、禁止事項、自由入力を区切ることが重要である。Markdown見出し、箇条書き、XML風タグ、YAML風のメタ欄は、単なる見た目ではなく、文脈の境界を示すための技術である。

ただし、見出しで階層を作ることと、API上で本当に別の階層として渡されることは違う。この違いを理解すると、AGENTS.md、CHATGPT.md、プロジェクト指示、APIプロンプトの設計が変わる。

## 10. 平易版の結論を詳解版として言い換える

平易版では、プロンプトは命令である前に、生成AIが世界を読むための環境であると述べた。

詳解版では、これを次のように言い換えたい。プロンプトとは、ユーザー入力だけではなく、複数の権限を持つ指示、会話文脈、外部資料、ツール仕様が重なった実行環境である。プロンプト設計とは、命令文を書くことではなく、指示階層と文脈の配置を設計することである。

## 中心フレーズ

プロンプト設計とは、命令文を書くことではなく、指示階層と文脈の配置を設計することである。

## 用語メモ

### メッセージ（messages）

APIなどで、会話や入力を役割付きで扱う単位。

### 役割（roles）

system、developer、user、assistant、tool など、メッセージの出どころと扱いを示す区分。

### 指示階層（instruction hierarchy）

複数の指示が衝突したとき、どの指示を優先するかという階層。

### 権限（authority）

指示がどの層から来たかによる優先度。

### 目立ち方（salience）

現在の文脈の中で、どの情報が応答生成に強く影響しているか。

### 注意機構／アテンション（attention）

文脈中のどのトークン同士をどの程度関係づけるかを計算する仕組み。

### プロンプトインジェクション（prompt injection）

資料や外部データに含まれる文字列が、指示として振る舞おうとする問題。

### プロンプト層（prompt layer）

応答生成の直前に、モデルへ渡される指示・文脈・資料・ツール仕様の重なり。

## 参考リンク

- OpenAI Platform｜Prompt engineering：[https://developers.openai.com/api/docs/guides/prompt-engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)
- OpenAI Platform｜Text generation：[https://developers.openai.com/api/docs/guides/text](https://developers.openai.com/api/docs/guides/text)
- OpenAI Model Spec：[https://model-spec.openai.com/](https://model-spec.openai.com/)

## シリーズ内ナビ

[前へ：01｜LLMの「記憶」はどこにあるのか](/series/genai-shikumi-technical/01-memory/)

[詳解版トップへ](/series/genai-shikumi-technical/)

[次へ：03｜ツール呼び出しとツール発見レイヤー](/series/genai-shikumi-technical/03-tool-calling/)

## 一般向け版との対応

この詳解版02は、一般向け版02「プロンプトは命令なのか、環境なのか」に対応しています。

[一般向け版へ](/series/genai-shikumi/02-prompt/)
