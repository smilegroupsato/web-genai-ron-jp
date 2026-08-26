# 公開版「膜」制作・出版専門チャット｜開始Handoff

- ページ作成日時：2026-08-26 12:54 JST
- 最終更新日時：2026-08-26 12:58 JST
- status：ready for specialist handoff
- intended repository path：`research/membrane-theory/60_web_publication/MEMBRANE_WEB_PUBLICATION_HANDOFF.md`

## 0. このHandoffの目的

この専門チャットは、`smilegroupsato/web-genai-ron-jp` に蓄積された膜研究を、`genai-ron.jp/membrane/` の公開版「膜 | MEMBRANE」として編集・実装・公開する担当である。

構想だけで終了せず、次を一続きの責務として扱う。

1. source archiveの確認
2. public editionの原稿作成
3. `content/membrane/` への公開Markdown正本化
4. route・index・metadataの登録
5. candidate生成と検証
6. desktop / mobile visual QA
7. 佐藤による公開差分の確認
8. 明示承認後の`site/`昇格
9. branch / commit / push / Draft PR
10. CI成功・競合・review確認後のmerge
11. `genai-ron.jp`での公開確認

既存HTML救出レーンは担当しない。公開版「膜」の制作と、新規文書publication laneへの接続だけを担当する。

## 1. 正本と入口

Repository：

- `https://github.com/smilegroupsato/web-genai-ron-jp`

公開サイト：

- `https://genai-ron.jp/`

公開予定namespace：

- `https://genai-ron.jp/membrane/`

作業開始時には必ず最新`main`を取得し、会話内のcommit番号より現行repoを優先する。

Handoff作成時点で確認した最新`main`：

- `9a8f1e448d8d4bfab5b7ebaab0b34e6cbff3983e`
- commit message：`Treat membrane computing as reading note`

これは再開地点の証拠であり、作業基点を固定する指定ではない。開始時に最新`origin/main`を再確認すること。

## 2. 最初に読む文書

巨大な履歴を無差別に読まず、まず次だけを順番に確認する。

### Repository Context

1. `README.md`
2. `CODEX.md`
3. `ARCHITECTURE.md`
4. `publishing/README.md`
5. `publishing/NEW_DOCUMENT_PUBLICATION.md`
6. `data/new-document-routes.json`
7. `content/templates/new-document.md`
8. `scripts/new_document_publication.py`

repo直下に`AGENTS.md`はない。現行の実装規範は`CODEX.md`を正本とする。

### 膜研究と公開計画

1. `research/membrane-theory/README.md`
2. `research/membrane-theory/CHARTER.md`
3. `research/membrane-theory/INDEX.md`
4. `research/membrane-theory/BIBLIOGRAPHY.md`
5. `research/membrane-theory/60_web_publication/README.md`
6. `research/membrane-theory/60_web_publication/2026.08.26_01_public_v0.1_inventory.md`
7. `research/membrane-theory/60_web_publication/2026.08.26_02_public_v0.1_implementation_plan.md`

個別sourceは、制作中のページに必要なものだけ追加で読む。

## 3. 現在地

### 完了済み

- 新規文書向けcontent-first publication lane v0.1
- 必須metadata検証
- source / route / canonical / index整合検証
- candidate HTML生成
- source・registry・index・candidateのSHA-256固定receipt
- candidate改ざん拒否
- 既存route上書き拒否
- test fixtureの公開拒否
- `--write-site`なしの公開拒否
- 単一targetへのcontrolled promotion
- desktop 1440px / mobile 390px visual QA
- route manifest再生成・PR scope検証

基盤PR：

- PR #67 `Add controlled new-document publication lane`
- merge commit：`c25afcbcfe77d25217547ee86526c2556bf92506`

### 未完了

- production文書を使った最初の本番通し公開
- `/membrane/` namespaceが現行validatorで扱えるかの技術確認
- `content/membrane/`階層の正式採用
- `/membrane/`自身をindexとしてpublication laneで公開できるかの確認
- genai-ron.jp本体から膜トップへの導線決定
- 既存theme採用か膜専用theme追加かの判断
- sitemap / manifest / asset copyの実ページ確認

したがって、出版基盤を全面的に作り直してはいけない。まず現行laneで`/membrane/`を扱えるか検証し、問題が確認された部分だけを最小拡張する。

## 4. 公開版「膜」の位置づけ

公開版は、`research/membrane-theory/`のミラーではない。

**生命・自己・世界・AIのあいだにある膜を考える公開研究ノート**として、genai-ron.jpの中に独立した入口・棚・内部導線を持たせる。

```text
research/membrane-theory/
  source archive / research canon
          ↓ 選定・再編集
research/membrane-theory/60_web_publication/
  公開候補台帳 / 編集方針 / public edition草稿
          ↓ 原稿確定
content/membrane/
  公開Markdown正本
          ↓ publication lane
site/membrane/
  公開HTML
```

`research/membrane-theory/`の原本を、公開のために削除・移動・書き換えない。

