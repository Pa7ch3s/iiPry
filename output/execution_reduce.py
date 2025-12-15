# -*- coding: utf-8 -*-


def reduce_execution_surfaces(surfaces):
    """
    Reduce execution-context–annotated surfaces to
    dynamic-ready attack surfaces.

    Structural rules only:
    - keep state-change
    - keep privileged
    - keep code-loading
    """

    kept = []

    for s in surfaces:
        risk = s.get("execution_risk")

        if risk in ("state-change", "privileged", "code-loading"):
            kept.append(s)

    return kept
