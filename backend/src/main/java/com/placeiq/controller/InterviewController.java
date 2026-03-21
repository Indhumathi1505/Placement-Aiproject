package com.placeiq.controller;

import com.placeiq.service.AIService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/interview")
@RequiredArgsConstructor
public class InterviewController {

    private final AIService aiService;

    /**
     * GET /api/interview/questions?role=SDE&company=TCS&difficulty=Medium
     * Returns AI-generated interview questions for the given parameters.
     */
    @GetMapping("/questions")
    public ResponseEntity<List<Map<String, String>>> getQuestions(
            @RequestParam(defaultValue = "SDE") String role,
            @RequestParam(defaultValue = "General") String company,
            @RequestParam(defaultValue = "Medium") String difficulty) {

        List<Map<String, String>> questions =
                aiService.generateInterviewQuestions(role, company, difficulty);
        return ResponseEntity.ok(questions);
    }
}
