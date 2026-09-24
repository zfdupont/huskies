"""Pure transform: existing generated/<state>/ensemble_data.json -> ensemble contract v1.

No GerryChain, no DB. Input is the dict produced by ensemble_analysis.py.
"""
from datetime import datetime, timezone
import re
import numpy as np

SCHEMA_VERSION = "1.0"
HIST_BINS = 50
HIST_RANGE = (0.0, 1.0)

# metric id -> (ensemble-array key, observed key, label)
METRICS = [
    ("geographic_variation", "area_variations", "area_variation", "Geographic Variation"),
    ("population_variation", "vap_total_variations", "vap_total_variation", "Population Variation"),
]


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def percentile_of(value, samples):
    arr = np.asarray(samples, dtype=float)
    if arr.size == 0:
        return 0.0
    pct = float((arr <= value).sum()) / arr.size
    return max(0.0, min(1.0, pct))


def histogram_50(samples):
    # Samples are CLIPPED into the end bins (not dropped), so sum(counts) == len(samples) == n.
    # A future switch to range-drop semantics would break that invariant.
    arr = np.clip(np.asarray(samples, dtype=float), HIST_RANGE[0], HIST_RANGE[1])
    counts, edges = np.histogram(arr, bins=HIST_BINS, range=HIST_RANGE)
    return {"bin_edges": [float(e) for e in edges], "counts": [int(c) for c in counts]}


def quantiles_5(samples):
    q = np.percentile(np.asarray(samples, dtype=float), [0, 25, 50, 75, 100])
    return {"0": float(q[0]), "0.25": float(q[1]), "0.5": float(q[2]),
            "0.75": float(q[3]), "1": float(q[4])}


def _metric(metric_id, label, observed, samples):
    return {
        "id": metric_id,
        "label": label,
        "unit": "fraction",
        "observed": float(observed),
        "observed_percentile": percentile_of(observed, samples),
        "ensemble": {
            "n": len(samples),
            "quantiles": quantiles_5(samples),
            "histogram": histogram_50(samples),
        },
    }


def transform_ensemble(ensemble_data, generated=None):
    if generated is None:
        generated = datetime.now(timezone.utc).isoformat()
    summary = ensemble_data["ensemble_summary"]
    incumbent_arrays = ensemble_data["incumbent_data"]
    enacted = ensemble_data.get("enacted_data", {}).get("incumbent_data", {})

    by_incumbent = []
    for name in sorted(incumbent_arrays.keys()):
        arrays = incumbent_arrays[name]
        observed_all = enacted.get(name, {})
        metrics = []
        for metric_id, arr_key, obs_key, label in METRICS:
            samples = arrays.get(arr_key)
            observed = observed_all.get(obs_key)
            if samples is None or observed is None:
                continue
            metrics.append(_metric(metric_id, label, observed, samples))
        if metrics:
            by_incumbent.append({"id": slugify(name), "name": name, "metrics": metrics})

    return {
        "schema_version": SCHEMA_VERSION,
        "meta": {
            "state": ensemble_data["name"],
            "plan": "enacted",
            "ensemble": {"size": summary["num_plans"], "method": "recom", "generated": generated},
        },
        "summary": {
            "num_plans": summary["num_plans"],
            "num_incumbents": summary["num_incumbents"],
            "avg_incumbent_winners": summary["avg_incumbent_winners"],
            "avg_geo_var": summary["avg_geo_var"],
            "avg_pop_var": summary["avg_pop_var"],
        },
        "metrics": {"by_incumbent": by_incumbent},
    }


def build_contract_file(state):
    """Read generated/<state>/ensemble_data.json, transform, write contract_<state>.json."""
    import json
    from settings import HUSKIES_HOME
    with open(f"{HUSKIES_HOME}/generated/{state}/ensemble_data.json") as f:
        ensemble_data = json.load(f)
    contract = transform_ensemble(ensemble_data)
    dst = f"{HUSKIES_HOME}/generated/{state}/contract_{state}.json"
    with open(dst, "w") as f:
        json.dump(contract, f)
    return dst


if __name__ == "__main__":
    for _state in ("GA", "NY", "IL"):
        print(build_contract_file(_state))
