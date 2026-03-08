# Messages UI Mobile Optimization Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Overhaul the UI of the messages list and conversation chat interfaces using Tailwind CSS to ensure they are mobile-responsive, modern, and visually consistent with the rest of the application.

**Architecture:** We will strip out the legacy inline `<style>` blocks in both templates and replace them with Tailwind utility classes. The HTML structure will be modernized to support flexbox layouts, rounded corners, and cleaner typography.

**Tech Stack:** Jinja2 Templates, Tailwind CSS

---

### Task 1: Overhaul Messages List UI (`messages.html`)

**Files:**
- Modify: `templates/messages.html`

**Step 1: Remove custom CSS**
Remove the `<style>` block at the bottom of the file entirely.

**Step 2: Update Header and Layout**
Update the main container and header to use responsive flexbox classes, ensuring buttons stack neatly on mobile.

**Step 3: Redesign Conversation Cards**
Transform the conversation items into sleek, clickable cards.
- Add hover effects (`hover:bg-gray-50`, `transition-colors`).
- Replace the "View Conversation" button with a subtle chevron or make the whole card clickable.
- Style unread badges with Tailwind (`bg-red-500 text-white rounded-full`).
- Truncate the latest message preview (`truncate`).
- Style the "No conversations" empty state with a centered, soft background layout.

**Step 4: Commit**
```bash
git add templates/messages.html
git commit -m "style(messages): overhaul messages list UI with Tailwind CSS for mobile responsiveness"
```

---

### Task 2: Overhaul Conversation Chat UI (`conversation.html`)

**Files:**
- Modify: `templates/conversation.html`

**Step 1: Remove custom CSS**
Remove the `<style>` block at the bottom of the file entirely.

**Step 2: Update Header and Layout**
Redesign the header. Remove the bulky "Back to Messages" button and replace it with a clean back arrow `<` icon. Arrange the title and action buttons (Delete, New Message) to fit comfortably on mobile screens.

**Step 3: Redesign Chat Messages**
Style the chat bubbles:
- Sent messages: `bg-primary-blue text-white ml-auto rounded-2xl rounded-br-sm`.
- Received messages: `bg-gray-100 text-gray-800 mr-auto rounded-2xl rounded-bl-sm`.
- Style the date markers, timestamps, and read receipts (`✓✓`) with subtle gray text.
- Improve the display of the delete button on hover (using Tailwind `group-hover` or similar).

**Step 4: Redesign Reply Form**
Remove the bulky "Reply" heading. Style the input form to look like a modern chat interface docked at the bottom, using flexbox to place the input field and send button side-by-side or stacked cleanly.

**Step 5: Commit**
```bash
git add templates/conversation.html
git commit -m "style(messages): overhaul conversation chat UI with Tailwind CSS for mobile responsiveness"
```