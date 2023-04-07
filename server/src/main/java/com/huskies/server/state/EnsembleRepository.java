package com.huskies.server.state;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface EnsembleRepository extends MongoRepository<Ensemble, String> {
    @Query(value = "{ 'name' :  ?0 }")
    Ensemble findByName(String name);
}
