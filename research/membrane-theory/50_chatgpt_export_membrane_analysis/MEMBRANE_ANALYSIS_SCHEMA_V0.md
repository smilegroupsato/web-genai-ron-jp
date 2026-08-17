# MEMBRANE ANALYSIS SCHEMA V0｜ChatGPT Export候補抽出・判定schema

ページ作成日時：2026-08-17 11:08 JST
最終更新日時：2026-08-17 11:08 JST

status: active / Phase 4 validated
scope: ChatGPT Export × 膜トポロジー分析の候補抽出・精読・縦断判定
operational_definition: `OPERATIONAL_DEFINITIONS_V0.md`

## 0. 目的

このschemaは、ChatGPT Exportから膜理論のoperationを直接ラベル付けするものではない。

観測可能なevent、provenance、反復範囲、rule revision、alternative route、frictionを先に記録し、その後にoperation固有gateを適用する。conversation、topic、頻度、artifact生成を、それだけでregion、membrane、sedimentation、fold等へ昇格させない。

raw conversation本文はGitHubへ保存しない。evidenceはmessage ID、UTC timestamp、短いsafe summaryへの参照として保持する。

## 1. Analysis hierarchy

```text
message event
  -> state segment
  -> transition episode
  -> proto-region / membrane candidate
  -> cross-episode trace
  -> longitudinal rule lineage
  -> sedimentation / path dependence
  -> fold / topology change
```

conversationは保存容器でありregionではない。階層を飛び越え、message keywordからmembrane、fold、inversion等を確定しない。

## 2. Observation layerとjudgment layer

### Observation layer

- ID、time、role、active path。
- U / A / T / I provenance。
- carrier、source/target、before/after。
- 明示された選択、拒否、訂正、実行、fallback。
- linked evidenceと観測限界。

### Judgment layer

- state / transitionの解釈。
- operation candidate。
- gate結果。
- counterevidence / confound。
- confidenceとreview status。

LLMがoperation名を先に決め、後から根拠を埋めてはならない。

## 3. 共通値規則

- timestampはUTC ISO 8601。確定できない値は`null`。
- tri-stateは`true | false | unknown`。欠損をfalseにしない。
- 観測不能は`unavailable_from_export`、観測範囲内で証拠なしは`not_observed`、negative testで棄却した候補は`rejected`として分ける。
- 複数値は配列で保持する。
- evidence refにはraw本文でなく短いsafe summaryを置く。

## 4. Record envelopeとevidence reference

```yaml
schema_version: membrane-analysis-v0
record_type:
record_id:
source_export_label:
conversation_ids: []
time_start:
time_end:
analysis_status: observed | candidate | reviewed | rejected | unknown
evidence_refs: []
review:
  method: deterministic | heuristic | llm | human
  reviewed_at:
  reviewer_note:
```

```yaml
evidence_ref_id:
conversation_id:
message_id:
timestamp:
origin: U | A | T | I
t_subtype: T-direct-tool-event | T-assistant-report-of-tool-event | T-user-confirmed-external-event | T-unknown | not_applicable
safe_summary:
source_locator:
carrier_id:
observation_limit:
```

assistantによる「実行した」「反映した」という報告を`T-direct-tool-event`へ昇格させない。

## 5. Message event

```yaml
message_id:
conversation_id:
timestamp:
role:
active_path_status: active | alternate | unknown
session_id:
explicit_transition_markers: []
explicit_action_markers: []
external_refs: []
tool_event_present:
t_subtype:
candidate_features:
  correction_or_rejection:
  enactment_or_return:
  rule_language:
  carrier_language:
```

machine layerはmarkerと位置を候補化するだけで、本文のoperation判定を確定しない。

## 6. State segment / transition episode

```yaml
segment_id:
conversation_id:
start_message_id:
end_message_id:
time_start:
time_end:
boundary_basis: []
state_vector:
  responsibility_pressure:
  reality_salience:
  intimacy:
  affect_intensity:
  bodily_salience:
  actionability:
  temporal_immediacy:
  ai_delegation:
  abstraction_level:
  freedom_constraint:
state_summary:
confidence:
```

topicだけをsegment boundaryにしない。

```yaml
episode_id:
source_segment_id:
target_segment_id:
trigger:
input_object:
selection:
  selected: []
  blocked: []
  delayed: []
transformation:
  occurred: true | false | unknown
  subtypes: []
  transformed_to:
  function_before:
  function_after:
transport:
  source_state:
  target_state:
  carrier_id:
  target_reuse_observed:
w4_user_actions: []
world_return:
  levels: []
  evidence_refs: []
outer_cycle:
  w1:
  w2:
  w3:
  w4:
  w5:
  confidence:
```

### Transformation subtype

一つのepisodeへ複数指定できる。

- `representational`
- `operational`
- `normative`
- `memorial`
- `narrative`
- `affective`

AI出力だけの変換と、U/Iが採用・再利用したHuman–AI system上の変換を分ける。

## 7. Proto-region / membrane candidate

