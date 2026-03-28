import asyncio
import logging
from typing import Any

from server.agents.advocate import AdvocateAgent, CrossExaminationAgent
from server.agents.arbiter import ArbiterAgent
from server.agents.base import AgentContext
from server.llm.router import LLMRouter

logger = logging.getLogger(__name__)

MAX_ADVOCATES = 5
MAX_ROUNDS = 3


async def run_deliberation(
    context: AgentContext,
    parties: list[str],
    router: LLMRouter,
) -> dict[str, Any]:
    """
    Run the 3-round deliberation protocol.

    Round 1: Independent statements from each advocate
    Round 2: Cross-examination
    Round 3: Arbiter convergence
    """
    # Cap at MAX_ADVOCATES
    parties = parties[:MAX_ADVOCATES]
    if len(parties) < 2:
        return {"error": "Need at least 2 parties for deliberation"}

    logger.info(
        "Starting deliberation with %d parties: %s", len(parties), parties
    )

    # Round 1: Independent Statements
    logger.info("Deliberation Round 1: Independent Statements")
    advocates = [AdvocateAgent(router, party) for party in parties]
    round1_results = await asyncio.gather(
        *(a.execute(context) for a in advocates),
        return_exceptions=True,
    )

    positions = []
    for r in round1_results:
        if isinstance(r, Exception):
            logger.error("Advocate failed in round 1: %s", r)
            continue
        positions.append(r.data)

    if len(positions) < 2:
        return {
            "error": "Too few advocates succeeded",
            "partial_positions": positions,
        }

    # Round 2: Cross-Examination
    logger.info("Deliberation Round 2: Cross-Examination")
    cross_agents = [
        CrossExaminationAgent(router, party) for party in parties
    ]
    cross_tasks = []
    for i, agent in enumerate(cross_agents):
        other = [p for j, p in enumerate(positions) if j != i]
        exam_context = AgentContext(
            {**context, "other_positions": other}
        )
        cross_tasks.append(agent.execute(exam_context))

    round2_results = await asyncio.gather(
        *cross_tasks, return_exceptions=True
    )

    examinations = []
    for r in round2_results:
        if isinstance(r, Exception):
            logger.error("Cross-examination failed: %s", r)
            continue
        examinations.append(r.data)

    # Round 3: Arbiter Convergence
    logger.info("Deliberation Round 3: Arbiter Convergence")
    arbiter_context = AgentContext({
        **context,
        "advocate_positions": positions,
        "cross_examinations": examinations,
    })
    arbiter = ArbiterAgent(router)
    arbiter_result = await arbiter.execute(arbiter_context)

    deliberation = arbiter_result.data.get("deliberation", {})

    # Check if unresolved items exceed threshold → flag Meeting Vortex
    unresolved = deliberation.get("unresolved", [])
    if len(unresolved) > 3:
        logger.warning(
            "Deliberation has %d unresolved items — Meeting Vortex risk",
            len(unresolved),
        )
        deliberation["meta_warning"] = (
            "🌀 Warning: This deliberation itself shows Meeting Vortex patterns. "
            "Too many unresolved items. Consider escalation."
        )

    return {
        "deliberation": deliberation,
        "rounds_completed": 3,
        "parties_count": len(parties),
        "advocate_positions": positions,
        "cross_examinations": examinations,
    }
