# -*- coding: utf-8 -*-

from collections import defaultdict
from copy import deepcopy


def cluster(findings):
    clusters = defaultdict(list)

    for f in findings:
        key = f.get("correlation_key")
        if not key:
            key = f.get("id") or id(f)
        clusters[key].append(f)

    clustered = []

    for key, members in clusters.items():
        if len(members) == 1:
            single = deepcopy(members[0])
            single["cluster_key"] = key
            single["cluster_size"] = 1
            single["children"] = []
            clustered.append(single)
            continue

        strongest_confidence = 0
        strongest_signal = 0
        primary = None

        for f in members:
            c = f.get("confidence", 0)
            s = f.get("signal_strength", 0)

            if c > strongest_confidence or s > strongest_signal:
                strongest_confidence = max(strongest_confidence, c)
                strongest_signal = max(strongest_signal, s)
                primary = f

        parent = deepcopy(primary)

        parent["cluster_key"] = key
        parent["cluster_size"] = len(members)
        parent["confidence"] = strongest_confidence
        parent["signal_strength"] = strongest_signal
        parent["children"] = [deepcopy(f) for f in members if f is not primary]

        clustered.append(parent)

    return clustered
