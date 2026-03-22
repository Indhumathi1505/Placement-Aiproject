package com.placeiq.service;

import com.placeiq.dto.AuthDTO;
import com.placeiq.model.Student;
import com.placeiq.model.PasswordResetToken;
import com.placeiq.repository.PasswordResetTokenRepository;
import com.placeiq.repository.StudentRepository;
import com.placeiq.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;
import java.util.regex.Pattern;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final StudentRepository studentRepository;
    private final PasswordResetTokenRepository tokenRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final AuthenticationManager authenticationManager;

    public AuthDTO.AuthResponse login(AuthDTO.LoginRequest request) {
        try {
            authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword())
            );
        } catch (Exception e) {
            throw new BadCredentialsException("Invalid email or password");
        }

        Student student = studentRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));

        String token = jwtUtil.generateToken(student.getEmail(), student.getRole());

        return new AuthDTO.AuthResponse(
                token,
                student.getId(),
                student.getName(),
                student.getEmail(),
                student.getRole(),
                student.getDepartment(),
                student.getProfilePictureUrl()
        );
    }

    public AuthDTO.AuthResponse register(AuthDTO.RegisterRequest request) {
        validatePassword(request.getPassword());
        
        if (studentRepository.existsByEmail(request.getEmail())) {
            throw new IllegalStateException("Email already registered: " + request.getEmail());
        }

        Student student = Student.builder()
                .name(request.getName())
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .department(request.getDepartment())
                .year(request.getYear())
                .rollNumber(request.getRollNumber())
                .college(request.getCollege())
                .phoneNumber(request.getPhoneNumber())
                .cgpa(request.getCgpa())
                .skills(request.getSkills())
                .targetRole(request.getTargetRole())
                .targetCompanies(request.getTargetCompanies())
                .profilePictureUrl(request.getProfilePictureUrl())
                .role("STUDENT")
                .isActive(true)
                .isPlaced(false)
                .build();

        student = studentRepository.save(student);

        String token = jwtUtil.generateToken(student.getEmail(), student.getRole());

        return new AuthDTO.AuthResponse(
                token,
                student.getId(),
                student.getName(),
                student.getEmail(),
                student.getRole(),
                student.getDepartment(),
                student.getProfilePictureUrl()
        );
    }

    private void validatePassword(String password) {
        if (password == null || password.length() < 8) {
            throw new IllegalArgumentException("Password must be at least 8 characters long");
        }
        
        boolean hasUppercase = !password.equals(password.toLowerCase());
        boolean hasDigit = password.chars().anyMatch(Character::isDigit);
        boolean hasSpecial = Pattern.compile("[!@#$%^&*(),.?\":{}|<>]").matcher(password).find();
        
        if (!hasUppercase || !hasDigit || !hasSpecial) {
            throw new IllegalArgumentException("Password must contain at least one uppercase letter, one digit, and one special character");
        }
    }

    public void processForgotPassword(String email) {
        Student student = studentRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("User not found: " + email));
        
        // Use static mock for reset token deletion for safety
        tokenRepository.deleteByUserEmail(email);
        
        String token = UUID.randomUUID().toString();
        PasswordResetToken resetToken = PasswordResetToken.builder()
                .token(token)
                .userEmail(email)
                .expiryDate(LocalDateTime.now().plusMinutes(15))
                .build();
        
        tokenRepository.save(resetToken);
        
        // Mock email sending
        System.out.println("DEBUG: Password reset link: http://localhost:5500/frontend/reset-password.html?token=" + token);
    }

    public void resetPassword(String token, String newPassword) {
        PasswordResetToken resetToken = tokenRepository.findByToken(token)
                .orElseThrow(() -> new IllegalArgumentException("Invalid or expired token"));
        
        if (resetToken.isExpired()) {
            tokenRepository.delete(resetToken);
            throw new IllegalArgumentException("Invalid or expired token");
        }
        
        validatePassword(newPassword);
        
        Student student = studentRepository.findByEmail(resetToken.getUserEmail())
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));
        
        student.setPasswordHash(passwordEncoder.encode(newPassword));
        studentRepository.save(student);
        
        tokenRepository.delete(resetToken);
    }
}