```yaml
proto_region_id:
member_segment_ids: []
state_vector_signature:
topic_independence_evidence:
transition_pattern_refs: []
confidence:

membrane_candidate_id:
proto_region_ids: []
operation_profile:
  selection:
  rejection:
  delay:
  transformation:
  exchange:
  signaling:
repetition_scopes: []
future_permeability_effect:
m_gates:
  M1_reproducible_difference:
  M2_concrete_operation:
  M3_repetition:
  M4_future_rule_change:
  M5_artifact_resistance:
alternative_explanations: []
confidence:
```

## 8. Repetition scopeとcross-episode trace

反復範囲は次を複数指定できる。

- `same_episode`
- `same_conversation`
- `cross_conversation`
- `cross_month`

carrier reuseとrule reuseを別々に記録する。

```yaml
trace_id:
source_episode_id:
later_episode_ids: []
what_changed:
repetition_scopes: []
carrier_reuse_scopes: []
rule_reuse_scopes: []
user_spontaneous_reuse: true | false | unknown
external_carrier_confounds: []
evidence_refs: []
confidence:
```

## 9. Rule lineage

ruleは現在値で上書きせず、versionと親子関係を持つ。

```yaml
lineage_id:
rule_versions:
  - rule_id:
    rule_summary:
    proposed_at:
    accepted_at:
    enacted_at:
    revised_at:
    superseded_at:
    stabilized_at:
    revision_parent:
    status: proposed | accepted | enacted | revised | superseded | stabilized | rejected | unknown
    applies_to_route_id:
    evidence_refs: []
revision_reason:
lineage_confidence:
```

日時は観測されたeventだけを埋める。旧routeと改訂routeを同一ruleの単純継続として潰さない。

## 10. Sedimentation assessment

```yaml
sedimentation_id:
lineage_id:
prior_rule_id:
later_rule_id:
observed_change:
later_similar_input_refs: []
reuse_scopes: []
future_selection_effect:
counterexamples: []
confounds:
  same_conversation_memory:
  project_instructions:
  repository_context:
  handoff:
  notion:
  github:
  gmail:
  tool_result:
  external_workflow:
system_level_stabilization: supported | not_supported | unknown
human_internalization_claim: supported | not_supported | unknown
gate_results: []
confidence:
```

minimum evidenceはprior rule、later rule、observed change、later similar input、reuse scope、future selection effect、counterexample、confoundである。same-conversationだけ、またはstabilized rule未確認ならC3にしない。

external carrier上で規則が定着した場合は`system_level_stabilization`を評価できる。しかし、それをそのまま佐藤内部の記憶沈殿と呼ばず、`human_internalization_claim`を独立判定する。

## 11. Alternative route ledger / path dependence

```yaml
route_ledger_id:
target_rule_id:
chosen_route:
  route_id:
  version:
plausible_alternatives:
  - route_id:
    description:
    alternative_used_before:
    alternative_rejected:
    alternative_bypassed:
    used_later:
    evidence_of_reduced_probability:
    evidence_refs: []
route_history_effect:
recency_or_instruction_confound:
path_dependence_confidence:
```

同じ経路が続いただけではpath dependenceにしない。alternativeが後に実際に使われた場合は旧routeを再評価し、改訂routeを別versionとして判定する。

## 12. Fold friction vector

gluingとfoldを別recordにする。

```yaml
gluing_id:
connected_proto_regions: []
mediator:
first_connection_at:
later_reuse_refs: []
gluing_confidence:

fold_id:
gluing_id:
before_after:
  explanation_burden: {before: null, after: null, direction: unknown, measurement: unknown}
  search_burden: {before: null, after: null, direction: unknown, measurement: unknown}
  intermediate_steps: {before: null, after: null, direction: unknown, measurement: unknown}
  delay: {before: null, after: null, direction: unknown, measurement: unknown}
  startup_prompt_length: {before: null, after: null, direction: unknown, measurement: unknown}
  turns_to_reactivation: {before: null, after: null, direction: unknown, measurement: unknown}
later_reuse_confirmed:
reduced_dimensions: []
counterevidence: []
confidence:
```

`direction`は`decreased | same | increased | mixed | unknown`。数値取得不能をfalseに変えない。文字数、turn数、経過時間はproxyであり、意味的な負担低下そのものではない。

## 13. External carrier confound

最低限、次を区別する。

- Repository Context
- Memory
- Project instructions
- Handoff
- Notion
- GitHub
- Gmail
- Tool result
- external workflow
- other / unknown

carrierはsystem-level continuityを支えうるが、人間内部への定着の直接証拠ではない。carrierが観測できない場合も、存在しないと推定しない。

## 14. High-risk operation discriminators

### Inversion negative test

```yaml
relation_before:
relation_after:
actual_role_reversal:
mere_growth_or_bidirectionality:
user_origin_evidence: []
downstream_effect:
confidence:
```

system growth、委譲増加、双方向修正、AIの誤判定だけならrejectする。

### Smoothing discriminator

```yaml
baseline_gradient:
synchronized_dimensions: []
duration:
restoration_afterward:
assistant_formatting_confound:
confidence:
```

baselineがなければC1上限または`insufficient`。単なる集中、気分改善、topic混在、assistantの統一書式では成立させない。

