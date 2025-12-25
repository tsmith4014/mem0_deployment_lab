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
    Theme: fast-moving engineer who likes automation and concise checklists.
    """
    user_id = "tony_stark_001"
    messages = [
        {"role": "user", "content": "My name is Tony. I prefer short, bullet-point runbooks for incidents."},
        {"role": "user", "content": "If production is on fire, page me by SMS first, then email a summary."},
        {"role": "user", "content": "I use GitHub Actions for CI and I like Terraform modules kept small and reusable."},
        {"role": "user", "content": "I drink espresso and I like status updates that include a clear ETA."},
        {"role": "user", "content": "When debugging, I start with logs, then metrics, then traces."},
        {"role": "user", "content": "My favorite quick win is adding health checks and sensible timeouts."},
    ]
    return _seed_user(user_id, messages)


@router.post("/seed/leia-organa")
async def seed_leia_organa(api_key: str = Depends(verify_api_key)):
    """
    Seed demo memories for "Leia Organa" (fictional).
    Theme: calm SRE who values reliability and clear incident comms.
    """
    user_id = "leia_organa_001"
    messages = [
        {"role": "user", "content": "My name is Leia. I prefer incident updates every 15 minutes during an outage."},
        {"role": "user", "content": "I like dashboards with SLOs: latency p95, error rate, and saturation."},
        {"role": "user", "content": "I use AWS and I want Terraform plans reviewed before apply in production."},
        {"role": "user", "content": "I prefer calm, clear write-ups: impact, timeline, root cause, and action items."},
        {"role": "user", "content": "For on-call, I like paging via a single channel to avoid alert fatigue."},
        {"role": "user", "content": "My favorite post-incident improvement is better alert thresholds and runbooks."},
    ]
    return _seed_user(user_id, messages)


@router.post("/seed/hermione-granger")
async def seed_hermione_granger(api_key: str = Depends(verify_api_key)):
    """
    Seed demo memories for "Hermione Granger" (fictional).
    Theme: detail-oriented engineer who likes documentation and reproducibility.
    """
    user_id = "hermione_granger_001"
    messages = [
        {"role": "user", "content": "My name is Hermione. I prefer exact commands and reproducible steps."},
        {"role": "user", "content": "I like README docs that link to the next step so I never have to hunt."},
        {"role": "user", "content": "I use Linux and I like troubleshooting checklists: verify env vars, logs, networking, then permissions."},
        {"role": "user", "content": "I prefer structured notes: prerequisites, steps, verification, and cleanup."},
        {"role": "user", "content": "When learning a new tool, I like examples with small inputs and clear expected outputs."},
        {"role": "user", "content": "I like to track changes with git commits that explain why, not just what."},
    ]
    return _seed_user(user_id, messages)


