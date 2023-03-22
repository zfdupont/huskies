package com.huskies.server.state;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.huskies.server.FeatureCollectionPOJO;
import com.huskies.server.district.DistrictRepository;
import com.huskies.server.districtPlan.DistrictPlan;
import org.geotools.feature.FeatureCollection;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.geo.GeoJson;
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


    public FeatureCollectionPOJO loadJson(String stateName) throws IOException {
        Path currentRelativePath = Paths.get("");
        String jsonPath = String.format("%s/scripts/merged%s.geojson", currentRelativePath.toAbsolutePath(), stateName);
        byte[] jsonData = Files.readAllBytes(Paths.get(jsonPath));
        ObjectMapper objectMapper = new ObjectMapper();
        FeatureCollectionPOJO f = objectMapper.readValue(jsonData, FeatureCollectionPOJO.class);
        return f;
    }
}
