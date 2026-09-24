import json, os
from jsonschema import Draft202012Validator
from build_contract import transform_ensemble, percentile_of, histogram_50, quantiles_5, slugify

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schema", "ensemble_contract.v1.json")

def sample_ensemble_data():
    return {
        "name": "GA",
        "ensemble_summary": {"num_plans": 4, "num_incumbents": 1,
                             "avg_incumbent_winners": 1.0, "avg_geo_var": 0.25, "avg_pop_var": 0.15},
        "winner_split": {"1/0": 4},
        "box_w_data": {},
        "incumbent_data": {"Austin Scott": {
            "area_variations": [0.10, 0.20, 0.30, 0.40],
            "vap_total_variations": [0.05, 0.15, 0.25, 0.35]}},
        "enacted_data": {"incumbent_data": {"Austin Scott": {
            "area_variation": 0.30, "vap_total_variation": 0.05}}},
    }

def test_slugify():
    assert slugify("Austin Scott") == "austin-scott"
    assert slugify("Nikema Williams") == "nikema-williams"

def test_percentile_is_fraction_leq_observed_and_clamped():
    assert percentile_of(0.30, [0.1, 0.2, 0.3, 0.4]) == 0.75   # 3 of 4 <= 0.30
    assert percentile_of(-1.0, [0.1, 0.2]) == 0.0
    assert percentile_of(9.9, [0.1, 0.2]) == 1.0

def test_histogram_has_51_edges_50_counts_summing_to_n():
    h = histogram_50([0.01, 0.99, 1.5, -0.5])   # out-of-range clipped into end bins
    assert len(h["bin_edges"]) == 51
    assert len(h["counts"]) == 50
    assert sum(h["counts"]) == 4

def test_quantiles_keys():
    q = quantiles_5([0.0, 0.25, 0.5, 0.75, 1.0])
    assert set(q.keys()) == {"0", "0.25", "0.5", "0.75", "1"}
    assert q["0.5"] == 0.5

def test_transform_produces_schema_valid_contract():
    contract = transform_ensemble(sample_ensemble_data(), generated="2024-01-01T00:00:00Z")
    with open(SCHEMA_PATH) as f:
        Draft202012Validator(json.load(f)).validate(contract)
    assert contract["meta"]["state"] == "GA"
    assert contract["meta"]["ensemble"]["size"] == 4
    inc = contract["metrics"]["by_incumbent"][0]
    assert inc["id"] == "austin-scott" and inc["name"] == "Austin Scott"
    geo = next(m for m in inc["metrics"] if m["id"] == "geographic_variation")
    assert geo["observed"] == 0.30
    assert geo["observed_percentile"] == 0.75
    assert geo["ensemble"]["n"] == 4

def test_transform_omits_metric_when_observed_missing():
    data = sample_ensemble_data()
    del data["enacted_data"]["incumbent_data"]["Austin Scott"]["vap_total_variation"]
    contract = transform_ensemble(data, generated="2024-01-01T00:00:00Z")
    ids = [m["id"] for m in contract["metrics"]["by_incumbent"][0]["metrics"]]
    assert ids == ["geographic_variation"]
