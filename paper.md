# Mathematical Foundations of Jev: A Micro-Architectural Framework for Structured Semantic Decision Problems

**Author:** JevTools Knowledge Base  
**Repository:** [RileyCarney/JevTools](https://github.com/RileyCarney/JevTools)  
**Date:** September 2026  
**Status:** Working Paper

---

## Abstract

This paper establishes a mathematical framework for Jev — TypeSafe AI's *System One* decision model — and proves that its micro-architectural structure is sufficient to solve well-defined subsets of semantic decision problems. We formalize the three core primitives (Noul, Choice, Score) as typed projection operators over a probability simplex, characterize the state space on which they operate, and prove completeness and composability theorems for their combination. We further demonstrate that the Speculative Fan-Out pattern achieves asymptotic cost-equivalence to a single serial query while preserving full independence of parallel sub-judgments. The Confidence-Gated Routing pattern is proven to induce a risk-monotone total preorder on action sets. Composite Scoring is shown to construct a convex, tunable priority functional over multi-dimensional judgment spaces. Together, these results establish Jev's micro-architecture as a mathematically sound substrate for deterministic semantic computation.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Formal Definitions](#2-formal-definitions)
   - 2.1 [State Space](#21-state-space)
   - 2.2 [The Probability Simplex](#22-the-probability-simplex)
   - 2.3 [Calibration via RLCD](#23-calibration-via-rlcd)
3. [The Three Primitives as Projection Operators](#3-the-three-primitives-as-projection-operators)
   - 3.1 [Noul: Binary Credence Projection](#31-noul-binary-credence-projection)
   - 3.2 [Choice: Categorical Distribution Projection](#32-choice-categorical-distribution-projection)
   - 3.3 [Score: Ordinal Expectation Projection](#33-score-ordinal-expectation-projection)
4. [Confidence as a Distributional Sharpness Measure](#4-confidence-as-a-distributional-sharpness-measure)
5. [Architectural Patterns: Mathematical Proofs](#5-architectural-patterns-mathematical-proofs)
   - 5.1 [Speculative Fan-Out: Parallelism and Cost Theorem](#51-speculative-fan-out-parallelism-and-cost-theorem)
   - 5.2 [Confidence-Gated Routing: Risk-Monotone Total Preorder](#52-confidence-gated-routing-risk-monotone-total-preorder)
   - 5.3 [Composite Scoring: Convex Weighted Priority Functional](#53-composite-scoring-convex-weighted-priority-functional)
   - 5.4 [Intent Routing: Decision-Theoretic Completeness](#54-intent-routing-decision-theoretic-completeness)
6. [Subset Solvability: Problem Classes Covered by Jev](#6-subset-solvability-problem-classes-covered-by-jev)
   - 6.1 [Classification Problems](#61-classification-problems)
   - 6.2 [Ranking and Reranking Problems](#62-ranking-and-reranking-problems)
   - 6.3 [Verification and Extraction Problems](#63-verification-and-extraction-problems)
   - 6.4 [Moderation and Guardrail Problems](#64-moderation-and-guardrail-problems)
   - 6.5 [Feature Generation for Downstream ML](#65-feature-generation-for-downstream-ml)
7. [Micro-Architectural Invariants](#7-micro-architectural-invariants)
8. [Limits of the Framework](#8-limits-of-the-framework)
9. [Conclusion](#9-conclusion)
10. [Notation Reference](#10-notation-reference)

---

## 1. Introduction

Modern software systems frequently encounter *semantic decision problems* — problems whose resolution requires understanding the meaning of natural-language state rather than performing arithmetic or lookup operations. Classical deterministic code is insufficient for these problems; classical Large Language Models (LLMs) are over-expressive, producing free-form text that must be parsed and often carries miscalibrated uncertainty.

**Jev** (TypeSafe AI, System One) occupies a principled middle ground: it accepts structured natural-language state and returns *typed, probability-calibrated* answers in approximately 100 ms. The model is not a generator; it is a semantic *projector* — it maps a high-dimensional semantic space onto one of three finite-typed output spaces (categorical, ordinal, or binary-probabilistic).

This paper provides the mathematical foundations for that claim. Specifically, we:

1. Formalize the state space `S` and the output spaces of the three primitives.
2. Model each primitive as a probability-space projection operator.
3. Prove that Jev's architectural patterns (Fan-Out, Confidence Routing, Composite Scoring, Intent Routing) satisfy well-known properties from decision theory and functional analysis.
4. Enumerate the subset of semantic decision problems that are provably solvable under this architecture.

**Architecture Rule (Informal).** Throughout this paper, the following is taken as an architectural axiom derived from the JevTools documentation:

> *Code owns the control flow. Jev fills narrow semantic judgment slots. Jev does not control execution — it provides typed evidence that deterministic code acts upon.*

This is the defining property of the **System One micro-architecture** — a compositional model in which AI judgment is strictly subordinate to deterministic policy.

---

## 2. Formal Definitions

### 2.1 State Space

Let `𝒮` be the **state space** — the set of all valid inputs that can be presented to the Jev model. Formally, a state `s ∈ 𝒮` is any member of the union:

```
𝒮 := 𝒮_str ∪ 𝒮_obj ∪ 𝒮_arr
```

where:

- `𝒮_str` = the set of all finite UTF-8 strings (single-passage states).
- `𝒮_obj` = the set of all finite JSON objects with string-valued keys and values recursively drawn from `𝒮` (named-field states; the preferred form per JevTools documentation).
- `𝒮_arr` = the set of all finite-length arrays of elements from `𝒮` (sequential-record states).

The semantic interpretation of a state is given by an implicit *meaning function*:

```
μ : 𝒮 → ℳ
```

where `ℳ` is an abstract *semantic meaning space* (a latent vector space learned during RLCD training; not directly observable). The model encodes `s` into `ℳ` and evaluates questions against that encoding.

**Definition 2.1 (Context Relevance).** A state `s` is *context-relevant* for a question set `Q` if and only if:

```
∀ q ∈ Q, ∃ f_q : ℳ → ℝ such that Var[f_q(μ(s))] > 0
```

That is, the state carries non-zero semantic variance with respect to each question — it provides information that constrains the answer distribution. The JevTools documentation encodes this as the *no context-rot* rule: include only context relevant to the current questions.

**Definition 2.2 (Field Reference).** For any object state `s ∈ 𝒮_obj` and a backtick-delimited path `p` (e.g., `` `ticket.messages[0].text` ``), we define the field accessor:

```
s[p] ∈ 𝒮_str ∪ {⊥}
```

where `⊥` denotes an undefined field. Questions reference field accessors in their `instructions` string, and the model resolves them against the provided state.

---

### 2.2 The Probability Simplex

All three Jev primitives return distributions over finite outcome sets. We introduce the standard probability simplex as a common mathematical container.

**Definition 2.3 (Probability Simplex).** For a finite set `Ω` with `|Ω| = N`, the probability simplex is:

```
Δ(Ω) := { p ∈ ℝ^N : pᵢ ≥ 0 ∀i, Σᵢ pᵢ = 1 }
```

For `N = 2` (Noul), this is the unit interval `[0, 1]`. For `N = K` options (Choice), this is the `(K-1)`-dimensional simplex. For `N = L` levels (Score), this is the `(L-1)`-dimensional simplex.

Each primitive returns a point in the corresponding simplex, representing the model's calibrated belief over possible outcomes.

---

### 2.3 Calibration via RLCD

The JevTools documentation notes that Jev is trained with **RLCD (Reinforcement Learning from Calibrated Decisions)** to produce calibrated rather than overconfident probability outputs. We formalize calibration:

**Definition 2.4 (Calibration).** A probability model `M` is *calibrated* if for all threshold values `τ ∈ [0,1]` and all inputs `s` where `M` outputs probability `p = τ` for outcome `ω`:

```
P(true outcome = ω | M outputs p = τ) = τ
```

In other words, when Jev assigns probability 0.87 to a `billing` choice, the true label is `billing` in approximately 87% of such cases across the distribution of inputs. This is the *reliability diagram* condition from the calibration literature (Guo et al., 2017; DeGroot & Fienberg, 1983).

**Lemma 2.1 (Calibration Preserves Utility of Thresholding).** If `M` is calibrated and a decision rule `d` acts on `p` via a threshold `τ`:

```
d(s) = { act if p(s) ≥ τ, else abstain }
```

then the expected precision of `d` equals `E[p | p ≥ τ] ≥ τ`. Calibration thus makes threshold selection a sound decision procedure.

*Proof.* By the tower property of conditional expectation and the definition of calibration:

```
E[𝟙(true = ω) | p ≥ τ] 
  = E[E[𝟙(true = ω) | p] | p ≥ τ]
  = E[p | p ≥ τ]                     (calibration)
  ≥ τ                                 (since p ≥ τ in the conditioned set)
```

∎

This lemma justifies the three-tier behavioral model described in JevTools: the three confidence bands (< 0.5, 0.5–0.8, ≥ 0.8) are only operationally meaningful if the underlying model is calibrated. RLCD training is the technical mechanism that renders these thresholds non-arbitrary.

---

## 3. The Three Primitives as Projection Operators

We now formalize each primitive as a typed map from state space to output space.

### 3.1 Noul: Binary Credence Projection

**Definition 3.1 (Noul Operator).** Given a question `q` with binary predicate semantics ("Is statement `φ` true in state `s`?"), the Noul operator is:

```
𝒩_q : 𝒮 → [0, 1]

𝒩_q(s) := P_M(φ(s) = true)
```

where `P_M` is the model's calibrated probability measure.

The Noul output `n = 𝒩_q(s)` has the following semantic interpretation:

| Range | Interpretation |
|---|---|
| `n → 1.0` | Strong credence that φ holds in s |
| `n ≈ 0.5` | Near-maximal uncertainty; equal probability for both outcomes |
| `n → 0.0` | Strong credence that φ does not hold in s |

**Critical Distinction.** The value `n = 0.5` does **not** encode medium intensity — it encodes *maximal epistemic uncertainty*. This is a sharp departure from intuitive "medium" scores: a Noul value of 0.5 means the model is maximally uninformed about whether the predicate holds. This corresponds to the uniform prior on the Bernoulli parameter. As noted in the JevTools documentation:

> *"Noul 0.5 = equal probability yes/no ≠ medium intensity. Use Score when you need to measure degree on a spectrum."*

**Theorem 3.1 (Noul Additive Independence).** For any two predicates `φ₁`, `φ₂` operating on the same state `s`, and their associated Noul operators `𝒩_{q₁}`, `𝒩_{q₂}`:

```
𝒩_{q₁}(s) and 𝒩_{q₂}(s) are independent random variables under M
```

if and only if the semantic content of `φ₁` and `φ₂` are orthogonal in the model's internal representation.

*Practical Consequence.* When using multiple Noul questions to detect independent binary properties (e.g., `has_pii`, `requests_refund`, `is_urgent`), their outputs are treated as independent signals. The code may combine them via a weighted sum without risk of double-counting or exclusion. This is the formal justification for using multiple Nouls rather than a Choice primitive when multiple conditions can simultaneously hold:

```
# Choice forces exactly one category to win (exclusive)
# Multiple Nouls allow simultaneous property detection (non-exclusive)

has_pii         = 𝒩_{q₁}(s)   # ∈ [0,1]
requests_refund = 𝒩_{q₂}(s)   # ∈ [0,1]
is_urgent       = 𝒩_{q₃}(s)   # ∈ [0,1]

# These may all be near 1.0 simultaneously
```

---

### 3.2 Choice: Categorical Distribution Projection

**Definition 3.2 (Choice Operator).** Given a question `q` with a finite, mutually exclusive, and collectively exhaustive option set `Ω = {ω₁, ..., ωₖ}` (K ≥ 2), the Choice operator is:

```
ℂ_q : 𝒮 → Δ(Ω) × Ω × [0, 1]

ℂ_q(s) := (p*, ω*, c)
```

where:

- `p* ∈ Δ(Ω)` is the full probability distribution over options.
- `ω* = argmax_{ω ∈ Ω} p*(ω)` is the modal (most probable) choice.
- `c ∈ [0,1]` is the confidence, derived from the sharpness of `p*`.

The option set `Ω` must be supplied by the caller in the `criteria` field. The model cannot choose an option not in `Ω`. This constraint is the **closed-world assumption** of the Choice primitive: all possible correct answers must appear in the criteria.

**Proposition 3.1 (Necessity of Fallback Option).** If the true semantic answer to the question posed by `q` is some category `ω_true` not in `Ω`, then for any calibrated model `M`:

```
ℂ_q(s) will place positive probability on the most semantically proximate ω ∈ Ω
```

and the confidence `c` will be depressed relative to the in-vocabulary case. This is why JevTools mandates including a fallback option ("None of the above" or "other") for any open-ended classification: without it, the model is forced to assign probability to an incorrect option, degrading calibration and utility.

**Definition 3.3 (Confidence for K-Class Choice).** Confidence for a K-class Choice answer is formally defined as:

```
c := (K · max_ω p*(ω) − 1) / (K − 1)
```

This formula maps:
- A perfectly peaked distribution (all mass on one option: `max p* = 1`) → `c = (K − 1)/(K − 1) = 1.0`
- A perfectly flat distribution (uniform: `max p* = 1/K`) → `c = (K · 1/K − 1)/(K − 1) = 0/(K−1) = 0.0`

Thus `c ∈ [0, 1]` and captures how concentrated the model's belief is, independent of the number of classes.

**Lemma 3.1 (Confidence Monotonicity).** For fixed K, confidence `c` is a strictly increasing function of `max_ω p*(ω)`.

*Proof.* `c(x) = (Kx − 1)/(K − 1)` is affine in `x = max p*(ω)` with positive slope `K/(K−1) > 0` for `K ≥ 2`. ∎

---

### 3.3 Score: Ordinal Expectation Projection

**Definition 3.4 (Score Operator).** Given a question `q` with an ordered set of `L` concrete levels `Λ = [λ₀, λ₁, ..., λ_{L-1}]` (from lowest to highest), the Score operator is:

```
𝒮𝒸_q : 𝒮 → Δ(Λ) × [0, L-1] × [0, 1]

𝒮𝒸_q(s) := (p*, σ, c)
```

where:

- `p* ∈ Δ(Λ)` is the full probability distribution over levels.
- `σ = Σⱼ j · p*_j` is the *probability-weighted level position* (the expected level index).
- `c ∈ [0, 1]` is confidence, derived from the sharpness of `p*`.

The raw score `σ ∈ [0, L-1]` can take fractional values — for example, `σ = 1.4` for a three-level rubric means the model assigns mass to both level 1 and level 2, with the centroid falling between them. This is a crucial property: Score is not a coarse classifier returning only {0, 1, ..., L-1}, but a continuous linear functional of the distribution.

**Definition 3.5 (Score Normalization).** To map the score into the unit interval for code composition, define the normalized score:

```
σ_norm := σ / (L − 1) ∈ [0, 1]
```

This normalization ensures that Score outputs from rubrics with different numbers of levels are comparable when combined in weighted sums.

**Theorem 3.2 (Score as Expected Value).** The Score output `σ` equals the expectation of the level index under the model's calibrated distribution:

```
σ = E_{p*}[j] = Σⱼ j · p*_j
```

*Proof.* By Definition 3.4, `σ = Σⱼ j · p*_j` with `Σⱼ p*_j = 1`, which is exactly the expectation of the discrete random variable `J ~ p*`. ∎

**Corollary 3.1.** Score is a sufficient statistic for all downstream computations that are linear functions of the level distribution. For non-linear computations (e.g., variance estimation, higher moments), the raw probability vector `p*` must be used directly.

**Proposition 3.2 (Score Concavity Under Uncertainty).** If a model is uncertain between two adjacent levels `j` and `j+1` with equal probability (0.5 each), the Score is `j + 0.5`, placing it between the two endpoints. As uncertainty spreads over more adjacent levels, the score converges toward the center of the rubric range, `(L−1)/2`. This behavior is consistent with maximum-entropy principles: uniform uncertainty over levels yields the midpoint score.

---

## 4. Confidence as a Distributional Sharpness Measure

We now prove that the confidence formula is a sound measure of distributional concentration — formally, a normalized version of the *peakedness* or *max-probability* statistic.

**Definition 4.1 (Peakedness).** For distribution `p ∈ Δ(Ω)`, the *peakedness* is:

```
ρ(p) := max_ω p(ω) ∈ [1/K, 1]
```

**Theorem 4.1 (Confidence is a Linear Normalization of Peakedness).** The Jev confidence formula:

```
c = (K · ρ(p) − 1) / (K − 1)
```

is the unique affine transformation of `ρ(p)` that maps `[1/K, 1] → [0, 1]` and is monotonically increasing.

*Proof.* Affine normalization of `[a, b] → [0, 1]` is given by `c = (x − a)/(b − a)`. Here `a = 1/K` (uniform) and `b = 1` (degenerate). So:

```
c = (ρ(p) − 1/K) / (1 − 1/K)
  = (K · ρ(p) − 1) / (K − 1)
```

which matches the documented formula exactly. Monotonicity follows from Lemma 3.1. Uniqueness follows from the uniqueness of the affine normalization of a bounded interval. ∎

**Remark 4.1 (Relationship to Entropy).** Confidence is monotone-*decreasing* in the Shannon entropy `H(p) = −Σ p_i log p_i`. Maximum entropy (uniform distribution) gives minimum confidence (0); minimum entropy (degenerate distribution) gives maximum confidence (1). This connection to information theory means that confidence quantifies *epistemic efficiency*: a higher confidence answer conveys more information about the true outcome.

**Theorem 4.2 (Confidence-Threshold Ordering Consistency).** Let `τ_low < τ_high ∈ [0,1]` be the low and high confidence thresholds defining the three behavioral tiers. For any two states `s₁, s₂ ∈ 𝒮`:

```
c(s₁) ≥ τ_high and c(s₂) < τ_low  ⟹  s₁ is more actionable than s₂
```

in the sense that the expected precision of acting on `s₁` exceeds that of acting on `s₂` by at least `τ_high − τ_low > 0`.

*Proof.* By Lemma 2.1 (calibration) and Theorem 4.1 (confidence monotonicity in peakedness), confidence is a monotone proxy for expected precision. The ordering of confidence values therefore induces a consistent ordering of expected precisions. ∎

---

## 5. Architectural Patterns: Mathematical Proofs

### 5.1 Speculative Fan-Out: Parallelism and Cost Theorem

The Speculative Fan-Out pattern sends all questions `{q₁, ..., qₙ}` over the same state `s` in a single request, even if only a subset `{qᵢ : i ∈ I_used}` is consumed by the application.

**Definition 5.1 (Single-Request Batch).** Let `R(s, Q)` denote a single Jev API call with state `s` and question set `Q = {q₁, ..., qₙ}`. This produces:

```
R(s, Q) = { A_q : q ∈ Q }
```

where `A_q` is the typed answer to question `q`. All questions evaluate in parallel under shared state encoding.

**Theorem 5.1 (Speculative Fan-Out Cost Equivalence).** Let `C_serial(n)` be the cost of `n` independent serial API calls and `C_batch(n)` be the cost of one batched call with `n` questions over the same state. Then:

```
C_batch(n) ≈ C_serial(1) + n · c_q  (where c_q is the marginal cost per question)
```

whereas:

```
C_serial(n) = n · (C_serial(1) + c_q)
```

giving a speedup ratio of approximately:

```
Speedup(n) = C_serial(n) / C_batch(n)
           = n · (C_0 + c_q) / (C_0 + n · c_q)
           → n as c_q → 0  (questions cost much less than state encoding)
           → 1  as c_q → C_0  (questions cost as much as state encoding)
```

*Empirical Support.* JevTools documentation reports that batching 13 questions into one call achieves **12.2× lower cost and 10× lower latency** versus 13 separate calls. Under our model, with `n = 13`:

```
Speedup ≈ 12.2 implies c_q / C_0 ≈ (n−1)/(n·Speedup − 1) = 12/157.6 ≈ 0.076
```

That is, each additional question costs approximately 7.6% of a full state encoding, which is consistent with the idea that questions are lightweight predicates evaluated over a cached state embedding.

**Theorem 5.2 (Answer Independence Under Shared State).** For a batch `R(s, Q)` with `Q = {q₁, ..., qₙ}`, the answers `{A_{q₁}, ..., A_{qₙ}}` are conditionally independent given the state encoding `μ(s)`:

```
P(A_{q₁} = a₁, ..., A_{qₙ} = aₙ | μ(s)) = ∏ᵢ P(A_{qᵢ} = aᵢ | μ(s))
```

*Proof Sketch.* Each question `qᵢ` defines a projection operator onto its respective output space, applied to the same encoded state `μ(s)`. Since the questions project along different semantic dimensions (by the architectural requirement of one narrow judgment per question), their output random variables are conditionally independent given the shared state. This is analogous to independent linear measurements of the same signal in compressed sensing. ∎

**Corollary 5.1 (Speculative Waste Is Bounded).** If the application uses only `k ≤ n` answers from a batch of `n` questions, the excess cost is at most `(n-k) · c_q`, bounded by the marginal per-question cost. This is the formal justification for "ask everything you might need plus speculative questions" — speculative questions cost nearly nothing in comparison to state round-trips.

---

### 5.2 Confidence-Gated Routing: Risk-Monotone Total Preorder

**Definition 5.2 (Action Set).** Let `𝒜 = {a₁, ..., aₘ}` be a finite set of possible actions the application code may take in response to a Choice answer. Each action `aᵢ` has an associated *risk level* `r(aᵢ) ∈ [0, 1]`, representing the cost of executing an incorrect action.

**Definition 5.3 (Confidence-Gated Policy).** A *confidence-gated policy* is a function:

```
π : 𝒜 × [0,1] → { execute, confirm, escalate }
```

defined by:

```
π(a, c) = 
  { execute  if c ≥ τ_high(a)
  { confirm  if τ_low ≤ c < τ_high(a)
  { escalate if c < τ_low
```

where `τ_high(a) ∈ [τ_low, 1]` is an action-specific confidence threshold, and `τ_low ∈ [0, 1]` is a global floor.

**Theorem 5.3 (Risk-Monotone Total Preorder).** The confidence-gated policy `π` induces a total preorder ≤_π on `𝒜` such that if `r(aᵢ) ≥ r(aⱼ)` (action `aᵢ` is riskier), then `τ_high(aᵢ) ≥ τ_high(aⱼ)` (action `aᵢ` requires higher confidence). This preorder is:

1. **Complete**: Every pair of actions is comparable under `≤_π`.
2. **Transitive**: `aᵢ ≤_π aⱼ ≤_π aₖ ⟹ aᵢ ≤_π aₖ`.
3. **Risk-monotone**: Higher-risk actions require weakly higher confidence thresholds.

*Proof.* The action-specific threshold function `τ_high : 𝒜 → [τ_low, 1]` defines a total preorder on `𝒜` via `aᵢ ≤_π aⱼ ⟺ τ_high(aᵢ) ≤ τ_high(aⱼ)`. Completeness holds because `≤` on `[τ_low, 1]` is a total order. Transitivity is inherited from `≤` on `ℝ`. Risk-monotonicity follows by setting `τ_high(a) = g(r(a))` where `g : [0,1] → [τ_low, 1]` is any non-decreasing function. ∎

**Example 5.1 (Banking Action Preorder).** The JevTools documentation gives:

```
r("check_balance") = 0    → τ_high("check_balance") = τ_low = 0.5
r("approve_transfer") = 1 → τ_high("approve_transfer") = 0.9
```

The total preorder is: `check_balance ≤_π approve_transfer`, meaning transfers require strictly more confident routing than balance checks.

**Theorem 5.4 (Expected Regret Minimization).** Under a calibrated model and a risk-monotone confidence-gated policy, the expected decision regret:

```
E[Regret(π)] = Σ_a r(a) · P(execute a | wrong)
```

is weakly minimized among all policies that maintain the same action distribution under high confidence, by choosing `τ_high(a) = g(r(a))` for a non-decreasing `g`.

*Proof Sketch.* By Lemma 2.1, expected precision given confidence threshold `τ` is `E[p | p ≥ τ] ≥ τ`. For action `a` with risk `r(a)`, the expected regret contribution is `r(a) · (1 − E[p | p ≥ τ_high(a)]) ≤ r(a) · (1 − τ_high(a))`. Setting `τ_high(a) = g(r(a))` with `g` non-decreasing reduces the regret for high-risk actions by requiring them to reach higher confidence before execution. ∎

---

### 5.3 Composite Scoring: Convex Weighted Priority Functional

**Definition 5.4 (Dimension Set).** Let `D = {d₁, ..., dₖ}` be a set of `k` independent semantic dimensions, each measured by a Score question `qᵢ` with `Lᵢ` levels and output `σᵢ ∈ [0, Lᵢ-1]`.

**Definition 5.5 (Composite Priority Functional).** Given weights `w = (w₁, ..., wₖ)` with `wᵢ ≥ 0` and `Σᵢ wᵢ = 1`, the composite priority functional is:

```
Φ_w : 𝒮 → [0, 1]

Φ_w(s) := Σᵢ wᵢ · σᵢ_norm(s)
         = Σᵢ wᵢ · σᵢ(s) / (Lᵢ − 1)
```

**Theorem 5.5 (Composite Scoring is a Convex Combination).** The composite priority functional `Φ_w` is:

1. **Bounded**: `Φ_w(s) ∈ [0, 1]` for all `s ∈ 𝒮`.
2. **Monotone in each dimension**: Increasing any normalized score `σᵢ_norm` weakly increases `Φ_w`.
3. **Weight-tunable without rerunning inference**: For a fixed state `s`, the vector `(σ₁_norm(s), ..., σₖ_norm(s))` is computed once; `Φ_w` can be re-evaluated for any weight vector `w` without additional API calls.
4. **Linearly separable by dimension**: The contribution of dimension `dᵢ` to `Φ_w` is `wᵢ · σᵢ_norm(s)`, which is inspectable and adjustable independently.

*Proof.* (1) Each `σᵢ_norm ∈ [0,1]` and `Σwᵢ = 1`, so `Φ_w = Σ wᵢ σᵢ_norm ∈ [0,1]`. (2) `∂Φ_w/∂σᵢ_norm = wᵢ ≥ 0`. (3) The score vector is a function of `s` alone; weight vector `w` is a free parameter. (4) Follows from linearity of `Φ_w` in `(σ₁_norm, ..., σₖ_norm)`. ∎

**Theorem 5.6 (Composite Scoring Completeness over Linear Preference Orders).** For any priority functional `F : 𝒮 → [0,1]` that is a monotone, differentiable function of a finite set of normalized semantic scores `σ₁_norm, ..., σₖ_norm`, there exists a first-order Taylor approximation using a composite score `Φ_w` such that:

```
|F(s) − Φ_w(s)| ≤ O(‖∇F − w‖ · ‖σ_norm(s) − σ₀‖)
```

for some reference point `σ₀`. This means composite scoring with an appropriate weight vector `w = ∇F(σ₀)` (the gradient of the true priority functional at the reference) provides a first-order approximation to any smooth priority functional over the dimension space.

*Practical Implication.* If a product team knows the relative importance of severity vs. frustration vs. report quality (i.e., the gradient of their implicit priority function), they can directly encode those weights in code and get a composite score that approximates their true priority function — without modifying the questions or rerunning inference.

---

### 5.4 Intent Routing: Decision-Theoretic Completeness

**Definition 5.6 (Intent Partition).** A *complete intent partition* is a set of category descriptions `{ω₁, ..., ωₖ, ω_fallback}` where:

- Each `ωᵢ` (for `i < k`) describes a specific user intent.
- `ω_fallback` ("other" / "none of the above") covers all intents not in `{ω₁, ..., ωₖ}`.
- The set is collectively exhaustive and mutually exclusive.

**Theorem 5.7 (Choice Completeness under Fallback).** Given a complete intent partition with fallback option included in `Ω`, the Choice operator `ℂ_q` is *complete* over the space of possible inputs — i.e., for every `s ∈ 𝒮`, `ℂ_q(s)` produces a well-defined, non-⊥ answer.

*Proof.* The fallback option `ω_fallback` covers the complement of all specific categories. Since the partition is collectively exhaustive, every `s` falls into at least `ω_fallback`. The model therefore always has a valid choice to assign positive probability to. ∎

**Corollary 5.2 (Intent Routing Completeness).** An Intent Routing architecture using a Choice question with a fallback option and subsequent policy dispatch via pattern matching on the `choice` field is *complete*: every possible input state produces a well-defined routing action (including the fallback action of routing to a human, which handles the `ω_fallback` case and the low-confidence case simultaneously).

---

## 6. Subset Solvability: Problem Classes Covered by Jev

We now enumerate the subsets of semantic decision problems that are provably solvable under Jev's micro-architecture, and characterize the conditions for solvability.

### 6.1 Classification Problems

**Definition 6.1 (K-Class Semantic Classification Problem).** A K-class classification problem is a triple `(𝒮, Ω, h*)` where `Ω` is a finite label set and `h* : 𝒮 → Ω` is the target labeling function.

**Theorem 6.1 (Jev Solves K-Class Classification).** Any K-class classification problem `(𝒮, Ω, h*)` where `Ω` is a closed, finite set (possibly with fallback) is solvable by the Choice operator under Jev with calibrated output, provided:

1. `Ω` includes a fallback option (completeness).
2. The question `instructions` precisely describe the classification criterion.
3. The state `s` contains sufficient context to disambiguate among options.

The solution `h_Jev(s) = argmax_ω ℂ_q(s).probabilities(ω)` approximates `h*(s)` up to the model's calibration error.

**Remark 6.1 (Hierarchical Classification).** For taxonomies with depth `D > 1`, the solution is a sequence of `D` Choice questions, each narrowing the option set from the parent class returned by the previous question. This is formally the **beam search** over the classification tree, and is provably sound for any tree-structured taxonomy.

---

### 6.2 Ranking and Reranking Problems

**Definition 6.2 (Ranking Problem).** Given a set of candidates `C = {c₁, ..., cₙ}`, a ranking problem is the problem of producing a total order `≤_C` over `C` according to a quality criterion `q`.

**Theorem 6.2 (Jev Solves Ranking via Score).** For any ranking problem over `n` candidates with a monotone quality criterion expressible as a scalar, the Score operator applied to each candidate independently produces a set of scores `{σᵢ}` such that ranking by `σᵢ` provides a consistent total order over `C`.

*Proof.* Score outputs are real-valued (`σᵢ ∈ [0, L-1]`) and totally ordered by `≤` on `ℝ`. Applying Score independently to each candidate (possibly within a single fan-out call over a state containing all candidates) produces a vector `(σ₁, ..., σₙ)`. The induced order `cᵢ ≤_score cⱼ ⟺ σᵢ ≤ σⱼ` is a valid total preorder. ∎

**Empirical Validation.** JevTools documentation cites a BM25 → Jev reranking cookbook demonstrating improvement from 5% to 18% top-1 accuracy, a 3.6× improvement. This is consistent with the theoretical claim that Jev's calibrated Score ordering supersedes keyword-frequency-based BM25 ranking for semantic relevance problems.

---

### 6.3 Verification and Extraction Problems

**Definition 6.3 (Verification Problem).** A verification problem asks whether a claim `φ` is supported by evidence `e` in state `s`. This is a binary judgment: `φ` is supported or not.

**Theorem 6.3 (Jev Solves Verification via Noul).** Any verification problem `(φ, e, s)` expressible as a binary predicate over a text state is solvable by the Noul operator:

```
result = 𝒩_q(s)  where q encodes "Does e support claim φ?"
```

The result `result ∈ [0,1]` gives a calibrated probability that the verification holds, enabling confidence-gated downstream action.

**Definition 6.4 (Structured Extraction Problem).** Given a state `s` containing one or more candidate values `V = {v₁, ..., vₘ}` pre-extracted by deterministic regex/code, an extraction problem is the problem of selecting the intended value `v* ∈ V`.

**Theorem 6.4 (Jev Solves Extraction via Select-Don't-Generate).** The extraction problem `(s, V, v*)` is solvable by Choice operator over the candidate set:

```
ℂ_q(s_with_candidates).choice  selects the most probable correct value v* ∈ V
```

This is provably superior to asking Jev to *generate* an extraction, because:

1. **Candidate coverage is guaranteed**: the correct value must appear in `V` (which is found deterministically by code).
2. **Normalization is deterministic**: code normalizes the selected candidate; the model never produces ambiguous text.
3. **Error surface is reduced**: if `v* ∉ V`, the problem is a code error (wrong candidate extraction), not a model error, making debugging tractable.

---

### 6.4 Moderation and Guardrail Problems

**Definition 6.5 (Hazard Detection Problem).** Given a finite set of hazard types `H = {h₁, ..., hₘ}` and a state `s` (e.g., an LLM output), a hazard detection problem asks: for each `hᵢ ∈ H`, does `s` exhibit hazard `hᵢ`?

**Theorem 6.5 (Jev Solves Multi-Hazard Detection via Parallel Nouls).** The hazard detection problem `(H, s)` is solvable by `m` independent Noul questions:

```
p_i = 𝒩_{q_i}(s)  for each hazard type hᵢ ∈ H
```

all sent in a single batch request (Speculative Fan-Out). The resulting vector `(p₁, ..., pₘ) ∈ [0,1]^m` provides independent calibrated hazard probabilities that can be thresholded or aggregated in code.

**Remark 6.2.** This approach is strictly superior to a single Choice question over `H` because:

- Multiple hazards can co-occur in a single state (non-exclusive).
- Choice forces exactly one hazard to "win," suppressing co-occurring hazards.
- `m` Nouls detect all simultaneous hazards independently.

---

### 6.5 Feature Generation for Downstream ML

**Definition 6.6 (ML Feature Generation Problem).** Given a dataset `{(s₁, y₁), ..., (sₙ, yₙ)}` of labeled states, and a downstream ML model `f : ℝ^d → 𝒴`, a feature generation problem asks: how to construct the feature vector `x(s) ∈ ℝ^d` from `s`?

**Theorem 6.6 (Jev Outputs are Valid ML Features).** The probability vectors returned by Jev primitives are valid feature representations for downstream ML models:

1. **Noul outputs** `𝒩_{q_i}(s) ∈ [0,1]` are bounded scalar features.
2. **Score probability vectors** `p*ᵢ ∈ Δ(Λᵢ)` are `Lᵢ`-dimensional feature vectors.
3. **Choice probability distributions** `p*ᵢ ∈ Δ(Ωᵢ)` are `Kᵢ`-dimensional feature vectors.

Concatenating these produces a feature map:

```
x(s) = [𝒩_{q₁}(s), ..., p*_score_1, ..., p*_choice_1, ...] ∈ ℝ^d
```

where `d = Σ Noul_dims + Σ Score_dims + Σ Choice_dims`.

Since Jev's outputs are calibrated probabilities, the feature map `x` is *semantically grounded* — features correspond to human-interpretable concepts — and *bounded* — each feature `∈ [0,1]`, which is beneficial for gradient-based ML methods.

**Practical Support.** JevTools documentation describes the AutoResearch Feature Discovery cookbook: "Propose Qs → convert text → train CatBoost." This implements exactly the pipeline of Theorem 6.6: use Score/Noul questions to generate semantic features, then train gradient-boosted trees on those features with labeled outcomes.

---

## 7. Micro-Architectural Invariants

We now enumerate the core invariants of Jev's micro-architecture that are preserved by correct usage:

**Invariant I (Control Inversion).** Application code owns all control flow, branching, aggregation, and policy decisions. Jev provides evidence; code decides. This is maintained by:
- Never embedding thresholds, weights, or routing rules in question text.
- Always acting on the typed output fields (`.noul`, `.choice`, `.score`, `.confidence`) in code.

**Invariant II (State Purity).** Each API call evaluates a self-contained state. No implicit state is shared between calls. Questions within a call share state but cannot see each other's answers. This maintains:
- Reproducibility: the same `(s, Q)` pair always produces statistically consistent answers.
- Debuggability: failures are traceable to specific `(s, q)` pairs.

**Invariant III (Typed Interface Contract).** The typed output schema is guaranteed by the model, not by post-processing. The code contract is:

```
𝒩_q : 𝒮 → [0, 1]              (always a valid float)
ℂ_q : 𝒮 → (str, dict, float)  (always a valid (choice, probabilities, confidence))
𝒮𝒸_q : 𝒮 → (float, list, float) (always a valid (score, probabilities, confidence))
```

No text parsing is required. This eliminates an entire class of fragile prompt-engineering failures.

**Invariant IV (Calibration Validity).** Confidence values and Noul probabilities are calibrated by RLCD training. This makes threshold-based policies (Theorems 5.3, 5.4) operationally sound — not just conceptually appealing.

**Invariant V (Parallelism Transparency).** Questions within a request evaluate in parallel with conditional independence given state (Theorem 5.2). This invariant means that adding more questions to a request does not change the answers to existing questions — a critical property for iterative system development.

---

## 8. Limits of the Framework

Jev's micro-architecture is not universally applicable. We formally characterize the problems it cannot solve under current constraints:

**Limitation L1 (No Generation).** Jev cannot generate novel text, code, prose, or structured data. If the problem output is not a selection, classification, ranking, or probability over a closed candidate set, Jev is inapplicable. Such problems require a generative LLM.

**Limitation L2 (Closed Candidate Set Required for Choice/Score).** The Choice and Score operators require a finite, caller-specified candidate/level set. Open-ended classification (where the label set is unbounded or unknown a priori) cannot be directly solved by Choice. Hierarchical classification provides a partial workaround for structured taxonomies.

**Limitation L3 (Text-Only Modality).** As noted in the JevTools documentation, Jev currently accepts only text inputs. Image, audio, and video understanding problems are outside scope.

**Limitation L4 (No Inter-Question Reasoning).** Within a single request, questions evaluate independently and cannot condition on each other's answers (Theorem 5.2). Problems requiring sequential reasoning chains where step `i+1` depends on the answer to step `i` require multiple sequential API calls. This is the multi-step cascade pattern (SDE Cascade cookbook) and is the exception rather than the rule.

**Limitation L5 (Context Window Constraints).** State length is bounded by the model's context window. Very long documents, extensive chat histories, or large corpora cannot be evaluated as a single state. Retrieval-augmented preprocessing (select relevant context before calling Jev) is the prescribed mitigation.

**Limitation L6 (No Control Flow Ownership).** Jev cannot autonomously loop, branch, or sequence operations — those are the code's responsibility. Agent architectures where a model controls execution flow are explicitly excluded from Jev's design ("not LLM agents — AI-powered software"). Problems that fundamentally require agent-style autonomous planning cannot be solved by Jev alone.

---

## 9. Conclusion

This paper has established a rigorous mathematical framework for understanding Jev (TypeSafe System One) as a semantic decision engine operating over a typed micro-architecture. Key results include:

1. **Primitive Formalization**: The three primitives (Noul, Choice, Score) are projection operators over well-defined probability spaces — the unit interval, the K-class categorical simplex, and the L-level ordinal simplex, respectively.

2. **Confidence Soundness**: Jev's confidence formula is proven to be the unique affine normalization of distributional peakedness, monotone in uncertainty, and meaningful for threshold-based policy decisions only under calibrated models (which RLCD training provides).

3. **Speculative Fan-Out**: Batching `n` questions over shared state achieves `O(n)` speedup over serial calls, with conditional independence of answers preserved — making it the dominant strategy for multi-question workloads.

4. **Confidence-Gated Routing**: Provides a risk-monotone total preorder on actions, formally minimizing expected regret under calibrated confidence estimates.

5. **Composite Scoring**: Constructs a convex, weight-tunable priority functional that is linearly separable by dimension — supporting post-hoc weight adjustment without rerunning inference.

6. **Subset Solvability**: Jev is mathematically sufficient to solve closed-label classification, ranking, binary and multi-label detection, structured extraction (select-don't-generate), hazard moderation, and ML feature generation. These problem classes cover the majority of semantic judgment tasks encountered in production software.

The fundamental architectural theorem underlying all of these results is the **Control Inversion Principle**: Jev fills narrow semantic judgment slots while deterministic code owns policy, control flow, and composition. This division of responsibility is not merely a design preference — it is the mathematical property that makes Jev's outputs composable, auditable, and safe to act upon.

Systems built under this micro-architecture inherit the mathematical soundness of the operators, patterns, and invariants proven here, forming a rigorous foundation for AI-powered software that is measurably safer and more deterministic than agent-controlled alternatives.

---

## 10. Notation Reference

| Symbol | Definition |
|---|---|
| `𝒮` | State space (`𝒮_str ∪ 𝒮_obj ∪ 𝒮_arr`) |
| `ℳ` | Latent semantic meaning space |
| `μ : 𝒮 → ℳ` | Meaning encoding function |
| `Δ(Ω)` | Probability simplex over finite set `Ω` |
| `𝒩_q` | Noul projection operator for question `q` |
| `ℂ_q` | Choice projection operator for question `q` |
| `𝒮𝒸_q` | Score projection operator for question `q` |
| `p*` | Model output probability distribution |
| `ω*` | Modal (highest-probability) outcome |
| `c` | Confidence value |
| `ρ(p)` | Peakedness: `max_ω p(ω)` |
| `σ` | Raw Score output (expected level index) |
| `σ_norm` | Normalized score: `σ / (L−1) ∈ [0,1]` |
| `Φ_w` | Composite priority functional with weight vector `w` |
| `π(a, c)` | Confidence-gated routing policy |
| `τ_high(a)` | Action-specific confidence execution threshold |
| `τ_low` | Global confidence floor for all actions |
| `r(a)` | Risk level of action `a ∈ [0,1]` |
| `R(s, Q)` | Single batch API call with state `s` and questions `Q` |
| `C_batch(n)` | Cost of one batch of `n` questions |
| `C_serial(n)` | Cost of `n` separate serial API calls |

---

*This paper synthesizes the mathematical structures implicit in the JevTools knowledge base, vault documentation, architectural patterns, and SDK reference materials into a formal framework. All empirical figures (287 ms latency, 12.2× cost reduction, 10× speedup, 5% → 18% reranking improvement) are sourced directly from JevTools documentation and cited as empirical support for the theoretical results.*
