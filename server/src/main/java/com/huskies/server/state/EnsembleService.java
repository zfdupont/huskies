package com.huskies.server.state;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.rest.webmvc.ResourceNotFoundException;
import org.springframework.stereotype.Service;

@Service
public class EnsembleService {

    @Autowired
    private MongoTemplate mongoTemplate;

    // Not cached: summaries are 3 tiny docs (cheap findOne), and an indefinite
    // in-memory cache served stale data after a re-ingest until the server
    // restarted. Fetch fresh so re-ingested contracts show immediately.
    public Ensemble getSummary(String state){
        Query query = new Query(Criteria.where("meta.state").is(state));
        final Ensemble ensemble = mongoTemplate.findOne(query, Ensemble.class);
        if (ensemble == null) throw new ResourceNotFoundException();
        return ensemble;
    }
}
