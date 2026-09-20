package com.capco.drools.controller;

import com.capco.drools.model.CaseFacts;
import com.capco.drools.model.RuleResult;
import com.capco.drools.service.RulesExecutionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/rules")
@CrossOrigin(origins = "*")
public class RulesController {

    @Autowired
    private RulesExecutionService rulesExecutionService;

    @PostMapping("/evaluate")
    public ResponseEntity<RuleResult> evaluateCase(@RequestBody CaseFacts facts) {
        RuleResult result = rulesExecutionService.executeRules(facts);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "healthy");
        response.put("service", "Drools Rules Engine");
        return ResponseEntity.ok(response);
    }

    @GetMapping("/list")
    public ResponseEntity<Map<String, Object>> listRules() {
        Map<String, Object> response = new HashMap<>();
        response.put("total_rules", 15);
        response.put("categories", new String[]{
            "compliance", "priority", "assignment", "strategy", "risk"
        });
        return ResponseEntity.ok(response);
    }
}
