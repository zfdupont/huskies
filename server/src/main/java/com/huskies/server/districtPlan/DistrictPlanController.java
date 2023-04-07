package com.huskies.server.districtPlan;

import com.huskies.server.FeatureCollectionPOJO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.rest.webmvc.ResourceNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/plan")
public class DistrictPlanController {
    @Autowired DistrictPlanService districtPlanService;
    @PostMapping (value = "")
    @ResponseBody
    public ResponseEntity addPlan(@RequestBody Map<String, String> json){
        try{
            districtPlanService.addDistrictPlan(json.get("name"), json.get("state"), json.get("plan"));
            return ResponseEntity.status(HttpStatus.CREATED).build();
        } catch (Exception e){
            System.err.println(e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    @GetMapping (value = "", consumes = MediaType.ALL_VALUE)
    @ResponseBody
    public ResponseEntity getPlan(@RequestBody Map<String, String> json){
        String planName = json.getOrDefault("plan", "");
        String planState = json.getOrDefault("state", "");
        try{
            return ResponseEntity.status(HttpStatus.ACCEPTED)
                    .body(districtPlanService.getDistrictPlan(planName, planState).getGeoJSON());
        } catch (Exception e){
            System.err.println(e);
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
    }

    @GetMapping(value = "/summary", consumes = MediaType.ALL_VALUE)
    public Map<String, Double> getSummary(@RequestBody String name){
        return null;
    }
}
