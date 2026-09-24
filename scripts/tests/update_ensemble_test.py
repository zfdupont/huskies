from mongo_engine import MongoEngine

class FakeCollection:
    def __init__(self): self.calls = []
    def update_one(self, query, update, upsert=False):
        self.calls.append({"query": query, "update": update, "upsert": upsert})

class FakeDB:
    def __init__(self): self.collections = {}
    def __getitem__(self, name):
        return self.collections.setdefault(name, FakeCollection())

def test_update_ensemble_keys_on_meta_state(monkeypatch):
    # MongoEngine is a singleton; build one and swap its db for a fake.
    engine = MongoEngine.__new__(MongoEngine)
    engine.db = FakeDB()
    contract = {"meta": {"state": "GA"}, "summary": {}, "metrics": {"by_incumbent": []}}
    engine.update_ensemble(contract)
    call = engine.db["states"].calls[0]
    assert call["query"] == {"meta.state": "GA"}
    assert call["upsert"] is True
    assert call["update"] == {"$set": contract}
