# MIT Executive Program — Capstone Playbook

**Implementing Agentic AI: Building Your Organizational Playbook**  
MIT Sloan School of Management × MIT Schwarzman College of Computing  
**Aug 2026**

**Author**: Min Qian (Taffy Qian)  
**Organization**: Huawei International Co. Ltd.  
**Role**: Project Manager  
**Date**: 27 July 2026

---

## Overview

This playbook is the critical learning asset of the MIT Executive Program. 
It contains a coherent, defensible recommendation for an organization's 
leadership team, structured around three governing questions:

1. **WHAT is agentic AI?** (Module 1)
2. **HOW will you implement it?** (Module 2)
3. **How will you SCALE it responsibly?** (Module 3)

The final output: a board-level recommendation covering strategy, design, 
governance, and scaling.

---

## Module 1: The WHAT

### 1.1 Defining agentic AI

> An agent is something my people are going to have to learn to **manage**. 
> Not use. Manage.

Key concepts covered:
- Position on the AI continuum (classical ML → generative AI → agentic AI)
- Three adoption realities:
  1. **Speed of iteration matters more than perfection of plan**
  2. **The biggest barriers are organizational, not technical**
  3. **Existing metrics will not capture the value agentic systems create**

### 1.2 Positioning the organization

Assessment framework:
- AI-first vs. AI-native spectrum
- Concrete example: AUTINOps Intelligent Operations solution 
  (9-step → 2-step closed loop)
- Constraint analysis: change capacity is the primary bottleneck

### 1.3 Candidate workflow selection

Selected: **AI Project Brain — Autonomous End-to-End Orchestration**

Transforms project management from reactive administration to proactive 
orchestration:
- Spans contract management, budget control, and governance reporting
- Identifies high-judgment decision points (budget trade-offs, client 
  communication framing)
- Measurable baselines established:
  - Contract processing: 3–5 days → 0.5 day
  - Budget monitoring: 4–6 hours/month → 0.5–1 hour/month
  - Meeting minutes closure: 48 hours → 2–4 hours
  - Client report generation: 4–8 hours → 15–30 min

---

## Module 2: The HOW

### 2.1 Five building blocks (Andreas)

| Building block | Design decision |
|---|---|
| **Perception** | Internal systems (MetaERP, ISDP, iSales, WeLink) + external benchmarks |
| **Action** | Predefined thresholds; read default; write requires human gate |
| **Planning** | Hybrid: single-step / chain-of-thought / sub-agent decomposition |
| **Memory** | Three-tier: within-session, between-sessions, between-deployments |
| **Safety** | Hardcoded financial caps; read-only credentials; immutable audit |

### 2.2 Build / Buy / Stack decision

- **Model**: Buy (procure commercial LLM for private deployment)
- **Framework**: Stack (open-source orchestration + self-built governance wrapper)
- **Business abstraction layer**: Build (shield agent from legacy complexity)

### 2.3 Human-in-the-loop threshold map

Three decision types with clear thresholds:

| Decision type | Agent autonomous | Escalate to human | Human originates |
|---|---|---|---|
| **Task/Resource Adjustment** | Non-critical subtasks | Milestone changes, cross-project conflicts | Project scope change |
| **Budget Approval** | Queries, forecasts, variance flags | Releases < $1,000 | Releases > $5,000 |
| **Contract Change** | Standard NDA, clause retrieval | Non-core term changes | Binding signatures |

### 2.4 Three-week MVP

**Scope**: Read-only, single-project agent that scans ISDP daily for 
schedule deviations ≥ 5 working days, generates structured deviation 
report with two corrective recommendations, routes to PM for accept/reject.

**Explicitly deferred**: cross-project conflict detection; automated 
corrective actions (until 85%+ adoption for 4 weeks).

### 2.5 Agent Manager role

Three new responsibilities beyond existing PM role:
1. **Review and accept/reject agent recommendations** (with reason)
2. **Maintain and refine threshold rules** (monthly review)
3. **Identify and flag edge cases** (become training data)

### 2.6 AgentOps discipline

**Real-time metrics**:
- Recommendation adoption rate
- Escalation-to-action latency

**Periodic human quality review**:
- Root-cause label accuracy (bi-weekly sampling)

**Skew detection**:
- Watch for input distribution shifts (e.g., terminology drift)
- Early warning: ≥ 10-point drop in adoption rate over 2 weeks

---

## Module 3: The SCALE

### 3.1 Autonomy dial

Five levels: **Constrained → Bounded → Supervised → Delegated → Autonomous**

Current position: Delegated (autonomous within strict thresholds)
12-month goal: Dynamic Delegated/Supervised mix

Migration conditions:
- ≥ 90% accuracy for 4 weeks
- Escalation rate < 10%
- ≥ 80% PM confidence
- Proven audit/rollback effectiveness

### 3.2 Four safeguard layers

| Layer | Concrete safeguard |
|---|---|
| **Hard-coded constraints** | System blocks MetaERP payments > $5,000 regardless of agent output |
| **Output verification** | Consistency check on ISDP task updates before execution |
| **Reversibility by design** | Two-stage budget release with 2-hour cancel window |
| **Escalation architecture** | Threshold-based + confidence-based routing |

### 3.3 Portfolio-scale governance

Three layers of defense:
1. **Foundation**: Data + model governance (extend existing ISO/IEC 42001)
2. **Operational**: Runtime guardrails, centralized AgentOps team
3. **Transparency**: AI Bill of Materials, non-human identity management

### 3.4 Non-human identity

Agent identity: `AI Project Brain Agent` — service account with:
- Read: ISDP, MetaERP, iSales, Teams/email
- Denied: HR PII, customer-sensitive data, write operations outside staging
- Quarterly permission reviews + trigger-based revocation

### 3.5 Governance as competitive differentiator

Positioning: In Huawei's enterprise and government segment, auditability 
and compliance are **deal-winning requirements**, not costs.

Credible 12-month posture:
- ISO/IEC 42001-certified framework operationalized into AgentArts platform
- Governance as platform capability, not policy document

---

## Board Recommendation (Executive Summary)

> Huawei should deploy the AI Project Brain as a deliberate, governed pilot, 
> starting with a read-only, single-project deviation detection workflow 
> that treats governance architecture, organizational readiness, and 
> non-human identity management as the core design variables, not as 
> constraints to be addressed after deployment.

**The ask**:
- Formal mandate to establish AI Project Operations Specialist role 
  (internal promotion path)
- Endorsement to prioritize non-human identity management on enterprise 
  IAM roadmap
- Budget for AgentOps dashboard and audit infrastructure

**The commitment**:
- Quarterly reviews with transparent reporting
- Clear exit condition: if adoption < 50% or accuracy < 70% for two 
  consecutive quarters, recommend pausing
- Deliver validated governance framework reusable across 20 deployments 
  within 12 months

---

## Key Takeaways

1. **Agentic AI adoption fails on organization, not technology**
2. **Governance can be a competitive differentiator, not a cost center**
3. **New roles emerge**: Agent Manager · AI Project Operations Specialist · 
   AgentOps Analyst · Project Data Steward
4. **Threshold maps + safeguard architecture must be designed before 
   deployment** — not retrofitted
5. **The autonomy dial moves by evidence, not by time**