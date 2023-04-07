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
    @Id private ObjectId id;
    @Indexed(unique = true) private String name;
    @DBRef(lazy = true)
    private Set<DistrictPlan> plans;
    public Ensemble() {
        this.plans = new HashSet<>();
    }

    public Ensemble(String name) {
        this.name = name;
        this.plans = new HashSet<>();
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Set<DistrictPlan> getPlans() {
        return plans;
    }

    public void addPlan(DistrictPlan plans) {
        this.plans.add(plans);
    }
}