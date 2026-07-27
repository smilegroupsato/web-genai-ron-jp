# genai-ron.jp v2 cutover strategy

ページ作成日時：2026-07-27 09:22 JST
最終更新日時：2026-07-27 09:22 JST

## 1. Decision summary

推奨は「現行サイトを公開したままv2をproduction非公開のstaging artifactとして並走構築し、完成後に検証済みartifactを一括切替」である。これは選択肢1と4の組合せであり、現時点でmaintenance/closeは行わない。

理由：

- v2は本文変更ではなく生成基盤変更で、並走検証が可能。
- 現行HTML 102ページに対しcontent sourceは22件で、救出前のcloseは便益がない。
- 既存`main`は安定版として保持でき、production artifactのrollback点にできる。
- route・text・asset・visual parityを公開前に確認できる。

## 2. Options comparison

| Option | Availability | Risk | Operational cost | Suitable when | Decision |
|---|---|---|---|---|---|
| 現行公開のままv2並走 | 高い | content drift、二重管理 | 中 | 現行が安定し、stagingを分離できる | 採用 |
| 全体をmaintenance pageへ切替 | 低い | SEO、外部link、読者アクセスを失う | 中 | security/data loss等で現行公開が危険 | contingency |
| topだけclose、既存記事URLは維持 | 中〜高 | navigation低下、状態が分かりにくい | 中 | topから新規流入を抑えつつarchiveを残す必要がある | contingency |
| staging branchで構築し完成後一括切替 | 高い | branch drift、大型merge | 中〜高 | artifact/parity gateと定期rebaseがある | 採用。ただし長寿命branchだけに依存しない |

「staging branch」はproduction branchではなく、v2 sourceとartifactを検証する作業線として使う。小分けPRをmainへ安全に取り込み、feature flag/output directoryでproductionから隔離する方が、巨大な最終mergeより望ましい。

## 3. Recommended topology

```text
main current site ─────────────── production
       │
       ├─ small reviewed v2 source PRs (no site write)
       │
       └─ pinned commit → build → immutable v2 artifact
                                  │
                                  ├─ staging deploy + parity gates
                                  └─ approval → same artifact → production

rollback: previous production artifact + previous main commit
```

stagingのURL、認証、検索index除外方法はhosting capability確認後に決める。検索に露出するstagingには`noindex`だけでなくaccess controlを優先する。

## 4. Cutover gates

### Content and metadata

- 全102 HTML routeがmanifestに存在する。
- content sourceのない公開本文が0件。
- title、description、canonical、日時の差分が説明済み。
- normalized text、見出し、表、引用、code、内部/外部linkのparityが合格。

### URL and assets

- 全existing URLの期待statusが定義される。
- alias / redirect destinationにloopやchainがない。
- internal link / fragment / sitemap crawlが合格。
- favicon、OG、QR、PDFが存在し、download hashが一致。

### Presentation and behavior

- home、各index、article chapter、note、essay、4種類のseries、support、redirectをdesktop/mobileで確認。
- header、reading width、table/code、footer、reading preferencesを確認。
- JS error、document horizontal overflow、keyboard/accessibilityの重大問題がない。
- Issue #27のsite-wide自動mount禁止を守る。

### Operations

- stagingとproductionへ同一immutable artifactを配れる。
- deploy対象file listと削除挙動を確認する。
- previous artifactを保存し、rollbackを事前リハーサルする。
- DNS/FTPS/cache/CDNの反映時間、担当者、go/no-go判断者を明記する。

## 5. Execution runbook

### T-7 days or earlier

1. current productionをcrawlし、status/title/canonical/hash snapshotを保存。
2. `main`のcutover base commitとproduction file snapshotを固定。
3. stagingへcandidate artifactをdeploy。
4. automated gatesとhuman visual/content samplingを完了。
5. content freeze windowを告知。緊急修正はmainとv2 sourceへ両方反映する。

### T-1 day

1. fresh buildで再検証し、candidate artifact hashを固定。
2. rollback artifactの再deploy手順を確認。
3. open blockersが0であることを確認。
4. route smoke list、担当、連絡経路を確定。

### T-0

1. production deploy直前のsnapshotを取得。
2. 承認済みcandidateとhash一致を確認。
3. productionへ一括deploy。
4. homepage、各page type、legacy aliases、downloads、sitemapをsmoke test。
5. error logs、404、asset failure、layout/JS errorを監視。

### T+1 hour / T+24 hours

1. crawlerを再実行し、pre-cutover snapshotと比較。
2. 404、redirect、download、metadata、search console相当を確認。
3. 問題がなければfreeze解除。問題があればseverity基準でrollback。

## 6. Rollback

即時rollback条件：

- 主要routeまたは本文の欠落
- PDF/assetの広範な404
- URL/canonicalの意図しない変更
- navigation不能、重大な表示崩れ、site-wide JS failure
- artifactがstaging承認済みhashと異なる

手順：

1. 新規deployを停止する。
2. 保存済みの直前production artifactを再deployする。
3. homepageと主要route、downloadをsmoke testする。
4. cutover commit/workflowをrevertする（履歴を書き換えない）。
5. incidentと差分を記録し、修正candidateはstagingから再検証する。

rollback時もcontent sourceやsalvage inventoryは削除しない。

## 7. Maintenance / close modes

maintenanceは通常手順ではなくcontingencyとする。

### Full maintenance

現行公開にdata loss/security/法的リスクがある場合、またはhosting制約でatomic deployができず破損時間が避けられない場合のみ使用する。可能なら503と`Retry-After`を返し、200の恒久ページとしてindexさせない。静的hosting/FTPSでstatus制御できるか事前確認が必要。

### Top-only close

topを案内ページにし、既存記事・PDFを残す。全体closeより安全だが、内部navigationとdiscoverabilityを損なうため、短期間に限る。記事URLをmaintenanceへredirectしない。

### Exit conditions

- maintenance開始/終了時刻と責任者が明確。
- archive/article/downloadへのアクセス方針が明確。
- robots/canonical/sitemapを一時状態で恒久変更しない。
- maintenance自体のrollbackがある。

## 8. Risk register

| Risk | Control |
|---|---|
| 並走中のcontent drift | freeze window、source-of-truth明示、fresh parity build |
| 長寿命branchのdrift | 小分けPR、main追随、artifactをcommitでpin |
| FTPSの非atomic更新 | maintenance contingency、deploy順確認、前artifact即時復元 |
| 削除漏れ/過剰削除 | artifact manifest、deploy dry-run、route crawl |
| cacheで旧新が混在 | fingerprint assets、cache purge/TTL確認 |
| canonical/SEO変化 | pre/post metadata snapshot |
| 不明日時の捏造 | null許容、evidence必須、Issue #32で判断 |
| legacy alias切断 | route fixtureとredirect test |

## 9. Go / no-go

goは全必須gate合格、reviewer承認、rollback rehearsal完了、candidate hash固定のときだけ出す。期限を理由に未救出本文、不明route、failed validationを受容しない。no-go時は現行公開を継続し、maintenanceへ自動移行しない。

## 更新履歴

- 2026-07-27 09:22 JST：Issue #33に基づき、並走構築と一括切替を推奨する初回cutover strategyを作成。
