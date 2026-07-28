---
title: "生成AIの歴史｜完全版年表"
route: "/notes/history-of-generative-ai/timeline.html"
source_html_path: "site/notes/history-of-generative-ai/timeline.html"
source_html_sha256: "0903d83c591ba1c3f97852398cbe1dede27f9451ebfe8a0d34099e6952b34929"
page_type: "note"
series_or_article: "notes"
order: null
chapter: null
meta_description: "生成AIの歴史を、学問史・技術史・計算資源史・企業／モデル史・社会／市場史の5層でたどる完全版年表。"
canonical: null
created_at: null
updated_at: "2026-06-18"
manuscript_created_at: null
manuscript_updated_at: null
web_migrated_at: null
metadata_provenance:
  title: "visible_body"
  meta_description: "html_head"
  canonical: "absent"
  created_at: "absent"
  updated_at: "visible_body"
  manuscript_created_at: "absent"
  manuscript_updated_at: "absent"
  web_migrated_at: "absent"
extraction_status: "source-reconstruction-draft"
---
Full Timeline

# 生成AIの歴史｜完全版年表

**生成AIを、モデル発売日一覧ではなく、複数の歴史が交差したものとして読む。**

学問史、技術史、計算資源史、企業／モデル史、社会／市場史の5層から、情報理論から推論モデルまでをたどる。

公開版 v1.1 / 最終更新：2026-06-18

PERIODS

