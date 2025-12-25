"""
Demo/seed routes for class.

Purpose:
- Provide "one click" Swagger endpoints that seed a realistic dataset into Mem0/Qdrant.
- Give students multiple users worth of memories so search results are meaningful.

These endpoints are safe to run multiple times (they just add more memories).
They use infer=false to make seeding deterministic and fast.
"""

from fastapi import APIRouter, Depends
from dependencies import memory, verify_api_key

router = APIRouter(prefix="/v1/demo", tags=["Demo (Seed Data)"])


def _seed_user(user_id: str, messages: list[dict]) -> dict:
    results = memory.add(messages, user_id=user_id, infer=False)
    return {
        "user_id": user_id,
        "seeded_count": len(results) if isinstance(results, list) else 0,
        "results": results,
    }


@router.post("/seed/tony-stark")
async def seed_tony_stark(api_key: str = Depends(verify_api_key)):
    """
    Seed demo memories for "Tony Stark" (fictional).
    Theme: Stark-tech energy: snarky, automation-obsessed, "ship it fast" incident handling.
    """
    user_id = "tony_stark_001"
    messages = [
        {"role": "user", "content": "My name is Tony Stark. I like incident runbooks that read like a suit-up checklist: fast, minimal, and effective."},
        {"role": "user", "content": "If production is melting down, page me by SMS first. If it's not urgent, email me a TL;DR with one graph."},
        {"role": "user", "content": "I want a 'JARVIS-style' incident update every 10–15 minutes: impact, hypothesis, next action, ETA."},
        {"role": "user", "content": "I like automation: if we do a thing twice, a bot should do it the third time."},
        {"role": "user", "content": "I use GitHub Actions for CI and I like Terraform modules that are small, reusable, and have clean inputs/outputs."},
        {"role": "user", "content": "My dashboards should glow like an arc reactor: error rate, p95 latency, and saturation are always visible."},
        {"role": "user", "content": "When debugging: logs first, then metrics, then traces. No guessing."},
        {"role": "user", "content": "My favorite quick win is adding health checks, timeouts, and retries that actually make sense."},
        {"role": "user", "content": "If a deploy breaks prod: rollback first, then postmortem. Heroics are for movies, not uptime."},
        {"role": "user", "content": "Alert philosophy: one loud page for a real incident. No alert storms."},
        {"role": "user", "content": "If you need my attention fast, open a GitHub issue labeled: 'STARK-LEVEL PRIORITY'."},
        {"role": "user", "content": "I name dashboards like suits: Mark-1 Latency, Mark-2 Errors, Mark-3 Saturation."},
        {"role": "user", "content": "Preferred incident summary format: what happened, impact, fix, and follow-ups. Keep it tight."},
        {"role": "user", "content": "If you ask me to hand-edit YAML at 2am, bring espresso (and maybe shawarma)."},
    ]
    return _seed_user(user_id, messages)


@router.post("/seed/leia-organa")
async def seed_leia_organa(api_key: str = Depends(verify_api_key)):
    """
    Seed demo memories for "Leia Organa" (fictional).
    Theme: Rebel leader energy: calm under pressure, mission-briefing comms, reliability-first.
    """
    user_id = "leia_organa_001"
    messages = [
        {"role": "user", "content": "My name is Leia Organa. During an outage, I want steady 'mission briefings' every 15 minutes."},
        {"role": "user", "content": "Preferred on-call message format: impact, current status, next step, ETA."},
        {"role": "user", "content": "I like dashboards with SLOs: p95 latency, error rate, saturation, and error budget burn rate."},
        {"role": "user", "content": "I use AWS and I want Terraform plans reviewed before apply in production. Treat changes like mission plans."},
        {"role": "user", "content": "For paging, I prefer a single channel. Alert fatigue is how you lose the war."},
        {"role": "user", "content": "If users are impacted, we communicate early and often. No radio silence."},
        {"role": "user", "content": "I prefer calm write-ups: impact, timeline, root cause, and action items with owners."},
        {"role": "user", "content": "Runbooks should start with verification, then mitigation, then deeper debugging."},
        {"role": "user", "content": "My favorite post-incident improvement is better alert thresholds and clearer runbooks."},
        {"role": "user", "content": "If you page me, include: what broke, who is impacted, what you tried, and what you need from me."},
        {"role": "user", "content": "If the graph looks like a 'moon', assume it's a scaling issue and bring evidence."},
        {"role": "user", "content": "Change management matters: deploy windows, rollback plans, and a clear owner."},
        {"role": "user", "content": "I like retrospectives that end with owners and deadlines, not vibes."},
    ]
    return _seed_user(user_id, messages)


@router.post("/seed/hermione-granger")
async def seed_hermione_granger(api_key: str = Depends(verify_api_key)):
    """
    Seed demo memories for "Hermione Granger" (fictional).
    Theme: Hogwarts-brain energy: library-first, precise, reproducible, and allergic to hand-wavy steps.
    """
    user_id = "hermione_granger_001"
    messages = [
        {"role": "user", "content": "My name is Hermione Granger. I prefer exact commands and reproducible steps (no hand-wavy 'just do the thing')."},
        {"role": "user", "content": "I live in the documentation like it's a library: docs should link to the next step so nobody has to hunt."},
        {"role": "user", "content": "I use Linux and I like troubleshooting checklists: env vars, logs, networking, then IAM permissions."},
        {"role": "user", "content": "I prefer structured notes: prerequisites, steps, verification, and cleanup."},
        {"role": "user", "content": "When learning a new tool, I want small examples with clear expected outputs."},
        {"role": "user", "content": "I like git commits that explain WHY, not just WHAT."},
        {"role": "user", "content": "If you forget to document it, I will remind you to update the README."},
        {"role": "user", "content": "During debugging: it's rarely magic. It's usually logs, configs, or permissions."},
        {"role": "user", "content": "I prefer code reviews that include: what changed, why, risks, and how to rollback."},
        {"role": "user", "content": "I like safe commands: warnings for destructive steps and confirmations for dangerous ops."},
        {"role": "user", "content": "I like tests that fail loudly and tell you exactly what to fix."},
        {"role": "user", "content": "I keep a personal runbook and 'check IAM permissions' is always near the top."},
        {"role": "user", "content": "I like Terraform variables with validation blocks. Guardrails are good engineering."},
        {"role": "user", "content": "If someone says 'it works on my machine', my next question is 'which machine', and then I ask for exact steps."},
        {"role": "user", "content": "If you name a file final_final_v3, I will notice. Name things properly."},
    ]
    return _seed_user(user_id, messages)


