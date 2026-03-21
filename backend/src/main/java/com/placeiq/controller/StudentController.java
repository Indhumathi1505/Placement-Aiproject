package com.placeiq.controller;

import com.placeiq.model.Prediction;
import com.placeiq.model.SkillGap;
import com.placeiq.model.Student;
import com.placeiq.service.StudentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.net.MalformedURLException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/students")
@RequiredArgsConstructor
public class StudentController {

    private final StudentService studentService;

    // ─── PROFILE ──────────────────────────────────────────────────────────────

    @GetMapping("/me")
    public ResponseEntity<Student> getMyProfile() {
        return ResponseEntity.ok(studentService.getCurrentStudent());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Student> getStudentById(@PathVariable String id) {
        return ResponseEntity.ok(studentService.getStudentById(id));
    }

    @PutMapping("/{id}")
    public ResponseEntity<Student> updateProfile(@PathVariable String id,
                                                  @RequestBody Student updates) {
        return ResponseEntity.ok(studentService.updateProfile(id, updates));
    }

    @PostMapping("/{id}/profile-picture")
    public ResponseEntity<Student> uploadProfilePicture(@PathVariable String id,
                                                         @RequestParam("file") MultipartFile file) throws IOException {
        return ResponseEntity.ok(studentService.uploadProfilePicture(id, file));
    }

    @GetMapping("/profile-picture/{filename}")
    public ResponseEntity<org.springframework.core.io.Resource> getProfilePicture(@PathVariable String filename) throws IOException {
        Path filePath = Paths.get("uploads/profiles/").resolve(filename);
        org.springframework.core.io.Resource resource = new org.springframework.core.io.UrlResource(filePath.toUri());
        return ResponseEntity.ok()
                .contentType(org.springframework.http.MediaType.IMAGE_JPEG)
                .body(resource);
    }

    // ─── RESUME ───────────────────────────────────────────────────────────────

    /**
     * POST /api/students/{id}/resume
     * Accepts a multipart PDF, runs AI analysis, returns Prediction.
     */
    @PostMapping("/{id}/resume")
    public ResponseEntity<Prediction> uploadResume(@PathVariable String id,
                                                    @RequestParam("file") MultipartFile file)
            throws IOException {
        return ResponseEntity.ok(studentService.uploadAndAnalyzeResume(id, file));
    }

    // ─── PREDICTION ───────────────────────────────────────────────────────────

    @GetMapping("/{id}/prediction")
    public ResponseEntity<Prediction> getLatestPrediction(@PathVariable String id) {
        return ResponseEntity.ok(studentService.getLatestPrediction(id));
    }

    @GetMapping("/{id}/prediction/history")
    public ResponseEntity<List<Prediction>> getPredictionHistory(@PathVariable String id) {
        return ResponseEntity.ok(studentService.getPredictionHistory(id));
    }

    @PostMapping("/{id}/prediction/refresh")
    public ResponseEntity<Prediction> refreshPrediction(@PathVariable String id) {
        return ResponseEntity.ok(studentService.refreshPrediction(id));
    }

    // ─── SKILL GAP ────────────────────────────────────────────────────────────

    @GetMapping("/{id}/skill-gap")
    public ResponseEntity<SkillGap> getSkillGap(@PathVariable String id,
                                                  @RequestParam(required = false) String role) {
        if (role != null && !role.isBlank()) {
            return ResponseEntity.ok(studentService.analyzeSkillGap(id, role));
        }
        return ResponseEntity.ok(studentService.getLatestSkillGap(id));
    }

    // ─── ADMIN ────────────────────────────────────────────────────────────────

    @GetMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<List<Student>> getAllStudents() {
        return ResponseEntity.ok(studentService.getAllStudents());
    }

    @GetMapping("/stats")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> getStats() {
        return ResponseEntity.ok(Map.of(
                "total", studentService.getTotalStudents(),
                "placed", studentService.getPlacedCount()
        ));
    }

    /** Toggle a student's placement status (Admin only) */
    @PutMapping("/{id}/placed")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Student> togglePlaced(@PathVariable String id, @RequestBody Map<String, Boolean> body) {
        return ResponseEntity.ok(studentService.setPlacedStatus(id, body.getOrDefault("placed", false)));
    }

    /** Download a student's uploaded resume PDF (Admin only) */
    @GetMapping("/{id}/resume/download")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<org.springframework.core.io.Resource> downloadResume(@PathVariable String id) throws MalformedURLException {
        Student s = studentService.getStudentById(id);
        if (s.getResumeFilePath() == null) {
            return ResponseEntity.notFound().build();
        }
        Path filePath = Paths.get(s.getResumeFilePath());
        org.springframework.core.io.Resource resource = new org.springframework.core.io.UrlResource(filePath.toUri());
        String filename = filePath.getFileName().toString();
        return ResponseEntity.ok()
                .header(org.springframework.http.HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .contentType(org.springframework.http.MediaType.APPLICATION_PDF)
                .body(resource);
    }
}
