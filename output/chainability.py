# -*- coding: utf-8 -*-

from collections import defaultdict


RISK_ORDER = {
    "read-only": 0,
    "state-change": 1,
    "privileged": 2,
    "code-loading": 3,
}


def build_execution_chains(surfaces):
    """
    Build directed execution chains between execution-reduced surfaces.

    Rules:
    - Chain only within the same structural anchor
    - Chain only if risk does NOT downgrade (monotonic progression)
    - No self-loops
    - Deterministic, sparse graph

    Adds:
    - parents[]
    - children[]
    - chain_strength (int)
    """

    index = defaultdict(list)

    # ----------------------------
    # Initialize + index
    # ----------------------------
    for s in surfaces:
        s["parents"] = []
        s["children"] = []
        s["chain_strength"] = 0

        key = (
            s.get("cluster_key")
            or s.get("correlation_key")
            or s.get("normalized")
            or s.get("value")
        )

        if key:
            index[key].append(s)

    # ----------------------------
    # Build chains
    # ----------------------------
    for _, group in index.items():
        if len(group) < 2:
            continue

        for src in group:
            src_risk = RISK_ORDER.get(src.get("execution_risk"), -1)

            for dst in group:
                if src is dst:
                    continue

                dst_risk = RISK_ORDER.get(dst.get("execution_risk"), -1)

                # Do not downgrade risk
                if src_risk > dst_risk:
                    continue

                # No duplicate edges
                if dst["id"] in src["children"]:
                    continue

                src["children"].append(dst["id"])
                dst["parents"].append(src["id"])
                src["chain_strength"] += 1

    return surfaces