## 5. routeと情報設計

第一候補は次のとおり。

```text
/membrane/
/membrane/about/
/membrane/research-map/
/membrane/thoughts/exchange-device/
/membrane/thoughts/origin-of-meaning/
/membrane/thoughts/topology-and-agency/
/membrane/thoughts/sedimentation-of-history/
/membrane/reading/<slug>/
/membrane/bibliography/
```

公開タイトル：

- `膜 | MEMBRANE`

仮subtitle：

- `生命・自己・世界・AIのあいだにあるもの`

独立性は別ドメインではなく、`/membrane/` namespace、独自トップ、独自内部ナビゲーション、必要に応じたthemeで実現する。genai-ron.jp全体の出版・deploy基盤は共用する。

## 6. 公開境界

### 公開候補

- 公開トップ「膜とは何か」
- この研究の立場
- 膜をめぐる先行研究地図
- 思索4本
- public editionへ整えた読書ノート
- 内部進捗・TODOを除いたBibliography
- claim boundaryと本文が一致する最小限の図版

### 原則非公開

- `40_observations/`の個人的観測記録
- ASC / CDS風self-test
- `90_chat_logs/`の全文対話録
- 個人的・臨床的・生活上の生データ
- 小説の未公開原稿、人物設定、story bible、scene board
- 内部分析schema、validation、作業ログ
- SGOS等の内部システム固有比較

非公開sourceの一部を使う場合は、公開可能な命題だけを抽出・再構成し、生データや個人文脈を露出させない。

## 7. 内容上の厳守事項

「膜」は一部を除いて比喩的・操作的概念である。情緒を安易に類型名で固定せず、記述を通じて立ち現れさせる。一方、何を膜と呼ぶかは厳密にする。

暫定定義：

> 膜とは、二つの領域を分けながら、完全には遮断せず、何かを選別・遅延・変質・調整して通す境界装置である。

最低条件：

- 二つの領域がある
- 完全遮断ではない
- 透過が調整される
- 通過時に変質が起きる
- 履歴・圧力・習慣によって膜自体が変化する

公開ページでは次を混同しない。

1. 既存研究が述べていること
2. 佐藤の読解
3. 膜という概念への接続
4. 未検証の作業仮説
5. 創作的転用

生体膜、現象学、精神病理、文学、AIを同一の実体として扱わない。「膜理論」を完成した統一理論として提示しない。

P system／膜コンピューティングは独立カテゴリにしない。`A Guide to Membrane Computing`の一読書ノートとしてReadingへ置き、SGOS比較は公開版へ含めない。

## 8. 最初の実作業

### Phase A：技術確認

まず公開HTMLを書かず、次を確認する。

1. `content/membrane/index.md`から`/membrane/`候補を生成できるか
2. nested source pathとnested routeをregistryが扱えるか
3. `/membrane/`自身をindexとして`index_source` / `index_html`契約へ載せられるか
4. production-enabled themeでcanonicalと日時が正しく出るか
5. manifest / sitemapが新routeを扱えるか
6. visual QAがdesktop / mobileで通るか

現行基盤で通るなら基盤コードを変更しない。通らない場合は、失敗箇所、既存契約、最小修正案、影響範囲を佐藤へ示してから変更する。

### Phase B：最初の3ページ

制作順：

1. `/membrane/`
2. `/membrane/about/`
3. `/membrane/research-map/`

大量の読書ノートを先に公開しない。この3ページでサイトの意味、語彙、epistemic boundary、内部ナビゲーションを固定する。

### Phase C：思索とReading

次に思索4本、生体膜3本、オートポイエーシス／身体性、現象学／精神病理、文学・膜コンピューティングの順で広げる。

## 9. 原稿の作り方

public edition草稿は、まず`research/membrane-theory/60_web_publication/`内に置く。佐藤が内容を確認した後、`content/membrane/`へ公開Markdown正本として昇格する。

読書ノートの基本構造：

```text
書誌
この文献は何をしたか
重要な概念
膜を考える上で何が重要か
ここから先は佐藤の読解
関連ページ
```

原文を一括コピーしない。引用は必要最小限にし、出典を明確にする。内部の読書進捗、TODO、作業ログは公開本文へ出さない。

## 10. 必須metadata

各`content/membrane/`文書は`content/templates/new-document.md`を基準に、少なくとも次を持つ。

```yaml
id: <stable-id>
title: <title>
subtitle: <subtitle>
slug: /membrane/<route>/
canonical_url: https://genai-ron.jp/membrane/<route>/
description: <description>
theme_id: <production-enabled-theme>
status: publication-candidate
page_created_at: YYYY-MM-DD HH:MM JST
last_updated_at: YYYY-MM-DD HH:MM JST
```

外部向け文書を新規作成した日時と、source内容が発生した時期を混同しない。既存public editionを更新するときは最終更新日時と末尾の更新履歴を更新する。

## 11. publication laneの標準操作

`data/new-document-routes.json`に、id、source、route、index正本、index公開HTMLを一対一で登録する。

