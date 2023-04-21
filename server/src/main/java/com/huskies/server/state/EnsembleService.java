package com.huskies.server.state;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.huskies.server.FeatureCollectionPOJO;
import com.huskies.server.districtPlan.DistrictPlan;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.rest.webmvc.ResourceNotFoundException;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;

@Service
public class EnsembleService {
    @Autowired
    EnsembleRepository ensembleRepo;

    @Autowired
    private MongoTemplate mongoTemplate;

    public Ensemble getSummary(String planName){
        Query query = new Query(Criteria.where("name").is(planName));
        final Ensemble ensemble = mongoTemplate.findOne(query, Ensemble.class);
        if (ensemble == null) throw new ResourceNotFoundException();
        return ensemble;
    }
}
