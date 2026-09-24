package com.huskies.server.state;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.bson.Document;
import org.junit.jupiter.api.Test;
import org.springframework.data.mongodb.core.convert.MappingMongoConverter;
import org.springframework.data.mongodb.core.convert.NoOpDbRefResolver;
import org.springframework.data.mongodb.core.mapping.MongoMappingContext;

import static org.junit.jupiter.api.Assertions.*;

class EnsembleDeserializeTest {

    private static final String CONTRACT = """
        {
          "schema_version": "1.0",
          "meta": { "state": "GA", "plan": "enacted",
                    "ensemble": { "size": 2, "method": "recom", "generated": "2024-01-01T00:00:00Z" } },
          "summary": { "num_plans": 2, "num_incumbents": 1, "avg_incumbent_winners": 1.0,
                       "avg_geo_var": 0.1, "avg_pop_var": 0.2 },
          "metrics": { "by_incumbent": [
            { "id": "jane-doe", "name": "Jane Doe", "metrics": [
              { "id": "geographic_variation", "label": "Geographic Variation", "unit": "fraction",
                "observed": 0.3, "observed_percentile": 0.75,
                "ensemble": { "n": 2,
                  "quantiles": { "0": 0.0, "0.25": 0.1, "0.5": 0.2, "0.75": 0.3, "1": 0.4 },
                  "histogram": { "bin_edges": [0.0, 0.5, 1.0], "counts": [1, 1] } } } ] } ] }
        }
        """;

    @Test
    void deserializesContractAndRoundTrips() throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        Ensemble e = mapper.readValue(CONTRACT, Ensemble.class);

        assertEquals("1.0", e.getSchemaVersion());
        assertEquals("GA", e.getMeta().getState());
        assertEquals(2, e.getMeta().getEnsemble().getSize());
        assertEquals(1, e.getSummary().getNumIncumbents());

        Ensemble.IncumbentMetrics inc = e.getMetrics().getByIncumbent().get(0);
        assertEquals("jane-doe", inc.getId());
        assertEquals("Jane Doe", inc.getName());
        Ensemble.Metric m = inc.getMetrics().get(0);
        assertEquals("geographic_variation", m.getId());
        assertEquals(0.3, m.getObserved());
        assertEquals(0.75, m.getObservedPercentile());
        assertEquals(2, m.getEnsemble().getHistogram().getCounts().size());

        // round-trips back to the same snake_case keys
        String out = mapper.writeValueAsString(e);
        assertTrue(out.contains("\"observed_percentile\":0.75"));
        assertTrue(out.contains("\"by_incumbent\""));
    }

    // Reads the document through Spring Data's MongoDB mapper (the real /api/summary
    // path, MongoTemplate.findOne). This is what Jackson's ObjectMapper test above
    // does NOT exercise: Mongo maps BSON keys by field name unless @Field is present,
    // so without @Field the snake_case keys (schema_version, num_plans, by_incumbent,
    // observed_percentile, bin_edges) deserialize to null/0. This test fails without
    // @Field on those fields.
    @Test
    void mapsFromMongoDocumentViaSpringData() {
        MongoMappingContext ctx = new MongoMappingContext();
        ctx.afterPropertiesSet();
        MappingMongoConverter converter = new MappingMongoConverter(NoOpDbRefResolver.INSTANCE, ctx);
        converter.afterPropertiesSet();

        Ensemble e = converter.read(Ensemble.class, Document.parse(CONTRACT));

        // The snake_case fields that were null/0 before @Field was added:
        assertEquals("1.0", e.getSchemaVersion());
        assertEquals(2, e.getSummary().getNumPlans());
        assertEquals(1, e.getSummary().getNumIncumbents());
        assertEquals(0.1, e.getSummary().getAvgGeoVar());
        assertNotNull(e.getMetrics().getByIncumbent(), "by_incumbent must map from Mongo");
        assertEquals(1, e.getMetrics().getByIncumbent().size());

        Ensemble.Metric m = e.getMetrics().getByIncumbent().get(0).getMetrics().get(0);
        assertEquals(0.75, m.getObservedPercentile());
        assertEquals(3, m.getEnsemble().getHistogram().getBinEdges().size());

        // meta (single-word keys) maps by field name either way
        assertEquals("GA", e.getMeta().getState());
        assertEquals(2, e.getMeta().getEnsemble().getSize());
    }
}
