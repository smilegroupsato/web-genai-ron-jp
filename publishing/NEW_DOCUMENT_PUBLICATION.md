# 新規文書 content-first 出版レーン v0.1

ページ作成日時：2026-08-11 15:35 JST
最終更新日時：2026-08-11 15:35 JST

## 目的

既存HTMLの救出とは分離し、新規文書を最初からMarkdown正本として作成し、候補生成・確認・明示承認・公開へ送る標準経路を定める。

```text
content Markdown
  -> metadata / route / index 検証
  -> structured candidate
  -> SHA-256固定receipt
  -> desktop / mobile visual QA
  -> 明示した1ページだけをsite/へ昇格
  -> route manifest再生成・PR検証
```

## 原稿作成

`content/templates/new-document.md`を複製し、検索可能な場所へ置く。原稿には次のmetadataを必須とする。

- `id`
- `title`
- `subtitle`
- `description`
- `slug`
- `canonical_url`
- `theme_id`
- `status: publication-candidate`
- `page_created_at: YYYY-MM-DD HH:MM JST`
- `last_updated_at: YYYY-MM-DD HH:MM JST`

`id`、source path、公開route、掲載先indexのMarkdown正本と公開HTMLは`data/new-document-routes.json`で一対一に登録する。`slug`、registryの`route`、canonical URLは一致しなければならない。index正本と公開HTMLの双方に、対象routeへのリンクを一つだけ置く。

## 候補生成

```bash
python scripts/new_document_publication.py prepare \
  --id <document-id> \
  --candidate-root _new_document_candidate \
  --receipt publishing/releases/<document-id>.json
```

`prepare`は次を拒否する。

- 必須metadataの欠落・placeholder・日時形式違反
- source / route / canonicalの不一致
- `site/`または既存route manifestに存在するroute
- indexに対象routeへのリンクがない状態
- production無効theme

生成されたreceiptはsource、registry、index正本、index公開HTML、candidateのSHA-256を固定する。

## 明示昇格

候補を確認した後、receiptに記録されたcandidate SHAを明示して実行する。

```bash
python scripts/new_document_publication.py promote \
  --receipt publishing/releases/<document-id>.json \
  --expected-sha <candidate-sha256> \
  --write-site
```

`promote`はcandidateを再生成し、receipt・source・registry・indexのhashが一致する場合だけ、registryから決定した単一targetへ同一byteを書き込む。出力先を引数で変更できない。test fixtureは公開できない。

`promote`は昇格と同時にroute manifestを再生成する。続いて整合性とPR scopeを確認する。

```bash
python scripts/build_site_manifest.py --check
python scripts/new_document_publication.py validate-pr --base-ref origin/main
```

## 現在の境界

v0.1の基盤PRはfixtureを使った通し検証だけを行い、`site/`へは書かない。基盤merge後、実際の新規文書1件を別PRでこの経路へ通し、公開フローを完成扱いにする。

## 更新履歴

- 2026-08-11 15:35 JST：新規文書専用のmetadata、route registry、SHA固定promotion、索引・既存route検証、visual QA契約を新規定義。