candidate生成：

```bash
python scripts/new_document_publication.py prepare \
  --id <document-id> \
  --candidate-root _new_document_candidate \
  --receipt publishing/releases/<document-id>.json
```

receipt検証：

```bash
python scripts/new_document_publication.py verify-receipt \
  --receipt publishing/releases/<document-id>.json
```

公開前にはcandidate SHA、生成差分、desktop/mobileの表示、公開route、変更対象ファイルを佐藤へ提示する。

明示承認後の昇格：

```bash
python scripts/new_document_publication.py promote \
  --receipt publishing/releases/<document-id>.json \
  --expected-sha <candidate-sha256> \
  --write-site
```

続けて検証する。

```bash
python scripts/build_site_manifest.py --check
python scripts/new_document_publication.py validate-pr --base-ref origin/main
git diff --check
```

実際のrepoに追加検証コマンドがある場合は、現行workflowを正本として併用する。

## 12. Git・公開操作

- 作業開始前に最新`origin/main`を取得する
- clean working treeを確認する
- 専用feature branchを使う
- 無関係な差分を混ぜない
- `git add .`、`git add -A`を使わない
- 対象pathだけを明示stageする
- force pushを使わない
- 公開単位は原則1ページまたは意味上まとまった最小セットとする
- Draft PRでCIとvisual QAを確認する
- review指摘、競合、失敗workflowを未確認のままmergeしない

専門チャットは原稿作成、ローカル実装、candidate生成、検証まで自律的に進めてよい。

次は佐藤の明示承認を得てから行う。

- `site/`への初回production昇格
- branchのremote push
- PR作成
- Ready化
- merge

承認後は、承認された範囲についてCI成功・競合なし・review指摘なしを確認し、最後まで進める。

## 13. 停止条件

次の場合は推測で続けず、短く報告して佐藤へ確認する。

- 公開／非公開境界が曖昧
- 個人情報、臨床情報、家族・生活情報が公開原稿へ混入する可能性がある
- 既存研究の主張と佐藤の仮説を分離できない
- `/membrane/`対応にpublication基盤の大幅変更が必要
- 既存route、site header、root `/`、CSS / JavaScriptへ広範な変更が必要
- source archiveの原本変更が必要
- 複数ページを同時公開しないと既存gateを通せない
- deploy credential、公開サーバ、GitHub Actionsの異常

## 14. やらないこと

- `research/membrane-theory/`全体の自動公開
- chat log viewer
- self-test公開
- 小説本文の同時公開
- 全文献の一括公開
- 大規模検索UI
- DB化
- publication基盤の全面作り直し
- root `/`や既存サイト全体の再設計
- CSS / JavaScriptの全面置換
- P system／膜コンピューティングの独立カテゴリ化

## 15. 完成条件

### 最初のproduction通し試験

- `/membrane/`のpublic editionが確定
- `content/membrane/`にMarkdown正本がある
- registry / index / canonical / metadataが整合
- candidateとreceiptが生成される
- desktop / mobile visual QAが成功
- 佐藤が差分とcandidateを確認
- 明示承認後に`site/membrane/index.html`へ同一byteで昇格
- manifest / sitemap / PR scopeが整合
- CI成功、競合なし、review指摘なし
- mainへmerge
- `https://genai-ron.jp/membrane/`で公開確認

### 公開版v0.1

- 初見の読者が「膜」の暫定定義を理解できる
- 生物学からAIまでを横断する理由が説明される
- 既存研究と佐藤の仮説が区別される
- 読書ノートから中心論考へ戻れる
- 個人的観測や生ログが露出していない
- desktop / mobileで読める
- publication lane、manifest、sitemapが整合する

## 16. 作業報告形式

各区切りで次だけを簡潔に報告する。

```text
現在地：
完了：
変更ファイル：
検証結果：
公開HTML変更：あり / なし
未確認点：
佐藤に必要な判断：
次の一手：
```

完了報告には、commit、PR、CI、公開URL、force push不使用、Repository Context影響の有無を含める。

## 17. 専門チャットへの開始指示

このHandoffを受け取ったら、まず次を行う。

1. 最新`origin/main`とclean working treeを確認する
2. 第2節の必須文書を読む
3. Handoff作成後の変更を確認し、計画との差分を整理する
4. `/membrane/` namespaceと`content/membrane/`の技術確認を行う
5. 公開HTMLを書かず、結果と必要な最小変更だけを佐藤へ報告する
6. 技術的に通るなら「膜とは何か」のpublic edition草稿作成へ進む

設計相談だけで停止せず、承認を必要としない範囲は実行する。公開判断、著者判断、個人的情報の境界は佐藤へ戻す。

## 更新履歴

- 2026-08-26 12:58 JST：専門チャットの固定入口として識別しやすいファイル名へ変更。
- 2026-08-26 12:54 JST：公開版「膜」の制作・技術確認・controlled publication・公開確認までを専門チャットへ引き継ぐ開始Handoffを作成。
