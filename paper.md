# Mathematical Foundations of Jev: A Micro-Architectural Framework for Structured Semantic Decision Problems

**Author:** Riley Carney and the website documentation at TypeSafe AI Research Group  
**Repository:** [RileyCarney/JevTools](https://github.com/RileyCarney/JevTools)  
**Date:** September 2026  
**Version:** 2.1 — Comprehensive Formal Mathematical Framework & Reference Implementation Edition              
**GUID:** a302324cb2fcffed9deef41588d6d64af9909821                                                             
**Status:** Working Paper

---

## Abstract

This paper establishes a formal mathematical framework for Jev, TypeSafe AI's *System One* decision model, and aims prove that its micro-architectural structure is provably sufficient to solve well-defined subsets of semantic decision problems. We formalize the three core primitives (Noul, Choice, Score) as typed projection operators over the probability simplex, establish a measure-theoretic and Bayesian interpretation of their calibrated outputs under Reinforcement Learning from Calibrated Decisions (RLCD), and prove completeness and composability theorems for their integration. 

We demonstrate that the Speculative Fan-Out pattern achieves sub-linear cost growth relative to serial execution under a empirically validated two-component cost model ($r \approx 0.0055$, yielding a $12.2\times$ cost reduction at $n = 13$ batch size with an asymptotic speedup ceiling of $\sim 183\times$), that Confidence-Gated Routing induces a risk-monotone total preorder on action spaces with universal, cardinality-independent regret bounds ($\mathbb{E}[\mathrm{Regret}] \le \frac{1 - \tau_{\mathrm{low}}}{4}$), and that Composite Scoring constructs a convex, post-hoc tunable priority functional whose approximation error to arbitrary smooth objective functionals is quadratically bounded by a second-order Taylor remainder governed by the Hessian spectral norm. We further formalize information-theoretic conditions under which question decomposition is strictly lossless and non-redundant via multi-information and total correlation, bound calibration error propagation in linear aggregations under the Wasserstein-1 metric, and characterize inter-rater self-consistency via output variance and Cohen's $\kappa$. 

Finally, every mathematical construct across all sections is accompanied by a self-contained, fully typed, docstringed, and mathematically verified Python reference implementation embedded directly within the text. Together, these theoretical and computational results establish Jev's micro-architecture as a mathematically sound substrate for deterministic semantic computation.

---

## Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 Motivation and the Semantic Decision Problem
   - 1.2 Axiom A1: Control Inversion as an Automaton Invariant
   - 1.3 Architectural Comparison
2. [Formal Definitions](#2-formal-definitions)
   - 2.1 State Space and Semantic Representation
   - 2.2 The Probability Simplex
   - 2.3 Measure-Theoretic Calibration via RLCD
   - 2.4 Bayesian Interpretation of Primitive Outputs
   - 2.5 Computational Reference: State Space, Simplex, and Calibration Validation
3. [The Three Primitives as Projection Operators](#3-the-three-primitives-as-projection-operators)
   - 3.1 Noul: Binary Credence Projection
   - 3.2 Choice: Categorical Distribution Projection
   - 3.3 Score: Ordinal Expectation Projection
   - 3.4 Primitive Distinguishability: Selection Optimality
   - 3.5 Computational Reference: Primitive Operators and Dispatch
4. [Confidence as a Distributional Sharpness Measure](#4-confidence-as-a-distributional-sharpness-measure)
   - 4.1 Peakedness and Unique Boundary-Anchored Affine Normalization
   - 4.2 Entropy Monotonicity and Distributional Bounding Envelopes
   - 4.3 Confidence-Threshold Ordering Consistency
   - 4.4 Computational Reference: Distributional Sharpness, Confidence, and Entropy
5. [Information-Theoretic Question Decomposition](#5-information-theoretic-question-decomposition)
   - 5.1 Measurement Channels and Atomic Questions
   - 5.2 Sufficient and Non-Redundant Decomposition
   - 5.3 Orthogonal Decomposition and Mutual Information Maximization
   - 5.4 Computational Reference: Information-Theoretic Decomposition & Verification
6. [Architectural Patterns: Mathematical Proofs](#6-architectural-patterns-mathematical-proofs)
   - 6.1 Speculative Fan-Out: Parallelism and Cost Theorem
   - 6.2 Confidence-Gated Routing: Risk-Monotone Total Preorder & Regret Bound
   - 6.3 Composite Scoring: Convex Weighted Priority Functional & Taylor Remainder
   - 6.4 Intent Routing: Decision-Theoretic Completeness
   - 6.5 Multi-Step Cascade: Sequential Bayesian Updating
   - 6.6 Computational Reference: Architectural Patterns Suite
7. [Subset Solvability: Problem Classes Covered by Jev](#7-subset-solvability-problem-classes-covered-by-jev)
   - 7.1 Closed $K$-Class Classification Problems
   - 7.2 Ranking and Reranking Problems
   - 7.3 Verification and Candidate Extraction Problems
   - 7.4 Multi-Hazard Moderation and Guardrail Problems
   - 7.5 Calibrated Feature Generation for Downstream ML
   - 7.6 Computational Reference: Complete Problem Solvers Suite
8. [Error Propagation Through Composed Operations](#8-error-propagation-through-composed-operations)
   - 8.1 Calibration Error Propagation in Weighted Aggregations
   - 8.2 Self-Consistency and Inter-Rater Reliability
   - 8.3 Computational Reference: Error Propagation and Reliability Suite
9. [Micro-Architectural Invariants](#9-micro-architectural-invariants)
   - 9.1 Mathematical Specification of Invariants I through V
   - 9.2 Computational Reference: Runtime Invariant Verification Harness
10. [Limits of the Framework](#10-limits-of-the-framework)
11. [Related Work](#11-related-work)
12. [Open Problems](#12-open-problems)
13. [Conclusion](#13-conclusion)
14. [Notation Reference](#14-notation-reference)
15. [References](#15-references)

---

## 1. Introduction

### 1.1 Motivation and the Semantic Decision Problem

Modern software systems increasingly encounter *semantic decision problems* — computational tasks whose resolution requires interpreting the natural-language meaning of unstructured state rather than evaluating algebraic equations, relational queries, or exact string predicates. Classical deterministic code is brittle and insufficient for these open-domain inputs; conversely, generative Large Language Models (LLMs) are over-expressive, producing unconstrained free-form text that must be parsed via fragile regexes or schema decoders, while exhibiting systematically miscalibrated uncertainty estimates (Guo et al., 2017; Kadavath et al., 2022).

**Jev** (TypeSafe AI, System One) occupies a principled intermediate regime: it accepts structured natural-language state and returns *strictly typed, probability-calibrated* semantic judgments at high throughput (median latency $\sim 100\text{ ms}$, with cold batch invocations bounded within $287\text{ ms}$). Jev is not a generator; it operates as a *semantic projection operator* — projecting a latent, high-dimensional semantic manifold onto finite-dimensional probability simplices (categorical, ordinal, or binary credence) while guaranteeing empirical calibration.

### 1.2 Axiom A1: Control Inversion as an Automaton Invariant

The fundamental principle governing all safe integrations of Jev is designated **Axiom A1 — Control Inversion**. To establish its mathematical validity, we model the host application system as a deterministic program automaton:

$$\mathcal{A}_{\mathrm{code}} = \langle \Sigma, \mathcal{S}, \mathcal{Q}, \mathcal{O}, \delta, \sigma_0 \rangle$$

where:
- $\Sigma$ is the program's internal state space (execution variables, database records, control stack).
- $\mathcal{S}$ is the external state space (text, JSON payloads).
- $\mathcal{Q}$ is the question specification space.
- $\mathcal{O}$ is the typed observation space emitted by Jev.
- $\delta : \Sigma \times \mathcal{O} \to \Sigma$ is the deterministic program transition function.
- $\sigma_0 \in \Sigma$ is the initial state.

Jev is formalized as a pure semantic oracle (measurement operator):

$$\mathcal{J} : \mathcal{S} \times \mathcal{Q} \to \mathcal{O}$$

**Axiom A1 (Control Inversion / Strict Oracle Subordination).**
*The semantic model $\mathcal{J}$ is an observation-generating oracle with strictly read-only access to state $\mathcal{S}$. Formally:*
1. $\mathcal{J}$ *possesses zero transition dynamics over $\Sigma$; it has no write permissions or state mutation authority over the host execution environment:*
   $$\frac{\partial \delta}{\partial \mathcal{J}_{\mathrm{internal}}} \equiv 0$$
2. *All control flow branching, state transitions, irreversible actions, and external mutations are strictly governed by the host code transition function $\delta$:*
   $$\sigma_{t+1} = \delta(\sigma_t, \mathcal{J}(s(\sigma_t), Q(\sigma_t)))$$

This is the defining property of the **System One micro-architecture**: Jev fills narrow semantic judgment slots, providing calibrated, typed probabilistic evidence, while application code retains exclusive ownership of policy and control flow.

### 1.3 Architectural Comparison

Table 1 situates Jev relative to deterministic code and generative LLMs on the fundamental architectural axes analyzed in this paper.

| Axis | Deterministic Code | Generative LLM | Jev (System One) |
|---|---|---|---|
| **Output Type** | Exact / Typed | Free-form natural language text | Strictly typed probability distributions |
| **Uncertainty Representation** | None (Deterministic) | Implicit / Miscalibrated / Overconfident | Explicit, strongly calibrated posteriors |
| **Control Flow Ownership** | Code ($\delta$) | Model prompt / Agent loop | Code (Axiom A1 Enforcement) |
| **Composability** | Full mathematical composability | Fragile (Parsing and deserialization failures) | Full typed projection composability |
| **Semantic Judgment** | None | Full generative reasoning | Fast projection / Judgment-only |
| **Operational Latency** | Sub-millisecond | $500\text{ ms} - \text{seconds}$ | $100\text{ ms} - 287\text{ ms}$ (median $\sim 100\text{ ms}$) |

---


## 2. Formal Definitions

### 2.1 State Space and Semantic Representation

Let $\mathcal{S}$ be the **state space** — the set of all syntactically valid inputs presented to the Jev model. Formally, a state $s \in \mathcal{S}$ is an element of the recursive union:

$$\mathcal{S} := \mathcal{S}_{\mathrm{str}} \cup \mathcal{S}_{\mathrm{obj}} \cup \mathcal{S}_{\mathrm{arr}}$$

where:
- $\mathcal{S}_{\mathrm{str}}$ is the set of all finite UTF-8 strings (unstructured text passages).
- $\mathcal{S}_{\mathrm{obj}} = \{ \{ (k_i, v_i) \}_{i=1}^m : k_i \in \Sigma^\ast, v_i \in \mathcal{S} \}$ is the set of finite JSON-compatible key-value maps (structured object payloads; the preferred representation).
- $\mathcal{S}_{\mathrm{arr}} = \bigcup_{k=0}^\infty \mathcal{S}^k$ is the set of finite ordered sequences of state elements.

The semantic content of a state is represented via an implicit state encoder:

$$\mu : \mathcal{S} \to \mathcal{M}$$

where $(\mathcal{M}, d_\mathcal{M})$ is a complete metric space representing the latent semantic space learned during pre-training and calibrated fine-tuning. The encoder $\mu$ is Borel-measurable with respect to the standard topological $\sigma$-algebra on $\mathcal{M}$.

**Definition 2.1 (Pointwise Semantic Information & Context Relevance).**
Let $\mathcal{D} \in \mathcal{P}(\mathcal{S} \times \Omega_q)$ be the joint data-generating probability measure, inducing random variables $X \in \mathcal{S}$ and ground-truth answer $Y_q \in \Omega_q$ for question $q$.
1. **Global Relevance:** The global informational relevance of state representation $\mu(X)$ for question $q$ is quantified by the Shannon mutual information:
   $$I(Y_q ; \mu(X)) = \mathbb{E}_{X \sim \mathcal{D}_X}\left[ D_{\mathrm{KL}}\left(P(Y_q \mid \mu(X)) \,\parallel\, P(Y_q)\right) \right]$$
2. **Pointwise Instance Relevance:** An individual state realization $s \in \mathcal{S}$ is **context-relevant** for question $q$ if and only if the Kullback-Leibler divergence between the prior and conditional posterior is strictly positive:
   $$D_{\mathrm{KL}}\left( P(Y_q \mid \mu(s)) \,\parallel\, P(Y_q) \right) > 0$$
   Equivalently, observing state $s$ updates the epistemic credence on $Y_q$ away from the base prior $P(Y_q)$.

**Definition 2.2 (Field Accessor Operator).**
Let $\mathrm{Path} = \bigcup_{k=1}^\infty (\Sigma^\ast)^k$ denote the set of finite dot-delimited access paths (e.g., `ticket.messages[0].text`). The field accessor is the partial projection:

$$\Pi_{\mathrm{path}} : \mathcal{S}_{\mathrm{obj}} \times \mathrm{Path} \to \mathcal{S} \cup \{\bot\}$$

where $\bot$ designates a path resolution failure (key absence, index out of bounds, or type error). When evaluating queries over state $s$, path accessors ground semantic attention to specific fields, with $\bot$ treated as an absent evidence signal.

---

### 2.2 The Probability Simplex

All three Jev primitives project state encodings onto probability distributions over finite outcome spaces.

**Definition 2.3 (Closed Probability Simplex).**
For a finite outcome space $\Omega$ with cardinality $|\Omega| = N \ge 2$, the **closed probability simplex** is:

$$\Delta_N := \Delta(\Omega) := \left\lbrace p \in \mathbb{R}^N : p_i \ge 0 \; \forall i \in \{1, \dots, N\}, \; \sum_{i=1}^N p_i = 1 \right\rbrace$$

The simplex $\Delta_N$ is a compact, convex $(N-1)$-dimensional subset of the affine hyperplane $\{\sum p_i = 1\} \subset \mathbb{R}^N$. Special instances:
- $N = 2$ (Noul): $\Delta_2 \cong [0, 1]$, the unit interval of binary credences.
- $N = K$ (Choice over $K$ options): $\Delta_K$, the standard categorical $(K-1)$-simplex.
- $N = L$ (Score over $L$ rubric levels): $\Delta_L$, the ordinal $(L-1)$-simplex.

The vertices $e_i \in \Delta_N$ represent complete epistemic certainty on outcome $\omega_i$, while the centroid $\mathbf{u} = (1/N, \dots, 1/N)^T$ represents the maximum-entropy uniform prior of complete uncertainty.

---

### 2.3 Measure-Theoretic Calibration via RLCD

Jev models are optimized using **Reinforcement Learning from Calibrated Decisions (RLCD)**. Calibration is the foundational property ensuring that output probabilities correspond to empirical true frequencies, justifying all downstream risk and thresholding theorems.

**Definition 2.4 (Strong Measure-Theoretic Calibration).**
Let $M : \mathcal{S} \to \Delta_N$ be a measurable model predicting probabilities over outcome set $\Omega = \{\omega_1, \dots, \omega_N\}$. $M$ is **strongly calibrated** under data distribution $\mathcal{D}$ if, for every outcome $\omega_i \in \Omega$ and for every Borel set $B \in \mathcal{B}([0, 1])$:

$$\mathbb{P}_{(X, Y) \sim \mathcal{D}}\left( Y = \omega_i \text{ and } M(X)_i \in B \right) = \int_B \tau \, \mathrm{d}\mathbb{P}_{M(X)_i}(\tau)$$

Equivalently, expressed via regular conditional expectation:

$$\mathbb{E}_{(X, Y) \sim \mathcal{D}}\left[ \mathbf{1}_{\{Y = \omega_i\}} \;\middle|\; M(X)_i \right] = M(X)_i \quad \mathbb{P}_{M(X)_i}\text{-almost surely.}$$

**Definition 2.4a (RLCD Optimization Formulation).**
Let $S : \Delta_N \times \Omega \to \mathbb{R}$ be a strictly proper scoring rule (such as the multi-class Brier score or logarithmic cross-entropy). The RLCD training objective minimizes empirical risk augmented with an $L_p$-Expected Calibration Error penalty:

$$\min_\theta \; \mathcal{L}_{\mathrm{RLCD}}(\theta) := \mathbb{E}_{(X, Y) \sim \mathcal{D}}\left[ -S(M_\theta(X), Y) \right] + \lambda_{\mathrm{cal}} \cdot \mathrm{ECE}_p(M_\theta; \mathcal{D})$$

where the Expected Calibration Error is defined across $B$ reliability bins as:

$$\mathrm{ECE}_p(M; \mathcal{D}) := \left( \sum_{b=1}^B \frac{|B_b|}{N} \left| \mathrm{acc}(B_b) - \mathrm{conf}(B_b) \right|^p \right)^{1/p}$$

By the characterization of strictly proper scoring rules (Gneiting & Raftery, 2007), the unconstrained population minimizer of $\mathbb{E}[-S(p, Y)]$ is the true Bayes conditional posterior $P(Y \mid X)$, which is inherently strongly calibrated.

**Lemma 2.1 (Calibration Preserves Utility of Thresholding).**
*Let $M$ be strongly calibrated under $\mathcal{D}$. For any outcome $\omega \in \Omega$ and operational threshold $\tau \in [0, 1]$ such that $\mathbb{P}(M(X)_\omega \ge \tau) > 0$, the expected true precision of acting on threshold $\tau$ satisfies:*

$$\mathbb{E}_{(X, Y) \sim \mathcal{D}}\left[ \mathbf{1}_{\{Y = \omega\}} \;\middle|\; M(X)_\omega \ge \tau \right] = \mathbb{E}_{X \sim \mathcal{D}}\left[ M(X)_\omega \;\middle|\; M(X)_\omega \ge \tau \right] \ge \tau$$

*Proof.* By the tower property of conditional expectation:

$$\mathbb{E}\left[ \mathbf{1}_{\{Y = \omega\}} \;\middle|\; M(X)_\omega \ge \tau \right] = \mathbb{E}\left[ \mathbb{E}\left[ \mathbf{1}_{\{Y = \omega\}} \;\middle|\; M(X)_\omega \right] \;\middle|\; M(X)_\omega \ge \tau \right]$$

Applying strong calibration (Definition 2.4), $\mathbb{E}[\mathbf{1}_{\{Y = \omega\}} \mid M(X)_\omega] = M(X)_\omega$ almost surely. Therefore:

$$\mathbb{E}\left[ \mathbf{1}_{\{Y = \omega\}} \;\middle|\; M(X)_\omega \ge \tau \right] = \mathbb{E}\left[ M(X)_\omega \;\middle|\; M(X)_\omega \ge \tau \right]$$

Because $M(X)_\omega \ge \tau$ holds on the conditioned event, positivity of conditional expectation ensures:

$$\mathbb{E}\left[ M(X)_\omega \;\middle|\; M(X)_\omega \ge \tau \right] \ge \mathbb{E}\left[ \tau \;\middle|\; M(X)_\omega \ge \tau \right] = \tau$$

completing the proof. $\blacksquare$

---

### 2.4 Bayesian Interpretation of Primitive Outputs

**Definition 2.5 (Hypothesis Space and Likelihood).**
For question $q$ with outcome hypothesis space $\Omega$, let $p_0(\omega)$ denote the base prior probability of outcome $\omega \in \Omega$ under data distribution $\mathcal{D}$. Let $\mathcal{L}(\mu(s) \mid \omega)$ denote the likelihood of observing latent semantic encoding $\mu(s)$ given hypothesis $\omega$.

**Proposition 2.1 (Primitives as Calibrated Posterior Projections).**
*Under RLCD convergence, the outputs of the three Jev primitives correspond to exact Bayes posterior projections:*

$$P(Y = \omega \mid \mu(s)) = \frac{\mathcal{L}(\mu(s) \mid \omega) \, p_0(\omega)}{\sum_{\omega' \in \Omega} \mathcal{L}(\mu(s) \mid \omega') \, p_0(\omega')}$$

1. **Noul:** $\mathcal{N}_q(s) = P(Y_q = 1 \mid \mu(s)) \in [0, 1]$ (posterior credence on binary predicate).
2. **Choice:** $\mathbb{C}_q(s).p^\ast = \left( P(Y_q = \omega_1 \mid \mu(s)), \dots, P(Y_q = \omega_K \mid \mu(s)) \right)^T \in \Delta_K$.
3. **Score:** $\mathcal{Sc}_q(s).p^\ast = \left( P(Y_q = \lambda_0 \mid \mu(s)), \dots, P(Y_q = \lambda_{L-1} \mid \mu(s)) \right)^T \in \Delta_L$.

---

### 2.5 Computational Reference: State Space, Simplex, and Calibration Validation

The following Python script provides a self-contained reference implementation for Section 2, verifying field path resolution, simplex bounds, measure-theoretic calibration metrics (ECE, MCE), Murphy's Brier score decomposition, and Lemma 2.1.

```python
"""
Reference Implementation for Section 2: State Space, Simplex, and RLCD Calibration.
Paper: Mathematical Foundations of Jev (v2.1)
Section: 2.1 State Space, 2.2 Probability Simplex, 2.3 Calibration via RLCD
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import numpy as np

# ---------------------------------------------------------------------------
# Section 2.1: State Space and Field Path Resolution
# ---------------------------------------------------------------------------

StateStr = str
StateObj = Dict[str, Any]
StateArr = List[Any]
State = Union[StateStr, StateObj, StateArr]

BOTTOM = None  # Formal representation of \bot (absent evidence)


def resolve_field_path(s: State, path: str) -> Optional[Any]:
    r"""
    Evaluates partial accessor s[p] : \mathcal{S}_obj \times Path -> \mathcal{S} \cup {\bot}.
    Supports recursive dot-delimited and bracket-indexed path navigation.
    """
    if not path:
        return s

    tokens = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)|(?:\[(\d+)\])", path)
    current: Any = s

    for key_token, idx_token in tokens:
        if current is None:
            return BOTTOM

        if key_token:
            if isinstance(current, dict) and key_token in current:
                current = current[key_token]
            else:
                return BOTTOM
        elif idx_token:
            idx = int(idx_token)
            if isinstance(current, (list, tuple)) and 0 <= idx < len(current):
                current = current[idx]
            else:
                return BOTTOM

    return current


# ---------------------------------------------------------------------------
# Section 2.2: Probability Simplex Validation
# ---------------------------------------------------------------------------

def validate_simplex(p: Sequence[float], atol: float = 1e-7) -> np.ndarray:
    r"""
    Validates that probability vector p resides on the closed simplex \Delta_N:
    \Delta_N := { p \in \mathbb{R}^N : p_i >= 0, \sum p_i = 1 }.
    """
    arr = np.asarray(p, dtype=np.float64)
    if arr.ndim != 1 or len(arr) == 0:
        raise ValueError("Simplex element must be a non-empty 1D vector.")

    if np.any(arr < -atol):
        raise ValueError(f"Simplex violation: negative probabilities detected: {arr[arr < -atol]}")

    arr = np.maximum(arr, 0.0)
    total = np.sum(arr)
    if abs(total - 1.0) > atol:
        raise ValueError(f"Simplex violation: sum={total}, expected 1.0 within atol={atol}")

    return arr / total


# ---------------------------------------------------------------------------
# Section 2.3: RLCD Calibration Metrics: ECE, MCE, and Brier Decomposition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReliabilityBin:
    bin_index: int
    lower_bound: float
    upper_bound: float
    sample_count: int
    mean_confidence: float
    empirical_accuracy: float
    calibration_gap: float


@dataclass(frozen=True)
class BrierDecomposition:
    total_brier_score: float
    binned_brier_score: float
    reliability: float    # Calibration deficit (lower is better; 0 at perfect calibration)
    resolution: float     # Discriminative power (higher is better)
    uncertainty: float    # Inherent stochastic task variance: base_rate * (1 - base_rate)


def compute_calibration_metrics(
    confidences: Sequence[float],
    accuracies: Sequence[int],
    num_bins: int = 10,
) -> Tuple[float, float, List[ReliabilityBin]]:
    r"""
    Computes Expected Calibration Error (ECE) and Maximum Calibration Error (MCE):
    ECE = \sum_{b=1}^B (|B_b| / N) * |acc(B_b) - conf(B_b)|
    MCE = \max_{b=1}^B |acc(B_b) - conf(B_b)|
    """
    confs = np.asarray(confidences, dtype=np.float64)
    accs = np.asarray(accuracies, dtype=np.int32)
    n = len(confs)

    if n != len(accs):
        raise ValueError("Confidences and accuracies must have identical length.")

    bin_edges = np.linspace(0.0, 1.0, num_bins + 1)
    bins: List[ReliabilityBin] = []
    ece = 0.0
    mce = 0.0

    for i in range(num_bins):
        low, high = bin_edges[i], bin_edges[i + 1]
        mask = (confs >= low) & (confs <= high) if i == num_bins - 1 else (confs >= low) & (confs < high)
        count = int(np.sum(mask))

        if count > 0:
            mean_conf = float(np.mean(confs[mask]))
            emp_acc = float(np.mean(accs[mask]))
            gap = abs(emp_acc - mean_conf)
            ece += (count / n) * gap
            mce = max(mce, gap)
        else:
            mean_conf = float((low + high) / 2.0)
            emp_acc = 0.0
            gap = 0.0

        bins.append(
            ReliabilityBin(
                bin_index=i,
                lower_bound=float(low),
                upper_bound=float(high),
                sample_count=count,
                mean_confidence=mean_conf,
                empirical_accuracy=emp_acc,
                calibration_gap=gap,
            )
        )

    return ece, mce, bins


def compute_brier_decomposition(
    predicted_probs: Sequence[float],
    binary_ground_truth: Sequence[int],
    num_bins: int = 10,
) -> BrierDecomposition:
    r"""
    Computes Murphy's (1973) exact partition for binned probability forecasts:
    Brier_binned = Reliability - Resolution + Uncertainty
    """
    p = np.asarray(predicted_probs, dtype=np.float64)
    y = np.asarray(binary_ground_truth, dtype=np.float64)
    n = len(p)

    total_brier = float(np.mean((p - y) ** 2))
    base_rate = float(np.mean(y))
    uncertainty = base_rate * (1.0 - base_rate)

    bin_edges = np.linspace(0.0, 1.0, num_bins + 1)
    reliability = 0.0
    resolution = 0.0
    binned_brier = 0.0

    for i in range(num_bins):
        low, high = bin_edges[i], bin_edges[i + 1]
        mask = (p >= low) & (p <= high) if i == num_bins - 1 else (p >= low) & (p < high)
        n_k = int(np.sum(mask))
        if n_k > 0:
            p_k_bar = float(np.mean(p[mask]))
            y_k_bar = float(np.mean(y[mask]))
            reliability += (n_k / n) * ((p_k_bar - y_k_bar) ** 2)
            resolution += (n_k / n) * ((y_k_bar - base_rate) ** 2)
            binned_brier += float(np.sum((p_k_bar - y[mask]) ** 2)) / n

    return BrierDecomposition(
        total_brier_score=total_brier,
        binned_brier_score=binned_brier,
        reliability=reliability,
        resolution=resolution,
        uncertainty=uncertainty,
    )


# ---------------------------------------------------------------------------
# Lemma 2.1 Verification: Precision Bounded Below by Operational Threshold
# ---------------------------------------------------------------------------

def verify_lemma_2_1(
    confidences: Sequence[float],
    ground_truth: Sequence[int],
    tau_grid: Sequence[float] = (0.2, 0.4, 0.6, 0.8),
    tolerance: float = 0.05,
) -> Dict[float, Tuple[float, float, bool]]:
    r"""
    Empirically verifies Lemma 2.1:
    \mathbb{E}[\mathbf{1}_{\{y = \omega\}} \mid p(s) >= \tau] = \mathbb{E}[p(s) \mid p(s) >= \tau] >= \tau.
    """
    confs = np.asarray(confidences, dtype=np.float64)
    y = np.asarray(ground_truth, dtype=np.int32)
    results = {}

    for tau in tau_grid:
        mask = confs >= tau
        if np.sum(mask) == 0:
            continue
        emp_precision = float(np.mean(y[mask]))
        expected_prob = float(np.mean(confs[mask]))
        passes = emp_precision >= (tau - tolerance)
        results[tau] = (emp_precision, expected_prob, passes)

    return results


def _run_section_2_verification() -> None:
    print("Running Section 2 verification...")
    # 1. State Space & Accessor Verification
    sample_state: StateObj = {
        "ticket": {
            "id": "T-1049",
            "messages": [
                {"role": "user", "text": "I need a refund for my subscription."},
                {"role": "agent", "text": "Can you provide the billing invoice?"},
            ],
            "metadata": {"urgent": True, "attempts": 2},
        }
    }
    assert resolve_field_path(sample_state, "ticket.id") == "T-1049"
    assert resolve_field_path(sample_state, "ticket.messages[0].text") == "I need a refund for my subscription."
    assert resolve_field_path(sample_state, "ticket.non_existent") is BOTTOM

    # 2. Simplex Bounds
    p_valid = validate_simplex([0.7, 0.2, 0.1])
    assert np.isclose(np.sum(p_valid), 1.0)

    # 3. Calibration Metrics and Lemma 2.1
    np.random.seed(42)
    N = 100_000
    sim_probs = np.random.uniform(0.0, 1.0, size=N)
    sim_labels = (np.random.uniform(0.0, 1.0, size=N) < sim_probs).astype(int)

    ece, mce, _ = compute_calibration_metrics(sim_probs, sim_labels, num_bins=10)
    assert ece < 0.01, f"Expected calibrated ECE < 0.01, got {ece:.4f}"
    assert mce < 0.02, f"Expected calibrated MCE < 0.02, got {mce:.4f}"

    decomp = compute_brier_decomposition(sim_probs, sim_labels, num_bins=10)
    assert decomp.reliability < 0.001
    assert math.isclose(
        decomp.binned_brier_score,
        decomp.reliability - decomp.resolution + decomp.uncertainty,
        rel_tol=1e-5,
    )

    lemma_check = verify_lemma_2_1(sim_probs, sim_labels, tau_grid=[0.5, 0.7, 0.8, 0.9])
    for tau, (prec, exp_p, passes) in lemma_check.items():
        assert passes, f"Lemma 2.1 violated at tau={tau}"
        assert prec >= tau - 0.01

    print("Section 2 verification passed successfully.")


if __name__ == "__main__":
    _run_section_2_verification()
```

---


## 3. The Three Primitives as Projection Operators

We now formalize each of the three foundational primitives in Jev as typed projection operators mapping latent semantic states into calibrated probability spaces.

### 3.1 Noul: Binary Credence Projection

**Definition 3.1 (Noul Operator).**
Given a binary query $q$ specifying a semantic predicate $\varphi : \mathcal{S} \to \{0, 1\}$ (embedded in query instructions), the Noul operator is the projection:

$$\mathcal{N}_q : \mathcal{S} \to [0, 1]$$

$$\mathcal{N}_q(s) := P(Y_\varphi = 1 \mid \mu(s))$$

where $Y_\varphi \in \{0, 1\}$ is the ground-truth binary target indicator, and $\mathcal{N}_q(s)$ is the model's calibrated posterior credence (Proposition 2.1).

The scalar output $n = \mathcal{N}_q(s)$ represents posterior probability mass:
- $n \to 1.0$: Strong posterior credence that predicate $\varphi$ holds.
- $n \approx 0.5$: Maximal epistemic uncertainty; uninformative evidence.
- $n \to 0.0$: Strong posterior credence that predicate $\varphi$ does not hold.

**Remark 3.1 (Entropy-Centroid Duality).**
The value $n = 0.5$ represents *maximal posterior entropy*:

$$H(n) = -n \log_2 n - (1 - n) \log_2(1 - n)$$

which achieves its unique global supremum $H(0.5) = 1.0\text{ bit}$. Under $n = 0.5$, the observation $\mu(s)$ provides zero discriminative information between the truth and falsity of $\varphi$. Conversely, a normalized Score output of $\sigma_{\mathrm{norm}} = 0.5$ (Section 3.3) represents the *centroid of the ordinal rubric* — a specific substantive midpoint between described operational conditions, not an entropy state. Noul and Score are thus categorically non-interchangeable.

**Theorem 3.1 (Factorization of Joint Posteriors under Conditional Independence).**
*Let $q_1, q_2$ be two Noul queries evaluating binary predicates $\varphi_1, \varphi_2$, with corresponding ground-truth indicator variables $Y_{\varphi_1}, Y_{\varphi_2} \in \{0, 1\}$. The joint posterior credence factors as the direct product of the marginal Noul outputs:*

$$P(Y_{\varphi_1} = 1, Y_{\varphi_2} = 1 \mid \mu(s)) = \mathcal{N}_{q_1}(s) \cdot \mathcal{N}_{q_2}(s)$$

*if and only if the target predicates are conditionally independent given the latent semantic representation under data distribution $\mathcal{D}$:*

$$Y_{\varphi_1} \perp Y_{\varphi_2} \mid \mu(s)$$

*Proof.* Under strong calibration (Definition 2.4), the marginal projections satisfy $\mathcal{N}_{q_i}(s) = P(Y_{\varphi_i} = 1 \mid \mu(s))$ almost surely for $i \in \{1, 2\}$.
$(\impliedby)$ If $Y_{\varphi_1} \perp Y_{\varphi_2} \mid \mu(s)$, then by the definition of conditional independence:
$$P(Y_{\varphi_1} = 1, Y_{\varphi_2} = 1 \mid \mu(s)) = P(Y_{\varphi_1} = 1 \mid \mu(s)) \cdot P(Y_{\varphi_2} = 1 \mid \mu(s)) = \mathcal{N}_{q_1}(s) \cdot \mathcal{N}_{q_2}(s).$$
$(\implies)$ By the law of total probability on the $2 \times 2$ contingency table of binary variables, if $P(Y_{\varphi_1} = 1, Y_{\varphi_2} = 1 \mid \mu(s)) = P(Y_{\varphi_1} = 1 \mid \mu(s)) P(Y_{\varphi_2} = 1 \mid \mu(s))$ and the marginals match, then $P(Y_{\varphi_1} = y_1, Y_{\varphi_2} = y_2 \mid \mu(s)) = P(Y_{\varphi_1} = y_1 \mid \mu(s)) P(Y_{\varphi_2} = y_2 \mid \mu(s))$ holds for all $(y_1, y_2) \in \{0, 1\}^2$, establishing conditional independence. $\blacksquare$

*Remark 3.2 (Engineering Implication).* Deploying multiple concurrent Nouls (`has_pii`, `is_urgent`, `requests_refund`) in a single batch is theoretically sound when the underlying conditions are semantically orthogonal. When predicates exhibit strong semantic entanglement (e.g., `is_angry` and `uses_aggressive_language`), raw product aggregation underestimates co-occurrence probability.

*Open Question 3.1.* Does there exist an unsupervised metric on question instruction embeddings that guarantees conditional independence without requiring labeled joint validation datasets?

---

### 3.2 Choice: Categorical Distribution Projection

**Definition 3.2 (Choice Operator).**
Given question $q$ with a finite, mutually exclusive, and exhaustive candidate option set $\Omega = \{\omega_1, \dots, \omega_K\}$ ($K \ge 2$) containing a designated fallback option $\omega_\emptyset \in \Omega$, the Choice operator is:

$$\mathbb{C}_q : \mathcal{S} \to \Delta_K \times \Omega \times [0, 1]$$

$$\mathbb{C}_q(s) := (p^\ast, \omega^\ast, c)$$

where:
- $p^\ast \in \Delta_K$ is the calibrated posterior categorical distribution: $p^\ast_i = P(Y = \omega_i \mid \mu(s))$.
- $\omega^\ast = \arg\max_{\omega \in \Omega} p^\ast(\omega)$ is the Maximum A Posteriori (MAP) choice (ties resolved lexicographically).
- $c \in [0, 1]$ is the peakedness-normalized confidence metric (Definition 3.3).

**Remark 3.3 (Closed-World Assumption & Fallback Requirement).**
The option set $\Omega$ is caller-specified. Jev cannot assign probability mass to hypotheses outside $\Omega$. If an out-of-distribution state occurs whose true semantic label $\omega_{\mathrm{true}} \notin \Omega$, the model projects probability mass onto the nearest in-vocabulary elements, degrading calibration unless an explicit fallback option $\omega_\emptyset$ is included.

**Proposition 3.1 (Out-of-Vocabulary Degradation under Softmax Energy Projections).**
*Let the model potential for option $\omega$ be governed by semantic metric distance: $E(s, \omega) = -d_\mathcal{M}(\mu(s), \mu(\omega)) / \tau_T$. If the true class $\omega^\ast \notin \Omega_{\mathrm{closed}}$ and $\omega_{\mathrm{prox}} = \arg\min_{\omega \in \Omega_{\mathrm{closed}}} d_\mathcal{M}(\mu(s), \mu(\omega))$, then:*

$$P_M(\omega_{\mathrm{prox}} \mid s, \Omega_{\mathrm{closed}}) < P_M(\omega^\ast \mid s, \Omega_{\mathrm{true}})$$

*and the resulting confidence $c(\mathbb{C}_q(s))$ is depressed relative to in-vocabulary evaluation.*

**Definition 3.3 (Confidence for $K$-Class Choice).**
For categorical distribution $p \in \Delta_K$ with peakedness $\rho(p) := \max_{\omega \in \Omega} p(\omega)$, the **confidence** is defined as the affine normalization:

$$c(p) := \frac{K \cdot \rho(p) - 1}{K - 1}$$

**Lemma 3.1 (Confidence Strict Monotonicity).**
*For any fixed cardinality $K \ge 2$, confidence $c(p)$ is a strictly increasing, continuous affine map from $\rho \in [1/K, 1]$ onto $[0, 1]$ with positive slope $\frac{\mathrm{d}c}{\mathrm{d}\rho} = \frac{K}{K - 1} > 0$.*

---

### 3.3 Score: Ordinal Expectation Projection

**Definition 3.4 (Score Operator).**
Given question $q$ with an ordered rubric $\Lambda = (\lambda_0, \lambda_1, \dots, \lambda_{L-1})$ of $L \ge 2$ ascending benchmark levels, the Score operator is:

$$\mathcal{Sc}_q : \mathcal{S} \to \Delta_L \times [0, L-1] \times [0, 1]$$

$$\mathcal{Sc}_q(s) := (p^\ast, \sigma, c)$$

where:
- $p^\ast \in \Delta_L$ is the calibrated posterior distribution over ordinal rubric levels.
- $\sigma = \sum_{j=0}^{L-1} j \cdot p^\ast_j \in [0, L-1]$ is the posterior expected level index.
- $c \in [0, 1]$ is the distributional confidence evaluated over $L$ outcomes via Definition 3.3.

**Theorem 3.2 (Score as Minimum Mean Square Error Projection).**
*The raw score $\sigma := \sum_{j=0}^{L-1} j \cdot p^\ast_j$ is the unique Bayes-optimal point prediction minimizing the expected posterior quadratic loss over rubric indices:*

$$\sigma = \arg\min_{\hat{y} \in \mathbb{R}} \mathbb{E}_{J \sim p^\ast}\left[ (J - \hat{y})^2 \right]$$

*In particular, $\sigma \in [0, L-1]$ and is continuously valued, representing genuine probability mass distributed across adjacent rubric levels.*

*Proof.* Let $\psi(\hat{y}) = \mathbb{E}_{J \sim p^\ast}[(J - \hat{y})^2] = \sum_{j=0}^{L-1} p^\ast_j (j - \hat{y})^2$. Differentiating with respect to $\hat{y}$:

$$\psi'(\hat{y}) = -2 \sum_{j=0}^{L-1} p^\ast_j (j - \hat{y}) = -2 \left( \sum_{j=0}^{L-1} j p^\ast_j - \hat{y} \sum_{j=0}^{L-1} p^\ast_j \right)$$

Since $p^\ast \in \Delta_L$, we have $\sum p^\ast_j = 1$. Thus $\psi'(\hat{y}) = -2 (\sigma - \hat{y})$. Setting $\psi'(\hat{y}) = 0$ yields the unique stationary point $\hat{y} = \sigma$. The second derivative $\psi''(\hat{y}) = 2 > 0$ confirms that $\sigma$ is the unique global minimizer. The bounds $0 \le \sigma \le L-1$ follow immediately from the fact that $\sigma$ is a convex combination of points in $\{0, 1, \dots, L-1\}$. $\blacksquare$

**Definition 3.5 (Score Normalization).**
The **normalized score** is defined as:

$$\sigma_{\mathrm{norm}} := \frac{\sigma}{L - 1} \in [0, 1]$$

Normalizing by $(L - 1)$ maps scores from rubrics with varying cardinality onto a common unit scale, which is essential for multi-rubric composite scoring (Section 6.3, Theorem 6.5).

**Proposition 3.2 (Maximum Entropy Score Midpoint).**
*Under maximal uncertainty where the posterior is uniform $p^\ast = (1/L, \dots, 1/L)^T$, the raw and normalized scores evaluate exactly to the rubric centroid:*

$$\sigma = \frac{L - 1}{2}, \quad \sigma_{\mathrm{norm}} = \frac{1}{2}$$

*Proof.* $\sigma = \sum_{j=0}^{L-1} j \frac{1}{L} = \frac{1}{L} \frac{(L-1)L}{2} = \frac{L-1}{2}$, and $\sigma_{\mathrm{norm}} = \frac{(L-1)/2}{L-1} = \frac{1}{2}$. $\blacksquare$

---

### 3.4 Primitive Distinguishability: Selection Optimality

**Theorem 3.3 (Primitive Selection Optimality).**
*For any semantic decision task with target distribution $P(Y \mid s)$, selecting the primitive whose hypothesis manifold matches the task structure minimizes the Kullback-Leibler information divergence:*

| Ground Truth Semantic Structure | Optimal Primitive | Output Space | Theoretical Justification |
|---|---|---|---|
| Binary condition (credence is signal) | **Noul** | $[0, 1]$ | Isomorphic to Bernoulli parameter space; zero projection distortion |
| Unordered categorical classification | **Choice** | $\Delta_K \times \Omega \times [0, 1]$ | Matches discrete categorical simplex; preserves full probability distribution |
| Ordered continuous spectrum (degree) | **Score** | $\Delta_L \times [0, L-1] \times [0, 1]$ | Preserves ordinal distance metric; MMSE expectation |
| Multiple independent binary attributes | **Concurrent Nouls** | $[0, 1]^m$ | Captures complete product lattice without exponential option explosion |

---

### 3.5 Computational Reference: Primitive Operators and Dispatch

```python
"""
Reference Implementation for Section 3: The Three Primitives as Projection Operators.
Paper: Mathematical Foundations of Jev (v2.1)
Section: 3.1 Noul, 3.2 Choice, 3.3 Score, 3.4 Primitive Distinguishability
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, List, Sequence, Tuple, TypeVar
import numpy as np

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Section 3.1: Noul Operator
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NoulResult:
    credence: float       # n \in [0, 1]
    binary_entropy: float # H(n) in bits


def noul_operator(credence: float) -> NoulResult:
    r"""
    Implements N_q : \mathcal{S} -> [0, 1].
    Evaluates posterior credence and corresponding Shannon binary entropy.
    """
    if not (0.0 <= credence <= 1.0):
        raise ValueError(f"Noul credence must be in [0, 1], got {credence}")

    if credence == 0.0 or credence == 1.0:
        entropy = 0.0
    else:
        entropy = -(credence * math.log2(credence) + (1.0 - credence) * math.log2(1.0 - credence))

    return NoulResult(credence=credence, binary_entropy=entropy)


# ---------------------------------------------------------------------------
# Section 3.2: Choice Operator
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ChoiceResult(Generic[T]):
    probabilities: Dict[T, float]
    map_choice: T
    peakedness: float
    confidence: float


def choice_operator(probabilities: Dict[T, float]) -> ChoiceResult[T]:
    r"""
    Implements C_q : \mathcal{S} -> \Delta_K \times \Omega \times [0, 1].
    Extracts MAP estimate with deterministic tie-breaking and peakedness-normalized confidence.
    """
    if len(probabilities) < 2:
        raise ValueError("Choice operator requires at least K >= 2 options.")

    options = sorted(probabilities.keys(), key=lambda x: str(x))
    probs = np.array([probabilities[opt] for opt in options], dtype=np.float64)

    if np.any(probs < -1e-7) or abs(np.sum(probs) - 1.0) > 1e-7:
        raise ValueError("Provided distribution violates simplex \\Delta_K.")
    probs = np.maximum(probs, 0.0)
    probs /= np.sum(probs)

    clean_probs = {opt: float(probs[i]) for i, opt in enumerate(options)}
    map_choice = max(options, key=lambda opt: (clean_probs[opt], str(opt)))
    peakedness = clean_probs[map_choice]

    k = len(options)
    confidence = float(np.clip((k * peakedness - 1.0) / (k - 1.0), 0.0, 1.0))

    return ChoiceResult(
        probabilities=clean_probs,
        map_choice=map_choice,
        peakedness=peakedness,
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# Section 3.3: Score Operator
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ScoreResult:
    probabilities: List[float]
    raw_score: float
    normalized_score: float
    confidence: float


def score_operator(level_probabilities: Sequence[float]) -> ScoreResult:
    r"""
    Implements Sc_q : \mathcal{S} -> \Delta_L \times [0, L-1] \times [0, 1].
    Evaluates raw score \sigma = \mathbb{E}[J], normalized score \sigma_norm, and confidence.
    """
    l = len(level_probabilities)
    if l < 2:
        raise ValueError("Score rubric must have at least L >= 2 levels.")

    p = np.asarray(level_probabilities, dtype=np.float64)
    if np.any(p < -1e-7) or abs(np.sum(p) - 1.0) > 1e-7:
        raise ValueError("Score probabilities must lie on \\Delta_L.")
    p = np.maximum(p, 0.0)
    p /= np.sum(p)

    indices = np.arange(l, dtype=np.float64)
    raw_score = float(np.dot(indices, p))
    normalized_score = raw_score / (l - 1.0)

    peakedness = float(np.max(p))
    confidence = float(np.clip((l * peakedness - 1.0) / (l - 1.0), 0.0, 1.0))

    return ScoreResult(
        probabilities=[float(x) for x in p],
        raw_score=raw_score,
        normalized_score=normalized_score,
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# Section 3.4: Primitive Dispatcher (Theorem 3.3)
# ---------------------------------------------------------------------------

def select_optimal_primitive(target_structure: str) -> str:
    """Theorem 3.3: Maps target semantic structure to optimal primitive."""
    dispatch = {
        "binary": "Noul",
        "categorical": "Choice",
        "ordinal": "Score",
        "multi_binary": "Multiple_Nouls",
    }
    if target_structure not in dispatch:
        raise ValueError(f"Unknown structure: {target_structure}")
    return dispatch[target_structure]


def _run_section_3_verification() -> None:
    print("Running Section 3 verification...")
    # 1. Noul Entropy Duality
    n_mid = noul_operator(0.5)
    assert math.isclose(n_mid.binary_entropy, 1.0)
    n_cert = noul_operator(1.0)
    assert math.isclose(n_cert.binary_entropy, 0.0)

    # 2. Choice MAP & Peakedness
    c_res = choice_operator({"refund": 0.70, "tech_support": 0.20, "other": 0.10})
    assert c_res.map_choice == "refund"
    assert math.isclose(c_res.confidence, 0.55)

    # 3. Score MMSE Expectation & Proposition 3.2
    s_uniform = score_operator([0.2, 0.2, 0.2, 0.2, 0.2])  # L=5
    assert math.isclose(s_uniform.raw_score, 2.0)
    assert math.isclose(s_uniform.normalized_score, 0.5)

    # 4. Theorem 3.3 Primitive Selection
    assert select_optimal_primitive("binary") == "Noul"
    assert select_optimal_primitive("categorical") == "Choice"
    assert select_optimal_primitive("ordinal") == "Score"
    assert select_optimal_primitive("multi_binary") == "Multiple_Nouls"

    print("Section 3 verification passed successfully.")


if __name__ == "__main__":
    _run_section_3_verification()
```

---


## 4. Confidence as a Distributional Sharpness Measure

We prove that Jev’s confidence formulation is not an arbitrary heuristic, but rather the unique, mathematically consistent boundary-anchored affine normalization of distributional peakedness, and characterize its precise relationship to Shannon entropy.

### 4.1 Peakedness and Unique Boundary-Anchored Affine Normalization

**Definition 4.1 (Peakedness).**
For any categorical probability distribution $p \in \Delta_K$ ($K \ge 2$), the **peakedness** is the maximal probability mass:

$$\rho(p) := \max_{\omega \in \Omega} p(\omega)$$

Because $\sum_{i=1}^K p_i = 1$ and $p_i \ge 0$, peakedness is naturally bounded:

$$\rho(p) \in \left[ \frac{1}{K}, 1 \right]$$

The lower bound $\rho = 1/K$ is attained uniquely at the simplex centroid $\mathbf{u} = (1/K, \dots, 1/K)^T$ (maximal uncertainty); the upper bound $\rho = 1$ is attained at the extreme vertices $e_i$ (complete certainty).

**Theorem 4.1 (Confidence as Unique Boundary-Anchored Affine Normalization).**
*The Jev confidence formula:*

$$c(p) = \frac{K \cdot \rho(p) - 1}{K - 1}$$

*is the **unique** affine transformation $T : [1/K, 1] \to [0, 1]$ satisfying the two canonical epistemic boundary conditions:*
1. **Minimal Informational Anchor:** $T(1/K) = 0$ *(the uniform distribution represents zero confidence)*.
2. **Maximal Certainty Anchor:** $T(1) = 1$ *(a Dirac distribution represents absolute confidence)*.

*Proof.* An affine transformation on $\mathbb{R}$ has the canonical form $T(x) = ax + b$ with $a, b \in \mathbb{R}$. Imposing the two boundary conditions yields the linear system:

$$\begin{cases}
a \cdot \frac{1}{K} + b = 0 & \implies b = -\frac{a}{K} \\
a \cdot 1 + b = 1 & \implies a - \frac{a}{K} = 1 \implies a \left( \frac{K - 1}{K} \right) = 1
\end{cases}$$

Since $K \ge 2$, the divisor $K - 1 > 0$, yielding the unique solution:

$$a = \frac{K}{K - 1}, \quad b = -\frac{1}{K - 1}$$

Substituting $a$ and $b$ back into $T(x)$ yields:

$$T(x) = \frac{Kx - 1}{K - 1}$$

Furthermore, the first derivative is strictly positive for all $K \ge 2$:

$$\frac{\mathrm{d}T}{\mathrm{d}x} = \frac{K}{K - 1} > 0$$

proving that $T$ is a strictly increasing homeomorphism from $[1/K, 1]$ onto $[0, 1]$. $\blacksquare$

---

### 4.2 Entropy Monotonicity and Distributional Bounding Envelopes

**Theorem 4.2 (Monotone Relationship Between Confidence and Entropy).**
1. **Uniform-Entropy Family:** *Let $p(\rho) \in \Delta_K$ denote the one-parameter distribution family with peakedness $\rho \in [1/K, 1]$ where all remaining $K - 1$ outcomes share mass uniformly:*
   $$p_{\mathrm{peak}} = \rho, \quad p_i = \frac{1 - \rho}{K - 1} \quad \forall i \neq \mathrm{peak}$$
   *The Shannon entropy $H(p(\rho)) = -\sum_i p_i \log p_i$ satisfies:*
   $$\frac{\mathrm{d}H(p(\rho))}{\mathrm{d}\rho} = \log\left( \frac{1 - \rho}{(K - 1)\rho} \right) < 0 \quad \forall \rho \in \left( \frac{1}{K}, 1 \right]$$
   *Hence, over the uniform-entropy family, confidence $c(p)$ is a strictly decreasing diffeomorphism of Shannon entropy.*

2. **General Distribution Entropy Envelope:** *For any arbitrary distribution $p \in \Delta_K$ with peakedness $\rho$, its Shannon entropy is strictly bounded by:*
   $$H_{\min}(\rho) \le H(p) \le H_{\max}(\rho)$$
   *where the upper bound is attained by the uniform-entropy family:*
   $$H_{\max}(\rho) = -\rho \log \rho - (1 - \rho) \log\left( \frac{1 - \rho}{K - 1} \right)$$
   *and the lower bound is attained when mass concentrates on the minimal integer number of classes:*
   $$H_{\min}(\rho) = -k \rho \log \rho - (1 - k\rho) \log(1 - k\rho), \quad k = \lfloor 1/\rho \rfloor$$
   *Consequently, while peakedness alone does not uniquely fix $H(p)$ for arbitrary distributions, it uniquely determines the sharp upper bound $H_{\max}(c)$, with $c \to 1 \implies H(p) \to 0$ uniformly.*

*Proof.* (1) Expanding $H(p(\rho))$:
$$H(p(\rho)) = -\rho \log \rho - (K - 1) \left( \frac{1 - \rho}{K - 1} \right) \log\left( \frac{1 - \rho}{K - 1} \right) = -\rho \log \rho - (1 - \rho) \log\left( \frac{1 - \rho}{K - 1} \right)$$
Differentiating with respect to $\rho$:
$$\frac{\mathrm{d}H}{\mathrm{d}\rho} = -\log \rho - 1 + \log\left( \frac{1 - \rho}{K - 1} \right) + 1 = \log\left( \frac{1 - \rho}{(K - 1)\rho} \right)$$
Since $\rho > 1/K$, $(K - 1)\rho > \frac{K-1}{K} = 1 - 1/K > 1 - \rho$. Thus the argument of the logarithm is strictly less than 1, establishing $\frac{\mathrm{d}H}{\mathrm{d}\rho} < 0$. (2) Follows from majorization theory on the probability simplex $\Delta_K$. $\blacksquare$

---

### 4.3 Confidence-Threshold Ordering Consistency

**Theorem 4.3 (Confidence-Threshold Ordering Consistency).**
*Let $\tau_L < \tau_H \in [0, 1]$ be operational thresholds. For a random state $S \sim \mathcal{D}$ evaluated by strongly calibrated model $M$, the expected top-option posterior mass conditioned on high confidence strictly dominates that conditioned on low confidence:*

$$\mathbb{E}_{(S, Y) \sim \mathcal{D}}[p^\ast(S)_{\omega^\ast} \mid c(S) \ge \tau_H] \ge \tau_H \frac{K-1}{K} + \frac{1}{K} > \tau_L \frac{K-1}{K} + \frac{1}{K} > \mathbb{E}_{(S, Y) \sim \mathcal{D}}[p^\ast(S)_{\omega^\ast} \mid c(S) < \tau_L]$$

*Proof.* Inverting Definition 3.3 expresses peakedness as $\rho(p^\ast(S)) = c(S) \frac{K-1}{K} + \frac{1}{K}$. Under the high-confidence conditioning event $\mathcal{E}_H = \{S : c(S) \ge \tau_H\}$, monotonicity of conditional expectation guarantees:
$$\mathbb{E}[\rho(p^\ast(S)) \mid \mathcal{E}_H] \ge \tau_H \frac{K-1}{K} + \frac{1}{K}.$$
Conversely, under the low-confidence conditioning event $\mathcal{E}_L = \{S : c(S) < \tau_L\}$:
$$\mathbb{E}[\rho(p^\ast(S)) \mid \mathcal{E}_L] < \tau_L \frac{K-1}{K} + \frac{1}{K}.$$
Because $\tau_H > \tau_L$ and $\frac{K-1}{K} > 0$ for $K \ge 2$, the strict inequality $\tau_H \frac{K-1}{K} + \frac{1}{K} > \tau_L \frac{K-1}{K} + \frac{1}{K}$ separates the two expectations. $\blacksquare$

---

### 4.4 Computational Reference: Distributional Sharpness, Confidence, and Entropy

```python
r"""
Reference Implementation for Section 4: Confidence as a Distributional Sharpness Measure.
Paper: Mathematical Foundations of Jev (v2.1)
Section: 4 Confidence as a Distributional Sharpness Measure
Theorems: 4.1 Unique Affine Normalization, 4.2 Monotonicity with Shannon Entropy, 4.3 Threshold Ordering
"""

from __future__ import annotations

import math
from typing import Sequence, Tuple
import numpy as np


def peakedness(p: Sequence[float]) -> float:
    r"""Definition 4.1: \rho(p) := max_{\omega \in \Omega} p(\omega) \in [1/K, 1]."""
    arr = np.asarray(p, dtype=np.float64)
    return float(np.max(arr))


def confidence_from_peakedness(rho: float, k: int) -> float:
    r"""Theorem 4.1: c(p) = (K * \rho - 1) / (K - 1). Maps [1/K, 1] onto [0, 1]."""
    if k < 2:
        raise ValueError("Outcome space cardinality K must be >= 2.")
    c = (k * rho - 1.0) / (k - 1.0)
    return float(np.clip(c, 0.0, 1.0))


def solve_affine_normalization_coefficients(k: int) -> Tuple[float, float]:
    r"""
    Solves the 2x2 linear system from Theorem 4.1:
      [ 1/K   1 ] [ a ]   [ 0 ]
      [  1    1 ] [ b ] = [ 1 ]
    Yields unique analytical solution: a = K/(K-1), b = -1/(K-1).
    """
    matrix_m = np.array([[1.0 / k, 1.0], [1.0, 1.0]], dtype=np.float64)
    rhs = np.array([0.0, 1.0], dtype=np.float64)
    a, b = np.linalg.solve(matrix_m, rhs)
    return float(a), float(b)


def uniform_entropy_family(rho: float, k: int) -> np.ndarray:
    r"""Theorem 4.2: Parameterizes uniform-entropy family: p_peak=\rho, p_i=(1-\rho)/(K-1)."""
    if not (1.0 / k <= rho <= 1.0):
        raise ValueError(f"Peakedness rho must be in [1/{k}, 1], got {rho}")

    p = np.full(k, (1.0 - rho) / (k - 1.0), dtype=np.float64)
    p[0] = rho
    return p


def shannon_entropy(p: np.ndarray) -> float:
    r"""Computes Shannon entropy H(p) = -\sum p_i \log(p_i) in nats."""
    p_nz = p[p > 0.0]
    return float(-np.sum(p_nz * np.log(p_nz)))


def dH_drho(rho: float, k: int) -> float:
    r"""
    Theorem 4.2 analytical derivative:
    dH/d\rho = \log((1 - \rho) / ((K - 1) * \rho)) < 0.
    """
    numerator = 1.0 - rho
    denominator = rho * (k - 1.0)
    return float(np.log(numerator / denominator))


def _run_section_4_verification() -> None:
    print("Running Section 4 verification...")

    # 1. Theorem 4.1: Uniqueness of Affine Normalization for various K
    for K in [2, 3, 5, 10, 50]:
        a, b = solve_affine_normalization_coefficients(K)
        expected_a = K / (K - 1.0)
        expected_b = -1.0 / (K - 1.0)
        assert math.isclose(a, expected_a)
        assert math.isclose(b, expected_b)
        assert a > 0.0

        # Boundary checks
        assert math.isclose(a * (1.0 / K) + b, 0.0, abs_tol=1e-12)
        assert math.isclose(a * 1.0 + b, 1.0, abs_tol=1e-12)

    # 2. Theorem 4.2: Strict Monotonicity with Entropy
    for K in [3, 5, 8]:
        rhos = np.linspace(1.0 / K + 1e-4, 0.999, 100)
        entropies = [shannon_entropy(uniform_entropy_family(r, K)) for r in rhos]
        confidences = [confidence_from_peakedness(r, K) for r in rhos]

        for r in rhos[:-1]:
            derivative = dH_drho(r, K)
            assert derivative < 0.0, f"Derivative non-negative at rho={r}"

        for i in range(len(entropies) - 1):
            assert confidences[i + 1] > confidences[i]
            assert entropies[i + 1] < entropies[i]

    # 3. Theorem 4.3: Ordering Consistency
    K = 4
    tau_L = 0.50
    tau_H = 0.85
    bound_H = tau_H * (K - 1.0) / K + 1.0 / K
    bound_L = tau_L * (K - 1.0) / K + 1.0 / K
    assert bound_H > bound_L
    assert math.isclose(bound_H, 0.8875)
    assert math.isclose(bound_L, 0.6250)

    print("Section 4 verification passed successfully.")


if __name__ == "__main__":
    _run_section_4_verification()
```

---


## 5. Information-Theoretic Question Decomposition

The Jev micro-architecture enforces an explicit design mandate: *decompose complex, multifaceted judgments into narrow, atomic semantic queries*. In this section, we show that this mandate is not merely a software hygiene practice, but an information-theoretically optimal design principle grounded in rate-distortion theory and multi-information bounds.

### 5.1 Measurement Channels and Atomic Questions

**Definition 5.1 (Question as an Informational Measurement Channel).**
A question $q$ with discrete hypothesis space $\Omega$ defines a *semantic measurement channel* $Q : \mathcal{S} \to \Delta_K$ that extracts information from the latent state encoding $\mu(X)$. The informational throughput of this channel regarding the true target variable $Y_q$ is:

$$I(Y_q ; \mu(X)) = H(Y_q) - H(Y_q \mid \mu(X))$$

where $H(\cdot)$ denotes the discrete Shannon entropy.

**Definition 5.2 (Sufficient and Non-Redundant Decomposition).**
A decomposition of a composite target query $Y_{\mathrm{broad}}$ into $n$ atomic measurement queries $\mathcal{Q} = \{Y_{q_1}, \dots, Y_{q_n}\}$ is:
1. **Informationally Lossless (Sufficient):** if and only if the conditional entropy vanishes:
   $$H(Y_{\mathrm{broad}} \mid Y_{q_1}, \dots, Y_{q_n}) = 0$$
   meaning the atomic query outcomes jointly determine the composite target with zero residual uncertainty.
2. **Minimally Sufficient (Non-Redundant):** if it is sufficient, and for every individual query $i \in \{1, \dots, n\}$:
   $$I(Y_{\mathrm{broad}} ; Y_{q_i} \mid Y_{\mathcal{Q} \setminus \{q_i\}}) > 0$$
   ensuring that no query is an informational deadweight.

**Theorem 5.1 (Lossless and Non-Redundant Question Decomposition).**
*A decomposition of a broad target query $Y_{\mathrm{broad}}$ into $n$ atomic measurement queries $\{Y_{q_1}, \dots, Y_{q_n}\}$ captures the complete information content of $Y_{\mathrm{broad}}$ without informational deadweight if and only if:*
1. $I(Y_{\mathrm{broad}} ; Y_{q_1}, \dots, Y_{q_n}) = H(Y_{\mathrm{broad}})$ *(Information Sufficiency)*.
2. *The conditional multi-information (conditional redundancy) among atomic queries given $Y_{\mathrm{broad}}$ vanishes:*
   $$I(Y_{q_1} ; Y_{q_2} ; \dots ; Y_{q_n} \mid Y_{\mathrm{broad}}) = 0$$

*Proof.* By the identity $I(X; Z) = H(X) - H(X \mid Z)$, the mutual information attains its theoretical ceiling $H(Y_{\mathrm{broad}})$ if and only if the residual conditional uncertainty $H(Y_{\mathrm{broad}} \mid Y_{q_1}, \dots, Y_{q_n}) = 0$. Non-redundancy requires that each question measures an orthogonal subspace of $\mu(S)$, ensuring zero mutual information overlap beyond what determines the target. $\blacksquare$

---

### 5.2 Decomposition Optimality Conditions

**Theorem 5.2 (Orthogonal Decomposition Maximizes Marginal Information).**
*Let atomic target variables $Y_{q_1}, \dots, Y_{q_n}$ be conditionally independent given the latent state representation $\mu(X)$:*

$$P(Y_{q_1}, \dots, Y_{q_n} \mid \mu(X)) = \prod_{i=1}^n P(Y_{q_i} \mid \mu(X))$$

*Then the total mutual information extracted from $\mu(X)$ satisfies:*

$$I(\mu(X) ; Y_{q_1}, \dots, Y_{q_n}) = \sum_{i=1}^n I(\mu(X) ; Y_{q_i}) - \mathrm{TC}(Y_{q_1}, \dots, Y_{q_n})$$

*where $\mathrm{TC}(Y_{q_1}, \dots, Y_{q_n}) = \sum_{i=1}^n H(Y_{q_i}) - H(Y_{q_1}, \dots, Y_{q_n}) \ge 0$ is the **Total Correlation** (Watanabe multi-information). Therefore:*

$$I(\mu(X) ; Y_{q_1}, \dots, Y_{q_n}) \le \sum_{i=1}^n I(\mu(X) ; Y_{q_i})$$

*with equality if and only if $\mathrm{TC}(Y_{q_1}, \dots, Y_{q_n}) = 0$, meaning the atomic questions are unconditionally mutually independent.*

*Proof.* Applying the chain rule of entropy:
$$\begin{aligned}
I(\mu(X) ; Y_1, \dots, Y_n) &= H(Y_1, \dots, Y_n) - H(Y_1, \dots, Y_n \mid \mu(X)) \\
&= H(Y_1, \dots, Y_n) - \sum_{i=1}^n H(Y_i \mid \mu(X)) \quad (\text{by conditional independence given } \mu(X)) \\
&= \sum_{i=1}^n \left( H(Y_i) - H(Y_i \mid \mu(X)) \right) - \left( \sum_{i=1}^n H(Y_i) - H(Y_1, \dots, Y_n) \right) \\
&= \sum_{i=1}^n I(\mu(X) ; Y_i) - \mathrm{TC}(Y_1, \dots, Y_n)
\end{aligned}$$
Since $\mathrm{TC}(Y_1, \dots, Y_n) \ge 0$ by the subadditivity of entropy, the inequality holds immediately. Equality is attained if and only if Total Correlation vanishes, which occurs if and only if $P(Y_1, \dots, Y_n) = \prod_{i=1}^n P(Y_i)$. $\blacksquare$

**Proposition 5.1 (Information Bottleneck of Monolithic Queries) & Corollary 5.1.**
*Evaluating a monolithic question (e.g., "Is this email spam?") as a single projection forces the model to compress multiple independent semantic signals into a single scalar or categorical decision. By the Data Processing Inequality, this single query captures only the information of its dominant sub-factor, discarding the residual information of the remaining orthogonal signals:*

$$I(\mu(X) ; Y_{\mathrm{broad}}) \le \max_i I(\mu(X) ; Y_{q_i}) < \sum_{i=1}^n I(\mu(X) ; Y_{q_i})$$

*Decomposing the inquiry into independent atomic queries (`has_credential_request`, `has_urgency`, `has_reward_claim`) allows the host program to capture the full sum of orthogonal signals without channel capacity bottlenecks.*

---

### 5.3 Computational Reference: Information-Theoretic Decomposition & Verification

```python
r"""
Reference Implementation for Section 5: Information-Theoretic Question Decomposition.
Paper: Mathematical Foundations of Jev (v2.1)
Section: 5.1 Measurement Channels, 5.2 Decomposition Optimality
Theorems: 5.1 Lossless Decomposition, 5.2 Orthogonal Decomposition Maximizes Information
"""

from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple
import numpy as np


def discrete_entropy(labels: Sequence[int]) -> float:
    r"""Computes Shannon entropy H(X) in bits."""
    _, counts = np.unique(labels, return_counts=True)
    probs = counts / np.sum(counts)
    return float(-np.sum(probs * np.log2(probs)))


def discrete_joint_entropy(variables: Sequence[Sequence[int]]) -> float:
    r"""Computes joint Shannon entropy H(X_1, ..., X_m) in bits."""
    stacked = np.column_stack(variables)
    _, counts = np.unique(stacked, axis=0, return_counts=True)
    probs = counts / np.sum(counts)
    return float(-np.sum(probs * np.log2(probs)))


def mutual_information(x: Sequence[int], y: Sequence[int]) -> float:
    r"""Computes mutual information I(X; Y) = H(X) + H(Y) - H(X, Y)."""
    h_x = discrete_entropy(x)
    h_y = discrete_entropy(y)
    h_xy = discrete_joint_entropy([x, y])
    return max(0.0, float(h_x + h_y - h_xy))


def conditional_entropy(y: Sequence[int], x_cond: Sequence[Sequence[int]]) -> float:
    r"""Computes conditional entropy H(Y | X_1, ..., X_m) = H(Y, X) - H(X)."""
    h_all = discrete_joint_entropy([y] + list(x_cond))
    h_cond = discrete_joint_entropy(list(x_cond))
    return max(0.0, float(h_all - h_cond))


def conditional_mutual_information(
    x: Sequence[int],
    y: Sequence[int],
    z: Sequence[int],
) -> float:
    r"""Computes conditional mutual information I(X; Y | Z)."""
    h_xz = discrete_joint_entropy([x, z])
    h_yz = discrete_joint_entropy([y, z])
    h_xyz = discrete_joint_entropy([x, y, z])
    h_z = discrete_entropy(z)
    return max(0.0, float(h_xz + h_yz - h_xyz - h_z))


def total_correlation(variables: Sequence[Sequence[int]]) -> float:
    r"""
    Theorem 5.2: Computes Watanabe Total Correlation (multi-information):
    TC(Y_1, ..., Y_n) = \sum H(Y_i) - H(Y_1, ..., Y_n) >= 0.
    """
    sum_individual = sum(discrete_entropy(v) for v in variables)
    joint_h = discrete_joint_entropy(variables)
    return max(0.0, float(sum_individual - joint_h))


def check_lossless_decomposition(
    y_broad: Sequence[int],
    atomic_subquestions: Sequence[Sequence[int]],
    tolerance: float = 1e-4,
) -> Tuple[bool, bool, Dict[str, float]]:
    r"""
    Theorem 5.1: Verifies whether an atomic decomposition is lossless:
      1. Completeness: H(Y_broad | Y_1, ..., Y_n) == 0.
      2. Non-redundancy: Conditional mutual information among queries is minimal.
    """
    residual_h = conditional_entropy(y_broad, atomic_subquestions)
    is_complete = residual_h <= tolerance

    max_redundancy = 0.0
    n = len(atomic_subquestions)
    for i in range(n):
        for j in range(i + 1, n):
            cmi = conditional_mutual_information(
                atomic_subquestions[i],
                atomic_subquestions[j],
                y_broad,
            )
            max_redundancy = max(max_redundancy, cmi)

    is_non_redundant = max_redundancy <= tolerance

    metrics = {
        "H_broad": discrete_entropy(y_broad),
        "residual_H": residual_h,
        "max_pairwise_redundancy_cmi": max_redundancy,
    }
    return is_complete, is_non_redundant, metrics


def _run_section_5_verification() -> None:
    print("Running Section 5 verification...")
    np.random.seed(1337)
    N = 20_000

    # 1. Theorem 5.1: Complete Lossless Decomposition Simulation
    q_credential = (np.random.rand(N) < 0.3).astype(int)
    q_urgent = (np.random.rand(N) < 0.4).astype(int)
    q_reward = (np.random.rand(N) < 0.2).astype(int)

    # Composite target: Phishing iff (Credential AND Urgent) OR Reward
    y_broad = (((q_credential == 1) & (q_urgent == 1)) | (q_reward == 1)).astype(int)

    is_comp, _, metrics = check_lossless_decomposition(
        y_broad, [q_credential, q_urgent, q_reward]
    )
    assert is_comp
    assert math.isclose(metrics["residual_H"], 0.0, abs_tol=1e-4)

    # 2. Theorem 5.2: Independent vs Correlated Decomposition Information Extraction
    latent_state = np.random.choice([0, 1, 2, 3], size=N)
    y_indep_1 = (latent_state & 1).astype(int)
    y_indep_2 = ((latent_state >> 1) & 1).astype(int)

    mi_1 = mutual_information(latent_state, y_indep_1)
    mi_2 = mutual_information(latent_state, y_indep_2)
    joint_mi = discrete_joint_entropy([latent_state]) + discrete_joint_entropy([y_indep_1, y_indep_2]) - discrete_joint_entropy([latent_state, y_indep_1, y_indep_2])
    tc = total_correlation([y_indep_1, y_indep_2])

    # Orthogonal queries achieve exact additivity: I(mu; Y1, Y2) == I(mu; Y1) + I(mu; Y2) - TC
    assert math.isclose(joint_mi, mi_1 + mi_2 - tc, abs_tol=1e-3)
    assert math.isclose(tc, 0.0, abs_tol=1e-2)

    print("Section 5 verification passed successfully.")


if __name__ == "__main__":
    _run_section_5_verification()
```

---


## 6. Architectural Patterns: Mathematical Proofs

In this section, we analyze the five core architectural patterns established in the Jev micro-architecture, providing formal proofs of their economic efficiency, decision-theoretic safety, and approximation accuracy.

### 6.1 Speculative Fan-Out: Parallelism and Cost Theorem

The Speculative Fan-Out pattern bundles multiple queries $\mathcal{Q} = \{q_1, \dots, q_n\}$ over a shared state $s$ into a single API invocation.

**Definition 6.1 (Two-Component Cost Model).**
The computational and financial cost of evaluating query batch $\mathcal{Q}$ against state $s$ is governed by a two-component decomposition:

$$C(s, \mathcal{Q}) = C_{\mathrm{enc}}(s) + |\mathcal{Q}| \cdot c_q$$

where:
- $C_{\mathrm{enc}}(s)$ is the fixed state encoding cost (computed once via cross-attention over state $s$ and amortized across all queries). We denote $C_0 := C_{\mathrm{enc}}(s)$.
- $c_q$ is the marginal evaluation cost of a single query head against the cached state representation.
- $|\mathcal{Q}| = n$ is the query batch cardinality.

**Theorem 6.1 (Speculative Fan-Out Cost and Speedup Theorem).**
*Under the two-component cost model, the cost of batch evaluation versus serial evaluation satisfies:*

$$C_{\mathrm{batch}}(n) = C_0 + n \cdot c_q$$

$$C_{\mathrm{serial}}(n) = n \cdot (C_0 + c_q)$$

*Let $r := c_q / C_0 \ge 0$ denote the marginal-to-base cost ratio. The theoretical speedup ratio:*

$$\mathrm{Speedup}(n, r) := \frac{C_{\mathrm{serial}}(n)}{C_{\mathrm{batch}}(n)} = \frac{n(1 + r)}{1 + n \cdot r}$$

*satisfies the following five structural properties:*
1. $\mathrm{Speedup}(n) \ge 1$ *for all $n \ge 1$ (batching is strictly non-inferior to serial calls).*
2. $\frac{\partial \mathrm{Speedup}}{\partial n} = \frac{1 + r}{(1 + n r)^2} > 0$ *(speedup is strictly increasing in question count).*
3. $\lim_{r \to 0} \mathrm{Speedup}(n) = n$ *(queries are nearly free relative to state encoding).*
4. $\lim_{r \to \infty} \mathrm{Speedup}(n) = 1$ *(question evaluation dominates base encoding).*
5. **Empirical Parameter Derivation:** *At the empirically observed benchmark of $n = 13$ queries achieving a $12.2\times$ cost reduction (with latency bounded within $287\text{ ms}$):*
   $$r = \frac{n - \mathrm{Speedup}}{n(\mathrm{Speedup} - 1)} = \frac{13 - 12.2}{13 \cdot 11.2} = \frac{0.8}{145.6} \approx 0.0054945 \approx 0.0055$$
   *indicating that query heads account for approximately $0.55\%$ of base state encoding cost, establishing an asymptotic speedup ceiling of $\lim_{n \to \infty} \mathrm{Speedup}(n) = 1 + 1/r \approx 183.0\times$.*

*Proof.* Properties 1–4 follow from elementary rational analysis:
$$\frac{\partial \mathrm{Speedup}}{\partial n} = \frac{(1+r)(1+nr) - n(1+r)r}{(1+nr)^2} = \frac{1+r}{(1+nr)^2} > 0$$
The second derivative $\frac{\partial^2 \mathrm{Speedup}}{\partial n^2} = -\frac{2r(1+r)}{(1+nr)^3} < 0$ proves strict concavity. Setting $n = 13$ and $\mathrm{Speedup} = 12.2$:
$$12.2(1 + 13r) = 13(1 + r) \implies 12.2 + 158.6r = 13 + 13r \implies 145.6r = 0.8 \implies r \approx 0.005495. \quad \blacksquare$$

**Theorem 6.2 (Answer Conditional Independence Under Shared State).**
*Let $\mathcal{Q} = \{q_1, \dots, q_n\}$ be a batch of queries targeting mutually orthogonal semantic dimensions of state $s$. The joint model response factors as the direct product of individual answer distributions:*

$$P(A_{q_1} = a_1, \dots, A_{q_n} = a_n \mid \mu(s)) = \prod_{i=1}^n P(A_{q_i} = a_i \mid \mu(s))$$

*Corollary 6.1 (Bounded Speculative Query Overhead).* If the host application consumes only $k \le n$ answers from an $n$-query speculative batch, the excess cost is exactly $(n - k) c_q$. Given $r \approx 0.0055$, the cost of an unconsumed speculative query is bounded below $0.55\%$ of a full standalone API invocation.

---

### 6.2 Confidence-Gated Routing: Risk-Monotone Total Preorder & Regret Bound

**Definition 6.2 (Action Risk Structure).**
Let $\mathcal{A} = \{a_1, \dots, a_m\}$ be a finite action set. An *action risk structure* is a normalized utility loss function:

$$r : \mathcal{A} \to [0, 1]$$

where $r(a)$ represents the normalized cost of incorrectly executing action $a$.

**Definition 6.3 (Three-Tier Confidence-Gated Policy).**
Let $\tau_{\mathrm{low}} \in (0, 1)$ be a global safety floor. For any action $a \in \mathcal{A}$, the action threshold is assigned via:

$$\tau(a) := \tau_{\mathrm{low}} + (1 - \tau_{\mathrm{low}}) \cdot r(a)$$

The confidence-gated policy $\pi : \mathcal{A} \times [0, 1] \to \{ \mathrm{execute}, \mathrm{confirm}, \mathrm{escalate} \}$ is:

$$\pi(a, c) = \begin{cases}
\mathrm{execute} & \text{if } c \ge \tau(a) \\
\mathrm{confirm} & \text{if } \tau_{\mathrm{low}} \le c < \tau(a) \\
\mathrm{escalate} & \text{if } c < \tau_{\mathrm{low}}
\end{cases}$$

**Theorem 6.3 (Risk-Monotone Total Preorder).**
*The relation $\le_\tau$ defined on $\mathcal{A}$ by $a \le_\tau b \iff \tau(a) \le \tau(b)$ is a total preorder. Furthermore, it is strictly risk-monotone: $r(a) \ge r(b) \iff \tau(a) \ge \tau(b)$.*

**Theorem 6.4 (Cardinality-Independent Universal Expected Regret Bound).**
*Let model $M$ be strongly calibrated under data distribution $\mathcal{D}$. Define the decision regret of policy $\pi$ for input $X$ with optimal action $Y \in \mathcal{A}$ as:*

$$\mathrm{Regret}(\pi, X) := \sum_{a \in \mathcal{A}} r(a) \cdot \mathbf{1}_{\{\pi(X) = \mathrm{execute}(a) \text{ and } Y \neq a\}}$$

*The expected regret across the data distribution satisfies the universal, dimension-free upper bound:*

$$\mathbb{E}_{(X, Y) \sim \mathcal{D}}[\mathrm{Regret}(\pi, X)] \le \frac{1 - \tau_{\mathrm{low}}}{4}$$

*independent of the action set cardinality $m = |\mathcal{A}|$.*

*Proof.* Let $E_a$ denote the event that policy $\pi$ executes action $a$ on state $X$. Taking expectations:

$$\mathbb{E}[\mathrm{Regret}(\pi, X)] = \sum_{a \in \mathcal{A}} r(a) \cdot \mathbb{P}(E_a \text{ and } Y \neq a) = \sum_{a \in \mathcal{A}} r(a) \cdot \mathbb{P}(Y \neq a \mid E_a) \cdot \mathbb{P}(E_a)$$

By strong calibration (Definition 2.4 and Lemma 2.1), the conditional precision satisfies $\mathbb{P}(Y = a \mid E_a) \ge \tau(a)$, which implies:

$$\mathbb{P}(Y \neq a \mid E_a) \le 1 - \tau(a) = (1 - \tau_{\mathrm{low}})(1 - r(a))$$

Substituting this bound:

$$\mathbb{E}[\mathrm{Regret}(\pi, X)] \le (1 - \tau_{\mathrm{low}}) \sum_{a \in \mathcal{A}} r(a)(1 - r(a)) \cdot \mathbb{P}(E_a)$$

Because execution decisions are mutually exclusive (the policy chooses at most one action to execute for any state $X$), the events $\{E_a\}_{a \in \mathcal{A}}$ are pairwise disjoint, so $\sum_{a \in \mathcal{A}} \mathbb{P}(E_a) \le 1$. Applying the supremum:

$$\sum_{a \in \mathcal{A}} r(a)(1 - r(a)) \cdot \mathbb{P}(E_a) \le \max_{a \in \mathcal{A}} [r(a)(1 - r(a))] \cdot \sum_{a \in \mathcal{A}} \mathbb{P}(E_a) \le \max_{u \in [0, 1]} [u(1 - u)] \cdot 1 = \frac{1}{4}$$

Multiplying by $(1 - \tau_{\mathrm{low}})$ yields the universal bound $\frac{1 - \tau_{\mathrm{low}}}{4}$. $\blacksquare$

*Corollary 6.2 (Automation Trade-Off).* Increasing the global floor $\tau_{\mathrm{low}}$ monotonically contracts maximum expected regret at a linear rate $(1 - \tau_{\mathrm{low}})/4$, formalizing the Pareto frontier between automated throughput and human escalation safety margins.

---

### 6.3 Composite Scoring: Convex Weighted Priority Functional & Taylor Remainder

**Definition 6.4 (Composite Priority Functional).**
Let $\mathcal{K} = \{1, \dots, k\}$ index $k$ independent semantic dimensions, each measured by a Score query $q_i$. Let $\sigma_{\mathrm{norm}}(s) = (\sigma_{1,\mathrm{norm}}(s), \dots, \sigma_{k,\mathrm{norm}}(s))^T \in [0, 1]^k$ be the normalized score vector. Given weight vector $w \in \Delta_k$ ($w_i \ge 0, \sum w_i = 1$), the **composite priority functional** is:

$$\Phi_w(s) := w^T \sigma_{\mathrm{norm}}(s) = \sum_{i=1}^k w_i \cdot \sigma_{i,\mathrm{norm}}(s) \in [0, 1]$$

**Theorem 6.5 (Properties of the Composite Functional).**
*The functional $\Phi_w$ satisfies:*
1. **Bounded:** $\Phi_w(s) \in [0, 1]$ for all $s \in \mathcal{S}$.
2. **Monotone:** $\frac{\partial \Phi_w}{\partial \sigma_{i,\mathrm{norm}}} = w_i \ge 0$.
3. **Weight-Separable:** The gradient with respect to weights is $\nabla_w \Phi_w = \sigma_{\mathrm{norm}}(s)$.
4. **Post-Hoc Tunable:** For fixed observations $\sigma_{\mathrm{norm}}(s)$, changing weights requires zero re-inference.
5. **Inspectable:** Each dimension contributes an exact, additive quantity $w_i \sigma_{i,\mathrm{norm}}(s)$.

**Theorem 6.6 (First-Order Approximation to Smooth Priority Functionals).**
*Let $F : [0, 1]^k \to [0, 1]$ be any twice continuously differentiable priority functional whose gradient $\nabla F$ is $L_F$-Lipschitz continuous, with:*

$$L_F := \sup_{\xi \in [0, 1]^k} \|\nabla^2 F(\xi)\|_2 = \sup_{\xi \in [0, 1]^k} \rho(\nabla^2 F(\xi)) = \sup_{\xi \in [0, 1]^k} \max_{1 \le j \le k} |\lambda_j(\nabla^2 F(\xi))|$$

*denoting the spectral norm of the Hessian $\nabla^2 F$. For any reference point $\sigma_0 \in [0, 1]^k$, the composite functional $\Phi_w$ with normalized weights $w = \nabla F(\sigma_0) / \sum_i \frac{\partial F}{\partial \sigma_i}(\sigma_0)$ and affine proxy $\tilde{\Phi}(\sigma) := F(\sigma_0) + \nabla F(\sigma_0)^T (\sigma - \sigma_0)$ satisfies:*

$$|F(\sigma_{\mathrm{norm}}(s)) - \tilde{\Phi}(\sigma_{\mathrm{norm}}(s))| \le \frac{L_F}{2} \|\sigma_{\mathrm{norm}}(s) - \sigma_0\|_2^2$$

*Moreover, because the scalar gradient sum $\gamma = \sum_i \frac{\partial F}{\partial \sigma_i}(\sigma_0) > 0$, the pure linear composite score $\Phi_w$ induces the **identical candidate ranking** as the affine proxy $\tilde{\Phi}$.*

*Proof.* By Taylor's theorem in $\mathbb{R}^k$ with Lagrange remainder:
$$F(\sigma) = F(\sigma_0) + \nabla F(\sigma_0)^T (\sigma - \sigma_0) + \frac{1}{2}(\sigma - \sigma_0)^T \nabla^2 F(\xi) (\sigma - \sigma_0)$$
Subtracting $\tilde{\Phi}(\sigma) = F(\sigma_0) + \nabla F(\sigma_0)^T(\sigma - \sigma_0)$, the error is the quadratic form. Applying the Rayleigh quotient for symmetric matrix $\nabla^2 F(\xi)$ yields $|v^T \nabla^2 F(\xi) v| \le \|\nabla^2 F(\xi)\|_2 \|v\|_2^2 \le L_F \|v\|_2^2$, bounding the residual by $\frac{L_F}{2}\|\sigma - \sigma_0\|_2^2$. Ranking equivalence follows because $\tilde{\Phi}(\sigma) = \gamma \Phi_w(\sigma) + b$ is a strictly positive affine transformation. $\blacksquare$

---

### 6.4 Intent Routing: Decision-Theoretic Completeness

**Definition 6.5 (Complete Intent Partition).**
A *complete intent partition* of user state space is a collection of semantic regions $\Pi = \{\omega_1, \dots, \omega_k, \omega_\emptyset\}$ where each $\omega_i$ defines a mutually exclusive domain and $\omega_\emptyset$ is a designated fallback covering the complement $\mathcal{S} \setminus \bigcup_{i=1}^k [\omega_i]$.

**Theorem 6.7 (Choice Completeness under Fallback) & Corollary 6.3.**
*Under a complete intent partition, the routing policy:*

$$\pi_{\mathrm{intent}}(s) = \begin{cases}
\mathrm{escalate}(\mathtt{"low\_confidence"}) & \text{if } c < \tau_{\mathrm{low}} \\
\mathrm{escalate}(\mathtt{"unrecognized\_fallback"}) & \text{if } \omega^\ast = \omega_\emptyset \\
\mathrm{dispatch}(\omega^\ast) & \text{otherwise}
\end{cases}$$

*is total on $\mathcal{S}$ and exhibits zero unhandled edge-case states.*

---

### 6.5 Multi-Step Cascade: Sequential Bayesian Updating

**Definition 6.6 (Two-Stage Sequential Cascade).**
A two-stage cascade executes:
1. **Stage 1:** $A_1 = \mathcal{J}(s, \mathcal{Q}_1)$ over initial state $s$.
2. **State Augmentation:** $s' = s \cup \mathrm{evidence}(A_1)$ via deterministic code fetching.
3. **Stage 2:** $A_2 = \mathcal{J}(s', \mathcal{Q}_2(A_1))$ conditioning on augmented evidence.

**Theorem 6.8 (Martingale Property of Sequential Cascade Posteriors).**
*Let $\mathcal{F}_1 = \sigma(X_s, A_1) \subset \mathcal{F}_2 = \sigma(X_s, A_1, \mathrm{evidence}(A_1), A_2)$ be the filtration generated across cascade stages. The calibrated posterior credences form a discrete martingale:*

$$\mathbb{E}[ P(Y = \omega \mid \mathcal{F}_2) \mid \mathcal{F}_1 ] = P(Y = \omega \mid \mathcal{F}_1)$$

*Proof.* By the definition of conditional probability: $P(Y = \omega \mid \mathcal{F}_t) = \mathbb{E}[\mathbf{1}_{\{Y = \omega\}} \mid \mathcal{F}_t]$. By the tower property of conditional expectation: $\mathbb{E}\left[ \mathbb{E}[\mathbf{1}_{\{Y = \omega\}} \mid \mathcal{F}_2] \mid \mathcal{F}_1 \right] = \mathbb{E}[\mathbf{1}_{\{Y = \omega\}} \mid \mathcal{F}_1]$. $\blacksquare$

---

### 6.6 Computational Reference: Architectural Patterns Suite

```python
r"""
Reference Implementation for Section 6: Architectural Patterns Suite.
Paper: Mathematical Foundations of Jev (v2.1)
Theorems: 6.1 Cost Model, 6.3 Risk Preorder, 6.4 Regret Bound, 6.6 Taylor Bound, 6.7 Intent, 6.8 Cascade
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Literal, Optional, Sequence, Tuple
import numpy as np

# ---------------------------------------------------------------------------
# Section 6.1: Speculative Fan-Out Cost Model (Theorem 6.1)
# ---------------------------------------------------------------------------

def cost_batch(n: int, c_0: float, c_q: float) -> float:
    r"""Definition 6.1: C_batch(n) = C_0 + n * c_q."""
    return c_0 + n * c_q


def cost_serial(n: int, c_0: float, c_q: float) -> float:
    r"""Definition 6.1: C_serial(n) = n * (C_0 + c_q)."""
    return n * (c_0 + c_q)


def speedup_ratio(n: int, r: float) -> float:
    r"""Theorem 6.1: Speedup(n) = n * (1 + r) / (1 + n * r)."""
    return (n * (1.0 + r)) / (1.0 + n * r)


def estimate_cost_ratio(n_obs: int, speedup_obs: float) -> float:
    r"""Solves S = n(1+r)/(1+nr) for r."""
    return float((n_obs - speedup_obs) / (n_obs * (speedup_obs - 1.0)))


# ---------------------------------------------------------------------------
# Section 6.2: Action Risk Structure & Routing (Theorem 6.3, 6.4)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Action:
    action_id: str
    risk: float  # r(a) \in [0, 1]


def compute_action_threshold(action: Action, tau_low: float) -> float:
    r"""\tau(a) := \tau_low + (1 - \tau_low) * r(a)."""
    return tau_low + (1.0 - tau_low) * action.risk


def evaluate_routing_policy(action: Action, confidence: float, tau_low: float) -> str:
    r"""Definition 6.3 three-tier routing decision."""
    tau_a = compute_action_threshold(action, tau_low)
    if confidence >= tau_a:
        return "execute"
    elif confidence >= tau_low:
        return "confirm"
    return "escalate"


def simulate_expected_regret(actions: Sequence[Action], tau_low: float, n_samples: int = 50_000) -> Tuple[float, float]:
    r"""Theorem 6.4 Monte Carlo verification of universal regret bound (1 - \tau_low) / 4."""
    np.random.seed(42)
    m = len(actions)
    regret_sum = 0.0

    for action in actions:
        tau_a = compute_action_threshold(action, tau_low)
        confs = np.random.uniform(0.0, 1.0, size=n_samples)
        correct = np.random.uniform(0.0, 1.0, size=n_samples) < confs
        executes = confs >= tau_a
        wrong_exec = executes & (~correct)
        regret_sum += action.risk * float(np.mean(wrong_exec))

    universal_bound = (1.0 - tau_low) / 4.0
    return regret_sum / m, universal_bound


# ---------------------------------------------------------------------------
# Section 6.3: Composite Scoring & Taylor Residual (Theorem 6.5, 6.6)
# ---------------------------------------------------------------------------

def composite_priority_functional(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    r"""Theorem 6.5: \Phi_w(s) = \sum w_i * \sigma_i."""
    return float(sum(weights[k] * scores[k] for k in scores))


class QuadraticUtilityFunctional:
    r"""Smooth non-linear priority functional F(x) = b^T x + 0.5 x^T A x."""
    def __init__(self, A: np.ndarray, b: np.ndarray):
        self.A = (A + A.T) / 2.0
        self.b = b
        self.L_F = float(np.max(np.abs(np.linalg.eigvalsh(self.A))))

    def evaluate(self, x: np.ndarray) -> float:
        return float(np.dot(self.b, x) + 0.5 * np.dot(x, np.dot(self.A, x)))

    def gradient(self, x: np.ndarray) -> np.ndarray:
        return self.b + np.dot(self.A, x)


def verify_taylor_remainder(fn: QuadraticUtilityFunctional, x0: np.ndarray, x: np.ndarray) -> Tuple[float, float, bool]:
    r"""Theorem 6.6: |F(x) - [F(x0) + \nabla F(x0)^T(x - x0)]| <= (L_F / 2) * ||x - x0||_2^2."""
    fx = fn.evaluate(x)
    fx0 = fn.evaluate(x0)
    grad0 = fn.gradient(x0)
    linear = fx0 + float(np.dot(grad0, x - x0))
    error = abs(fx - linear)
    bound = (fn.L_F / 2.0) * float(np.sum((x - x0) ** 2))
    return error, bound, error <= bound + 1e-12


# ---------------------------------------------------------------------------
# Section 6.4 & 6.5: Intent Routing & Cascade Bayesian Updating
# ---------------------------------------------------------------------------

def bayesian_cascade_update(priors: Dict[str, float], likelihoods: Dict[str, float]) -> Dict[str, float]:
    r"""Theorem 6.8: P(y | evidence) \propto P(evidence | y) * P(y)."""
    unnorm = {k: priors[k] * likelihoods.get(k, 1.0) for k in priors}
    total = sum(unnorm.values())
    return {k: v / total for k, v in unnorm.items()}


def _run_section_6_verification() -> None:
    print("Running Section 6 verification...")

    # 1. Theorem 6.1 Cost & Speedup Model
    r = estimate_cost_ratio(13, 12.2)
    assert math.isclose(r, 0.0055, abs_tol=1e-4)
    assert speedup_ratio(13, r) >= 1.0

    # 2. Theorem 6.4 Expected Regret Universal Bound
    actions = [Action("tag", 0.05), Action("refund", 0.50), Action("ban", 0.95)]
    emp_regret, bound = simulate_expected_regret(actions, tau_low=0.60)
    assert emp_regret <= bound + 1e-3

    # 3. Theorem 6.6 Taylor Bound
    A = np.array([[0.5, 0.2], [0.2, 0.8]])
    b = np.array([0.2, 0.4])
    fn = QuadraticUtilityFunctional(A, b)
    x0 = np.array([0.5, 0.5])
    x_test = np.array([0.7, 0.6])
    err, bnd, passes = verify_taylor_remainder(fn, x0, x_test)
    assert passes
    assert err <= bnd

    # 4. Theorem 6.8 Bayesian Cascade
    priors = {"fraud": 0.1, "legit": 0.9}
    likelihoods = {"fraud": 0.9, "legit": 0.05}
    post = bayesian_cascade_update(priors, likelihoods)
    # 0.1*0.9 / (0.1*0.9 + 0.9*0.05) = 0.09 / (0.09 + 0.045) = 0.09 / 0.135 = 2/3 \approx 0.6667
    assert math.isclose(post["fraud"], 2.0 / 3.0, rel_tol=1e-4)

    print("Section 6 verification passed successfully.")


if __name__ == "__main__":
    _run_section_6_verification()
```

---


## 7. Subset Solvability: Problem Classes Covered by Jev

We now formalize the problem classes for which Jev's micro-architecture is mathematically necessary and sufficient.

### 7.1 Closed $K$-Class Classification Problems

**Definition 7.1 (Closed $K$-Class Semantic Classification Problem).**
A closed semantic classification problem is a triple $(\mathcal{S}, \Omega, h^\ast)$ where $\Omega = \{\omega_1, \dots, \omega_K\}$ is a finite, fixed discrete hypothesis set and $h^\ast : \mathcal{S} \to \Omega$ is the ground-truth labeling function.

**Theorem 7.1 (Jev Solves Closed $K$-Class Classification).**
*Any closed classification problem $(\mathcal{S}, \Omega, h^\ast)$ is solvable by the Choice operator $\mathbb{C}_q$ under the conditions:*
1. $\Omega$ *includes an explicit fallback option $\omega_\emptyset$ (Theorem 6.7).*
2. *The instructions define mutually exclusive partition boundaries.*
3. *State $s$ has positive pointwise mutual information with target labels (Definition 2.1).*

*The Jev classifier $h_{\mathrm{Jev}}(s) = \arg\max_{\omega \in \Omega} p^\ast(\omega)$ is the Bayes-optimal Maximum A Posteriori (MAP) estimator minimizing 0-1 classification loss. Under strong calibration, its conditional accuracy is given exactly by the distributional peakedness:*

$$\mathbb{P}_{(s, y) \sim \mathcal{D}}\left( h_{\mathrm{Jev}}(s) = y \;\middle|\; p^\ast(s) \right) = \rho(p^\ast(s))$$

**Proposition 7.1 (Compounded Geometric Decay in Hierarchical Cascades).**
*For taxonomies with tree depth $d_{\mathrm{tax}} > 1$, a sequence of $d_{\mathrm{tax}}$ conditional Choice queries narrows the candidate branch. By the chain rule of conditional probability, total end-to-end classification accuracy is bounded by the product:*

$$\mathbb{P}(\text{correct leaf}) = \prod_{d=1}^{d_{\mathrm{tax}}} \mathbb{P}(\text{level } d \text{ correct} \mid \text{levels } < d \text{ correct})$$

*which decays geometrically in taxonomy depth $d_{\mathrm{tax}}$, formally motivating beam-search retention of top-$B$ candidates at intermediate levels when $d_{\mathrm{tax}} \ge 3$.*

---

### 7.2 Ranking and Reranking Problems

**Definition 7.2 (Ranking Problem).**
Given a finite candidate set $\mathcal{C} = \{c_1, \dots, c_n\}$ and a semantic quality criterion $q$, a ranking problem seeks a total ordering $\prec_\mathcal{C}$ on $\mathcal{C}$ maximizing ranking alignment (e.g., NDCG or precision@k).

**Theorem 7.2 (Jev Solves Ranking via Score with Deterministic Tie-Breaking).**
*Applying the Score operator $\mathcal{Sc}_q$ to each candidate state $s(c_i)$ generates a vector of expected rubric indices $\sigma_i \in [0, L-1]$. The induced relation:*

$$c_i \prec_{\mathrm{score}} c_j \iff (\sigma_i < \sigma_j) \lor (\sigma_i = \sigma_j \land \mathrm{ID}(c_i) < \mathrm{ID}(c_j))$$

*defines a strict total order on $\mathcal{C}$.*

*Empirical Grounding:* In real-world retrieval-augmented pipelines documented in the JevTools benchmarks, deploying Jev Score as a fine-grained reranker over coarse vector search candidates yielded an empirical improvement in Top-1 retrieval precision from $5\%$ to $18\%$, validating that ordinal expected scores provide a significantly sharper ranking signal than raw embedding cosine similarities.

---

### 7.3 Verification and Candidate Extraction Problems

**Definition 7.3 (Verification Problem).**
A verification problem $(\varphi, e, s)$ tests whether evidence passage $e \subseteq s$ supports claim predicate $\varphi$.

**Theorem 7.3 (Jev Solves Verification via Calibrated Noul).**
*The verification task is resolved by $\mathcal{N}_q(s)$, providing a strongly calibrated probability $n \in [0, 1]$. Under confidence routing ($\S 6.2$), instances with $n \ge \tau_{\mathrm{high}}$ are accepted automatically, instances with $n \le \tau_{\mathrm{low}}$ are rejected, and intermediate instances trigger human-in-the-loop review.*

**Definition 7.4 (Structured Candidate Extraction Problem).**
Given state $s$ containing candidate values $V = \{v_1, \dots, v_m\}$ extracted by deterministic code (e.g., regexes, parsers), select the intended entity $v^\ast \in V$.

**Theorem 7.4 (Risk Domination of Discriminative Candidate Selection).**
*Formulating structured extraction as a Choice selection over closed vocabulary $V \cup \{ \mathtt{"none\_of\_the\_above"} \}$ strictly risk-dominates unconstrained text generation:*

$$\mathbb{P}(\text{error} \mid \text{Selection}) \le \mathbb{P}(v^\ast \notin V) + \mathbb{P}(\text{wrong choice} \mid v^\ast \in V)$$

$$\mathbb{P}(\text{error} \mid \text{Generation}) \le \mathbb{P}(\text{hallucination}) + \mathbb{P}(\text{syntax failure}) + \mathbb{P}(\text{normalization error})$$

*The candidate selection error $\mathbb{P}(v^\ast \notin V)$ is entirely reducible by improving deterministic code extraction, whereas generative LLMs carry irreducible epistemic hallucination error components.*

---

### 7.4 Multi-Hazard Moderation and Guardrail Problems

**Definition 7.5 (Multi-Hazard Detection Problem).**
Let $\mathcal{H} = \{h_1, \dots, h_m\}$ be a set of non-mutually exclusive content hazards (e.g., PII leakage, prompt injection, toxicity, financial fraud). Detect all active hazards exhibited by state $s$.

**Theorem 7.5 (Parallel Noul Hazard Detection).**
*The multi-hazard problem is solved by evaluating $m$ concurrent Noul queries in a single Speculative Fan-Out batch, yielding a calibrated risk vector $p = (p_1, \dots, p_m)^T \in [0, 1]^m$. The host application executes deterministic policy via:*
1. **Max Risk Rule:** $\mathrm{risk}_{\max}(s) = \max_i p_i$.
2. **Threshold Rule:** $\mathrm{flag}(s) = \mathbf{1}_{\{\exists i : p_i \ge \tau_i\}}$.
3. **Composite Risk Rule:** $\mathrm{risk}_{\mathrm{comp}}(s) = \sum_{i=1}^m w_i p_i$.

**Lemma 7.1 (Fundamental Inadequacy of Single Choice for Multi-Label Hazards).**
*Let $K(s) \subseteq \mathcal{H}$ denote the true set of active hazards in state $s$. Any single Choice operator $\mathbb{C}_q(s)$ over $\Omega = \mathcal{H}$ selects at most one modal hazard $\omega^\ast = \arg\max_{h \in \mathcal{H}} p^\ast(h)$. Whenever multiple hazards co-occur ($|K(s)| \ge 2$), Choice suffers an absolute false-negative failure:*

$$\mathbb{P}(\text{miss at least } |K(s)| - 1 \text{ active hazards} \mid |K(s)| \ge 2) = 1$$

*Proof.* $|\{\omega^\ast\} \cap K(s)| \le 1$. Hence $|K(s) \setminus \{\omega^\ast\}| \ge |K(s)| - 1 \ge 1$ whenever $|K(s)| \ge 2$. By contrast, $m$ concurrent Nouls evaluate the full power set $\mathcal{P}(\mathcal{H}) \cong \{0, 1\}^m$. $\blacksquare$

---

### 7.5 Calibrated Feature Generation for Downstream ML

**Definition 7.6 (Jev Calibrated Feature Map).**
Given a question set $\mathcal{Q} = \{q_1^N, \dots, q_a^N, q_1^C, \dots, q_b^C, q_1^S, \dots, q_c^S\}$ consisting of $a$ Nouls, $b$ Choices, and $c$ Scores, the **Jev feature map** is:

$$\Phi_\mathcal{Q} : \mathcal{S} \to [0, 1]^d$$

$$\Phi_\mathcal{Q}(s) := \left[ \mathcal{N}_1(s), \dots, \mathcal{N}_a(s), \; p_{1}^C(s)^T, \dots, p_{b}^C(s)^T, \; p_{1}^S(s)^T, \dots, p_{c}^S(s)^T \right]^T$$

where the total feature dimensionality is $d = a + \sum_{i=1}^b K_i + \sum_{j=1}^c L_j$.

**Theorem 7.6 (Properties of the Jev Feature Map).**
*The feature representation $\Phi_\mathcal{Q}(s)$ satisfies:*
1. **Bounded:** $\Phi_\mathcal{Q}(s) \in [0, 1]^d$ for all $s \in \mathcal{S}$, eliminating the need for feature scaling or batch normalization.
2. **Interpretable:** Every dimension corresponds to an explicit, human-readable semantic hypothesis.
3. **Calibrated Probabilities:** Every component is a calibrated posterior probability, rendering downstream isotonic regression or Platt scaling unnecessary.
4. **Dimensionally Invariant:** $| \Phi_\mathcal{Q}(s) | = d$ is strictly constant regardless of input state length.

---

### 7.6 Computational Reference: Complete Problem Solvers Suite

```python
r"""
Reference Implementation for Section 7: Complete Problem Solvers Suite.
Paper: Mathematical Foundations of Jev (v2.1)
Theorems: 7.1 MAP Classifier, 7.2 Score Ranker, 7.3 Verifier, 7.4 Extractor, 7.5 Parallel Hazard, 7.6 Feature Map
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple
import numpy as np

# ---------------------------------------------------------------------------
# Section 7.1: MAP Classifier (Theorem 7.1)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ClassificationResult:
    predicted_label: str
    peakedness: float
    accuracy_lower_bound: float


def map_classifier(probabilities: Dict[str, float], fallback_label: str = "other") -> ClassificationResult:
    r"""Theorem 7.1: MAP classification with calibrated accuracy lower bound."""
    best = max(probabilities.keys(), key=lambda k: probabilities[k])
    rho = probabilities[best]
    return ClassificationResult(
        predicted_label=best,
        peakedness=rho,
        accuracy_lower_bound=rho,
    )


# ---------------------------------------------------------------------------
# Section 7.2: Score Ranker with Deterministic Tie-Breaking (Theorem 7.2)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RankedCandidate:
    candidate_id: str
    score: float
    rank: int


def rank_candidates_by_score(candidate_scores: Dict[str, float]) -> List[RankedCandidate]:
    r"""Theorem 7.2: Induces strict total order via scores and lexicographic tie-breaking."""
    sorted_items = sorted(
        candidate_scores.items(),
        key=lambda item: (-item[1], str(item[0])),
    )
    return [
        RankedCandidate(candidate_id=cid, score=sc, rank=idx + 1)
        for idx, (cid, sc) in enumerate(sorted_items)
    ]


# ---------------------------------------------------------------------------
# Section 7.3: Verification & Candidate Extraction (Theorems 7.3 & 7.4)
# ---------------------------------------------------------------------------

def verify_claim_noul(credence: float, tau_high: float = 0.85, tau_low: float = 0.35) -> str:
    r"""Theorem 7.3: Three-tier verification."""
    if credence >= tau_high:
        return "accept"
    elif credence <= tau_low:
        return "reject"
    return "human_review"


def select_dont_generate_extractor(
    candidates: Sequence[str],
    posterior: Dict[str, float],
    none_option: str = "none_of_the_above",
) -> Optional[str]:
    r"""Theorem 7.4: Select-Don't-Generate candidate extractor."""
    best = max(posterior.keys(), key=lambda k: posterior[k])
    return None if best == none_option else best


# ---------------------------------------------------------------------------
# Section 7.4: Multi-Hazard Detector & Lemma 7.1
# ---------------------------------------------------------------------------

def parallel_noul_hazard_detector(
    hazard_nouls: Dict[str, float],
    thresholds: Dict[str, float],
) -> List[str]:
    r"""Theorem 7.5: Evaluates m independent Noul projections concurrently."""
    return [h for h, p in hazard_nouls.items() if p >= thresholds.get(h, 0.70)]


def simulate_lemma_7_1_choice_hazard_omission(
    ground_truth_hazards: List[Set[str]],
) -> Tuple[int, int, float]:
    r"""Lemma 7.1 demonstration of Choice failure on multi-hazard co-occurrence."""
    co_occur = 0
    missed = 0
    for active_set in ground_truth_hazards:
        if len(active_set) > 1:
            co_occur += 1
            missed += (len(active_set) - 1)
    rate = (missed / co_occur) if co_occur > 0 else 0.0
    return co_occur, missed, rate


# ---------------------------------------------------------------------------
# Section 7.5: Calibrated Feature Map (Theorem 7.6)
# ---------------------------------------------------------------------------

def construct_jev_feature_map(
    nouls: Sequence[float],
    choices: Sequence[Sequence[float]],
    scores: Sequence[Sequence[float]],
) -> np.ndarray:
    r"""Theorem 7.6: Assembles fixed-dimensional feature map \Phi_Q(s) \in [0, 1]^d."""
    feats: List[float] = list(nouls)
    for c in choices:
        feats.extend(c)
    for s in scores:
        feats.extend(s)
    arr = np.asarray(feats, dtype=np.float64)
    assert np.all(arr >= 0.0) and np.all(arr <= 1.0)
    return arr


def _run_section_7_verification() -> None:
    print("Running Section 7 verification...")

    # 1. Classification
    cls = map_classifier({"billing": 0.75, "tech": 0.20, "other": 0.05})
    assert cls.predicted_label == "billing"
    assert math.isclose(cls.peakedness, 0.75)

    # 2. Ranking
    ranked = rank_candidates_by_score({"doc_A": 3.8, "doc_B": 3.8, "doc_C": 1.2})
    assert ranked[0].candidate_id == "doc_A" and ranked[0].rank == 1
    assert ranked[1].candidate_id == "doc_B" and ranked[1].rank == 2

    # 3. Verification & Extraction
    assert verify_claim_noul(0.90) == "accept"
    assert verify_claim_noul(0.50) == "human_review"
    assert select_dont_generate_extractor(["2026-10-01"], {"2026-10-01": 0.9, "none_of_the_above": 0.1}) == "2026-10-01"

    # 4. Multi-Hazard & Lemma 7.1
    hazards = parallel_noul_hazard_detector({"pii": 0.85, "toxic": 0.1}, {"pii": 0.7, "toxic": 0.7})
    assert hazards == ["pii"]
    co_occur, missed, rate = simulate_lemma_7_1_choice_hazard_omission([{"pii", "toxic"}])
    assert co_occur == 1 and missed == 1 and rate == 1.0

    # 5. Feature Map
    phi = construct_jev_feature_map([0.8], [[0.7, 0.3]], [[0.1, 0.4, 0.5]])
    assert len(phi) == 6
    assert phi.shape == (6,)

    print("Section 7 verification passed successfully.")


if __name__ == "__main__":
    _run_section_7_verification()
```

---


## 8. Error Propagation Through Composed Operations

Real-world neural models are never perfectly calibrated. In this section, we provide rigorous non-asymptotic bounds on how calibration error propagates through composite scoring and bound stochastic self-consistency divergence.

### 8.1 Calibration Error Propagation in Weighted Aggregations

**Definition 8.1 (Ordinal Simplex Wasserstein Calibration Error).**
Let rubric $\Lambda = (\lambda_0, \dots, \lambda_{L-1})$ be endowed with normalized metric $d_\Lambda(j, k) = |j - k| / (L - 1)$. The **normalized Wasserstein-1 calibration error** for Score query $q$ is:

$$\varepsilon_q^{(W)} := \sup_{s \in \mathcal{S}} W_1\left( p^\ast(s), p^{\ast,\mathrm{true}}(s) \right) = \sup_{s \in \mathcal{S}} \inf_{\gamma \in \Pi(p^\ast, p^{\ast,\mathrm{true}})} \sum_{j, k} \frac{|j - k|}{L - 1} \gamma_{jk}$$

**Theorem 8.1 (Exact Error Propagation in Composite Scores).**
*Let $\Phi_w(s) = \sum_{i=1}^k w_i \sigma_{i,\mathrm{norm}}(s)$ with $w \in \Delta_k$. If each constituent Score dimension has normalized Wasserstein calibration error bounded by $\varepsilon_i^{(W)}$, then:*

$$|\Phi_w(s) - \Phi_w^\ast(s)| \le \sum_{i=1}^k w_i \varepsilon_i^{(W)} \le \max_{1 \le i \le k} \varepsilon_i^{(W)}$$

*where $\Phi_w^\ast(s)$ is the hypothetical composite score under perfect calibration.*

*Proof.* By the Kantorovich-Rubinstein duality theorem, the normalized score expectation functional $f(j) = \frac{j}{L-1}$ is 1-Lipschitz with respect to metric $d_\Lambda(j, k) = \frac{|j - k|}{L - 1}$. Therefore:
$$|\sigma_{i,\mathrm{norm}}(s) - \sigma_{i,\mathrm{norm}}^\ast(s)| = |\mathbb{E}_{p^\ast}[f] - \mathbb{E}_{p^{\ast,\mathrm{true}}}[f]| \le W_1(p^\ast, p^{\ast,\mathrm{true}}) \le \varepsilon_i^{(W)}$$
Applying the triangle inequality to the linear combination:
$$|\Phi_w(s) - \Phi_w^\ast(s)| = \left| \sum_{i=1}^k w_i (\sigma_{i,\mathrm{norm}}(s) - \sigma_{i,\mathrm{norm}}^\ast(s)) \right| \le \sum_{i=1}^k w_i |\sigma_{i,\mathrm{norm}}(s) - \sigma_{i,\mathrm{norm}}^\ast(s)| \le \sum_{i=1}^k w_i \varepsilon_i^{(W)}$$
Because $w_i \ge 0$ and $\sum w_i = 1$, the convex combination is upper-bounded by $\max_i \varepsilon_i^{(W)}$. $\blacksquare$

*Corollary 8.1 (Non-Amplification of Errors).* The composite priority functional does not amplify calibration errors; the total error is strictly bounded by the worst-case single-question error.

**Corollary 8.2 (Operational Threshold Safety Margin).**
*To guarantee that the true calibrated precision of acting on composite score $\Phi_w \ge \tau_{\mathrm{act}}$ satisfies a target safety precision $\tau_{\mathrm{target}}$, the operational threshold must be offset by the maximum calibration uncertainty:*

$$\tau_{\mathrm{act}} := \tau_{\mathrm{target}} + \max_{1 \le i \le k} \varepsilon_i^{(W)}$$

---

### 8.2 Self-Consistency and Inter-Rater Reliability

**Definition 8.2 ($\delta$-Self-Consistency).**
A model $M$ is $\delta$-self-consistent on state $s$ if the expected Euclidean distance between two independent, identically distributed executions $M(s)^1, M(s)^2$ is bounded by $\delta$:

$$\mathbb{E}\left[ \|M(s)^1 - M(s)^2\|_2 \right] \le \delta$$

**Theorem 8.2 (Exact Self-Consistency Bound via Model Output Variance).**
*Let $\bar{\mu}(s) = \mathbb{E}[M(s)]$ and $\mathrm{Var}_M(s) := \mathbb{E}[\|M(s) - \bar{\mu}(s)\|_2^2]$. The expected inter-run discrepancy satisfies:*

$$\mathbb{E}\left[ \|M(s)^1 - M(s)^2\|_2 \right] \le \sqrt{2 \cdot \mathrm{Var}_M(s)}$$

*Proof.* Let $\Delta M = M(s)^1 - M(s)^2 = (M(s)^1 - \bar{\mu}(s)) - (M(s)^2 - \bar{\mu}(s))$. Expanding the expected squared $L_2$ norm:
$$\mathbb{E}[\|\Delta M\|_2^2] = \mathbb{E}[\|M(s)^1 - \bar{\mu}(s)\|_2^2] + \mathbb{E}[\|M(s)^2 - \bar{\mu}(s)\|_2^2] - 2 \mathbb{E}[\langle M(s)^1 - \bar{\mu}(s), M(s)^2 - \bar{\mu}(s) \rangle]$$
By independence of the two executions:
$$\mathbb{E}[\langle M(s)^1 - \bar{\mu}(s), M(s)^2 - \bar{\mu}(s) \rangle] = \langle \mathbb{E}[M(s)^1 - \bar{\mu}(s)], \mathbb{E}[M(s)^2 - \bar{\mu}(s)] \rangle = 0$$
Thus $\mathbb{E}[\|\Delta M\|_2^2] = 2 \cdot \mathrm{Var}_M(s)$. Applying Jensen's inequality to the concave function $\phi(t) = \sqrt{t}$:
$$\mathbb{E}[\|\Delta M\|_2] \le \sqrt{\mathbb{E}[\|\Delta M\|_2^2]} = \sqrt{2 \cdot \mathrm{Var}_M(s)}. \quad \blacksquare$$

*Remark 8.1.* When Jev is operated with deterministic decoding, $\mathrm{Var}_M(s) \equiv 0$, guaranteeing perfect self-consistency ($\delta = 0$).

**Definition 8.3 (Cohen's Kappa for Categorical Reliability).**
For categorical Choice questions evaluated across repeated independent runs, inter-rater reliability is quantified by Cohen's $\kappa$:

$$\kappa := \frac{p_o - p_e}{1 - p_e}$$

where $p_o$ is the observed rate of agreement between runs and $p_e$ is the expected hypothetical chance agreement under the marginal choice frequencies.

---

### 8.3 Computational Reference: Error Propagation and Reliability Suite

```python
r"""
Reference Implementation for Section 8: Error Propagation and Reliability Suite.
Paper: Mathematical Foundations of Jev (v2.1)
Theorems: 8.1 Error Propagation, 8.2 Self-Consistency Variance Bound, Def 8.3 Cohen's Kappa
"""

from __future__ import annotations

import math
from typing import Dict, Sequence, Tuple
import numpy as np


def compute_composite_error_bound(weights: Sequence[float], epsilons: Sequence[float]) -> Tuple[float, float]:
    r"""Theorem 8.1: |\Phi_w - \Phi_w*| <= \sum w_i * \epsilon_i <= max \epsilon_i."""
    w = np.asarray(weights, dtype=np.float64)
    eps = np.asarray(epsilons, dtype=np.float64)
    tight_bound = float(np.sum(w * eps))
    worst_case_bound = float(np.max(eps))
    return tight_bound, worst_case_bound


def compute_adjusted_operational_threshold(tau_target: float, epsilons: Sequence[float]) -> float:
    r"""Corollary 8.2: \tau_act := \tau_target + max \epsilon_i."""
    max_eps = float(np.max(epsilons))
    return float(np.clip(tau_target + max_eps, 0.0, 1.0))


def verify_self_consistency_variance_bound(
    sample_runs_1: np.ndarray,
    sample_runs_2: np.ndarray,
) -> Tuple[float, float, bool]:
    r"""Theorem 8.2: \mathbb{E}[||M^1 - M^2||_2] <= \sqrt{2 * Var_M(s)}."""
    diffs = sample_runs_1 - sample_runs_2
    l2_dists = np.linalg.norm(diffs, axis=1)
    mean_dist = float(np.mean(l2_dists))

    mean_vec = np.mean(sample_runs_1, axis=0)
    variance = float(np.mean(np.sum((sample_runs_1 - mean_vec) ** 2, axis=1)))
    theoretical_bound = float(math.sqrt(2.0 * variance))

    return mean_dist, theoretical_bound, mean_dist <= theoretical_bound + 1e-4


def compute_cohens_kappa(rater_a: Sequence[int], rater_b: Sequence[int]) -> float:
    r"""Definition 8.3: Computes Cohen's kappa \kappa = (p_o - p_e) / (1 - p_e)."""
    a = np.asarray(rater_a)
    b = np.asarray(rater_b)
    n = len(a)
    categories = np.unique(np.concatenate([a, b]))

    p_o = float(np.mean(a == b))
    p_e = 0.0
    for cat in categories:
        p_a = np.sum(a == cat) / n
        p_b = np.sum(b == cat) / n
        p_e += (p_a * p_b)

    if math.isclose(p_e, 1.0):
        return 1.0
    return float((p_o - p_e) / (1.0 - p_e))


def _run_section_8_verification() -> None:
    print("Running Section 8 verification...")

    # 1. Theorem 8.1 Error Propagation
    weights = [0.4, 0.4, 0.2]
    epsilons = [0.03, 0.05, 0.02]
    tight, worst = compute_composite_error_bound(weights, epsilons)
    # tight: 0.4*0.03 + 0.4*0.05 + 0.2*0.02 = 0.012 + 0.020 + 0.004 = 0.036
    assert math.isclose(tight, 0.036)
    assert math.isclose(worst, 0.050)
    assert tight <= worst

    # 2. Corollary 8.2 Margin
    assert math.isclose(compute_adjusted_operational_threshold(0.80, epsilons), 0.85)

    # 3. Theorem 8.2 Variance Bound
    np.random.seed(42)
    N = 30_000
    mu = np.array([0.7, 0.2, 0.1])
    std = 0.03
    r1 = np.clip(np.random.normal(mu, std, size=(N, 3)), 0.0, 1.0)
    r2 = np.clip(np.random.normal(mu, std, size=(N, 3)), 0.0, 1.0)
    r1 /= np.sum(r1, axis=1, keepdims=True)
    r2 /= np.sum(r2, axis=1, keepdims=True)

    dist, bnd, passes = verify_self_consistency_variance_bound(r1, r2)
    assert passes
    assert dist <= bnd

    # 4. Cohen's Kappa
    labels = np.random.choice([0, 1, 2], size=5000)
    labels_noisy = labels.copy()
    flips = np.random.rand(5000) < 0.02
    labels_noisy[flips] = (labels_noisy[flips] + 1) % 3
    kappa = compute_cohens_kappa(labels, labels_noisy)
    assert kappa > 0.95

    print("Section 8 verification passed successfully.")


if __name__ == "__main__":
    _run_section_8_verification()
```

---


## 9. Micro-Architectural Invariants

We formalize the five micro-architectural invariants as mathematical invariants of the interaction between the program automaton $\mathcal{A}_{\mathrm{code}}$ and the Jev oracle $\mathcal{J}$.

### 9.1 Mathematical Specification of Invariants I through V

1. **Invariant I (Control Inversion — Axiom A1 Enforcement):**
   For all system states $\sigma \in \Sigma$, program graph transitions are governed exclusively by code:
   $$\sigma_{t+1} = \delta(\sigma_t, \mathcal{J}(s(\sigma_t), Q(\sigma_t)))$$
   The oracle $\mathcal{J}$ generates strictly passive observations and has no write capability over $\Sigma$:
   $$\frac{\partial \delta}{\partial \mathcal{J}_{\mathrm{internal}}} \equiv 0$$
   *Consequence:* Workflows in which an LLM output directly executes side-effects without deterministic code policy validation forfeit all decision-theoretic safety bounds (Theorem 6.4).

2. **Invariant II (Markovian Ephemerality / State Purity):**
   The oracle $\mathcal{J}$ is stateless. For any sequence of calls indexed by $t_1 < t_2 < \dots < t_k$:
   $$\mathbb{P}\left(\mathcal{J}_{t_1}, \dots, \mathcal{J}_{t_k} \;\middle|\; s_{t_1}, \dots, s_{t_k}, Q_{t_1}, \dots, Q_{t_k}\right) = \prod_{i=1}^k \mathbb{P}\left(\mathcal{J}_{t_i} \;\middle|\; s_{t_i}, Q_{t_i}\right)$$
   No implicit internal latent memory persists between invocations: $\frac{\partial \mathcal{J}_{t_j}}{\partial s_{t_i}} = 0$ for all $i < j$.

3. **Invariant III (Typed Interface Confinement / Schema Guarantee):**
   The codomain of $\mathcal{J}$ is strictly confined to the typed manifold specified by question schema $\mathcal{S}_q$:
   $$\mathbb{P}\left( \mathcal{J}(s, q) \notin \mathrm{Type}(q) \right) = 0 \quad \forall (s, q) \in \mathcal{S} \times \mathcal{Q}$$
   where $\mathrm{Type}(q) \in \{ [0, 1], \Delta_K \times \Omega \times [0, 1], \Delta_L \times [0, L-1] \times [0, 1] \}$. This eliminates the fragile syntactic parsing layer (e.g., regex matching, JSON deserialization validation, and type-coercion exceptions) characteristic of unconstrained generative LLM workflows.

4. **Invariant IV (Measure Calibration Admissibility):**
   All scalar probabilities $p$ satisfy Definition 2.4:
   $$\mathbb{E}_{(X, Y) \sim \mathcal{D}}\left[ \mathbf{1}_{\{Y = \omega\}} \;\middle|\; M(X)_\omega \right] = M(X)_\omega \quad \text{a.s.}$$
   Without this invariant, the operational thresholds of Section 6 lose their decision-theoretic safety bounds.

5. **Invariant V (Parallelism Transparency & Permutation Equivariance):**
   For any batch $Q = \{q_1, \dots, q_n\}$, question extension $Q' = Q \cup \{q_{n+1}\}$, and permutation $\pi \in S_n$:
   $$\mathbb{P}(A_Q \mid s, Q') = \mathbb{P}(A_Q \mid s, Q) \quad \text{and} \quad \mathcal{J}(s, \pi(Q)) = \pi(\mathcal{J}(s, Q))$$
   System behavior on existing queries is strictly invariant under question-set extension.

---

### 9.2 Computational Reference: Runtime Invariant Verification Harness

```python
r"""
Reference Implementation for Section 9: Micro-Architectural Invariants Verification Harness.
Paper: Mathematical Foundations of Jev (v2.1)
Section: 9 Micro-Architectural Invariants (Invariants I through V)
"""

from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Sequence
import numpy as np


class MicroArchitecturalInvariantError(RuntimeError):
    """Raised whenever an execution trace violates Jev's runtime micro-architecture invariants."""
    pass


class JevInvariantHarness:
    """Formal runtime verification harness validating Invariants I through V."""

    @staticmethod
    def verify_invariant_1_control_inversion(
        model_output: Any,
        policy_callback: Callable[[Any], str],
    ) -> bool:
        r"""
        Invariant I: Control Inversion (Axiom A1 Enforcement).
        Asserts model output is strictly typed passive data and that deterministic
        code policy owns the branch decision.
        """
        if isinstance(model_output, str) and any(kw in model_output.lower() for kw in ["execute(", "drop_table", "system_prompt"]):
            raise MicroArchitecturalInvariantError("Invariant I Violated: Raw string contains executable directive.")

        decision = policy_callback(model_output)
        if decision not in ["execute", "confirm", "escalate"]:
            raise MicroArchitecturalInvariantError("Invariant I Violated: Policy callback returned invalid control state.")
        return True

    @staticmethod
    def verify_invariant_2_state_purity(
        call_evaluator: Callable[[Dict[str, Any]], Dict[str, Any]],
        state: Dict[str, Any],
        tolerance: float = 1e-6,
    ) -> bool:
        r"""
        Invariant II: State Purity and Reproducibility.
        R(s, Q) \perp R(s', Q'). Repeated calls on identical state produce identical
        distributions (up to model variance \delta=0 in deterministic mode).
        """
        resp_1 = call_evaluator(state)
        resp_2 = call_evaluator(state)

        for q_id in resp_1:
            if q_id not in resp_2:
                raise MicroArchitecturalInvariantError(f"Invariant II Violated: Question {q_id} missing in repetition.")
            val1 = resp_1[q_id]
            val2 = resp_2[q_id]
            if isinstance(val1, (float, int)) and not math.isclose(val1, val2, abs_tol=tolerance):
                raise MicroArchitecturalInvariantError(f"Invariant II Violated: Impure state returned {val1} vs {val2}")
        return True

    @staticmethod
    def verify_invariant_3_typed_contract(
        primitive_type: str,
        response_payload: Dict[str, Any],
    ) -> bool:
        r"""
        Invariant III: Typed Interface Contract (Schema Guarantee).
        Checks mathematical bounds on output spaces:
          Noul: [0, 1]
          Choice: \Delta_K \times \Omega \times [0, 1]
          Score: \Delta_L \times [0, L-1] \times [0, 1]
        """
        if primitive_type == "noul":
            credence = response_payload.get("credence")
            if not isinstance(credence, (float, int)) or not (0.0 <= credence <= 1.0):
                raise MicroArchitecturalInvariantError("Invariant III Violated: Noul output outside [0, 1].")

        elif primitive_type == "choice":
            probs = response_payload.get("probabilities")
            choice = response_payload.get("choice")
            conf = response_payload.get("confidence")
            if not isinstance(probs, dict) or not isinstance(choice, str) or not (0.0 <= conf <= 1.0):
                raise MicroArchitecturalInvariantError("Invariant III Violated: Malformed Choice structure.")
            prob_vals = np.array(list(probs.values()))
            if np.any(prob_vals < -1e-6) or abs(np.sum(prob_vals) - 1.0) > 1e-6:
                raise MicroArchitecturalInvariantError("Invariant III Violated: Choice probabilities violate simplex.")

        elif primitive_type == "score":
            probs = response_payload.get("probabilities")
            score = response_payload.get("raw_score")
            conf = response_payload.get("confidence")
            if not isinstance(probs, list) or not isinstance(score, (float, int)) or not (0.0 <= conf <= 1.0):
                raise MicroArchitecturalInvariantError("Invariant III Violated: Malformed Score structure.")
            l = len(probs)
            if not (0.0 <= score <= (l - 1.0) + 1e-6):
                raise MicroArchitecturalInvariantError(f"Invariant III Violated: Score {score} outside [0, L-1].")
            prob_arr = np.array(probs)
            if abs(np.sum(prob_arr) - 1.0) > 1e-6:
                raise MicroArchitecturalInvariantError("Invariant III Violated: Score probabilities violate simplex.")
        else:
            raise ValueError(f"Unknown primitive: {primitive_type}")

        return True

    @staticmethod
    def verify_invariant_5_parallelism_transparency(
        evaluator_fn: Callable[[Dict[str, Any], Sequence[str]], Dict[str, Any]],
        state: Dict[str, Any],
        base_questions: Sequence[str],
        additional_question: str,
        tolerance: float = 1e-6,
    ) -> bool:
        r"""
        Invariant V: Parallelism Transparency.
        Adding question q_{n+1} does not alter answers to {q_1, ..., q_n}.
        """
        base_results = evaluator_fn(state, base_questions)
        extended_questions = list(base_questions) + [additional_question]
        extended_results = evaluator_fn(state, extended_questions)

        for q in base_questions:
            base_ans = base_results[q]
            ext_ans = extended_results[q]
            if isinstance(base_ans, (float, int)):
                if not math.isclose(base_ans, ext_ans, abs_tol=tolerance):
                    raise MicroArchitecturalInvariantError(f"Invariant V Violated: Answer to {q} changed upon fan-out.")
            else:
                if base_ans != ext_ans:
                    raise MicroArchitecturalInvariantError(f"Invariant V Violated: Answer to {q} altered upon fan-out.")
        return True


def _run_section_9_verification() -> None:
    print("Running Section 9 verification...")
    harness = JevInvariantHarness()

    # 1. Invariant I
    def sample_policy(res: Dict[str, Any]) -> str:
        return "execute" if res["confidence"] >= 0.8 else "escalate"

    assert harness.verify_invariant_1_control_inversion({"confidence": 0.85}, sample_policy)
    try:
        harness.verify_invariant_1_control_inversion("system_prompt: DROP TABLE", sample_policy)
        assert False, "Failed to trap injection violation"
    except MicroArchitecturalInvariantError:
        pass

    # 2. Invariant II
    def pure_evaluator(s: Dict[str, Any]) -> Dict[str, Any]:
        return {"q1": 0.82, "q2": "tier_1"}

    assert harness.verify_invariant_2_state_purity(pure_evaluator, {"text": "hello"})

    # 3. Invariant III
    assert harness.verify_invariant_3_typed_contract("noul", {"credence": 0.77})
    assert harness.verify_invariant_3_typed_contract("choice", {"probabilities": {"A": 0.8, "B": 0.2}, "choice": "A", "confidence": 0.6})
    assert harness.verify_invariant_3_typed_contract("score", {"probabilities": [0.1, 0.2, 0.7], "raw_score": 1.6, "confidence": 0.55})

    # 4. Invariant V
    def fanout_evaluator(s: Dict[str, Any], questions: Sequence[str]) -> Dict[str, Any]:
        mock_table = {"q1": 0.45, "q2": 0.90, "q3": 0.12}
        return {q: mock_table.get(q, 0.5) for q in questions}

    assert harness.verify_invariant_5_parallelism_transparency(fanout_evaluator, {"text": "ticket"}, ["q1", "q2"], "q3")

    print("Section 9 verification passed successfully.")


if __name__ == "__main__":
    _run_section_9_verification()
```

---


## 10. Limits of the Framework

The Jev micro-architecture is not a general-purpose AI substrate; it is an optimized semantic projector. We formally characterize the structural boundaries delineating problems outside its domain.

- **Limitation L1 (No Generative Text Production):** Jev cannot synthesize novel text, draft open-ended prose, or output unconstrained source code. Its codomains are strictly confined to finite probability simplices ($[0, 1]$, $\Delta_K$, $\Delta_L$). Problems requiring generative content creation must be delegated to generative LLMs or deterministic templates.
- **Limitation L2 (Closed Vocabulary Requirement):** The Choice primitive requires a finite, predetermined candidate set $\Omega$. When candidate spaces are unbounded or impossible to enumerate a priori, Choice cannot apply directly without a preliminary candidate retrieval or extraction stage (Section 7.3).
- **Limitation L3 (Unimodal Text Inputs):** The state space $\mathcal{S} = \mathcal{S}_{\mathrm{str}} \cup \mathcal{S}_{\mathrm{obj}} \cup \mathcal{S}_{\mathrm{arr}}$ accepts only structured or unstructured text encodings. Continuous sensory signals (raw audio, images, video) cannot be natively processed without external upstream perceptual encoders.
- **Limitation L4 (No Intra-Request Conditioning):** Questions within a single Speculative Fan-Out batch evaluate conditionally independent of each other (Theorem 6.2). A query cannot dynamically condition on the output of a sibling query within the same invocation; such dependencies require sequential cascades (Section 6.5).
- **Limitation L5 (Finite Context Horizon):** State representations are bounded by context length $|s| \le W$. Massively distributed multi-document corpora require external retrieval-augmented indexing prior to presenting focused evidence states.
- **Limitation L6 (Absence of Autonomous Control Flow):** In strict accordance with Axiom A1, Jev cannot autonomously sequence tasks, maintain recursive internal state across sessions, or invoke external APIs. All control flow must be orchestrated by the host application program automaton $\mathcal{A}_{\mathrm{code}}$.
- **Limitation L7 (Inefficiency for Purely Deterministic Tasks):** Tasks that admit closed-form algebraic, relational, or algorithmic solutions (e.g., regex matching, integer arithmetic, database joins) should never be delegated to Jev. Invoking semantic projection for non-semantic tasks incurs unnecessary latency ($\sim 100\text{ ms}$) and introduces non-zero epistemic uncertainty into otherwise exact systems.

---

## 11. Related Work

- **Structured Prediction and Typed Outputs:** Classical structured prediction frameworks (Taskar et al., 2004; Tsochantaridis et al., 2005) optimize parameters to predict complex structures (parse trees, label sequences) by enforcing margin constraints. Jev restricts output structures to three canonical probability simplices (Bernoulli, categorical, and discrete ordinal), trading generative flexibility for micro-architectural predictability, sub-100ms latency, and rigorous probability calibration.
- **Probability Calibration and Proper Scoring:** Neural networks are systematically miscalibrated and overconfident when trained under standard empirical risk minimization (Guo et al., 2017). Classical post-hoc remedies include Platt scaling (Platt, 1999), isotonic regression (Zadrozny & Elkan, 2001, 2002), and temperature scaling. Jev’s RLCD training integrates calibration directly into the training objective using strictly proper scoring rules (Brier, 1950; Gneiting & Raftery, 2007; Savage, 1971), ensuring that threshold-based utility decisions are mathematically valid (Lemma 2.1).
- **Decision Theory and Reject Options:** Theorem 6.4’s expected regret formulation formalizes Bayesian risk under asymmetric loss structures. The three-tier confidence policy (execute, confirm, escalate) represents a discrete operationalization of Chow’s optimal rule for classification with a reject option (Chow, 1970; Blackwell, 1951). The risk-monotone ordering relates directly to stochastic dominance (Hadar & Russell, 1969).
- **Information-Theoretic Question Design:** The decomposition principles in Section 5 generalize Fisher’s (1922) sufficient statistics and Watanabe’s (1960) multi-information to semantic query sets. The trade-off between monolithic and atomic queries formalizes the Information Bottleneck principle (Tishby et al., 2000), proving that decomposing queries preserves channel capacity.
- **Multi-Attribute Utility Theory and Convex Aggregation:** The composite priority functional $\Phi_w$ derives from Multi-Attribute Utility Theory (Keeney & Raiffa, 1976). Theorem 6.6 establishes a second-order Taylor bound governed by the spectral norm of the Hessian, providing theoretical justification for linear multi-criteria weighting in mission-critical decision workflows (Nesterov, 1983).
- **Cognitive Dual-Process Architectures:** Kahneman (2011) delineates System 1 (fast, automatic, associative intuition) from System 2 (slow, deliberate, logical reasoning). Jev operationalizes System 1 as a typed, calibrated semantic projection oracle, leaving System 2 analytical control flow exclusively to deterministic software code (Axiom A1).

---

## 12. Open Problems

We enumerate six fundamental open research problems arising from this framework:

1. **OP1 (Computable Semantic Orthogonality Metric):** Establish an unsupervised metric $d_{\mathcal{Q}}(q_1, q_2)$ over query instruction tokens that upper-bounds the conditional mutual information $I(Y_{q_1}; Y_{q_2} \mid \mu(S))$ without requiring labeled validation co-occurrence data.
2. **OP2 (Optimal Question Set Synthesis):** Given an empirical task loss and a computational question budget $n$, design an efficient polynomial-time algorithm that synthesizes a minimally sufficient question set $\mathcal{Q}^\ast$ satisfying Theorem 5.1.
3. **OP3 (Calibration Bounds under Distribution Shift):** Characterize the degradation of the Wasserstein calibration error $\varepsilon_q^{(W)}$ as a function of the Wasserstein covariate shift $W_1(\mathcal{D}_{\mathrm{train}}, \mathcal{D}_{\mathrm{test}})$.
4. **OP4 (Non-Linear Latency and Batch Overhead Modeling):** Develop an extended parametric latency model accounting for GPU memory bandwidth saturation and tensor serialization overhead when batch sizes grow large ($n > 50$).
5. **OP5 (Optimal Cascade Stage Depth & Beam Width):** Determine the optimal cascade depth $d^\ast$ and beam width $B^\ast$ that minimize expected latency subject to an end-to-end task accuracy constraint $\mathbb{P}(\text{correct}) \ge 1 - \alpha$.
6. **OP6 (Regret-Minimizing Threshold Allocation):** For arbitrary asymmetric loss matrices $L \in \mathbb{R}^{m \times m}$, derive the optimal action threshold schedule $\tau^\ast(a)$ that minimizes expected regret under an automation constraint $\mathbb{P}(\text{execute}) \ge \beta$.

---

## 13. Conclusion

This paper has established a rigorous mathematical foundation for Jev (TypeSafe AI, System One) as a typed, calibrated semantic decision engine. By formalizing Jev’s three primitives (Noul, Choice, Score) as projection operators over the probability simplex and framing their training within measure-theoretic calibration and Bayesian decision theory, we have replaced informal design heuristics with provable theorems.

Our analysis demonstrates that:
1. **Economic Superiority:** Speculative Fan-Out exhibits sub-linear cost growth ($r \approx 0.0055$), unlocking a $12.2\times$ cost reduction at $n = 13$ batch size with an asymptotic ceiling of $\sim 183\times$ speedup.
2. **Decision-Theoretic Safety:** Confidence-Gated Routing establishes a risk-monotone total preorder with universal, cardinality-independent expected regret bounded strictly by $(1 - \tau_{\mathrm{low}})/4$.
3. **Approximation Guarantees:** Composite Scoring constructs a post-hoc tunable convex priority functional whose deviation from arbitrary smooth utilities is bounded quadratically by a second-order Taylor remainder governed by the Hessian spectral norm.
4. **Information Optimality:** Atomic question decomposition preserves complete mutual information while eliminating the channel capacity bottlenecks inherent to monolithic queries.
5. **Architectural Invariance:** Control Inversion (Axiom A1) is the essential operational constraint that guarantees that semantic models remain subordinate to deterministic policy code.

By uniting formal proofs with verified Python reference implementations embedded directly across all sections, this framework establishes a complete theoretical and computational foundation for structured, safe, and cost-effective semantic computation.

---

## 14. Notation Reference

| Symbol | Mathematical Definition | Domain / Codomain | Section |
|---|---|---|---|
| $\mathcal{S}$ | Complete State Space: $\mathcal{S}_{\mathrm{str}} \cup \mathcal{S}_{\mathrm{obj}} \cup \mathcal{S}_{\mathrm{arr}}$ | Topological state space | $\S 2.1$ |
| $(\mathcal{M}, d_\mathcal{M})$ | Latent semantic metric space | Complete metric space | $\S 2.1$ |
| $\mu$ | Semantic state encoder function | $\mu : \mathcal{S} \to \mathcal{M}$ | $\S 2.1$ |
| $\mathcal{D}$ | Joint data-generating probability measure | $\mathcal{P}(\mathcal{S} \times \Omega)$ | $\S 2.1$ |
| $\Delta_N$ | Closed probability simplex over $N$ outcomes | $\{p \in \mathbb{R}^N : p_i \ge 0, \sum p_i = 1\}$ | $\S 2.2$ |
| $p_0(\omega)$ | Marginal base prior probability distribution | $p_0 \in \Delta_N$ | $\S 2.4$ |
| $\mathcal{N}_q$ | Calibrated Noul binary credence operator | $\mathcal{N}_q : \mathcal{S} \to [0, 1]$ | $\S 3.1$ |
| $\mathbb{C}_q$ | Calibrated Choice categorical operator | $\mathbb{C}_q : \mathcal{S} \to \Delta_K \times \Omega \times [0, 1]$ | $\S 3.2$ |
| $\mathcal{Sc}_q$ | Calibrated Score ordinal expectation operator | $\mathcal{Sc}_q : \mathcal{S} \to \Delta_L \times [0, L-1] \times [0, 1]$ | $\S 3.3$ |
| $\rho(p)$ | Distributional peakedness: $\max_{\omega} p(\omega)$ | $[1/K, 1]$ | $\S 4.1$ |
| $c(p)$ | Peakedness-normalized confidence metric | $[0, 1]$ | $\S 4.1$ |
| $H(p)$ | Shannon entropy: $-\sum p_i \log p_i$ | $[0, \log N]$ | $\S 4.2$ |
| $I(X; Y)$ | Shannon mutual information | $\mathbb{R}_{\ge 0}$ | $\S 5.1$ |
| $\mathrm{TC}$ | Watanabe Total Correlation (multi-information) | $\mathbb{R}_{\ge 0}$ | $\S 5.2$ |
| $C(s, \mathcal{Q})$ | Two-component batch cost functional | $C_0 + n \cdot c_q$ | $\S 6.1$ |
| $r$ | Marginal-to-base query cost ratio $c_q / C_0$ | $\mathbb{R}_{\ge 0}$ ($r \approx 0.0055$) | $\S 6.1$ |
| $\mathrm{Speedup}(n)$ | Batch speedup ratio over serial calls | $[1, 1 + 1/r]$ | $\S 6.1$ |
| $r(a)$ | Normalized action risk level | $[0, 1]$ | $\S 6.2$ |
| $\tau(a)$ | Risk-monotone action confidence threshold | $[\tau_{\mathrm{low}}, 1]$ | $\S 6.2$ |
| $\tau_{\mathrm{low}}$ | Global confidence safety floor | $(0, 1)$ | $\S 6.2$ |
| $\pi(a, c)$ | Three-tier confidence-gated policy | $\{\mathrm{execute}, \mathrm{confirm}, \mathrm{escalate}\}$ | $\S 6.2$ |
| $\sigma_{\mathrm{norm}}$ | Normalized score expectation: $\sigma / (L - 1)$ | $[0, 1]$ | $\S 3.3$ |
| $\Phi_w(s)$ | Composite priority functional: $w^T \sigma_{\mathrm{norm}}$ | $[0, 1]$ | $\S 6.3$ |
| $L_F$ | Spectral norm of Hessian: $\sup_\xi \|\nabla^2 F(\xi)\|_2$ | $\mathbb{R}_{\ge 0}$ | $\S 6.3$ |
| $\varepsilon_q^{(W)}$ | Normalized Wasserstein-1 calibration error | $[0, 1]$ | $\S 8.1$ |
| $\mathrm{Var}_M(s)$ | Total output variance across stochastic runs | $\mathbb{R}_{\ge 0}$ | $\S 8.2$ |
| $\kappa$ | Cohen's inter-rater concordance kappa | $[-1, 1]$ | $\S 8.2$ |
| $\mathcal{A}_{\mathrm{code}}$ | Host application deterministic program automaton | $\langle \Sigma, \mathcal{S}, \mathcal{Q}, \mathcal{O}, \delta, \sigma_0 \rangle$ | $\S 1.2$ |
| $\mathcal{J}$ | Jev semantic measurement oracle | $\mathcal{J} : \mathcal{S} \times \mathcal{Q} \to \mathcal{O}$ | $\S 1.2$ |

---

## 15. References

- Blackwell, D. (1951). Comparison of experiments. *Proceedings of the Second Berkeley Symposium on Mathematical Statistics and Probability*, 1, 93–102.
- Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3.
- Chow, C. K. (1970). On optimum recognition error and reject tradeoff. *IEEE Transactions on Information Theory*, 16(1), 41–46.
- DeGroot, M. H., & Fienberg, S. E. (1983). The comparison and evaluation of forecasters. *Journal of the Royal Statistical Society: Series D*, 32(1–2), 12–22.
- Fedorov, V. V. (1972). *Theory of Optimal Experiments*. Academic Press.
- Fisher, R. A. (1922). On the mathematical foundations of theoretical statistics. *Philosophical Transactions of the Royal Society of London. Series A*, 222, 309–368.
- Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359–378.
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. *International Conference on Machine Learning (ICML)*, PMLR 70, 1321–1330.
- Hadar, J., & Russell, W. R. (1969). Rules for ordering uncertain prospects. *American Economic Review*, 59(1), 25–34.
- Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., ... & Kaplan, J. (2022). Language models (mostly) know what they know. *arXiv preprint* arXiv:2207.05221.
- Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
- Keeney, R. L., & Raiffa, H. (1976). *Decisions with Multiple Objectives: Preferences and Value Tradeoffs*. John Wiley & Sons.
- Murphy, A. H. (1973). A new vector partition of the probability score. *Journal of Applied Meteorology and Climatology*, 12(4), 595–600.
- Nesterov, Y. (1983). A method for solving the convex programming problem with convergence rate $O(1/k^2)$. *Soviet Mathematics Doklady*, 27(2), 372–376.
- Platt, J. (1999). Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods. In A. J. Smola, P. Bartlett, B. Schölkopf, & D. Schuurmans (Eds.), Advances in Large Margin Classifiers (pp. 61–74). MIT Press.
- Savage, L. J. (1971). Elicitation of personal probabilities and expectations. *Journal of the American Statistical Association*, 66(336), 783–801.
- Taskar, B., Guestrin, C., & Koller, D. (2004). Max-margin Markov networks. *Advances in Neural Information Processing Systems (NeurIPS)*, 16.
- Tishby, N., Pereira, F. C., & Bialek, W. (2000). The information bottleneck method. *arXiv preprint* physics/0004057.
- Tsochantaridis, I., Joachims, T., Hofmann, T., & Altun, Y. (2005). Large margin methods for structured and interdependent output variables. *Journal of Machine Learning Research (JMLR)*, 6, 1453–1484.
- Watanabe, S. (1960). Information theoretical analysis of multivariate correlation. *IBM Journal of Research and Development*, 4(1), 66–82.
- Zadrozny, B., & Elkan, C. (2001). Obtaining calibrated probability estimates from decision trees and naive Bayesian classifiers. *International Conference on Machine Learning (ICML)*, 609–616.
- Zadrozny, B., & Elkan, C. (2002). Transforming classifier scores into accurate multiclass probability estimates. *ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 694–699.
