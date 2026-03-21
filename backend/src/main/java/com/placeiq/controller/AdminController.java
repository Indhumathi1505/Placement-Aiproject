package com.placeiq.controller;

import com.placeiq.model.Student;
import com.placeiq.service.StudentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
@PreAuthorize("hasRole('ADMIN')")
public class AdminController {

    private final StudentService studentService;

    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        return ResponseEntity.ok(Map.of(
                "total", studentService.getTotalStudents(),
                "placed", studentService.getPlacedCount()
        ));
    }

    @GetMapping("/students")
    public ResponseEntity<List<Student>> getAllStudents() {
        return ResponseEntity.ok(studentService.getAllStudents());
    }

    @PutMapping("/students/{id}/placed")
    public ResponseEntity<Student> togglePlaced(@PathVariable String id, @RequestBody Map<String, Boolean> body) {
        return ResponseEntity.ok(studentService.setPlacedStatus(id, body.getOrDefault("placed", false)));
    }
}
