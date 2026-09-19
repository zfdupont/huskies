package com.huskies.server.districtPlan;

import org.bson.Document;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.rest.webmvc.ResourceNotFoundException;
import org.springframework.stereotype.Service;

@Service
public class DistrictPlanService {
    @Autowired
    private MongoTemplate mongoTemplate;


    // Project only the stored GeoJSON subdocument and hand it back as a raw JSON
    // string. This avoids deserializing the multi-MB payload into a POJO and then
    // re-serializing it on the way out; the string is cached ready-to-serve.
    @Cacheable(value = "plans", key = "#state + ':' + #name")
    public String getDistrictPlanGeoJson(String state, String name){
        Query query = new Query(Criteria.where("name").is(name).and("state").is(state));
        query.fields().include("geojson");
        Document doc = mongoTemplate.findOne(query, Document.class, "plans");
        if (doc == null || !(doc.get("geojson") instanceof Document geojson)) {
            throw new ResourceNotFoundException();
        }
        return geojson.toJson();
    }
}
