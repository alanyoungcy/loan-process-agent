# 🔧 Debugging Visual Editors

## How to Check What's Wrong

### Step 1: Open Browser Console
1. Go to http://localhost:5173/workflows/designer
2. Press **F12** or right-click → **Inspect**
3. Click **Console** tab

### Step 2: Look for Error Messages

You should see console logs like:
- `🔧 Initializing BPMN modeler...`
- `✅ BPMN modeler created`
- `📄 Importing BPMN XML...`
- `✅ BPMN XML imported successfully`

**If you see errors**, they will tell us exactly what's wrong:
- Missing imports?
- CSS not loading?
- XML parsing errors?

### Step 3: Check Network Tab
1. Click **Network** tab in DevTools
2. Refresh the page
3. Look for any **404 errors** or **failed** requests
4. Especially check for:
   - `diagram-js.css`
   - `bpmn-js.css`
   - `dmn-js-*.css`

---

## Common Issues & Fixes

### Issue 1: Editors Show "Loading..." Forever
**Cause**: JavaScript error preventing initialization

**Fix**: Check console for errors

### Issue 2: Blank White Box
**Cause**: CSS not loading or container height = 0

**Fix**: 
- Check Network tab for CSS 404s
- Container has explicit height (700px)

### Issue 3: "Failed to load editor" Error
**Cause**: XML parsing error or library import issue

**Fix**: Check console for specific error message

---

## 🎯 Action Items

1. **Open http://localhost:5173/workflows/designer**
2. **Open browser console (F12)**
3. **Tell me what errors you see**

I've added detailed console logging, so you'll see exactly where it fails!

---

## Quick Test

Try this in the browser console:
```javascript
// Check if libraries loaded
console.log('BpmnModeler:', typeof BpmnModeler);
console.log('DmnModeler:', typeof DmnModeler);
```

If both say "undefined", the imports failed.
