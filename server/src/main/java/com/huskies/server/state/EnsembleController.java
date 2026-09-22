package com.huskies.server.state;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class EnsembleController {
    @Autowired
    EnsembleService ensembleService;

    @GetMapping(value = "/summary", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<Ensemble> getState(@RequestParam String state) {
        return ResponseEntity.ok(ensembleService.getSummary(state));
    }
}
