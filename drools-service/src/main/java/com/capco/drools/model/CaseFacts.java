package com.capco.drools.model;

import lombok.Data;
import java.util.ArrayList;
import java.util.List;

@Data
public class CaseFacts {
    // Case identification
    private String caseId;
    private String customerId;
    private String loanId;

    // Financial data
    private Double principalAmount;
    private Double overdueAmount;
    private Integer overdueDays;

    // Customer data
    private String customerSegment; // VIP, premium, standard, high_risk
    private Integer creditScore;
    private String riskLevel;

    // Case status
    private String status;
    private Integer priority;
    private String assignedTo;

    // Contact history
    private Integer contactCount;
    private Integer dailyContactCount;
    private Integer contactAttemptsToday;
    private Double contactSuccessRate;

    // Flags
    private Boolean disputeFlag;
    private Boolean legalFlag;
    private Boolean paymentPromiseKept;

    // Timing
    private Integer currentHour;
    private String currentDay; // monday, tuesday, etc.
    private Integer daysSinceLastContact;

    // Scores and ratings
    private Double willingnessScore;
    private Double abilityScore;

    // Results (populated by rules)
    private Boolean canContact;
    private List<String> violations = new ArrayList<>();
    private List<String> recommendations = new ArrayList<>();
    private String recommendedChannel;
    private String recommendedScript;
    private String recommendedAction;
    private List<String> tags = new ArrayList<>();

    // Modifications tracking
    private Integer priorityAdjustment = 0;

    public void addViolation(String violation) {
        this.violations.add(violation);
    }

    public void addRecommendation(String recommendation) {
        this.recommendations.add(recommendation);
    }

    public void addTag(String tag) {
        this.tags.add(tag);
    }

    public void adjustPriority(int adjustment) {
        this.priorityAdjustment += adjustment;
        if (this.priority != null) {
            this.priority += adjustment;
        }
    }
}