[第1期｜情報を形式化する](#period-1)

[第2期｜統計的言語処理へ](#period-2)

[第3期｜深層学習とTransformer](#period-3)

[第4期｜生成AIの社会化](#period-4)

[第5期｜推論・エージェント時代](#period-5)

[出典・参考資料](#sources)

## 凡例

5期は歴史全体の時代区分、5層は各イベントの分類タグである。5期と5層は混同しない。

### 学問史

言語観、知能観、統計、情報理論、認知科学。

### 技術史

ニューラルネット、Attention、Transformer、RLHF、Diffusion。

### 計算資源史

GPU、TPU、クラウド、Webコーパス、データセンター。

### 企業／モデル史

OpenAI、Google、Anthropic、Meta、Stability AI、Midjourneyなど。

### 社会／市場史

検索、SNS、SaaS、教育、開発支援、規制、知的労働。

第1期｜1948〜1989

## 情報を形式化する

知能、言語、情報を形式化しようとした時代。生成AIの直接の技術ではないが、機械が言語を扱うための問いがここで立ち上がる。

1948

学問史

### Claude Shannon『A Mathematical Theory of Communication』

情報を意味ではなく、符号化・通信・ノイズ・エントロピーとして扱う枠組みが成立した。「言語を確率的系列として見る」視点の前史になる。

1950

学問史

### Alan Turing『Computing Machinery and Intelligence』

機械が知能を持つとは何か、対話によって知能を評価できるのか、という問いが定式化された。

1956

学問史

### ダートマス会議

Artificial Intelligenceという名称が定着する出発点。生成AIそのものの始まりではないが、AIを研究分野として名づけた基点である。

1957

学問史

### Noam Chomsky『Syntactic Structures』

言語を有限の規則から無限の文を生成する体系として捉える生成文法が登場した。後の生成AIとは異なるが、「生成」という問いの重要な前史である。

1966

技術史

### ELIZA

対話型プログラムの初期例。理解しているように見えるインターフェースの原型として、後のチャットAIを考えるうえで重要である。

1986

技術史

### 誤差逆伝播法の普及

多層ニューラルネットを学習するための実用的手法として広がり、後の深層学習の基礎条件になった。

1980s

社会／市場史

### エキスパートシステムの流行と限界

人間の知識をルールとして記述するAIが期待されたが、現実世界の曖昧さと常識量にぶつかった。

第2期｜1990〜2011

## 統計的言語処理への転換

AIは、人間がルールを書くものから、大量データから確率的に学ぶものへ移る。Webは、人類の言語化された世界を巨大な機械可読コーパスに変えていく。

1990s

技術史

### 統計的自然言語処理の主流化

ルールを人間が書くより、大量データから確率的に学ぶ方向へ移行した。意味理解よりも分布処理が実用的成果を出し始める。

1997

技術史

### LSTM

長期依存を扱うRNN系モデルとして登場し、Transformer以前の系列処理を支える重要技術になった。

1998

社会／市場史

### Google創業

Webを巨大な言語・リンク構造として索引化する検索エンジンが成長した。後のLLM時代に向けて、Webが巨大な学習資源になる前提が形成される。

2001

社会／市場史

### Wikipedia開始

人類の知識が機械可読な大規模テキストとして蓄積される象徴的出来事。

2006〜2012

計算資源史

### GPUによる深層学習の実用化が進む

大規模ニューラルネットを現実的な時間で学習できる条件が整い始める。

2009

社会／市場史

### ImageNet公開

画像認識における大規模データセット時代を象徴し、後の視覚モデル・マルチモーダルAIへの前史になる。

第3期｜2012〜2021

## 深層学習とTransformer

深層学習、表現学習、生成モデル、Attention、Transformerが接続し、現在のLLMの直接的な基盤が成立する。

2012

技術史

### AlexNetがImageNetで大きな成果

深層学習とGPU計算の有効性が広く認識された。

2013

技術史

### word2vec

単語をベクトルとして扱い、意味を空間上の関係として捉える流れが強まった。

2014

技術史

### Sequence-to-Sequence

入力系列から出力系列を生成するニューラル機械翻訳の基礎が整う。

2014

技術史

### GAN

生成モデルが画像生成などで注目を集める。

2014〜2015

技術史

### Attention機構

モデルが入力のどこを見るかを学習する仕組みが発展し、Transformerへの重要な前段階になる。

2015

技術史

### Diffusion Model

ノイズからデータを生成する考え方が登場し、後の画像生成AIの重要な流れにつながる。

2015

企業／モデル史

### OpenAI設立

大規模AI研究組織として登場し、後のGPT系列の開発主体になる。

2017

技術史

### Transformer

Attentionだけに基づくアーキテクチャとして提案され、並列計算と大規模学習に適したLLMの基盤になる。

2018

企業／モデル史

### GPT-1

Transformerを用いた事前学習と微調整の方向を示し、GPT系列の出発点になる。

2018

企業／モデル史

### BERT

Transformerを使った事前学習モデルが、自然言語処理の中心へ移り始める。

2019

企業／モデル史

### GPT-2

大規模化によって自然な文章生成能力が注目され、公開範囲や安全性をめぐる議論も起きた。

2020

企業／モデル史

### GPT-3

スケーリングによって、少数例からタスクに対応する能力が注目された。

2021

計算資源史

### 大規模学習のクラウド化・産業化

巨大モデルの学習は、研究室単独ではなく、クラウド、専用チップ、データセンター、資本投下と結びつく。

2021

企業／モデル史

### GitHub Copilot

生成AIが文章生成だけでなく、実務的なソフトウェア開発支援へ進出した節目。

2021

企業／モデル史

### Anthropic設立

AI安全、Constitutional AI、スケーリングに伴うリスクを前面に出す企業として登場。

2021

技術史

### CLIP

画像と言語を対応づける表現学習が、後の画像生成・マルチモーダルAIの基礎になる。

第4期｜2022〜2023

## 生成AIの社会化

生成AIが研究技術から一般ユーザーの道具へ移る。ChatGPTは「生成AI技術の誕生日」ではなく、社会的普及の転換点である。

2022-01

技術史

### InstructGPT

大規模言語モデルを、人間の指示に従いやすい形へ調整する方向を明確にした。

2022

技術史

### RLHF

人間のフィードバックを用いて、モデル出力を人間の意図や好みに合わせる調整手法が重要になる。

2022

企業／モデル史

### Stable Diffusion

画像生成AIが一般ユーザーやクリエイターに広がり、著作権や創作の議論も拡大した。

2022

企業／モデル史

### Midjourney

プロンプトによる画像生成が、デザイン、アート、広告、SNSの文脈へ広がる。

2022-11-30

企業／モデル史

### ChatGPT公開

LLMが自然言語で誰でも使える社会的インターフェースを得た。生成AIの社会的爆発の転換点。

2022〜2023

社会／市場史

### 教育・仕事・著作権をめぐる議論の拡大

生成AIは、便利なツールであると同時に、評価、創作、労働、情報信頼性をめぐる社会問題として現れる。

2023-03

企業／モデル史

### GPT-4

高性能LLMの代表的節目。生成AIが文章生成だけでなく、推論、コード、画像理解へ広がる可能性を示す。

2023-03

企業／モデル史

### Claude

Anthropicによる対話型AI。安全性、長文対話、憲法AIなどの観点が注目される。

2023-07

企業／モデル史

### Llama 2

オープンモデル陣営を成立させた象徴的イベント。生成AI史は「最高性能モデル競争」だけでなく、「誰がモデルへアクセスできるか」の歴史でもあることを示す。

2023-12

企業／モデル史

### Google Gemini 1.0

Google DeepMind体制下で、マルチモーダル基盤モデルGeminiを発表。

第5期｜2024〜

## 推論・エージェント時代

生成AIは、文章生成AIから推論AIへ、推論AIからエージェントへ、エージェントから知的作業環境の再編へ進みつつある。

2024-02

企業／モデル史

### Gemini 1.5

長文コンテキストとマルチモーダル処理が重要な競争軸になる。

2024-03

企業／モデル史

### Claude 3

Opus / Sonnet / Haiku の3モデル構成で発表。性能、速度、コストの使い分けが前面に出る。

2024-04

企業／モデル史

### Llama 3

オープンモデルの性能競争がさらに進み、ローカルLLMや企業内利用の可能性が広がる。

2024-05

企業／モデル史

### GPT-4o

テキスト、音声、画像を横断するマルチモーダルな対話体験が前面に出た。

2024-09

企業／モデル史

### o1-preview / o1-mini

生成から推論へ、単発回答から計画・検証・問題解決へと競争軸が移り始めた。

2024〜

社会／市場史

### 知的作業環境への埋め込み

ブラウザ、IDE、オフィススイート、検索、チャット、社内ナレッジ、カレンダー、メールなどにAIが埋め込まれる。

現在地

社会／市場史

### 生成AI史は知的作業環境の再編史へ

生成AIはモデル史であると同時に、検索、文書作成、開発、教育、経営判断の作業環境そのものを再編する歴史になりつつある。

## 出典・参考資料

主要な一次資料・論文・公式発表。今後、各イベントごとの出典リンクをさらに細かく追加する。

1. [Claude Shannon, A Mathematical Theory of Communication](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf)
2. [Alan Turing, Computing Machinery and Intelligence](https://academic.oup.com/mind/article/LIX/236/433/986238)
3. [Vaswani et al., Attention Is All You Need](https://arxiv.org/abs/1706.03762)
4. [Brown et al., Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)
5. [Ouyang et al., Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)
6. [OpenAI, Introducing ChatGPT](https://openai.com/index/chatgpt/)
7. [OpenAI, GPT-4](https://openai.com/index/gpt-4-research/)
8. [OpenAI, Hello GPT-4o](https://openai.com/index/hello-gpt-4o/)
9. [OpenAI, Introducing OpenAI o1-preview](https://openai.com/index/introducing-openai-o1-preview/)
10. [Anthropic, The Claude 3 model family](https://www.anthropic.com/news/claude-3-family)
11. [Meta AI, Llama 2](https://ai.meta.com/blog/llama-2/)
12. [Google, Introducing Gemini](https://blog.google/technology/ai/google-gemini-ai/)
