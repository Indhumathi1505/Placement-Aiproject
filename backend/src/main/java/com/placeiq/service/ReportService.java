package com.placeiq.service;

import com.placeiq.model.Prediction;
import com.placeiq.model.Student;
import com.placeiq.repository.PredictionRepository;
import com.placeiq.repository.StudentRepository;
import jakarta.mail.MessagingException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class ReportService {

    private final EmailService emailService;
    private final StudentRepository studentRepository;
    private final PredictionRepository predictionRepository;

    public void sendCareerReportByEmail(String email) throws MessagingException {
        Student student = studentRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("Student not found"));
        
        Optional<Prediction> predictionOpt = predictionRepository.findTopByStudentIdOrderByPredictedAtDesc(student.getId());
        
        String htmlBody = buildReportHtml(student, predictionOpt);
        emailService.sendHtmlEmail(student.getEmail(), "Your PlaceIQ Career Progress Report", htmlBody);
    }

    private String buildReportHtml(Student s, Optional<Prediction> pOpt) {
        StringBuilder html = new StringBuilder();
        html.append("<html><body style='font-family: Arial, sans-serif; color: #333; line-height: 1.6;'>");
        html.append("<div style='max-width: 600px; margin: 0 auto; border: 1px solid #e1e8f0; border-radius: 12px; overflow: hidden;'>");
        
        // Header
        html.append("<div style='background: #0C1422; padding: 30px; text-align: center;'>");
        html.append("<h1 style='color: #4F9EFF; margin: 0; font-size: 24px;'>PlaceIQ Career Report</h1>");
        html.append("<p style='color: #7A95B5; margin: 5px 0 0 0;'>AI-Powered Placement Insights</p>");
        html.append("</div>");

        // Body
        html.append("<div style='padding: 30px;'>");
        html.append("<p>Hello <strong>").append(s.getName()).append("</strong>,</p>");
        html.append("<p>Here is your personalized career readiness report based on your latest profile and resume analysis.</p>");
        
        // Stats
        html.append("<div style='background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;'>");
        html.append("<h3 style='margin-top: 0; color: #0C1422;'>📊 Placement Metrics</h3>");
        if (pOpt.isPresent()) {
            Prediction p = pOpt.get();
            html.append("<p><strong>Placement Probability:</strong> <span style='color: #4F9EFF;'>").append(Math.round(p.getPlacementProbability() * 100)).append("%</span></p>");
            html.append("<p><strong>ATS Score:</strong> <span style='color: #3DDCB2;'>").append(p.getAtsScore()).append("/100</span></p>");
            html.append("<p><strong>Readiness Score:</strong> ").append(p.getReadinessScore()).append("/10</p>");
        } else {
            html.append("<p style='color: #FF6B6B;'>No analysis found. Upload your resume to get insights.</p>");
        }
        html.append("</div>");

        // Profile
        html.append("<h3 style='color: #0C1422;'>🧩 Profile Summary</h3>");
        html.append("<p><strong>Target Role:</strong> ").append(s.getTargetRole() != null ? s.getTargetRole() : "Not set").append("</p>");
        html.append("<p><strong>Skills:</strong> ").append(s.getSkills() != null ? String.join(", ", s.getSkills()) : "None identified").append("</p>");

        // Roadmap
        html.append("<h3 style='color: #0C1422;'>🗺️ Roadmap Progress</h3>");
        if (s.getRoadmapTasksProgress() != null && !s.getRoadmapTasksProgress().isEmpty()) {
            long completed = s.getRoadmapTasksProgress().values().stream().filter(v -> v).count();
            long total = s.getRoadmapTasksProgress().size();
            double pct = (double)completed / total * 100;
            html.append("<p>Progress: ").append(Math.round(pct)).append("% (").append(completed).append("/").append(total).append(" tasks completed)</p>");
        } else {
            html.append("<p>Roadmap not started yet. Head to the app to generate your path!</p>");
        }

        html.append("<div style='margin-top: 30px; padding-top: 20px; border-top: 1px solid #e1e8f0; text-align: center;'>");
        html.append("<a href='https://placeiq-frontend.vercel.app' style='background: #4F9EFF; color: #fff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;'>Open PlaceIQ Dashboard</a>");
        html.append("</div>");

        html.append("</div>"); // End content
        
        // Footer
        html.append("<div style='background: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b;'>");
        html.append("<p>Best regards,<br>The PlaceIQ AI Team</p>");
        html.append("<p>&copy; 2026 PlaceIQ. All rights reserved.</p>");
        html.append("</div>");

        html.append("</div></body></html>");
        return html.toString();
    }
}
