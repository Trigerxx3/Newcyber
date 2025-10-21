# Case Activities - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Access a Case
1. Navigate to **Admin → Cases** (`/admin/cases`)
2. Click the **"View"** button on any case
3. You'll see the case details page with tabs

### Step 2: Add Your First Activity
1. Click the **"Activities"** tab
2. Click **"+ Add Activity"** button
3. Fill in the form:
   - **Title**: "Initial suspect identification"
   - **Description**: "Through social media analysis, identified 3 potential suspects based on communication patterns..."
   - **Type**: Finding
   - **Priority**: High
   - **Tags**: suspect-1, social-media
   - **Time Spent**: 120 minutes
   - ✅ **Include in PDF report**: Checked
4. Click **"Create"**

### Step 3: Generate PDF Report
1. Click **"Download PDF Report"** button (top right)
2. Your PDF will include all activities marked for report inclusion
3. PDF contains:
   - Case overview
   - Your activity with full details
   - Time tracking
   - Professional formatting

---

## 📋 Activity Types Explained

| Type | When to Use | Example |
|------|-------------|---------|
| **Note** | General investigation notes | "Reviewed suspect's social media history" |
| **Finding** | Important discoveries | "Found evidence of drug trafficking network" |
| **Evidence** | Evidence collection | "Collected screenshots of incriminating messages" |
| **Interview** | Interview documentation | "Interview with Suspect A - denied involvement" |
| **Analysis** | Analysis results | "Analysis shows pattern of coordinated activity" |
| **Action** | Actions taken | "Issued search warrant for suspect's residence" |
| **Meeting** | Team meetings | "Briefing with law enforcement partners" |
| **Observation** | Notable observations | "Suspect changed phone number after surveillance began" |
| **Recommendation** | Next steps | "Recommend additional surveillance for 2 weeks" |

---

## 🎯 Common Workflows

### Daily Investigation Logging
```
Morning:
1. Add activity: Type = "Note", Title = "Daily investigation log - [Date]"
2. Document what you're working on today
3. Mark "Include in report" = false (daily logs usually excluded)

During Investigation:
1. When you find something important → Type = "Finding"
2. When you collect evidence → Type = "Evidence"
3. When you analyze data → Type = "Analysis"

End of Day:
1. Review activities
2. Toggle report inclusion for important items
3. Update time spent
```

### Interview Documentation
```
Before Interview:
1. Type = "Note", Title = "Pre-interview preparation"
2. Document questions and approach

During Interview:
1. Type = "Interview", Title = "Interview with [Subject Name]"
2. Full transcript or detailed notes
3. Priority = High (if critical)

After Interview:
1. Type = "Analysis", Title = "Interview analysis"
2. Key takeaways and next steps
```

### Evidence Collection
```
For Each Evidence Item:
1. Type = "Evidence"
2. Title = Brief description
3. Description = Full details, where found, how obtained
4. Tags = evidence-type, location, date
5. ✅ Include in report = true
```

---

## 💡 Pro Tips

### 1. Use Tags Effectively
```
✅ Good tags:
- suspect-1, suspect-2, suspect-3
- location-downtown, location-warehouse
- evidence-digital, evidence-physical
- high-value, medium-value

❌ Poor tags:
- important (too vague)
- misc (not useful)
- 123 (not descriptive)
```

### 2. Track Time Accurately
- Round to nearest 15 minutes
- Include research, analysis, and documentation time
- Don't forget meeting time
- Use summary to see total time invested

### 3. Report Inclusion Strategy
```
✅ Include in Report:
- Key findings
- Evidence collected
- Interview summaries
- Analysis conclusions
- Recommendations

❌ Exclude from Report:
- Daily routine notes
- Internal team communications
- Incomplete drafts
- Personal reminders
```

### 4. Edit vs. New Activity
```
EDIT existing activity when:
- Adding more details to same topic
- Correcting information
- Updating status

CREATE new activity when:
- Different topic or finding
- Different day/timeframe
- Different type of work
```

---

## 🔍 Finding Activities

### Use Filters
1. **All** - Show everything
2. **In Report** - Show only items included in PDF
3. **By Type** - Filter by activity type (dropdown)

### Sort & Search
- Activities sorted by date (newest first)
- Use browser Ctrl+F to search within visible activities

---

## 📊 Activity Summary

At the top of the Activities tab, you'll see:

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Total Activities│  Time Tracked   │  Most Common    │  Contributors   │
│       25        │     42.5h       │     Finding     │        3        │
│  20 in report   │  2,550 minutes  │  Activity type  │     Analysts    │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

This gives you instant insight into:
- How much work has been done
- How much time invested
- What type of work is most common
- How many team members involved

---

## 📄 Generate Reports

### Two Options in Reports Tab

1. **Basic Report** (Download icon 📥)
   - Standard case report
   - Case details and summary
   - Quick generation

2. **Detailed Report** (Chart icon 📊) ← **NEW!**
   - Everything from basic report PLUS:
   - All analyst activities (grouped by type)
   - Time tracking summaries
   - Evidence and content sections
   - Professional multi-page format

### Download from Case Details
- Click "Download PDF Report" on case details page
- Generates detailed report with all activities marked for inclusion

---

## ⚙️ Settings & Options

### Priority Levels
- **Low** - Routine work
- **Medium** - Standard investigation work (default)
- **High** - Important findings or time-sensitive
- **Critical** - Urgent, case-breaking information

### Visibility Levels
- **Team** - Visible to all team members (default)
- **Confidential** - Marked as sensitive

### Status
- **Active** - Current/ongoing (default)
- **Completed** - Finished
- **Archived** - Historical reference

---

## ❓ FAQ

**Q: Can I delete an activity?**  
A: Yes, if you created it. Admins can delete any activity.

**Q: What happens when I edit an activity?**  
A: Edit count increments, and "edited by" information is stored.

**Q: Can I attach files?**  
A: File upload is coming in a future update. For now, add URLs in description.

**Q: How do I share activities with the team?**  
A: All activities are visible to the team by default. PDF reports can be exported and shared.

**Q: What if I forget to track time?**  
A: You can edit the activity later and add time spent.

**Q: Can I import activities from a spreadsheet?**  
A: Not yet, but you can copy-paste into the description field.

---

## 🎓 Best Practices

1. **Be Descriptive** - Write titles and descriptions that will make sense weeks later
2. **Tag Consistently** - Use same tag format across activities
3. **Track Time** - Helps justify resources and demonstrates thoroughness
4. **Edit, Don't Duplicate** - Update existing activities rather than creating duplicates
5. **Mark Confidential** - Protect sensitive information appropriately
6. **Review Before PDF** - Check report inclusion flags before generating final report
7. **Regular Updates** - Log work daily while details are fresh

---

## 🆘 Troubleshooting

**Activities not showing in PDF?**
- Check the "Include in report" flag (eye icon)
- Must be checked/enabled

**Can't create activity?**
- Title and description are required
- Check you're authenticated
- Try refreshing the page

**Time not adding up?**
- View Activities Summary for totals
- Each activity's time contributes to total

**Lost changes?**
- Changes save immediately on submit
- If browser crashes, recently saved activities are preserved
- Edit count shows how many times activity was modified

---

## 📞 Need Help?

For technical issues or questions:
- Check the console for error messages (F12)
- Verify backend is running (check health endpoint)
- Review logs in browser developer tools
- Check that migrations are applied

---

**Ready to track your investigation work like a pro! 🚀**

