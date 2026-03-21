package com.placeiq.service;

import com.placeiq.dto.AuthDTO;
import com.placeiq.model.Student;
import com.placeiq.repository.StudentRepository;
import com.placeiq.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final StudentRepository studentRepository;
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
}
