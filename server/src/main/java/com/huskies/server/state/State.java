package com.huskies.server.state;

import com.fasterxml.jackson.annotation.JsonIdentityInfo;
import com.fasterxml.jackson.annotation.ObjectIdGenerators;
import com.huskies.server.districtPlan.DistrictPlan;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.HashSet;
import java.util.Set;

@Document("state")
public class State {
    @Id
    private String id;
    private Set<DistrictPlan> plans;
    private String geoid;
    public State() {}

    public State(String id) {
        this.id = id;
        this.plans = new HashSet<>();
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getId() {
        return id;
    }

    public Set<DistrictPlan> getPlans() {
        return plans;
    }

    public void setPlans(Set<DistrictPlan> plans) {
        this.plans = plans;
    }

    public String getGeoid() {
        return geoid;
    }

    public void setGeoid(String geoid) {
        this.geoid = geoid;
    }
}