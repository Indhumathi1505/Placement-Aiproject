package com.placeiq.service;

import com.placeiq.model.Prediction;
import com.placeiq.model.SkillGap;
import com.placeiq.model.Student;
import com.placeiq.repository.PredictionRepository;
import com.placeiq.repository.SkillGapRepository;
import com.placeiq.repository.StudentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class StudentService {

    private final StudentRepository studentRepository;
    private final PredictionRepository predictionRepository;
    private final SkillGapRepository skillGapRepository;
    private final AIService aiService;

    private static final String UPLOAD_DIR = "uploads/resumes/";

    // ─── CURRENT STUDENT ─────────────────────────────────────────────────────

    public Student getCurrentStudent() {
        String email = SecurityContextHolder.getContext().getAuthentication().getName();
        return studentRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Student not found"));
    }

    // ─── PROFILE ──────────────────────────────────────────────────────────────

    public Student getStudentById(String id) {
        return studentRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Student not found: " + id));
    }

    public Student updateProfile(String id, Student updates) {
        Student existing = getStudentById(id);
        if (updates.getName() != null) existing.setName(updates.getName());
        if (updates.getDepartment() != null) existing.setDepartment(updates.getDepartment());
        if (updates.getYear() != null) existing.setYear(updates.getYear());
        if (updates.getCollege() != null) existing.setCollege(updates.getCollege());
        if (updates.getPhoneNumber() != null) existing.setPhoneNumber(updates.getPhoneNumber());
        if (updates.getCgpa() != null) existing.setCgpa(updates.getCgpa());
        if (updates.getSkills() != null) existing.setSkills(updates.getSkills());
        if (updates.getTargetRole() != null) existing.setTargetRole(updates.getTargetRole());
        if (updates.getTargetCompanies() != null) existing.setTargetCompanies(updates.getTargetCompanies());
        if (updates.getInternshipCount() != null) existing.setInternshipCount(updates.getInternshipCount());
        if (updates.getProjectCount() != null) existing.setProjectCount(updates.getProjectCount());
        if (updates.getCertificationCount() != null) existing.setCertificationCount(updates.getCertificationCount());
        return studentRepository.save(existing);
    }

    public Student uploadProfilePicture(String id, MultipartFile file) throws IOException {
        String originalName = file.getOriginalFilename();
        if (originalName == null || (!originalName.toLowerCase().endsWith(".jpg") && !originalName.toLowerCase().endsWith(".jpeg") && !originalName.toLowerCase().endsWith(".png"))) {
            throw new IllegalArgumentException("Only JPG/JPEG/PNG files are accepted.");
        }

        Path uploadPath = Paths.get("uploads/profiles/");
        Files.createDirectories(uploadPath);
        String filename = id + "_" + UUID.randomUUID() + originalName.substring(originalName.lastIndexOf("."));
        Path filePath = uploadPath.resolve(filename);
        Files.copy(file.getInputStream(), filePath);

        Student student = getStudentById(id);
        // Serve through static handler or a dedicated controller. For simplicity, we'll store the relative path.
        student.setProfilePictureUrl("/api/students/profile-picture/" + filename);
        return studentRepository.save(student);
    }

    // ─── RESUME ───────────────────────────────────────────────────────────────

    /**
     * Save uploaded PDF and trigger AI analysis.
     */
    public Prediction uploadAndAnalyzeResume(String studentId, MultipartFile file) throws IOException {
        // Validate file type
        String originalName = file.getOriginalFilename();
        if (originalName == null || !originalName.toLowerCase().endsWith(".pdf")) {
            throw new IllegalArgumentException("Only PDF files are accepted.");
        }

        // Save file to disk
        Path uploadPath = Paths.get(UPLOAD_DIR);
        Files.createDirectories(uploadPath);
        String filename = studentId + "_" + UUID.randomUUID() + ".pdf";
        Path filePath = uploadPath.resolve(filename);
        Files.copy(file.getInputStream(), filePath);

        // Update student's resume path
        Student student = getStudentById(studentId);
        student.setResumeFilePath(filePath.toString());
        studentRepository.save(student);

        // Trigger AI analysis
        Prediction prediction = aiService.analyzeResume(file, student);

        // Permanently Update user's verified skills
        if (prediction.getExtractedSkills() != null && !prediction.getExtractedSkills().isEmpty()) {
            student.setSkills(prediction.getExtractedSkills());
            studentRepository.save(student);
            
            // Immediately refresh skill gap analysis with new verified skills
            analyzeSkillGap(studentId, student.getTargetRole());
        }

        return prediction;
    }

    // ─── PREDICTION ───────────────────────────────────────────────────────────

    public Prediction getLatestPrediction(String studentId) {
        return predictionRepository.findTopByStudentIdOrderByPredictedAtDesc(studentId)
                .orElseGet(() -> {
                    // If no prediction exists, generate one now
                    Student student = getStudentById(studentId);
                    return aiService.predictPlacement(student);
                });
    }

    public List<Prediction> getPredictionHistory(String studentId) {
        return predictionRepository.findByStudentIdOrderByPredictedAtDesc(studentId);
    }

    public Prediction refreshPrediction(String studentId) {
        Student student = getStudentById(studentId);
        return aiService.predictPlacement(student);
    }

    // ─── SKILL GAP ────────────────────────────────────────────────────────────

    public SkillGap getLatestSkillGap(String studentId) {
        return skillGapRepository.findTopByStudentIdOrderByAnalyzedAtDesc(studentId)
                .orElseGet(() -> {
                    Student student = getStudentById(studentId);
                    return aiService.analyzeSkillGap(student, student.getTargetRole());
                });
    }

    public SkillGap analyzeSkillGap(String studentId, String targetRole) {
        Student student = getStudentById(studentId);
        return aiService.analyzeSkillGap(student, targetRole);
    }

    // ─── ADMIN ────────────────────────────────────────────────────────────────

    public List<Student> getAllStudents() {
        return studentRepository.findAll();
    }

    public long getTotalStudents() {
        return studentRepository.count();
    }

    public long getPlacedCount() {
        return studentRepository.countByIsPlacedTrue();
    }

    public Student setPlacedStatus(String id, boolean placed) {
        Student student = getStudentById(id);
        student.setPlaced(placed);
        return studentRepository.save(student);
    }
}
