package com.placeiq.repository;

import com.placeiq.model.Student;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.mongodb.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface StudentRepository extends MongoRepository<Student, String> {

    Optional<Student> findByEmail(String email);

    boolean existsByEmail(String email);

    List<Student> findByDepartment(String department);

    List<Student> findByIsPlacedTrue();

    List<Student> findByIsPlacedFalse();

    @Query("{ 'cgpa': { $gte: ?0 } }")
    List<Student> findByCgpaGreaterThanEqual(Double cgpa);

    @Query("{ 'skills': { $in: ?0 } }")
    List<Student> findBySkillsIn(List<String> skills);

    long countByDepartment(String department);

    long countByIsPlacedTrue();
}
