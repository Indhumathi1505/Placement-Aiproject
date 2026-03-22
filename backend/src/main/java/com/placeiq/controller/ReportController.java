package com.placeiq.controller;

import com.placeiq.service.ReportService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/reports")
@RequiredArgsConstructor
@CrossOrigin
public class ReportController {

    private final ReportService reportService;

    @PostMapping("/send-email")
    public ResponseEntity<String> sendEmailReport(@AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails == null) {
            return ResponseEntity.status(401).body("User not authenticated");
        }
        
        try {
            // Find student by email (which is the username in our Security config)
            reportService.sendCareerReportByEmail(userDetails.getUsername());
            return ResponseEntity.ok("Report sent successfully to " + userDetails.getUsername());
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.internalServerError().body("Failed to send report: " + e.getMessage());
        }
    }
}
