package com.huskies.server.districtPlan;
import org.springframework.data.mongodb.core.index.CompoundIndex;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

@Document("plans")
@CompoundIndex( def = "{'state' : 1, 'name': 1}", unique = true)
public class DistrictPlan {
    private String name;

    @Field("geojson")
    private FeatureCollectionPOJO geoJSON;
    private String state;

    public DistrictPlan() {}

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public FeatureCollectionPOJO getGeoJson() {
        return geoJSON;
    }

    public void setGeoJson(FeatureCollectionPOJO geoJSON) {
        this.geoJSON = geoJSON;
    }

    public String getState() {
        return state;
    }

    public void setState(String state) {
        this.state = state;
    }
}
