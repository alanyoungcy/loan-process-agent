# Fake/Mock Content Audit

## Areas to Review and Clean:

### 1. Dashboard Page
- Stats cards (may have hardcoded numbers)
- Charts (may have mock data)
- Recent activity feed

### 2. Cases List Page
- Case list (may be hardcoded)
- Pagination
- Filters

### 3. Analytics Page
- Charts and graphs
- Performance metrics
- Trend data

### 4. Case Detail Page
- Customer information
- Case history
- Action logs

### 5. GenAI Page
- Chat history
- Suggestions

### 6. Settings Page
- User preferences
- System settings

---

## Pages Already Clean:

✅ **Workflows Page** - Shows real workflows from Camunda  
✅ **Rules Page** - Shows real DMN decisions from Camunda  
✅ **BPMN Designer** - Real workflow editor  
✅ **DMN Designer** - Real decision editor  

---

## Next Steps:

Will review each page and either:
1. Connect to real backend API
2. Show "No data yet" state
3. Remove mock data entirely
