# Mentorship Settings Feature Design

## Goal
Extract the mentorship opt-in from the main edit profile page into a dedicated settings page and add "Program/Field" and "Duration" options for mentors.

## Database & Architecture
- **Models**: Add `mentorship_program` (String) and `mentorship_duration` (String) fields to `AlumniProfile` and `ResearcherProfile` models.
- **Migration**: Apply a database migration to add these new fields.

## Forms & Data Flow
- **Forms**:
  - Remove `open_to_mentor` from `ProfileForm`.
  - Create `MentorshipSettingsForm` with fields: `open_to_mentor` (Boolean), `mentorship_program` (String), and `mentorship_duration` (String).
- **Routes**:
  - Add `/profile/mentorship` route in `forum/routes.py` to handle displaying and saving the new `MentorshipSettingsForm`. Only users with role ALUMNI or RESEARCHER can access/save this.

## UI Components & Frontend
- **Navigation**: Add a "Mentorship Settings" link in the top navigation profile dropdown (in `base.html`).
- **Settings Page (`mentorship_settings.html`)**:
  - A form with the "Open to Mentorship" checkbox.
  - If checked, show `mentorship_program` and `mentorship_duration` text inputs using JavaScript.
- **Mentors Directory (`mentors.html`)**:
  - Update the mentor cards to display the offered "Program/Field" and "Duration" when available.
  
## Cleanup
- Remove the `open_to_mentor` checkbox logic and rendering from the main `edit_profile.html` and `forum/routes.py` `edit_profile` function.