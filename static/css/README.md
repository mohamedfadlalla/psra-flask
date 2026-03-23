# PSRA CSS Design System

This directory contains all stylesheets for the PSRA website, organized using a modular architecture.

## 📁 Directory Structure

```
css/
├── base/                    # Foundation styles
│   ├── variables.css        # CSS custom properties (design tokens)
│   ├── reset.css            # CSS reset and base element styles
│   └── typography.css       # Heading, text, and font styles
├── components/              # Reusable UI components
│   ├── alerts.css           # Alert and toast notifications
│   ├── avatars.css          # User avatar components
│   ├── badges.css           # Status badges and labels
│   ├── buttons.css          # Button styles and variants
│   ├── cards.css            # Card containers
│   ├── footer.css           # Site footer
│   ├── forms.css            # Form inputs and validation
│   ├── modals.css           # Modal dialogs
│   └── navigation.css       # Header, nav, and mobile nav
├── modules/                 # Feature-specific styles
│   ├── auth.css             # Login and register pages
│   ├── profile.css          # User profile pages
│   ├── forum.css            # Forum module (TODO)
│   ├── admin.css            # Admin dashboard (TODO)
│   ├── events.css           # Events pages (TODO)
│   ├── dashboard.css        # User dashboard (TODO)
│   └── home.css             # Homepage sections (TODO)
├── layouts/                 # Layout utilities (TODO)
├── utilities/               # Utility classes
│   └── utilities.css        # Flexbox, grid, spacing, etc.
└── style.css                # Main import file
```

## 🎨 Design Tokens

All design tokens are defined in `base/variables.css`. Use these CSS variables throughout your code:

### Colors

```css
/* Primary */
--primary-blue: #2D577B;
--primary-blue-light: #607D9B;
--primary-blue-dark: #1E3A5F;

/* Accent */
--accent-orange: #F59E0B;
--accent-orange-hover: #D97706;
--accent-green: #4ADE80;

/* Semantic */
--color-success: #22C55E;
--color-warning: #F59E0B;
--color-error: #EF4444;
--color-info: #3B82F6;

/* Text */
--text-primary: #1E293B;
--text-secondary: #64748B;
--text-muted: #94A3B8;
--text-inverse: #FFFFFF;

/* Background */
--bg-primary: #FFFFFF;
--bg-secondary: #F8FAFC;
--bg-tertiary: #F1F5F9;
```

### Spacing

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
```

### Typography

```css
--font-family-heading: 'Montserrat', sans-serif;
--font-family-body: 'Inter', sans-serif;

--font-size-xs: 0.75rem;    /* 12px */
--font-size-sm: 0.875rem;   /* 14px */
--font-size-base: 1rem;     /* 16px */
--font-size-lg: 1.125rem;   /* 18px */
--font-size-xl: 1.25rem;    /* 20px */
--font-size-2xl: 1.5rem;    /* 24px */
--font-size-3xl: 1.875rem;  /* 28px */
--font-size-4xl: 2.25rem;   /* 36px */

--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

### Border Radius

```css
--radius-sm: 4px;
--radius-md: 6px;
--radius-lg: 8px;
--radius-xl: 12px;
--radius-2xl: 16px;
--radius-full: 9999px;
```

### Shadows

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
```

## 🧩 Component Usage

### Buttons

```html
<!-- Primary Button -->
<button class="btn btn-primary">Primary</button>

<!-- Secondary Button -->
<button class="btn btn-secondary">Secondary</button>

<!-- Outline Button -->
<button class="btn btn-outline">Outline</button>

<!-- Small Button -->
<button class="btn btn-primary btn-sm">Small</button>

<!-- Large Button -->
<button class="btn btn-primary btn-lg">Large</button>

<!-- Icon Button -->
<button class="btn btn-primary">
    <i class="fas fa-plus"></i> Add
</button>
```

### Cards

```html
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Card Title</h3>
    </div>
    <div class="card-body">
        <p class="card-text">Card content goes here...</p>
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">Action</button>
    </div>
</div>
```

### Badges

```html
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>
<span class="badge badge-error">Error</span>
<span class="badge badge-live">Live</span>
```

### Alerts

```html
<div class="alert alert-success">
    <i class="fas fa-check-circle alert-icon"></i>
    <div class="alert-content">
        <p class="alert-title">Success!</p>
        <p>Operation completed successfully.</p>
    </div>
    <button class="alert-close">&times;</button>
</div>
```

### Forms

```html
<div class="form-group">
    <label class="form-label">Email</label>
    <input type="email" class="form-input" placeholder="Enter email">
    <p class="form-hint">We'll never share your email.</p>
