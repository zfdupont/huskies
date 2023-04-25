package com.huskies.server.state;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import java.util.List;
import java.util.Map;

@Document("states")
public class Ensemble {
    private String name;
    @Field("ensemble_summary")
    @JsonProperty("ensemble_summary")
    private Map<String, ? extends Number> ensembleSummary;
    @Field("winner_split")
    @JsonProperty("winner_split")
    private Map<String, Integer> winnerSplit;
    @Field("box_w_data")
    @JsonProperty("box_w_data")
    private Object boxWhiskersData;
    @Field("incumbent_data")
    @JsonProperty("incumbent_data")
    private Object incumbentData;

    public Ensemble() {
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Map<String, ? extends Number> getEnsembleSummary() {
        return ensembleSummary;
    }

    public void setEnsembleSummary(Map<String, ? extends Number> ensembleSummary) {
        this.ensembleSummary = ensembleSummary;
    }

    public Map<String, Integer> getWinnerSplit() {
        return winnerSplit;
    }

    public void setWinnerSplit(Map<String, Integer> winnerSplit) {
        this.winnerSplit = winnerSplit;
    }

    public Object getBoxWhiskersData() {
        return boxWhiskersData;
    }

    public void setBoxWhiskersData(Object boxWhiskersData) {
        this.boxWhiskersData = boxWhiskersData;
    }

    public Object getIncumbentData() {
        return incumbentData;
    }

    public void setIncumbentData(Object incumbentData) {
        this.incumbentData = incumbentData;
    }

    @Override
    public String toString() {
        try {
            return new ObjectMapper().writeValueAsString(this);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }
}