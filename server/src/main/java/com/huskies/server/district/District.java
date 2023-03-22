package com.huskies.server.district;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

@Document("district")
public class District {

    @Id
    private String id;

    private String geoid;

    private Map<String, Integer> election, pop;

    public District() {}

    public District(String id) {
        this.id = id;
        this.election = new HashMap<>();
        this.pop = new HashMap<>();
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getGeoid() {
        return geoid;
    }

    public void setGeoid(String geoid) {
        this.geoid = geoid;
    }

    public Map<String, Integer> getElection() {
        return election;
    }

    public void setElection(Map<String, Integer> election) {
        this.election = election;
    }

    public Map<String, Integer> getPop() {
        return pop;
    }

    public void setPop(Map<String, Integer> pop) {
        this.pop = pop;
    }
}
