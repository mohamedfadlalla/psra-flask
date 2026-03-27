# Auto-Clear Dashboard Notifications Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement client-side auto-clearing for dashboard notification badges using localStorage.

**Architecture:** Use frontend JavaScript in `dashboard.html` to store previously seen badge counts in `localStorage`. Compare current template-rendered counts against stored counts. Only show badges if the current count is greater than the stored count (i.e., new items arrived). Finally, update localStorage with the current counts so they are marked as "seen".

**Tech Stack:** HTML, Jinja2, JavaScript (localStorage)

---

### Task 1: Inject Jinja badge counts into JavaScript

**Files:**
- Modify: `templates/dashboard.html` (script tag at the bottom)

**Step 1: Modify the template**

Add a script block that serializes the Jinja `badge_counts` dictionary into a JavaScript object.

```html
<script>
    // Inject server-side badge counts into JS
    const currentBadgeCounts = {
        events: {{ badge_counts.events | default(0) }},
        projects: {{ badge_counts.projects | default(0) }},
        mentorships: {{ badge_counts.mentorships | default(0) }},
        research: {{ badge_counts.research | default(0) }},
        announcements: {{ badge_counts.announcements | default(0) }}
    };
</script>
```

**Step 2: Commit**
```bash
git add templates/dashboard.html
git commit -m "feat(dashboard): inject badge counts into JS"
```

---

### Task 2: Implement localStorage comparison logic

**Files:**
- Modify: `templates/dashboard.html` (inside the DOMContentLoaded listener)

**Step 1: Add comparison logic**

Read `dashboard_seen_counts` from localStorage. For each badge type, check if a badge element exists. If the current count is less than or equal to the seen count, hide the badge. Update `localStorage` with the new counts.

```javascript
    document.addEventListener("DOMContentLoaded", function() {
        // ... existing code ...

        // Notification Auto-Clear Logic
        const seenCountsJSON = localStorage.getItem('dashboard_seen_counts');
        let seenCounts = {};
        if (seenCountsJSON) {
            try {
                seenCounts = JSON.parse(seenCountsJSON);
            } catch (e) {
                console.error("Error parsing seen counts", e);
            }
        }

        const badgeElements = {
            events: document.querySelector('.dashboard-tile-events .dashboard-tile-badge'),
            projects: document.querySelector('.dashboard-tile-projects .dashboard-tile-badge'),
            mentorships: document.querySelector('.dashboard-tile-mentorships .dashboard-tile-badge'),
            research: document.querySelector('.dashboard-tile-research .dashboard-tile-badge'),
            announcements: document.querySelector('.dashboard-tile-announcements .dashboard-tile-badge')
        };

        // Compare current counts with seen counts
        for (const [key, currentCount] of Object.entries(currentBadgeCounts)) {
            const seenCount = seenCounts[key] || 0;
            const badgeEl = badgeElements[key];
            
            if (badgeEl) {
                if (currentCount <= seenCount) {
                    // No new items, hide the badge
                    badgeEl.style.display = 'none';
                } else {
                    // Show only the difference (number of NEW items)
                    const newItemsCount = currentCount - seenCount;
                    badgeEl.textContent = newItemsCount;
                    badgeEl.style.display = 'inline-block'; // Or whatever display property is appropriate
                }
            }
        }

        // Update localStorage with current counts to mark them as seen
        localStorage.setItem('dashboard_seen_counts', JSON.stringify(currentBadgeCounts));
```

**Step 2: Commit**
```bash
git add templates/dashboard.html
git commit -m "feat(dashboard): implement auto-clearing notification logic via localStorage"
```