package com.placeiq.repository;

import com.placeiq.model.SkillGap;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SkillGapRepository extends MongoRepository<SkillGap, String> {

    Optional<SkillGap> findTopByStudentIdOrderByAnalyzedAtDesc(String studentId);

    List<SkillGap> findByStudentIdOrderByAnalyzedAtDesc(String studentId);
}
