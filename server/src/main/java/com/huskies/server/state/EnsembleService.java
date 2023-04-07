package com.huskies.server.state;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.huskies.server.FeatureCollectionPOJO;
import com.huskies.server.districtPlan.DistrictPlan;
import org.springframework.beans.factory.annotation.Autowired;
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

    public Map<String, Double> getSummary(String planName){
        // TODO
        return null;
    }
}
