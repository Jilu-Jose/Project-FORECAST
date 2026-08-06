"""Benchmark Agent — uses NIM (nemotron-3-ultra-550b-a55b) to compare
extracted assumptions against real sector benchmarks based on internal knowledge.
"""

from __future__ import annotations

import asyncio
import logging

from app.agents.state import AuditState
from app.services.llm import get_nim_client

logger = logging.getLogger(__name__)

BENCHMARK_SYSTEM_PROMPT = """You are a startup finance analyst. Given an extracted assumption (metric name, value, unit, sector),
use web search to find current realistic benchmark ranges for that metric in that sector and stage
(pre-seed/seed/Series A — infer from context if given). Classify the assumption as realistic, aggressive,
or unrealistic relative to the benchmark. Cite the benchmark source. Be skeptical of extreme values
(e.g. >20% MoM growth sustained >12 months, >95% gross margin for a non-software business).
Output strict JSON: {"verdict": "realistic|aggressive|unrealistic|unknown", "benchmark_range": "X-Y%", "source": "source URL or name", "reasoning": "one line reasoning"}"""


async def benchmark_node(state: AuditState) -> dict:
    """Benchmark each extracted assumption against real sector data.

    Reads: assumptions, sector
    Writes: assumptions (updated with benchmark fields)
    """
    logger.info("Benchmark Agent: checking assumptions against sector benchmarks")

    assumptions = state.get("assumptions", [])
    sector = state.get("sector") or "technology startup"

    if not assumptions:
        logger.info("Benchmark Agent: no assumptions to benchmark")
        return {"current_agent": "benchmark"}

    # Process in small batches to respect rate limits
    benchmarked = []
    batch_size = 3
    nim = get_nim_client()

    try:
        for i in range(0, len(assumptions), batch_size):
            batch = assumptions[i : i + batch_size]
            tasks = [
                _benchmark_single(nim, assumption, sector)
                for assumption in batch
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for assumption, result in zip(batch, results):
                if isinstance(result, Exception):
                    logger.warning(f"Benchmark failed for {assumption.get('name')}: {result}")
                    benchmarked.append(assumption)  # Keep original without benchmark
                else:
                    benchmarked.append(result)

            # Small delay between batches
            if i + batch_size < len(assumptions):
                await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Benchmark Agent error: {e}")
        return {
            "current_agent": "benchmark",
            "agent_errors": [f"Benchmark Agent error: {str(e)}"],
        }

    # We need to replace the assumptions list entirely.
    # Since the reducer is operator.add, we can't replace — so we return
    # the benchmarked versions that will be reconciled in the report agent.
    # Store benchmarked data back in the same format.
    logger.info(f"Benchmark Agent: benchmarked {len(benchmarked)} assumptions")

    # We override by returning the full updated list.
    # The graph wiring will handle state merge.
    return {
        "current_agent": "benchmark",
        "assumptions": benchmarked,
    }


async def _benchmark_single(nim, assumption: dict, sector: str) -> dict:
    """Benchmark a single assumption using NIM."""
    name = assumption.get("name", "Unknown")
    value = assumption.get("value", 0)
    unit = assumption.get("unit", "")

    prompt = (
        f"Benchmark this startup financial assumption:\n"
        f"- Metric: {name}\n"
        f"- Value: {value} {unit}\n"
        f"- Sector: {sector}\n\n"
        f"Find current realistic benchmark ranges for this metric in the {sector} sector."
    )
    
    messages = [
        {"role": "system", "content": BENCHMARK_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    try:
        response = await nim.chat_json(
            messages=messages,
            temperature=0.2,
        )

        if isinstance(response, dict) and not response.get("parse_error"):
            # Update assumption with benchmark data
            updated = dict(assumption)
            updated["benchmark_verdict"] = response.get("verdict", "unknown")
            updated["benchmark_range"] = response.get("benchmark_range")
            updated["benchmark_source"] = response.get("source")
            updated["benchmark_reasoning"] = response.get("reasoning")
            return updated
    except Exception as e:
        logger.warning(f"NIM benchmark call failed for {name}: {e}")

    return assumption
