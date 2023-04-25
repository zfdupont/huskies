package com.huskies.server.districtPlan;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.rest.webmvc.ResourceNotFoundException;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class DistrictPlanController {
    @Autowired DistrictPlanService districtPlanService;
    @GetMapping(value = "/plan", consumes = MediaType.ALL_VALUE)
    public ResponseEntity getPlan(@RequestParam Map<String, String> params){
        String name = params.getOrDefault("plan", "");
        String state = params.getOrDefault("state", "");
        try {
            FeatureCollectionPOJO planData = districtPlanService.getDistrictPlan(state, name).getGeoJson();
            return ResponseEntity.status(200).body(planData);
        } catch ( ResourceNotFoundException rne ) {
            return ResponseEntity.status(404).body(rne.getMessage());
        } catch ( Exception e ) {
            return ResponseEntity.status(500).body(e.getMessage());
        }
    }
}
