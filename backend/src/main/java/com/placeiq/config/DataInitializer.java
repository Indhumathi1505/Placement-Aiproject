package com.placeiq.config;

import com.placeiq.model.Student;
import com.placeiq.repository.StudentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.List;

@Configuration
@RequiredArgsConstructor
@Slf4j
public class DataInitializer {

    private final StudentRepository studentRepository;
    private final PasswordEncoder passwordEncoder;

    @Bean
    public CommandLineRunner initializeAdminUser() {
        return args -> {
            String adminEmail = "admin@placeiq.com";
            
            if (!studentRepository.existsByEmail(adminEmail)) {
                log.info("Creating default admin account...");
                
                Student admin = Student.builder()
                        .name("System Admin")
                        .email(adminEmail)
                        .passwordHash(passwordEncoder.encode("admin123"))
                        .department("Administration")
                        .role("ADMIN")
                        .isActive(true)
                        .isPlaced(false)
                        .skills(List.of("System Administration", "Management"))
                        .targetRole("Administrator")
                        .build();

                studentRepository.save(admin);
                log.info("Default admin account created successfully.");
            } else {
                log.info("Admin account already exists.");
            }
        };
    }
}
