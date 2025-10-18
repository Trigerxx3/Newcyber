# Using Both Spiderfoot and Sherlock in the UI

## ✅ What I've Done

I've enhanced the User Investigation UI to beautifully display results from **BOTH Spiderfoot and Sherlock** tools, clearly showing which tool found each profile.

## 🎨 New UI Features

### 1. **Grouped Results by Tool**
Results are now organized into separate cards by source:
- 🕷️ **Spiderfoot** (purple) - Comprehensive OSINT
- 🔍 **Sherlock** (blue) - Social Media Discovery  
- 🌐 **URL Checker** (green) - Fast URL Verification

### 2. **Tool-Specific Statistics**
The "Investigation Details" tab now shows:
- Status for each tool (✅ success or ❌ error)
- Number of findings per tool
- Error messages if a tool fails
- Tool-specific metadata

### 3. **Confidence Badges**
Spiderfoot results show confidence levels (high/medium/low)

### 4. **Color-Coded Display**
Each tool has its own color theme for easy identification

## 🚀 How to Use

### Step 1: Start Spiderfoot Web UI (Required for Spiderfoot Results)

**Option A: Double-click the batch file**
```
start_spiderfoot.bat
```

**Option B: Run manually**
```powershell
cd osint_tools\spiderfoot
python sf.py -l 127.0.0.1:5001
```

Keep this window open!

### Step 2: Start Your Backend

```powershell
cd flask_backend
python run.py
```

### Step 3: Start Your Frontend

```powershell
cd cyber
npm run dev
```

### Step 4: Use the UI

1. Go to `http://localhost:3000/dashboard/user-investigation`
2. Enter a username (e.g., "testuser123")
3. Click "Start Investigation"
4. Wait 30-60 seconds

## 📊 What You'll See

### Without Spiderfoot Running

```
🔍 Sherlock (Social Media): 160 profiles
🌐 URL Checker (Fast Check): 15 profiles

Total: ~175 profiles
Time: 10-30 seconds
```

### With Spiderfoot Running

```
🕷️ Spiderfoot (Comprehensive OSINT): 50+ profiles
🔍 Sherlock (Social Media): 160 profiles
🌐 URL Checker (Fast Check): 15 profiles

Total: ~225+ profiles
Time: 30-60 seconds
```

## 🎯 UI Examples

### Linked Profiles Tab
Shows profiles grouped by source tool:

```
🕷️ Spiderfoot (Comprehensive OSINT) [52 profiles]
├─ GitHub [high confidence]
├─ Twitter [medium confidence]
└─ LinkedIn [high confidence]

🔍 Sherlock (Social Media) [160 profiles]
├─ Instagram
├─ Reddit
└─ TikTok
  ... and 157 more

🌐 URL Checker (Fast Check) [15 profiles]
├─ GitHub
├─ YouTube
└─ Spotify
  ... and 12 more
```

### Investigation Details Tab
Shows tool-specific statistics:

```
🕷️ Spiderfoot
   Status: ✅ completed
   Findings: 52

🔍 Sherlock
   Status: ✅ success
   Profiles Found: 160

🌐 URL Checker
   Status: ✅ success
   Profiles Found: 15
   Method: URL pattern checking
```

## 🔍 Features

### Profile Cards
Each profile shows:
- ✅ Platform name
- ✅ Full URL (clickable)
- ✅ Confidence badge (for Spiderfoot)
- ✅ External link button
- ✅ Hover effects

### Tool Status
- Green badge = Success
- Red badge = Error
- Shows error messages if tools fail

### Smart Fallback
- If Spiderfoot isn't running, you still get Sherlock + URL Checker
- No error messages, just works!

## 📝 Troubleshooting

### "Only seeing Sherlock results"
**Solution**: Start Spiderfoot web UI using `start_spiderfoot.bat`

### "Spiderfoot shows error in UI"
**Reason**: Web UI not running
**Check**: Open `http://127.0.0.1:5001` in browser - should see Spiderfoot interface

### "Investigation is slow"
**Normal**: Spiderfoot takes 30-60 seconds for comprehensive scans
**Tip**: Sherlock results appear first, then Spiderfoot results are added

## 🎨 Color Scheme

| Tool | Color | Icon | Purpose |
|------|-------|------|---------|
| Spiderfoot | Purple | 🕷️ | Comprehensive OSINT, multiple data types |
| Sherlock | Blue | 🔍 | Fast social media discovery |
| URL Checker | Green | 🌐 | Quick URL pattern verification |

## ✨ Benefits

✅ **Clear Attribution** - See which tool found each profile
✅ **Visual Organization** - Color-coded, easy to scan
✅ **Detailed Stats** - Know exactly what each tool found
✅ **Professional UI** - Beautiful, modern interface
✅ **Error Transparency** - See if a tool fails and why
✅ **Confidence Indicators** - Know how reliable each finding is

## 🎯 Best Practices

### For Comprehensive Results:
1. Start Spiderfoot web UI first
2. Allow 60 seconds for investigation
3. Check all three tool sections

### For Quick Results:
1. Just run without Spiderfoot
2. Get results in 10-30 seconds
3. Still covers 400+ platforms via Sherlock

## 📊 Expected Output

### Investigation Results Header
```
Investigation Results for "username"
High Risk | high Confidence

Found 225 potential profiles for username 'username'
```

### Tools Used Badge
```
Tools: spiderfoot, sherlock, fallback_api
```

### Results Breakdown
Each tool's results are displayed in separate, color-coded cards with:
- Tool icon and name
- Profile count badge
- List of found profiles with URLs
- Confidence levels (for Spiderfoot)
- External link buttons

## 🚀 Summary

Your User Investigation UI now:
- ✅ Displays Spiderfoot results beautifully
- ✅ Shows Sherlock results separately
- ✅ Groups results by source tool
- ✅ Provides detailed statistics
- ✅ Uses color-coding for easy identification
- ✅ Shows confidence levels
- ✅ Handles errors gracefully

Just start Spiderfoot web UI and both tools will work together perfectly in the UI! 🎉
