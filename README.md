# Once Upon a Page 📖✨
*Every page holds a little magic.*

A beautiful, interactive digital storybook platform built with **Python Flask**, **MySQL**, **Flask-Login**, **Bootstrap 5**, and **StPageFlip.js**.

---

## 🌟 Implemented Phases & Features

### Part 1: Full-Screen Redesigned Welcome Page (`/welcome`)
- **Full Viewport Immersion**: Fullscreen illustration (`100vw` by `100vh`) of the little girl reading under the blanket tent with flashlight, plush friends, and warm glowing fairy lights.
- **Uncluttered & Focused**: All extra cards, feature lists, and bullet points completely removed.
- **Display Content**:
  - Symbol: `✦`
  - Label: `Cozy Bedtime Stories`
  - Main Heading: **"Welcome to a World of Little Stories"**
  - Subtitle: *"Every little story holds a little magic. Come, let's explore!"*
  - Divider: `✦ ❧ ✦`
  - Button: **"Enter the Story World ✨"** (with glowing aura and smooth hover animation, redirecting to `/dashboard`).

### Part 2: Storybook Library Dashboard (`/dashboard`)
- Preserves the website identity **Once Upon a Page** (no third-party branding).
- Top navigation with Logo, Home, My Books, Favorites, Notifications, and User Profile.
- Left sidebar with Dashboard, All Books, Favorites, History, Settings, Logout, and floral corner illustration.
- Personalized welcome banner: *"Hello, [User's Name]! 👋"* and *"Explore your favourite little stories."*
- Section: *"Story Books 📚"*.
- **The First Storybook: TWINKLE**:
  - Uses the **Official Front Cover** (`static/images/covers/twinkle-cover.png`) untouched and uncropped.
  - Standing 3D physical book with spine, paper edge block, realistic drop shadow, glowing edges, and 3D hover tilt.

### Part 3 & 4: Twinkle Interactive Storybook (`/reader/twinkle`)
- Powered by **StPageFlip.js** (`page-flip.browser.js`).
- **Physical Hardcover Opening**:
  - Rigid front cover displaying the complete official **Twinkle** illustration (`twinkle-cover.png`).
  - Rigid back cover with Once Upon a Page gold seal.
  - Soft, flexible paper bending physics for inside story pages.
- **8 Illustrated Story Spreads**:
  - More illustrations (~70% page area) and short, readable sentences (1–3 sentences per page).
  - High character consistency: Twinkle with golden glow, rosy cheeks, big expressive eyes; the little girl in pink pyjamas with dark wavy hair; and the smiling crescent Moon.
  - Complete, preserved story text from meeting Twinkle to the heartwarming conclusion:
    > *"And sometimes, the smallest lights make the biggest difference. 💛"*
- **Realistic Page-Turning Sound**:
  - Natural crisp paper rustle synthesized via Web Audio API (zero audio download lag, 100% offline reliability).
  - Sound toggle on/off button in top controls.
- **Controls**:
  - Previous / Next buttons, page counter (`Cover`, `Pages 1 - 2 of 8`, `The End`), keyboard arrow navigation, and Back to Bookshelf button.

---

## 📁 Key File Locations

```text
storybook/
├── app.py                             # Flask routes (/welcome, /dashboard, /reader/twinkle)
├── templates/
│   ├── welcome.html                   # Part 1: Redesigned full-screen welcome page
│   ├── dashboard.html                 # Part 2: Storybook library dashboard with 3D books
│   └── twinkle_reader.html            # Part 3 & 4: StPageFlip interactive reader
├── static/
│   ├── css/
│   │   └── style.css                  # Fullscreen styles, 3D book engine & StPageFlip styling
│   ├── js/
│   │   ├── page-flip.browser.js       # StPageFlip.js vendor script
│   │   ├── twinkle-reader.js          # Reader engine & Web Audio API page sound synthesizer
│   │   └── script.js                  # Auth & dashboard interactions
│   └── images/
│       ├── covers/
│       │   └── twinkle-cover.png      # Official Twinkle front cover
│       ├── storybook/twinkle/         # 8 distinct inside scene illustrations
│       │   ├── twinkle_scene1.jpg
│       │   └── ... twinkle_scene8.jpg
│       └── welcome_bg.jpg             # Bedtime reading under blanket illustration
└── test_app.py                        # Automated unit test suite (7 tests)
```

---

## 🚀 How to Run Locally

1. Run the Flask server:
   ```bash
   python app.py
   ```
2. Navigate to:
   👉 **http://127.0.0.1:5000**
3. Log in to explore:
   - **Full-Screen Welcome Page** (`/welcome`)
   - Click **"Enter the Story World ✨"** to open the **Dashboard** (`/dashboard`)
   - Click **Twinkle** to open the **Interactive Children's Storybook** (`/reader/twinkle`) with realistic page-turning animations and sounds!


