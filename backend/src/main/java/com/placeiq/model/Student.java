package com.placeiq.model;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.index.Indexed;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "students")
public class Student {

    @Id
    private String id;

    private String name;
    private String profilePictureUrl;

    @Indexed(unique = true)
    private String email;

    private String passwordHash;

    private String department;       // CSE, IT, ECE, MECH, etc.
    private String year;             // 2nd, 3rd, 4th
    private String section;
    private String rollNumber;
    private String college;
    private String phoneNumber;

    private Double cgpa;
    private Integer backlogs;

    // Skills & Technical Profile
    private List<String> skills;
    private List<String> programmingLanguages;
    private List<String> frameworks;
    private List<String> tools;

    // Experience
    private List<String> internships;   // company names or descriptions
    private Integer internshipCount;
    private List<String> projects;
    private Integer projectCount;
    private List<String> certifications;
    private Integer certificationCount;

    // Career targets
    private String targetRole;          // SDE, Data Scientist, DevOps, etc.
    private List<String> targetCompanies;

    // Resume
    private String resumeFilePath;
    private String resumeText;          // extracted text for AI analysis

    // Roles
    private String role;                // STUDENT, ADMIN

    // Status flags
    private boolean isActive;
    private boolean isPlaced;
    private String placedCompany;

    private java.util.Map<String, Boolean> roadmapProgress; // e.g., {"Month 1": true, "Month 2": false}
    private java.util.Map<String, Boolean> roadmapTasksProgress; // e.g., {"Month 1_Task 1": true}
    
    private java.time.LocalDate lastActivityDate;
    private Integer completionStreak;

    @CreatedDate
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;
}
