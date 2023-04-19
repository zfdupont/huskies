package com.huskies.server.state;

import com.huskies.server.districtPlan.DistrictPlanService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;

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

    @GetMapping(value="/state/{name}", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<State> getState(@PathVariable String name) throws IOException {
        State s = stateService.getState(name);
        return ResponseEntity.status(200).body(s);
    }

}
