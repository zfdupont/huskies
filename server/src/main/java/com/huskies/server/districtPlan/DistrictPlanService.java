package com.huskies.server.districtPlan;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
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
import org.springframework.data.rest.webmvc.ResourceNotFoundException;
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


    public DistrictPlan getDistrictPlan(String state, String name){
        Query query = new Query(Criteria.where("name").is(name).and("state").is(state));
        final DistrictPlan plan = mongoTemplate.findOne(query, DistrictPlan.class);
        if (plan == null) throw new ResourceNotFoundException();
        return plan;
    }
}
