package com.huskies.server.state;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.huskies.server.FeatureCollectionPOJO;
import com.huskies.server.district.DistrictRepository;
import com.huskies.server.districtPlan.DistrictPlan;
import org.geotools.feature.FeatureCollection;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.geo.GeoJson;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

@Service
public class StateService {
    @Autowired StateRepository stateRepo;
    @Autowired DistrictRepository districtRepo;

    @Autowired MongoTemplate mongoTemplate;


    public State getState(String name){
        Query q = new Query();
        q.addCriteria(Criteria.where("name").is(name));
        return mongoTemplate.findOne(q, State.class);
    }
}
