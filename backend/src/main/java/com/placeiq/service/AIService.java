package com.placeiq.service;

import com.placeiq.model.Prediction;
import com.placeiq.model.SkillGap;
import com.placeiq.model.Student;
import com.placeiq.repository.PredictionRepository;
import com.placeiq.repository.SkillGapRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.io.IOException;
import java.time.Duration;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class AIService {

    private final WebClient aiWebClient;
    private final PredictionRepository predictionRepository;
    private final SkillGapRepository skillGapRepository;

    @org.springframework.beans.factory.annotation.Value("${ai.service.url}")
    private String aiServiceUrl;

    // ─── RESUME ANALYSIS ──────────────────────────────────────────────────────

    /**
     * Extract raw text from uploaded PDF resume using Apache PDFBox,
     * then send it to Python AI microservice for analysis.
     */
    public Prediction analyzeResume(MultipartFile file, Student student) throws IOException {
        // 1. Extract text from PDF
        String resumeText = extractTextFromPdf(file);
        log.info("Extracted {} chars from resume PDF", resumeText.length());

        // 2. Build request payload for Python service
        Map<String, Object> payload = new HashMap<>();
        payload.put("resume_text", resumeText);
        payload.put("student_id", student.getId());
        payload.put("target_role", student.getTargetRole() != null ? student.getTargetRole() : "SDE");
        payload.put("target_companies", student.getTargetCompanies() != null ? student.getTargetCompanies() : List.of());

        // 3. Call Python AI microservice
        Map<String, Object> aiResponse = callAiService("/analyze/resume", payload);

        // 4. Build and persist Prediction document
        Prediction prediction = Prediction.builder()
                .studentId(student.getId())
                .placementProbability(getDouble(aiResponse, "placement_probability"))
                .readinessScore(getDouble(aiResponse, "readiness_score"))
                .resumeScore(getInt(aiResponse, "resume_score"))
                .atsScore(getInt(aiResponse, "ats_score"))
                .companyProbabilities(castToDoubleMap(aiResponse.get("company_probabilities")))
                .extractedSkills(castToStringList(aiResponse.get("extracted_skills")))
                .missingSkills(castToStringList(aiResponse.get("missing_skills")))
                .overallSummary((String) aiResponse.get("summary"))
                .aiRecommendations(castToStringList(aiResponse.get("recommendations")))
                .improvementTips(castToStringList(aiResponse.get("improvement_tips")))
                .cgpaAtPrediction(student.getCgpa())
                .skillsAtPrediction(student.getSkills())
                .predictedAt(java.time.LocalDateTime.now())
                .build();

        return predictionRepository.save(prediction);
    }

    // ─── PLACEMENT PREDICTION ─────────────────────────────────────────────────

    /**
     * Predict placement probability based on student profile (no resume required).
     */
    public Prediction predictPlacement(Student student) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("student_id", student.getId());
        payload.put("cgpa", student.getCgpa() != null ? student.getCgpa() : 0.0);
        payload.put("skills", student.getSkills() != null ? student.getSkills() : List.of());
        payload.put("internship_count", student.getInternshipCount());
        payload.put("project_count", student.getProjectCount());
        payload.put("certification_count", student.getCertificationCount());
        payload.put("backlogs", student.getBacklogs());
        payload.put("target_role", student.getTargetRole() != null ? student.getTargetRole() : "SDE");
        payload.put("target_companies", student.getTargetCompanies() != null ? student.getTargetCompanies() : List.of());

        Map<String, Object> aiResponse = callAiService("/predict/placement", payload);

        Prediction prediction = Prediction.builder()
                .studentId(student.getId())
                .placementProbability(getDouble(aiResponse, "placement_probability"))
                .readinessScore(getDouble(aiResponse, "readiness_score"))
                .atsScore(getInt(aiResponse, "ats_score"))
                .resumeScore(getInt(aiResponse, "resume_score"))
                .companyProbabilities(castToDoubleMap(aiResponse.get("company_probabilities")))
                .aiRecommendations(castToStringList(aiResponse.get("recommendations")))
                .cgpaAtPrediction(student.getCgpa())
                .skillsAtPrediction(student.getSkills())
                .predictedAt(java.time.LocalDateTime.now())
                .build();

        return predictionRepository.save(prediction);
    }

    // ─── SKILL GAP ANALYSIS ───────────────────────────────────────────────────

    public SkillGap analyzeSkillGap(Student student, String targetRole) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("student_id", student.getId());
        payload.put("current_skills", student.getSkills() != null ? student.getSkills() : List.of());
        String finalRole = targetRole != null ? targetRole : student.getTargetRole();
        payload.put("target_role", finalRole != null ? finalRole : "SDE");
        payload.put("cgpa", student.getCgpa() != null ? student.getCgpa() : 0.0);

        Map<String, Object> aiResponse = callAiService("/analyze/skill-gap", payload);

        // Build SkillEntry list
        List<SkillGap.SkillEntry> skillEntries = new ArrayList<>();
        Object rawEntries = aiResponse.get("skill_entries");
        if (rawEntries instanceof List<?> entries) {
            for (Object entry : entries) {
                if (entry instanceof Map<?, ?> m) {
                    skillEntries.add(SkillGap.SkillEntry.builder()
                            .skillName((String) m.get("skill_name"))
                            .currentLevel(((Number) m.get("current_level")).intValue())
                            .requiredLevel(((Number) m.get("required_level")).intValue())
                            .priority((String) m.get("priority"))
                            .build());
                }
            }
        }

        // Build CourseRecommendation list
        List<SkillGap.CourseRecommendation> courses = new ArrayList<>();
        Object rawCourses = aiResponse.get("recommended_courses");
        if (rawCourses instanceof List<?> courseList) {
            for (Object course : courseList) {
                if (course instanceof Map<?, ?> c) {
                    courses.add(SkillGap.CourseRecommendation.builder()
                            .skillName((String) c.get("skill_name"))
                            .courseName((String) c.get("course_name"))
                            .platform((String) c.get("platform"))
                            .url((String) c.get("url"))
                            .duration((String) c.get("duration"))
                            .priority((String) c.get("priority"))
                            .build());
                }
            }
        }

        SkillGap gap = SkillGap.builder()
                .studentId(student.getId())
                .targetRole(targetRole != null ? targetRole : student.getTargetRole())
                .currentSkills(skillEntries)
                .missingSkills(castToStringList(aiResponse.get("missing_skills")))
                .criticalSkills(castToStringList(aiResponse.get("critical_skills")))
                .recommendedCourses(courses)
                .gapScore(getDouble(aiResponse, "gap_score"))
                .estimatedWeeksToClose(getInt(aiResponse, "estimated_weeks"))
                .analyzedAt(java.time.LocalDateTime.now())
                .build();

        return skillGapRepository.save(gap);
    }

    // ─── INTERVIEW QUESTIONS ──────────────────────────────────────────────────

    public List<Map<String, String>> generateInterviewQuestions(String targetRole,
                                                                  String company,
                                                                  String difficulty) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("target_role", targetRole);
        payload.put("company", company);
        payload.put("difficulty", difficulty);
        payload.put("count", 7);

        Map<String, Object> aiResponse = callAiService("/generate/interview-questions", payload);

        Object questions = aiResponse.get("questions");
        if (questions instanceof List<?> list) {
            return list.stream()
                    .filter(q -> q instanceof Map)
                    .map(q -> (Map<String, String>) q)
                    .toList();
        }
        return Collections.emptyList();
    }

    // ─── HTTP HELPER ──────────────────────────────────────────────────────────

    @SuppressWarnings("unchecked")
    private Map<String, Object> callAiService(String path, Map<String, Object> payload) {
        // Ensure path doesn't start with / if baseUrl already has it, or vice versa
        String cleanPath = path.startsWith("/") ? path.substring(1) : path;
        
        try {
            log.info("Calling AI service at: {}/{}", aiServiceUrl, cleanPath);
            return aiWebClient.post()
                    .uri(cleanPath)
                    .bodyValue(payload)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .timeout(Duration.ofSeconds(120))
                    .block();
        } catch (Exception e) {
            log.error("CRITICAL: AI service call failed for {}/{} | Error: {}", 
                      aiServiceUrl, cleanPath, e.getMessage());
            return buildFallbackResponse(e.getMessage());
        }
    }

    private Map<String, Object> buildFallbackResponse(String error) {
        Map<String, Object> fallback = new HashMap<>();
        fallback.put("placement_probability", 0.5);
        fallback.put("readiness_score", 5.0);
        fallback.put("resume_score", 50);
        fallback.put("ats_score", 50);
        fallback.put("company_probabilities", Map.of());
        fallback.put("extracted_skills", List.of());
        fallback.put("missing_skills", List.of());
        fallback.put("critical_skills", List.of());
        fallback.put("skill_entries", List.of());
        fallback.put("recommended_courses", List.of());
        fallback.put("gap_score", 0.5);
        fallback.put("estimated_weeks", 8);
        fallback.put("summary", "AI Analysis was unable to connect to the smart engine. ERROR: " + error);
        fallback.put("recommendations", List.of());
        fallback.put("improvement_tips", List.of());
        return fallback;
    }

    // ─── PDF EXTRACTION ───────────────────────────────────────────────────────

    private String extractTextFromPdf(MultipartFile file) throws IOException {
        try (PDDocument document = Loader.loadPDF(file.getBytes())) {
            PDFTextStripper stripper = new PDFTextStripper();
            return stripper.getText(document);
        }
    }

    // ─── TYPE HELPERS ─────────────────────────────────────────────────────────

    private Double getDouble(Map<String, Object> map, String key) {
        Object val = map.get(key);
        if (val instanceof Number n) return n.doubleValue();
        return 0.0;
    }

    private Integer getInt(Map<String, Object> map, String key) {
        Object val = map.get(key);
        if (val instanceof Number n) return n.intValue();
        return 0;
    }

    @SuppressWarnings("unchecked")
    private List<String> castToStringList(Object obj) {
        if (obj instanceof List<?> list) {
            return list.stream().map(Object::toString).toList();
        }
        return Collections.emptyList();
    }

    @SuppressWarnings("unchecked")
    private Map<String, Double> castToDoubleMap(Object obj) {
        if (obj instanceof Map<?, ?> map) {
            Map<String, Double> result = new LinkedHashMap<>();
            map.forEach((k, v) -> result.put(k.toString(), ((Number) v).doubleValue()));
            return result;
        }
        return Collections.emptyMap();
    }
}
