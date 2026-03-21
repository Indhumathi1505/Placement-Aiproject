package com.placeiq.controller;

import com.placeiq.model.Student;
import com.placeiq.repository.StudentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/roadmap")
@RequiredArgsConstructor
public class RoadmapController {

    private final StudentRepository studentRepository;

    @PostMapping("/progress")
    public ResponseEntity<Student> updateProgress(@RequestBody Map<String, Boolean> progress) {
        String email = ((UserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsername();
        Student student = studentRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));

        // If the key contains an underscore, it's a task: "Month 1_Task Name"
        Map<String, Boolean> taskProgress = student.getRoadmapTasksProgress();
        if (taskProgress == null) taskProgress = new HashMap<>();

        Map<String, Boolean> monthProgress = student.getRoadmapProgress();
        if (monthProgress == null) monthProgress = new HashMap<>();

        for (Map.Entry<String, Boolean> entry : progress.entrySet()) {
            if (entry.getKey().contains("_")) {
                taskProgress.put(entry.getKey(), entry.getValue());
            } else {
                monthProgress.put(entry.getKey(), entry.getValue());
            }
        }
        
        student.setRoadmapTasksProgress(taskProgress);
        student.setRoadmapProgress(monthProgress);

        // Streak logic
        java.time.LocalDate today = java.time.LocalDate.now();
        java.time.LocalDate last = student.getLastActivityDate();
        Integer streak = student.getCompletionStreak();
        if (streak == null) streak = 0;

        if (last == null) {
            streak = 1;
        } else if (last.equals(today.minusDays(1))) {
            streak++;
        } else if (!last.equals(today)) {
            streak = 1;
        }
        
        student.setLastActivityDate(today);
        student.setCompletionStreak(streak);
        
        return ResponseEntity.ok(studentRepository.save(student));
    }

    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        String email = ((UserDetails) SecurityContextHolder.getContext().getAuthentication().getPrincipal()).getUsername();
        Student student = studentRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));

        Map<String, Boolean> progress = student.getRoadmapProgress();
        if (progress == null) {
            progress = new HashMap<>();
        }

        long completed = progress.values().stream().filter(v -> v).count();
        int total = 6; // Standard 6-month roadmap

        Map<String, Object> stats = new HashMap<>();
        stats.put("completed", completed);
        stats.put("pending", total - completed);
        stats.put("percentage", (double) completed / total * 100);

        return ResponseEntity.ok(stats);
    }
}
