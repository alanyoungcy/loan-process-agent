package com.capco.drools.model;

import lombok.Data;
import java.util.List;

@Data
public class RuleInfo {
    private String name;
    private String description;
    private String category;
    private Integer priority;
    private Boolean enabled;
    private List<String> tags;
    private Long executionCount;
}
