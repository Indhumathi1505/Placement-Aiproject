package com.placeiq.repository;

import com.placeiq.model.Prediction;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PredictionRepository extends MongoRepository<Prediction, String> {

    Optional<Prediction> findTopByStudentIdOrderByPredictedAtDesc(String studentId);

    List<Prediction> findByStudentIdOrderByPredictedAtDesc(String studentId);
}