### Leakage / nesting

leakageはexplicit transport/reference/handoffを除外し、source patternの時間的先行とtargetへの無標識流入を要求する。nestingはouter/innerで異なるoperation ruleと複数episodeでの持続を要求し、UI、folder、DB hierarchyだけならrejectする。

## 15. Confidence C0–C3

| level | meaning |
|---|---|
| C0 | non-evidence、rejected、またはartifact/alternativeで説明される |
| C1 | 単一episodeまたは一部gateのみを満たすweak candidate |
| C2 | 複数evidenceでsupportedだがlongitudinal scope、future effect、confound排除のいずれか不足 |
| C3 | operation固有の全必須gateと後続効果を満たすstrong evidence |
| insufficient | 必要fieldが観測不能で成立/不成立を決められない |

confidenceは真偽確率ではなく、現時点のログが主張をどこまで支えるかの強度である。各operationへ独立に付ける。

## 16. Operation-specific gates

### Common gates

- G0: U/A/T/IとT subtypeを区別。
- G1: before/afterまたはsource/targetを識別。
- G2: topic名やconversation境界だけではない。
- G3: strongest counterexampleを記録。
- G4: Memory/instruction/carrier/workflow confoundを記録。
- G5: repetition scopeを明示。

### Membrane

M1 reproducible difference、M2 concrete operation、M3 repetitionでC2候補。C3はさらにM4 future rule change、M5 artifact resistance、原則cross-conversation/month evidenceを要求する。

### Sedimentation

S1 prior/later rule、S2 enacted change、S3 later similar input、S4 future selection effect、S5 reuse scope、S6 counterexample/confound、S7 stabilized version。same-conversationだけ、またはS7なしはC2上限。

### Path dependence

P1 route/version、P2 plausible alternative、P3 alternativeの過去利用/reject/bypass、P4 chosen routeの相対確率上昇、P5 recency/instruction以外の履歴効果を要求する。

### Fold

F1 gluing、F2 later reuse、F3 friction 1軸以上の低下、F4 U/T evidenceまたは再現可能proxy、F5 carrierコピー/assistant連想ではないことを要求する。F1+F2だけならC2上限。

### Inversion

relation before/after、actual reversal、U-origin、downstream effect、growth/bidirectionality除外をすべて要求する。

### Smoothing

baseline gradient、同期次元、duration、restoration/persistence、topic/formatting confound除外を要求する。

outer cycle C3やartifact生成をmembrane/sedimentation C3へ伝播させない。

## 17. Extraction / review classification

| class | 主な対象 |
|---|---|
| deterministic | IDs、timestamp、role、active path、month、time gap、URL/path/tool structure、文字数、turn数 |
| heuristic | correction/reject/rule marker、carrier mention、tool実行報告候補、explicit transition marker |
| LLM-review-required | segment/state、trigger、transformation subtype、rule identity/version、future effect、alternative、operation gates |
| human-review-preferred | inversion、leakage、smoothing、nesting、human internalization、高影響の曖昧判定 |
| unavailable-from-export | 未報告world action、offlineの身体/情緒状態、人間内部の記憶定着の一部 |

candidate scoreをconfidenceへ直接変換しない。Phase 5ではpositive候補と同程度のnegative/alternative候補を残す。

## 18. Phase 2 / Phase 3 backtest

Phase 4で、raw本文をGitHubへ移さず、既存safe判定へ本schemaをbacktestした。

- Phase 2 negative control: 主要operationのfalse positiveは0。
- Phase 3 Path A: sedimentation C2、path dependence C1、fold/inversion C0を再現。
- Phase 3 Path B: 改訂routeのsedimentation/path dependence/fold C3、初期route rejected、inversion C0を再現。
- Phase 3 Path C: sedimentation C3、fold C1、inversion C0を再現。
- confidence変更: 0件。

Path B/Cのsedimentationは`system_level_stabilization`と`human_internalization_claim`を分離することで、confidenceを変えず主張範囲を限定した。

## 19. Limitations

- tool event metadataの一貫性は小規模raw shape auditが必要。
- rule identity/revisionは文字列一致だけでは確定できない。
- 文字数、turn数、経過時間はfrictionのproxyにすぎない。
- Memory、Project instructions、Repository Contextの可視性はconversationごとに異なりうる。
- human internalizationはexportだけでは確定できない場合が多い。
- leakage、smoothing、nestingはpositive caseによる実地校正が未完了。
- schemaはChatGPT接触面の観測器であり、全人格・会話外状態を記述しない。

## 20. Phase 5 gate

機械候補抽出へ進行できる。全件精読や全件operation確定へは直行しない。

```text
deterministic inventory
-> heuristic candidate narrowing
-> positive / negative / alternative pairing
-> narrowed window close reading
-> longitudinal gate judgment
```

開始前に少数rawでT subtype、active path linkage、Memory/Project instructionsの可視性を確認する。判別不能値は`unknown`として保持する。

## 更新履歴

- 2026-08-17 11:08 JST：Phase 2/3 backtest済みのschema、field dictionary、operation固有gate、machine/review境界を正本化。negative control false positive 0と既存confidence不変を記録。
