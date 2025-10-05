### **Project Brief: PSRA Website Development**

**To the Developer:**

This document contains the complete instructions for building the official website for the Pharmaceutical Studies and Research Association (PSRA). The primary goal is to create a professional, informative, and functional online platform for students, researchers, and potential partners.

A key requirement for this project is a **minimalist, professional, and academic aesthetic**. All styling should be kept simple, using a strict black, white, and grayscale color palette.

---

### **1. General Design & Styling Guidelines**

*   **Color Palette:**
    *   **Primary Background:** White (`#FFFFFF`) or a very light gray (`#F4F4F4`).
    *   **Primary Text:** Black (`#000000`) or a very dark gray (`#212121`).
    *   **Secondary Text/Accents:** Medium Gray (`#888888`) for things like timestamps, metadata, or placeholders.
    *   **Borders & Lines:** Light Gray (`#CCCCCC`).
    *   **Buttons/Links (Hover):** A slightly darker gray background on hover to indicate interactivity. No color.

*   **Typography:**
    *   **Font Family:** Use a clean, standard sans-serif font like **Lato**, **Open Sans**, or **Arial**. Ensure it's web-safe and legible.
    *   **Headings (H1, H2, H3):** Bold weight. Keep sizes proportional and clean.
    *   **Body Text:** Regular weight. A comfortable size for reading (e.g., 16px).

*   **Layout & Spacing:**
    *   Use a grid-based layout for consistency and alignment.
    *   Be generous with whitespace to create a clean, uncluttered feel.
    *   The website must be fully responsive and functional on desktop, tablet, and mobile devices.

*   **Imagery:**
    *   **ALL IMAGES** used on the site, including photos of team members and background images, must be **desaturated to black and white**. This is a critical instruction to maintain the "dull" and professional aesthetic.

---

### **2. Asset Management**

The following image files are provided. They should be optimized for the web and used as specified below.

*   `logo.png`: The official PSRA logo. To be used in the header and footer.
*   `image1.jpg` & `image2.jpg`: General-purpose images.
    *   Use one of these for the Home page hero section background (desaturated).
    *   The other can be used on the "Collaborate with Us" or "About Us" page as a banner or illustrative image (desaturated).
*   **Team Member Photos (JPGs):** These files correspond to the team members and contributors. They must be used on the "About Us" page.
    *   `Abrar Mohammed_Salih Ahmed.jpg`
    *   `Alfatih Mohammed Alarabi.jpg`
    *   `Basmala Samir Atim.jpg`
    *   `Fatima Yousif Elbashir.jpg`
    *   `Manhal kamal Hamza.jpg`
    *   `Nafeesa Abdelhafiz Eltayeb.jpg`
    *   `Omnia Eltaher Elhassan.jpg`
    *   `Rayan Yousif Ali Ahmed.jpg`
    *   `Razan Mohammed salih Almahi.jpg`
    *   `Rubba Abdelazeim Hussein.jpg`
    *   `Suaad Atif Abdien.jpg`
    *   `Tarteel Mohamed Hassan.jpg`

---

### **3. Sitemap & Website Structure**

The website will have the following pages and structure:

*   **Main Navigation:**
    *   `/` (Home)
    *   `/research` (Research)
    *   `/forum` (Forum)
    *   `/events` (Events)
    *   `/support` (Support & Donations)

*   **Forum Sub-Pages:**
    *   `/forum/login`
    *   `/forum/register`
    *   `/forum/post/{post_id}` (Viewing a single post and its comments)
    *   `/forum/terms` (Terms and Conditions)

*   **Footer Navigation:**
    *   `/about` (About Us / Team Page)
    *   `/collaborate` (Collaborate with Us)
    *   `/forum/login` (Login)
    *   `/contact` (Contact Us)
    *   `/privacy` (Privacy Policy)
    *   `/faq` (FAQ)

---

### **4. Global Elements**

#### **A. Header / Top Navigation**

*   **Layout:** Clean, single row.
*   **Left Side:** PSRA Logo (`logo.png`). Clicking it should always lead to the Home page.
*   **Right Side:** Navigation links: **Home | Research | Forum | Events | Support & Donations**.
*   **Styling:** Simple text links. The active page link should be underlined or bold.

#### **B. Footer**

