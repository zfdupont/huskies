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

    private Object ensemble_summary, winner_split, box_w_data, incumbent_data;
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

    public Object getEnsemble_summary() {
        return ensemble_summary;
    }

    public void setEnsemble_summary(Object ensemble_summary) {
        this.ensemble_summary = ensemble_summary;
    }

    public Object getWinner_split() {
        return winner_split;
    }

    public void setWinner_split(Object winner_split) {
        this.winner_split = winner_split;
    }

    public Object getBox_with_data() {
        return box_w_data;
    }

    public void setBox_with_data(Object box_with_data) {
        this.box_w_data = box_with_data;
    }

    public Object getIncumbent_data() {
        return incumbent_data;
    }

    public void setIncumbent_data(Object incumbent_data) {
        this.incumbent_data = incumbent_data;
    }
}