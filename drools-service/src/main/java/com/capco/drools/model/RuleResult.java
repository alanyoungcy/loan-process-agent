package com.capco.drools.model;

import lombok.Data;
import java.util.ArrayList;
import java.util.List;

@Data
public class RuleResult {
    private String caseId;
    private List<String> rulesExecuted = new ArrayList<>();
    private List<String> actionsTaken = new ArrayList<>();
    private List<String> violations = new ArrayList<>();
    private List<String> recommendations = new ArrayList<>();
    private Boolean canContact;
    private Integer priority;
    private Integer priorityAdjustment;
    private String assignedTo;
    private String recommendedChannel;
    private String recommendedScript;
    private String recommendedAction;
    private List<String> tags = new ArrayList<>();
    private Boolean applied;

    public void addRuleExecuted(String ruleName) {
        this.rulesExecuted.add(ruleName);
    }

    public void addAction(String action) {
        this.actionsTaken.add(action);
    }
}
