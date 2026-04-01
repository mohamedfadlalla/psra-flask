# Mentorship Settings Feature Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extract mentorship opt-in from the main profile edit page into a dedicated settings page and add "Program/Field" and "Duration" fields.

**Architecture:** We will add fields to the database models, create a new form and route for the settings, and update the UI templates to integrate the new page and display the new fields in the mentor directory.

**Tech Stack:** Python, Flask, SQLAlchemy, WTForms, Jinja2, HTML/CSS/JS

---

### Task 1: Update Database Models and Generate Migration

**Files:**
- Modify: `models.py`
- Create: Migration script via `flask db migrate`

**Step 1: Write the failing test**
Run: `pytest tests/` (assuming basic test setup, though checking DB models directly is tricky without specific test files. We will verify by running the app/db commands).
Let's just update the models.

**Step 2: Write minimal implementation**
In `models.py`, add `mentorship_program` and `mentorship_duration` to both `AlumniProfile` and `ResearcherProfile`:

```python
# models.py - under AlumniProfile
mentorship_program = db.Column(db.String(200), nullable=True)
mentorship_duration = db.Column(db.String(100), nullable=True)

# models.py - under ResearcherProfile
mentorship_program = db.Column(db.String(200), nullable=True)
mentorship_duration = db.Column(db.String(100), nullable=True)
```

**Step 3: Generate Migration**
Run: `flask db migrate -m "add mentorship fields"`

**Step 4: Upgrade Database**
Run: `flask db upgrade`

**Step 5: Commit**
```bash
git add models.py migrations/
git commit -m "feat(models): add mentorship_program and mentorship_duration fields"
```

---

### Task 2: Create MentorshipSettingsForm

**Files:**
- Modify: `forum/forms.py`

**Step 1: Write minimal implementation**
Add `MentorshipSettingsForm` to `forum/forms.py`.

```python
class MentorshipSettingsForm(FlaskForm):
    open_to_mentor = BooleanField('Open to Mentorship Requests')
    mentorship_program = StringField('Mentorship Program/Field', validators=[Optional(), Length(max=200)])
    mentorship_duration = StringField('Duration', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Save Settings')
```

Remove `open_to_mentor` from `ProfileForm` in `forum/forms.py`.

**Step 2: Commit**
```bash
git add forum/forms.py
git commit -m "feat(forms): add MentorshipSettingsForm and remove open_to_mentor from ProfileForm"
```

---

### Task 3: Implement Backend Routes

**Files:**
- Modify: `forum/routes.py`

**Step 1: Write minimal implementation**
In `forum/routes.py`, update `edit_profile` to remove `open_to_mentor` logic.
Add a new route `/profile/mentorship`.

```python
from forum.forms import MentorshipSettingsForm

@forum_bp.route('/profile/mentorship', methods=['GET', 'POST'])
@login_required
def mentorship_settings():
    if current_user.role not in [UserRole.ALUMNI, UserRole.RESEARCHER]:
        flash('Mentorship settings are only available for Alumni and Researchers.', FLASH_ERROR)
        return redirect(url_for('forum.profile'))

    form = MentorshipSettingsForm()
    
    # Pre-populate
    if request.method == 'GET':
        if current_user.role == UserRole.ALUMNI and current_user.alumni_profile:
            form.open_to_mentor.data = current_user.alumni_profile.open_to_mentor
            form.mentorship_program.data = current_user.alumni_profile.mentorship_program
            form.mentorship_duration.data = current_user.alumni_profile.mentorship_duration
        elif current_user.role == UserRole.RESEARCHER and current_user.researcher_profile:
            form.open_to_mentor.data = current_user.researcher_profile.open_to_mentor
            form.mentorship_program.data = current_user.researcher_profile.mentorship_program
            form.mentorship_duration.data = current_user.researcher_profile.mentorship_duration

    # Handle submit
    if form.validate_on_submit():
        if current_user.role == UserRole.ALUMNI:
            profile = current_user.alumni_profile
            if not profile:
                profile = AlumniProfile(user_id=current_user.id)
                db.session.add(profile)
            profile.open_to_mentor = form.open_to_mentor.data
            profile.mentorship_program = form.mentorship_program.data
            profile.mentorship_duration = form.mentorship_duration.data
        elif current_user.role == UserRole.RESEARCHER:
            profile = current_user.researcher_profile
            if not profile:
                profile = ResearcherProfile(user_id=current_user.id)
                db.session.add(profile)
            profile.open_to_mentor = form.open_to_mentor.data
            profile.mentorship_program = form.mentorship_program.data
            profile.mentorship_duration = form.mentorship_duration.data
            
        db.session.commit()
        flash('Mentorship settings updated successfully.', FLASH_SUCCESS)
        return redirect(url_for('forum.mentorship_settings'))

    return render_template('mentorship_settings.html', form=form)
```

**Step 2: Commit**
```bash
git add forum/routes.py
git commit -m "feat(routes): implement /profile/mentorship route"
```

---

### Task 4: Create Settings Template and Update Navigation

**Files:**
- Create: `templates/mentorship_settings.html`
- Modify: `templates/base.html`, `templates/edit_profile.html`

**Step 1: Write minimal implementation**
Create `templates/mentorship_settings.html` with the form and JS logic to toggle field visibility based on the checkbox. Remove the `open_to_mentor` section and related JS from `templates/edit_profile.html`. Add link to `templates/base.html` in the user dropdown.

**Step 2: Commit**
```bash
git add templates/mentorship_settings.html templates/base.html templates/edit_profile.html
git commit -m "feat(ui): add mentorship settings page and update navigation"
```

---

### Task 5: Update Mentors Directory

**Files:**
- Modify: `templates/hub/mentors.html`

**Step 1: Write minimal implementation**
In `templates/hub/mentors.html`, display `mentorship_program` and `mentorship_duration` inside the mentor card if they are set.

```html
<!-- Inside the mentor card -->
{% set program = mentor.alumni_profile.mentorship_program if mentor.role.value == 'alumni' else mentor.researcher_profile.mentorship_program %}
{% set duration = mentor.alumni_profile.mentorship_duration if mentor.role.value == 'alumni' else mentor.researcher_profile.mentorship_duration %}

{% if program or duration %}
<div class="hub-mentor-details mt-2">
    {% if program %}
    <p class="mb-1"><i class="fas fa-book-reader text-muted me-2"></i> <strong>Program/Field:</strong> {{ program }}</p>
    {% endif %}
    {% if duration %}
    <p class="mb-0"><i class="far fa-clock text-muted me-2"></i> <strong>Duration:</strong> {{ duration }}</p>
    {% endif %}
</div>
{% endif %}
```

**Step 2: Commit**
```bash
git add templates/hub/mentors.html
git commit -m "feat(ui): show mentorship program and duration on mentor cards"
```