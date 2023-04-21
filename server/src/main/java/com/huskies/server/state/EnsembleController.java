package com.huskies.server.state;

import com.huskies.server.state.Ensemble;
import com.huskies.server.districtPlan.DistrictPlanService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.crossstore.ChangeSetPersister;
import org.springframework.data.rest.webmvc.ResourceNotFoundException;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;

@RestController
@RequestMapping("/api")
public class EnsembleController {
    @Autowired
    EnsembleService ensembleService;
    @GetMapping(value="/summary", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity getState(@RequestParam String state) {
        try {
            return ResponseEntity.status(200).body(ensembleService.getSummary(state));
        } catch (ResourceNotFoundException rne){
            return ResponseEntity.status(404).body(rne.getMessage());
        } catch ( Exception e ){
            return ResponseEntity.status(500).body(e.getMessage());
        }
    }

}
