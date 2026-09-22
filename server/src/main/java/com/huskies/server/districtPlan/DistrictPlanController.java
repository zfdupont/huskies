package com.huskies.server.districtPlan;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class DistrictPlanController {
    @Autowired DistrictPlanService districtPlanService;

    @GetMapping(value = "/plan", consumes = MediaType.ALL_VALUE)
    public ResponseEntity<String> getPlan(@RequestParam Map<String, String> params){
        String name = params.getOrDefault("plan", "");
        String state = params.getOrDefault("state", "");
        String planData = districtPlanService.getDistrictPlanGeoJson(state, name);
        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .body(planData);
    }
}
