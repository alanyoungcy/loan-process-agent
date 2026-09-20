package com.capco.drools.service;

import com.capco.drools.model.CaseFacts;
import com.capco.drools.model.RuleResult;
import org.kie.api.runtime.KieContainer;
import org.kie.api.runtime.KieSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class RulesExecutionService {

    @Autowired
    private KieContainer kieContainer;

    public RuleResult executeRules(CaseFacts facts) {
        // Create a new session for each execution
        KieSession kieSession = kieContainer.newKieSession();

        try {
            // Initialize result tracking
            facts.setCanContact(true); // Default to true

            // Insert facts into session
            kieSession.insert(facts);

            // Fire all rules
            int rulesFired = kieSession.fireAllRules();

            // Build result
            RuleResult result = new RuleResult();
            result.setCaseId(facts.getCaseId());
            result.setCanContact(facts.getCanContact());
            result.setPriority(facts.getPriority());
            result.setPriorityAdjustment(facts.getPriorityAdjustment());
            result.setViolations(facts.getViolations());
            result.setRecommendations(facts.getRecommendations());
            result.setRecommendedChannel(facts.getRecommendedChannel());
            result.setRecommendedScript(facts.getRecommendedScript());
            result.setRecommendedAction(facts.getRecommendedAction());
            result.setTags(facts.getTags());
            result.setAssignedTo(facts.getAssignedTo());
            result.addAction("Executed " + rulesFired + " rules");

            return result;

        } finally {
            kieSession.dispose();
        }
    }
}
