package com.capco.camunda.controller;

import com.capco.camunda.model.CaseFacts;
import com.capco.camunda.model.RuleResult;
import com.capco.camunda.service.DmnExecutionService;
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
    private DmnExecutionService dmnExecutionService;

    @PostMapping("/evaluate")
    public ResponseEntity<RuleResult> evaluateCase(@RequestBody CaseFacts facts) {
        RuleResult result = dmnExecutionService.executeRules(facts);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> response = new HashMap<>();
        response.put("status", "healthy");
        response.put("service", "Camunda DMN Engine");
        return ResponseEntity.ok(response);
    }

    @GetMapping("/list")
    public ResponseEntity<Map<String, Object>> listRules() {
        Map<String, Object> response = new HashMap<>();
        response.put("total_decisions", 3);
        response.put("decisions", new String[]{
            "complianceCheck", "priorityScoring", "contactStrategy"
        });
        response.put("engine", "Camunda DMN");
        return ResponseEntity.ok(response);
    }
}
