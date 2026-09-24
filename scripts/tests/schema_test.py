import json, os
from jsonschema import Draft202012Validator

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schema", "ensemble_contract.v1.json")

def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)

def test_schema_is_itself_valid():
    Draft202012Validator.check_schema(load_schema())

def test_minimal_valid_document_passes():
    doc = {
        "schema_version": "1.0",
        "meta": {"state": "GA", "plan": "enacted",
                 "ensemble": {"size": 2, "method": "recom", "generated": "2024-01-01T00:00:00Z"}},
        "summary": {"num_plans": 2, "num_incumbents": 1, "avg_incumbent_winners": 1.0,
                    "avg_geo_var": 0.1, "avg_pop_var": 0.1},
        "metrics": {"by_incumbent": [
            {"id": "jane-doe", "name": "Jane Doe", "metrics": [
                {"id": "geographic_variation", "label": "Geographic Variation", "unit": "fraction",
                 "observed": 0.2, "observed_percentile": 0.5,
                 "ensemble": {"n": 2,
                    "quantiles": {"0": 0.0, "0.25": 0.1, "0.5": 0.2, "0.75": 0.3, "1": 0.4},
                    "histogram": {"bin_edges": [i/50 for i in range(51)], "counts": [0]*50}}}]}]}
    }
    Draft202012Validator(load_schema()).validate(doc)

def test_extra_field_is_rejected():
    import pytest
    from jsonschema import ValidationError
    doc = {"schema_version": "1.0", "meta": {}, "summary": {}, "metrics": {}, "bogus": 1}
    with pytest.raises(ValidationError):
        Draft202012Validator(load_schema()).validate(doc)
