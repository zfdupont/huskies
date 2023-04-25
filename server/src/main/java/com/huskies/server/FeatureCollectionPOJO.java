package com.huskies.server;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.*;

class GeometryPOJO {
    public String type;
    public List<Double[]> coordinates;

    public GeometryPOJO() {}

    public void setType(String type) {
        this.type = type;
    }

    public void setCoordinates(List<Double[]> coordinates) {
        this.coordinates = coordinates;
    }
}
class FeaturePOJO {
    public String type;
    public GeometryPOJO geometry;
    public Map<String, Object> properties;

    public FeaturePOJO() {}

    public void setType(String type) {
        this.type = type;
    }

    public void setGeometry(GeometryPOJO geometry) {
        this.geometry = geometry;
    }

    public void setProperties(Map<String, Object> properties) {
        this.properties = properties;
    }
}
public class FeatureCollectionPOJO {
    public String type;

    public ArrayList<HashMap<String, Object>> features;

    public FeatureCollectionPOJO() {}

    @Override
    public String toString() {
        try {
            return new ObjectMapper().writeValueAsString(this);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }
}
