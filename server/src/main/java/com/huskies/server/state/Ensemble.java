package com.huskies.server.state;

import com.huskies.server.districtPlan.DistrictPlan;

import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.ReadOnlyProperty;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.DBRef;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.DocumentReference;

import java.util.HashSet;
import java.util.Set;

@Document("state")
public class Ensemble {
    private String name;
    private Object ensemble_summary, winner_split, box_w_data, incumbent_data;
    public Ensemble(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
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

    public Object getBox_w_data() {
        return box_w_data;
    }

    public void setBox_w_data(Object box_w_data) {
        this.box_w_data = box_w_data;
    }

    public Object getIncumbent_data() {
        return incumbent_data;
    }

    public void setIncumbent_data(Object incumbent_data) {
        this.incumbent_data = incumbent_data;
    }
}