package com.placeiq.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.util.List;

// ─── AUTH ────────────────────────────────────────────────────────────────────

public class AuthDTO {

    @Data
    public static class LoginRequest {
        @NotBlank @Email
        private String email;

        @NotBlank @Size(min = 6)
        private String password;
    }

    @Data
    public static class RegisterRequest {
        @NotBlank
        private String name;

        @NotBlank @Email
        private String email;

        @NotBlank @Size(min = 6)
        private String password;

        private String department;
        private String year;
        private String rollNumber;
        private String college;
        private String phoneNumber;
        private Double cgpa;
        private List<String> skills;
        private String targetRole;
        private List<String> targetCompanies;
        private String profilePictureUrl;
    }

    @Data
    public static class AuthResponse {
        private String token;
        private String studentId;
        private String name;
        private String email;
        private String role;
        private String department;
        private String profilePictureUrl;

        public AuthResponse(String token, String studentId, String name,
                            String email, String role, String department, String profilePictureUrl) {
            this.token = token;
            this.studentId = studentId;
            this.name = name;
            this.email = email;
            this.role = role;
            this.department = department;
            this.profilePictureUrl = profilePictureUrl;
        }
    }
}
