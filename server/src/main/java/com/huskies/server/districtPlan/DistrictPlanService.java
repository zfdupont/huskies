package com.huskies.server.districtPlan;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.rest.webmvc.ResourceNotFoundException;
import org.springframework.stereotype.Service;

@Service
public class DistrictPlanService {
    @Autowired
    private MongoTemplate mongoTemplate;


    public DistrictPlan getDistrictPlan(String state, String name){
        Query query = new Query(Criteria.where("name").is(name).and("state").is(state));
        final DistrictPlan plan = mongoTemplate.findOne(query, DistrictPlan.class);
        if (plan == null) throw new ResourceNotFoundException();
        return plan;
    }
}
