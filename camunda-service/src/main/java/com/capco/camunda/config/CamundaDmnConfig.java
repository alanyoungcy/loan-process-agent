package com.capco.camunda.config;

import org.camunda.bpm.dmn.engine.DmnDecisionTableResult;
import org.camunda.bpm.dmn.engine.DmnEngine;
import org.camunda.bpm.dmn.engine.DmnEngineConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class CamundaDmnConfig {

    @Bean
    public DmnEngine dmnEngine() {
        return DmnEngineConfiguration
                .createDefaultDmnEngineConfiguration()
                .buildEngine();
    }
}
