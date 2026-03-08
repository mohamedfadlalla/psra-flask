# Dashboard UI/UX Improvements Design

**Goal:** Transform the current dashboard navigation cards into content widgets with previews, and add a consolidated chronological activity feed below them to improve mobile UX and quick data consumption.

**Architecture:**
- **Backend (`app.py`):** Update the `dashboard` route to not only fetch the separate lists of jobs, events, announcements, etc. (which we need for the widget previews), but to also aggregate them into a single `feed_items` list. Each feed item will be a normalized dictionary (type, title, subtitle, timestamp, url/details). Sort this list descending by timestamp.
- **Frontend (`dashboard.html`):** 
  - Restructure the top section from a 2-column grid to a 3-column grid (`grid-cols-3` on desktop, maybe `grid-cols-2` on mobile) of smaller tiles. Remove the old accordion logic from these tiles. Add 1-line dynamic previews to each card (e.g., the title of the newest event).
  - Add a new "Recent Updates" section below the grid. Render the `feed_items` list as a vertical timeline. 
  - Attach the existing accordion expand/collapse JavaScript logic to the items in this new activity feed.

**Key Components:**
- Widget Grid (Events, Jobs, Projects, Mentorships, Research, Announcements)
- Unified Activity Feed
- Inline Expand/Collapse JS for the Feed