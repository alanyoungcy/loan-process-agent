package com.capco.camunda.model;

import lombok.Data;
import java.util.ArrayList;
import java.util.List;

@Data
public class RuleResult {
    private String caseId;
    private Boolean canContact;
    private List<String> violations = new ArrayList<>();
    private List<String> recommendations = new ArrayList<>();
    private String recommendedChannel;
    private String recommendedScript;
    private String recommendedAction;
    private List<String> tags = new ArrayList<>();
    private Integer priorityAdjustment = 0;
    private Integer finalPriority;

    private String status = "success";
    private String message = "Rules evaluated successfully";
}