*   **Layout:** A multi-column layout on desktop, stacking vertically on mobile.
*   **Column 1:** Small PSRA logo (`logo.png`) and copyright notice (e.g., `© 2024 Pharmaceutical Studies and Research Association. All Rights Reserved.`).
*   **Column 2 (Links):** `About Us`, `Collaborate with Us`, `Login`, `Contact Us`.
*   **Column 3 (Resources):** `Privacy Policy`, `FAQ`.
*   **Column 4 (Social Media):**
    *   Display simple, grayscale icons for Telegram, Instagram, LinkedIn, and Facebook.
    *   Each icon must link to the corresponding URL provided in the brief.

---

### **5. Page-by-Page Breakdown**

#### **A. Home Page (`/`)**

1.  **Hero Section:**
    *   **Background:** Use `image1.jpg` (desaturated to B&W) as a full-width background image. Apply a dark overlay (e.g., 60% black) to ensure text is readable.
    *   **Content:** Centered text over the background image.
        *   **Main Title (H1):** `Pharmaceutical Studies and Research Association`
        *   **Hero Text (Paragraph):** "Scientific research is your gateway to discovering opportunities and making an impact. Here, ideas turn into research, and research into achievements that serve pharmacy and the community."
        *   **Call to Action (CTA) Buttons:**
            *   **Primary Button:** `Join Now` (Links to `/forum/register`). Solid dark gray background, white text.
            *   **Secondary Button:** `Learn More` (Scrolls down to the "Our Vision" section). Outlined button with a gray border and text.

2.  **Our Vision Section:**
    *   A full-width section with a white or light gray background.
    *   **Heading (H2):** `Our Vision`
    *   **Paragraph:** Display the full vision text.

3.  **Our Goals Section:**
    *   **Heading (H2):** `Our Goals`
    *   **Layout:** Display the goals as a grid (e.g., 3 columns on desktop). Each grid item should contain a simple, line-art icon and the text for one goal.

4.  **Associated Logos Section:**
    *   **Heading (H3):** `In Association With`
    *   **Content:** Display the logos for **Faculty of Pharmacy, UofK**, **FPSA**, and **PharmaRx**. Use placeholders and request the actual logo files from the client. Display them in a row, in grayscale.

#### **B. Collaborate with Us Page (`/collaborate`)**

*   **Layout:** A simple, single-column text page. Use headings to structure the content clearly.
*   **Content:**
    *   **H1:** `Collaboration and Partnership`
    *   **H2:** `Why Collaborate With Us?` (followed by the paragraph).
    *   **H2:** `Who Can Collaborate With Us?` (followed by the bulleted list).
    *   **H2:** `Collaboration Opportunities` (followed by the bulleted list).
    *   **H2:** `What Others Gain From Collaborating With Us` (followed by the "For Our Partners" and "For Our Students & Association" sections).
*   **CTA Section (at the bottom):**
    *   A prominent button with the text `Collaborate With Us!`.
    *   This button **must link** to the provided Google Form: `https://forms.gle/emxkdU3UJciHRVxh7`.

#### **C. About Us / Team Page (`/about`)**

*   **Section 1: About PSRA & FPSA**
    *   **H1:** `About PSRA`
    *   **Content:** Use the text from "1. About PSRA & FPSA".

*   **Section 2: Team & Contributors**
    *   **H2:** `Our Team`
    *   **Layout:** A responsive grid of profile cards.
    *   **Profile Card Content:**
        *   **Image:** Use the corresponding team member's photo (e.g., `Tarteel Mohamed Hassan.jpg`), cropped into a circle or square and **desaturated to black and white**.
        *   **Name (H3):** The person's full name (e.g., `Tarteel Mohamed Hassan`).
        *   **Title/Role (Paragraph):** Assign titles based on the brief (e.g., `Tarteel Mohamed - PSRA President`). For others, use a placeholder like "Team Member" or "Contributor" until roles are provided.
    *   **List of Members to Include:**
        *   Tarteel Mohamed Hassan (PSRA President)
        *   Abrar Mohammed-Salih Ahmed (Collaboration & Partnership Team)
        *   Ahmed Ruba Abdelazeim (Use `Rubba Abdelazeim Hussein.jpg`, assuming this is the correct person) (Collaboration & Partnership Team)
        *   Hussein Twosl Tilal Eissa (Collaboration & Partnership Team - *Note: no image provided, use a generic placeholder icon*)
        *   Duaa Babiker (Forum Design Team - *Note: no image provided, use a generic placeholder icon*)
        *   Razan Mohammed (Use `Razan Mohammed salih Almahi.jpg`) (Forum Design Team)
        *   *...and create a profile card for every other person listed in the image files.*

