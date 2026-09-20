package com.capco.camunda.service;

import com.capco.camunda.model.CaseFacts;
import com.capco.camunda.model.RuleResult;
import org.camunda.bpm.dmn.engine.DmnDecision;
import org.camunda.bpm.dmn.engine.DmnDecisionTableResult;
import org.camunda.bpm.dmn.engine.DmnEngine;
import org.camunda.bpm.engine.variable.VariableMap;
import org.camunda.bpm.engine.variable.Variables;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.InputStream;
import java.util.*;

@Service
public class DmnExecutionService {

    @Autowired
    private DmnEngine dmnEngine;

    private Map<String, DmnDecision> decisionCache = new HashMap<>();

    public RuleResult executeRules(CaseFacts facts) {
        RuleResult result = new RuleResult();
        result.setCaseId(facts.getCaseId());
        result.setCanContact(true); // Default to true unless compliance rules say otherwise

        try {
            // Prepare variables
            VariableMap variables = Variables.createVariables();
            variables.put("currentHour", facts.getCurrentHour());
            variables.put("dailyContactCount", facts.getDailyContactCount());
            variables.put("currentDay", facts.getCurrentDay());
            variables.put("riskLevel", facts.getRiskLevel());
            variables.put("overdueAmount", facts.getOverdueAmount());
            variables.put("overdueDays", facts.getOverdueDays());
            variables.put("customerSegment", facts.getCustomerSegment());

            // Execute compliance check
            DmnDecisionTableResult complianceResult = evaluateDecision("compliance-check.dmn", "complianceCheck", variables);
            processComplianceResult(complianceResult, result);

            // Execute priority scoring
            DmnDecisionTableResult priorityResult = evaluateDecision("priority-scoring.dmn", "priorityScoring", variables);
            processPriorityResult(priorityResult, result, facts);

            // Execute contact strategy (only if can contact)
            if (result.getCanContact()) {
                DmnDecisionTableResult strategyResult = evaluateDecision("contact-strategy.dmn", "contactStrategy", variables);
                processStrategyResult(strategyResult, result);
            }

        } catch (Exception e) {
            result.setStatus("error");
            result.setMessage("Error executing DMN rules: " + e.getMessage());
        }

        return result;
    }

    private DmnDecisionTableResult evaluateDecision(String dmnFile, String decisionKey, VariableMap variables) {
        try {
            DmnDecision decision = decisionCache.get(decisionKey);
            if (decision == null) {
                InputStream inputStream = new ClassPathResource("dmn/" + dmnFile).getInputStream();
                List<DmnDecision> decisions = dmnEngine.parseDecisions(inputStream);
                decision = decisions.stream()
                        .filter(d -> d.getKey().equals(decisionKey))
                        .findFirst()
                        .orElseThrow(() -> new RuntimeException("Decision not found: " + decisionKey));
                decisionCache.put(decisionKey, decision);
            }
            return dmnEngine.evaluateDecisionTable(decision, variables);
        } catch (Exception e) {
            throw new RuntimeException("Failed to evaluate decision: " + decisionKey, e);
        }
    }

    private void processComplianceResult(DmnDecisionTableResult result, RuleResult ruleResult) {
        for (Map<String, Object> row : result.getResultList()) {
            Boolean canContact = (Boolean) row.get("canContact");
            if (canContact != null && !canContact) {
                ruleResult.setCanContact(false);
            }

            String violation = (String) row.get("violation");
            if (violation != null && !violation.isEmpty()) {
                ruleResult.getViolations().add(violation);
            }

            String recommendation = (String) row.get("recommendation");
            if (recommendation != null && !recommendation.isEmpty()) {
                ruleResult.getRecommendations().add(recommendation);
            }

            String tag = (String) row.get("tag");
            if (tag != null && !tag.isEmpty()) {
                ruleResult.getTags().add(tag);
            }
        }
    }

    private void processPriorityResult(DmnDecisionTableResult result, RuleResult ruleResult, CaseFacts facts) {
        int totalAdjustment = 0;

        for (Map<String, Object> row : result.getResultList()) {
            Integer adjustment = (Integer) row.get("priorityAdjustment");
            if (adjustment != null) {
                totalAdjustment += adjustment;
            }

            String recommendation = (String) row.get("recommendation");
            if (recommendation != null && !recommendation.isEmpty()) {
                ruleResult.getRecommendations().add(recommendation);
            }

            String tag = (String) row.get("tag");
            if (tag != null && !tag.isEmpty()) {
                ruleResult.getTags().add(tag);
            }
        }

        ruleResult.setPriorityAdjustment(totalAdjustment);
        if (facts.getPriority() != null) {
            ruleResult.setFinalPriority(facts.getPriority() + totalAdjustment);
        }
    }

    private void processStrategyResult(DmnDecisionTableResult result, RuleResult ruleResult) {
        if (!result.isEmpty()) {
            Map<String, Object> firstMatch = result.getSingleResult();

            String channel = (String) firstMatch.get("recommendedChannel");
            if (channel != null) {
                ruleResult.setRecommendedChannel(channel);
            }

            String script = (String) firstMatch.get("recommendedScript");
            if (script != null) {
                ruleResult.setRecommendedScript(script);
            }

            String recommendation = (String) firstMatch.get("recommendation");
            if (recommendation != null && !recommendation.isEmpty()) {
                ruleResult.getRecommendations().add(recommendation);
            }
        }
    }
}
