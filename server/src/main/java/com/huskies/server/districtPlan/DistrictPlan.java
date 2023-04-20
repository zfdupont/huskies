package com.huskies.server.districtPlan;
import com.huskies.server.FeatureCollectionPOJO;
import org.bson.types.ObjectId;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.CompoundIndex;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

@Document("plans")
@CompoundIndex( def = "{'state' : 1, 'name': 1}", unique = true)
public class DistrictPlan {
    @Id private ObjectId id;
    @Indexed private String name;

    private FeatureCollectionPOJO geojson;
    private String state;


    public DistrictPlan() {}

    public DistrictPlan(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public FeatureCollectionPOJO getGeoJson() {
        return geojson;
    }

    public void setGeoJson(FeatureCollectionPOJO geojson) {
        this.geojson = geojson;
    }

    public String getState() {
        return state;
    }

    public void setState(String state) {
        this.state = state;
    }
}
