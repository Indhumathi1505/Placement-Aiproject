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
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "skill_gaps")
public class SkillGap {

    @Id
    private String id;

    @Indexed
    private String studentId;

    private String targetRole;          // SDE, Data Scientist, etc.

    private List<SkillEntry> currentSkills;
    private List<String> missingSkills;
    private List<String> criticalSkills;   // Must have for target role
    private List<CourseRecommendation> recommendedCourses;

    private Double gapScore;            // 0.0 - 1.0 (how big the gap is)
    private Integer estimatedWeeksToClose;

    @CreatedDate
    private LocalDateTime analyzedAt;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SkillEntry {
        private String skillName;
        private Integer currentLevel;   // 0-100
        private Integer requiredLevel;  // 0-100
        private String priority;        // CRITICAL, HIGH, MEDIUM, LOW
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CourseRecommendation {
        private String skillName;
        private String courseName;
        private String platform;        // YouTube, Udemy, Coursera, etc.
        private String url;
        private String duration;        // e.g., "2 weeks"
        private String priority;
    }
}
