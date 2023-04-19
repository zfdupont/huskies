package com.huskies.server.districtPlan;

import com.huskies.server.FeatureCollectionPOJO;
import org.apache.coyote.Response;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.Map;

@RestController
@RequestMapping("/api/plan")
public class DistrictPlanController {

    @Autowired DistrictPlanService districtPlanService;
    @PatchMapping (value = "/precinct", consumes = MediaType.ALL_VALUE)
    @ResponseBody
    public int patchPrecinct(@RequestBody Map<String, String> json){
        try {
            String planName = json.get("plan");
            String candidateName = json.get("candidate");
            String stateId = json.get("state");
            String districtId = stateId+json.get("district");
            String precinctId = districtId+json.get("precinct");
            char party = json.get("party").charAt(0);
            int votes = Integer.parseInt(json.get("votes"));
            districtPlanService.addPrecinctToPlan(planName, candidateName, precinctId, districtId,
                    votes, party);
            return 201;
        } catch (Exception ignore) {
            System.err.println(ignore);
            return 500;
        }
    }
    @PatchMapping (value = "/cvap", consumes = MediaType.ALL_VALUE)
    @ResponseBody
    public void patchCVAP(@RequestBody Map<String, String> json){
        String precinct = json.get("precinct");
        Map<String, Integer> req;
        int total = Integer.parseInt(json.getOrDefault("total", "0"));
        int white = Integer.parseInt(json.getOrDefault("white", "0"));
        int black = Integer.parseInt(json.getOrDefault("black", "0"));
        int asian = Integer.parseInt(json.getOrDefault("asian", "0"));
        int pacific = Integer.parseInt(json.getOrDefault("pacific", "0"));
        int latino = Integer.parseInt(json.getOrDefault("latino", "0"));
        int indian = Integer.parseInt(json.getOrDefault("native", "0"));

    }

    @GetMapping(value = "/plan", consumes = MediaType.ALL_VALUE)
    public ResponseEntity getPlan(@RequestBody Map<String, String> body) throws IOException {
        String state = body.get("state");
        String plan = body.get("plan");
        try {
            FeatureCollectionPOJO planData = districtPlanService.loadJson(state, plan);
            return ResponseEntity.status(200).body(planData);
        } catch ( IOException ioe ) {
            return ResponseEntity.status(404).body(ioe.getMessage());
        } catch ( Exception e ) {
            return ResponseEntity.status(500).body(e.getMessage());
        }
    }
    @GetMapping(value = "/summary", consumes = MediaType.ALL_VALUE)
    public Map<String, Double> getSummary(@RequestBody String name){
        return null;
    }
}