</div>

<div class="form-group">
    <label class="form-label">Password</label>
    <div class="password-input-wrapper">
        <input type="password" class="form-input" placeholder="Enter password">
        <button type="button" class="password-toggle">
            <i class="fas fa-eye"></i>
        </button>
    </div>
</div>
```

### Avatars

```html
<!-- Avatar with Image -->
<div class="avatar avatar-md">
    <img src="user.jpg" alt="User Name">
</div>

<!-- Avatar with Initials -->
<div class="avatar avatar-md avatar-placeholder">
    U
</div>

<!-- Avatar Sizes -->
<div class="avatar avatar-sm">SM</div>
<div class="avatar avatar-md">MD</div>
<div class="avatar avatar-lg">LG</div>
<div class="avatar avatar-xl">XL</div>
<div class="avatar avatar-2xl">2XL</div>
```

## 🔧 Utility Classes

### Flexbox

```html
<div class="flex items-center justify-between">
    <div>Left</div>
    <div>Right</div>
</div>

<div class="flex flex-col gap-4">
    <div>Item 1</div>
    <div>Item 2</div>
</div>
```

### Grid

```html
<div class="grid grid-cols-2 gap-4">
    <div>Column 1</div>
    <div>Column 2</div>
</div>

<div class="grid grid-cols-3 md:grid-cols-4 gap-6">
    <!-- Responsive grid -->
</div>
```

### Spacing

```html
<!-- Margin -->
<div class="m-4">Margin all sides</div>
<div class="mt-4">Margin top</div>
<div class="mb-4">Margin bottom</div>
<div class="mx-auto">Centered horizontally</div>

<!-- Padding -->
<div class="p-4">Padding all sides</div>
<div class="pt-4">Padding top</div>
<div class="pb-4">Padding bottom</div>
<div class="px-4">Padding left & right</div>
```

### Text

```html
<p class="text-center">Centered text</p>
<p class="text-primary">Primary color</p>
<p class="text-muted">Muted color</p>
<p class="font-bold">Bold text</p>
<p class="text-lg">Large text</p>
```

## 📱 Responsive Design

Breakpoints follow a mobile-first approach:

```css
/* Mobile (default) */
.element { /* styles */ }

/* Tablet (≥768px) */
@media (min-width: 768px) {
    .element { /* styles */ }
}

/* Desktop (≥1024px) */
@media (min-width: 1024px) {
    .element { /* styles */ }
}

/* Large Desktop (≥1280px) */
@media (min-width: 1280px) {
    .element { /* styles */ }
}
```

## 🎯 Best Practices

1. **Use CSS Variables**: Always use design tokens from `variables.css`
2. **Component First**: Check if a component exists before writing custom CSS
3. **Utility Classes**: Use utility classes for simple layouts and spacing
4. **BEM Naming**: Follow BEM-like naming for components (`.block__element--modifier`)
5. **Mobile First**: Write mobile styles first, then enhance for larger screens
6. **Accessibility**: Ensure sufficient color contrast and focus states

## 🚀 Adding New Components

1. Create a new file in `components/` directory
2. Add `@import` statement in `style.css`
3. Document usage in this README
4. Test across different screen sizes

## 📝 TODO

- [ ] Extract `forum.css` module
- [ ] Extract `admin.css` module
- [ ] Extract `events.css` module
- [ ] Extract `dashboard.css` module
- [ ] Extract `home.css` module
- [ ] Create layout utilities
- [ ] Add dark mode documentation
- [ ] Add print styles

## 🔄 Migration Notes

The CSS was refactored from a single 10,307-line file into a modular architecture:

- **Before**: 10,307 lines in `style.css`
- **After**: ~9,000 lines distributed across 20+ organized files
- **Benefit**: Easier maintenance, better reusability, faster development

### Migration Completed

**Phase 1: Foundation** ✅
- Created directory structure
- Extracted variables, reset, typography to `base/`
- Created comprehensive utility classes
- Updated `style.css` with `@import` statements

**Phase 2: Components** ✅
- Extracted 9 component files: buttons, forms, cards, badges, avatars, alerts, modals, navigation, footer
- Moved inline styles from templates to CSS modules:
  - `profile.html` → `modules/profile.css`
  - `login.html` → `modules/auth.css`
  - `register.html` → `modules/auth.css`

**Phase 3: Modules** ✅
- Extracted feature modules: forum, admin, dashboard, home
- All major page-specific styles now in `modules/`

**Phase 4: Documentation** ✅
- Created comprehensive README.md
- Documented all components with usage examples
