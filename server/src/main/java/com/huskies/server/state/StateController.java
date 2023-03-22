package com.huskies.server.state;

import com.huskies.server.FeatureCollectionPOJO;
import com.huskies.server.districtPlan.DistrictPlanService;
import org.geotools.feature.FeatureCollection;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class StateController {
    @Autowired StateService stateService;
    @Autowired
    DistrictPlanService districtPlanService;

    @GetMapping(value="/hi")
    public String sayHi(){
        return "Hi";
    }

    @GetMapping(value="/states/{name}", produces = MediaType.APPLICATION_JSON_VALUE)
    public FeatureCollectionPOJO getState(@PathVariable String name){
        // returns a single state
        try {
            return stateService.loadJson(name);
        } catch (Exception e){
            return null;
        }

    }

}