#### **D. Contact Us Page (`/contact`)**

*   **Layout:** Two-column layout on desktop.
*   **Left Column:**
    *   **H1:** `Contact Us`
    *   **Location:** Display the address and an embedded Google Maps frame for `Faculty of Pharmacy - UofK`.
    *   **Social Links:** List the social media profiles with their icons and full links.
*   **Right Column:**
    *   A simple contact form with fields for: Name, Email, Subject, Message, and a "Send Message" button.

#### **E. Placeholder Pages (`/research`, `/events`, `/support`, `/privacy`, `/faq`)**

*   For pages where content is not yet provided, create a simple page with the header and footer.
*   The main content should be a centered H1 title (e.g., "Research") and a paragraph stating "Content for this page is coming soon. Please check back later."

---

### **6. Forum Mechanics & Design (`/forum`)**

This is the most complex functional part of the site. It requires a backend and database.

#### **A. Database Schema (Conceptual):**

*   `users`: (id, name, email, password_hash, profile_picture_url, created_at)
*   `posts`: (id, user_id, category, title, content, created_at)
*   `comments`: (id, post_id, user_id, content, created_at)
*   `likes`: (user_id, post_id) - A simple table to track likes.

#### **B. Forum Main Page (`/forum`)**

*   **Layout:** Two-column layout as described in the brief.
*   **Left Column (Sticky Navigation):**
    *   Search Bar (`Search Discussion`).
    *   Category Links: `Pharmacology`, `Clinical Pharmacy`, `Research Skills`. Clicking these should filter the posts shown in the right column.
*   **Right Column (Content Feed):**
    *   Breadcrumb navigation at the top (e.g., `Forum > Pharmacology`).
    *   "Start New Discussion" button (visible only to logged-in users). This could open a modal or lead to a new page to create a post.
    *   A list of posts, ordered by most recent.
    *   **Post Preview Card:** Should show:
        *   Author's Name & Profile Picture (small circle).
        *   Timestamp (e.g., "posted 2 hours ago").
        *   Post Title (clickable, linking to the full post page `/forum/post/{id}`).
        *   A short snippet of the post content.
        *   Like and Comment counts.

#### **C. Single Post Page (`/forum/post/{id}`)**

*   Displays the full content of the selected post (text, images, files).
*   Below the post, display the "Like" and "Comment" buttons.
*   Below that, show a list of all comments for that post.
*   At the bottom, a "Write a message..." text area for logged-in users to add a new comment.

#### **D. User Authentication Pages**

*   **Login (`/forum/login`):**
    *   A centered form with: `Email/Username` field, `Password` field, `Forgot Password?` link, `Login` button, and a link below saying `Don't have an account? Create one`.
*   **Registration (`/forum/register`):**
    *   A centered form with fields for: `Email`, `Name`, `Password`, `Confirm Password`.
    *   An optional "Upload Profile Picture" field.
    *   A checkbox: `I agree to the <a href="/forum/terms">Terms and Conditions</a>`. This must be checked to enable the "Create Account" button.
*   **Terms & Conditions (`/forum/terms`):**
    *   A static page displaying all the forum rules as provided in the brief.

#### **E. Forum Functionality**

*   **User Roles:**
    *   **Guest:** Can view posts and comments. Cannot create posts, comment, or like.
    *   **Registered User:** Can do everything a guest can, plus create posts, comment on posts, and like posts.
    *   **Admin/Moderator:** Can delete or edit any post/comment that violates the rules. (This requires a backend admin panel).
*   **Posting:** Logged-in users should be able to create new posts with text and optionally upload one image per post.
*   **Commenting:** Logged-in users can add text-based comments to any post.
*   **Liking:** The like button should be a toggle. Clicking it adds a like; clicking again removes it. The total like count should update dynamically (using JavaScript).