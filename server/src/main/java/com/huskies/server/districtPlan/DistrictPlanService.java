package com.huskies.server.districtPlan;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.huskies.server.FeatureCollectionPOJO;
import com.huskies.server.state.Ensemble;
import com.huskies.server.state.EnsembleRepository;
import org.geotools.data.DataUtilities;
import org.geotools.data.FileDataStore;
import org.geotools.data.FileDataStoreFinder;
import org.geotools.data.collection.SpatialIndexFeatureCollection;
import org.geotools.data.simple.SimpleFeatureSource;
import org.geotools.feature.FeatureCollection;
import org.opengis.feature.simple.SimpleFeature;
import org.opengis.feature.simple.SimpleFeatureType;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.mongodb.core.query.Update;
import org.springframework.stereotype.Service;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.attribute.BasicFileAttributes;

@Service
public class DistrictPlanService {
    @Autowired DistrictPlanRepository districtPlanRepo;
    @Autowired
    EnsembleRepository ensembleRepo;
    @Autowired
    private MongoTemplate mongoTemplate;


    public DistrictPlan findPlan(String planID, String planName){
        return districtPlanRepo.findByName(planName)
                .orElse(districtPlanRepo.findById(planID)
                        .orElseThrow());
    }

    public FeatureCollectionPOJO loadJson(String planID, String planName) throws IOException {
        return null;
//        Path currentRelativePath = Paths.get("");
//        String jsonPath = String.format("%s/scripts/merged%s.geojson", currentRelativePath.toAbsolutePath(), stateName);
//        byte[] jsonData = Files.readAllBytes(Paths.get(jsonPath));
//        ObjectMapper objectMapper = new ObjectMapper();
//        FeatureCollectionPOJO f = objectMapper.readValue(jsonData, FeatureCollectionPOJO.class);
//        return f;
    }

    public void addDistrictPlan(String name, String state, String planData){

        DistrictPlan newPlan = new DistrictPlan();
        newPlan.setName(name);
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            FeatureCollectionPOJO geoJSON = objectMapper.readValue(planData, FeatureCollectionPOJO.class);
            newPlan.setGeoJSON(geoJSON);
            newPlan.setState(state);
            mongoTemplate.save(newPlan);
            Query query = new Query(Criteria.where("name").is(state));
            Update update = new Update().addToSet("plans", newPlan);
            mongoTemplate.upsert(query, update, Ensemble.class);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    public DistrictPlan getDistrictPlan(String name, String state){
        Query query = new Query(Criteria.where("name").is(name).and("state").is(state));
        return mongoTemplate.findOne(query, DistrictPlan.class);
    }
}
