package com.capco.drools.config;

import org.kie.api.KieServices;
import org.kie.api.builder.*;
import org.kie.api.runtime.KieContainer;
import org.kie.api.runtime.KieSession;
import org.kie.internal.io.ResourceFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.io.File;

@Configuration
public class DroolsConfig {

    private static final String RULES_PATH = "rules/";

    @Bean
    public KieContainer kieContainer() {
        KieServices kieServices = KieServices.Factory.get();
        KieFileSystem kieFileSystem = kieServices.newKieFileSystem();

        // Load all DRL files from resources/rules directory
        loadRulesFromDirectory(kieFileSystem, RULES_PATH);

        KieBuilder kieBuilder = kieServices.newKieBuilder(kieFileSystem);
        kieBuilder.buildAll();

        KieModule kieModule = kieBuilder.getKieModule();
        Results results = kieBuilder.getResults();

        if (results.hasMessages(Message.Level.ERROR)) {
            throw new RuntimeException("Build Errors:\n" + results.toString());
        }

        return kieServices.newKieContainer(kieModule.getReleaseId());
    }

    private void loadRulesFromDirectory(KieFileSystem kieFileSystem, String rulesPath) {
        // Load comprehensive rules
        String[] ruleFiles = {
            "comprehensive.drl"
        };

        for (String ruleFile : ruleFiles) {
            String path = RULES_PATH + ruleFile;
            kieFileSystem.write(
                ResourceFactory.newClassPathResource(path)
            );
        }
    }

    @Bean
    public KieSession kieSession() {
        return kieContainer().newKieSession();
    }
}
