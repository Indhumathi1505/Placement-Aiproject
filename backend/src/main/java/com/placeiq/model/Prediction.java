package com.placeiq.model;

import lombok.Data;
import lombok.Builder;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.index.Indexed;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "predictions")
public class Prediction {

    @Id
    private String id;

    @Indexed
    private String studentId;

    // Overall scores
    private Double placementProbability;    // 0.0 - 1.0
    private Double readinessScore;          // 0.0 - 10.0
    private Integer resumeScore;            // 0 - 100
    private Integer atsScore;              // 0 - 100

    // Per-company predictions (companyName -> probability %)
    private Map<String, Double> companyProbabilities;

    // AI analysis outputs
    private List<String> extractedSkills;
    private List<String> missingSkills;
    private String overallSummary;
    private List<String> aiRecommendations;
    private List<String> improvementTips;

    // Input snapshot (for history)
    private Double cgpaAtPrediction;
    private List<String> skillsAtPrediction;
    private Integer internshipsAtPrediction;
    private Integer projectsAtPrediction;

    @CreatedDate
    private LocalDateTime predictedAt;
}
