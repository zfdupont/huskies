package com.huskies.server.districtPlan;



import com.huskies.server.district.District;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.HashSet;
import java.util.Set;

@Document("districtplan")
public class DistrictPlan {
    @Id
    private String id;
    private Set<District> districts;

    private String name;

    public DistrictPlan() {}

    public DistrictPlan(String name) {
        this.name = name;
        this.districts = new HashSet<>();
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public Set<District> getDistricts() {
        return districts;
    }

    public void setDistricts(Set<District> districts) {
        this.districts = districts;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
