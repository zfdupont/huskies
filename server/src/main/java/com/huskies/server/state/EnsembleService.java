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

    public Ensemble getSummary(String planName){
        Query query = new Query(Criteria.where("name").is(planName));
        final Ensemble ensemble = mongoTemplate.findOne(query, Ensemble.class);
        if (ensemble == null) throw new ResourceNotFoundException();
        return ensemble;
    }
}
