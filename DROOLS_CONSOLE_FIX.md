# Drools Console Fix - Opens BPMN.js Designer

## Problem
Clicking "Drools Console" or "Open Drools Console" buttons opened:
```
http://localhost:8081/api/rules/health
```
This just showed a health check page, not a visual designer.

## Expected Behavior
Should open the BPMN.js/DMN.js visual designer to create and edit decision tables.

## Root Cause
The `openDrools()` function in `DmnModeler.tsx` was hardcoded to open an external URL instead of the integrated designer.

## Solution Applied

### 1. Fixed DmnModeler.tsx
**File**: `loan-agent-frontend/src/components/bpmn/DmnModeler.tsx`

**Before:**
```typescript
const openDrools = () => {
  window.open('http://localhost:8081/api/rules/health', '_blank');
};
```

**After:**
```typescript
const openDrools = () => {
  // Open the DMN designer in the same app instead of external Drools console
  window.location.href = '/workflows/designer?mode=dmn';
};
```

### 2. Enhanced WorkflowManagementPage
**File**: `loan-agent-frontend/src/pages/workflows/WorkflowManagementPage.tsx`

Added support for `?mode=dmn` query parameter:
```typescript
import { useSearchParams } from 'react-router-dom';

// Check for mode parameter on mount
useEffect(() => {
  const mode = searchParams.get('mode');
  if (mode === 'dmn') {
    setActiveTab('dmn');
  } else if (mode === 'bpmn') {
    setActiveTab('bpmn');
  }
}, [searchParams]);
```

## How It Works Now

### User Flow
1. User clicks **"Open Drools Console"** button
2. Navigates to `/workflows/designer?mode=dmn`
3. WorkflowManagementPage detects `mode=dmn` parameter
4. Automatically switches to DMN tab
5. DMN designer (dmn-js) loads
6. User can visually create decision tables

### Visual Designer Features
- **DMN Decision Tables**: Visual editor for business rules
- **BPMN Workflows**: Process flow designer
- **Drag & Drop**: Visual modeling interface
- **Export**: Can export to Drools DRL format
- **Deploy**: Deploy directly to Camunda/Drools

## Where This Button Appears

The "Open Drools Console" button appears in:
1. DMN Modeler component toolbar
2. DMN empty state card
3. Any page that uses the DmnModelerComponent

## URLs and Routes

```
Frontend Routes:
  /workflows/designer              → Opens BPMN tab by default
  /workflows/designer?mode=bpmn   → Opens BPMN workflow designer
  /workflows/designer?mode=dmn    → Opens DMN decision table designer

Old (Wrong):
  http://localhost:8081/api/rules/health  ❌ Just health check

New (Correct):
  /workflows/designer?mode=dmn            ✅ Visual DMN designer
```

## Testing

### Test the Fix
1. Navigate to `/workflows/designer`
2. Click the "DMN Decision Tables" tab
3. Click "Open Drools Console" button
4. Should stay in app and show DMN designer (not open external URL)

### Alternative Access
- From Rules page: Click "Configure" or "Open DMN Designer"
- From Workflows page: Click "Open BPMN/DMN Designer"
- Direct URL: `/workflows/designer?mode=dmn`

## What Changed

### Files Modified
```
✅ loan-agent-frontend/src/components/bpmn/DmnModeler.tsx
   - Changed openDrools() to navigate to /workflows/designer?mode=dmn

✅ loan-agent-frontend/src/pages/workflows/WorkflowManagementPage.tsx
   - Added useSearchParams hook
   - Added useEffect to detect mode parameter
   - Auto-switches tab based on ?mode=dmn or ?mode=bpmn
```

## Benefits

1. **Integrated Experience**: No need to open external services
2. **Visual Designer**: Full BPMN.js and DMN.js modelers
3. **Consistent UI**: Stays within the application
4. **Better UX**: Direct access to the actual designer, not a health page

## Summary

✅ **Drools Console button** now opens the integrated DMN designer
✅ **Query parameter support** for direct access to BPMN or DMN tabs
✅ **No more external health page** - proper visual designer loads
✅ **Works from multiple entry points** - Rules page, Workflows page, DMN modeler

The Drools Console button now does what users expect - opens a visual rule designer! 🎉
