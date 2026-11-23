# Once Upon a Page 📖✨
*Every page holds a little magic.*

A modern, interactive children's digital storybook platform built with **Python (Flask)**, **TiDB / MySQL**, **Flask-Login**, **Bootstrap 5**, **StPageFlip.js**, and **Cloudinary**, deployed serverless on **Vercel**.

🌐 **Live Website**: [https://once-upon-a-page.vercel.app](https://once-upon-a-page.vercel.app)

---

## 🌟 Key Features

### 1. 📖 Interactive 3D Storybook Reader
- **Physics-Based Page Turning**: Powered by `StPageFlip.js` with natural paper curl and shadow physics.
- **Adaptive Screen Orientation**:
  - **Desktop / Tablet (Landscape)**: Authentic two-page spread (illustrations on left, story text on right).
  - **Mobile (Portrait)**: Single-page focus with touch swipe gestures.
- **Realistic Paper-Turn Sound**: Crisp paper rustle synthesized natively via the browser's **Web Audio API** (zero download lag, 100% offline reliability).
- **Auto-Closing Book at The End**: Automatically closes the 3D physical book cover with a smooth reverse animation upon finishing the last page, smoothly resetting the next open to Page 1 while preserving reading history logs.
- **Reading Progress & Resume**: Automatically records reading progress; reopening a book in-progress resumes exactly where the reader left off.
- **High-Resolution PDF Download**: Generates and downloads the opened storybook as a high-quality PDF with full covers, illustrations, and formatted story pages.

### 2. 📚 Storybook Library & User Dashboard
- **3D Physical Book Cards**: Realistic book spine, page blocks, drop shadows, and 3D hover tilt.
- **Personalized Experience**: User login/registration, reading history, favorites, categories, and light/dark theme toggle.
- **Magical Touch Sparkles**: Delicate, tiny 4-point golden sparkles appear on tap or click anywhere on the site.

### 3. 🎨 Dynamic Admin CMS & Cloudinary Media
- **Admin Dashboard**: Upload new storybooks, manage categories, add/edit page spreads, and manage user accounts.
- **Cloudinary Integration**: Story illustrations and book covers are stored securely in the cloud with automatic CDN delivery, keeping the application lightweight on serverless runtimes.

### 4. 🌙 Ambient Welcome Page
- Fullscreen cozy illustration with soothing background audio, ambient twinkling stars, and quick access to the storybook library.

---

## ❓ Template Architecture: `twinkle_reader.html` vs `reader.html`

| Template | Purpose |
|---|---|
| **`twinkle_reader.html`** | Original dedicated reader template created for the first flagship storybook, **Twinkle** (`/reader/twinkle` or Book ID 1). |
| **`reader.html`** | Universal reader template for all dynamic and admin-created storybooks (`/reader/<book_identifier>`). |

> **Why both exist**: `twinkle_reader.html` is retained so existing routes, bookmarks, and tests for the flagship *Twinkle* storybook continue to function seamlessly. Under the hood, both templates share the same interactive StPageFlip engine (`static/js/twinkle-reader.js`) and features.

---

## 📁 Project Structure

```text
story_book/
├── app.py                     # Flask application routes, auth, PDF generator, and APIs
├── config.py                  # Environment configuration & database connection settings
├── vercel.json                # Vercel serverless deployment routing & static builds
├── requirements.txt           # Python dependencies (Flask, PyMySQL, Cloudinary, Pillow)
├── templates/                 # Jinja2 HTML templates
│   ├── base.html              # Core layout (navbar, theme toggle, sparkle script)
│   ├── welcome.html           # Full-screen bedtime welcome page
│   ├── login.html             # User login
│   ├── register.html          # User registration
│   ├── dashboard.html         # User dashboard & 3D book library
│   ├── reader.html            # Universal storybook reader template
│   ├── twinkle_reader.html    # Flagship Twinkle storybook reader template
│   ├── admin_dashboard.html   # Admin management panel
│   ├── admin_books.html       # Storybook creation & editing
│   └── ...
├── static/                    # Local static assets
│   ├── css/
│   │   └── style.css          # Core stylesheets, 3D animations, and mobile styles
│   ├── js/
│   │   ├── twinkle-reader.js  # StPageFlip engine, Web Audio sound, & auto-close logic
│   │   ├── page-flip.browser.js # StPageFlip library
│   │   └── script.js          # UI interactions & audio controls
│   └── images/
│       ├── logo.png           # Official Once Upon a Page logo
│       └── covers/            # Default storybook covers
├── public/                    # Vercel static asset mirror
│   └── static/                # Synchronized static files for CDN delivery
└── tests/
```

---

## ⚙️ Environment Variables

For local development or deployment on **Vercel**, set the following environment variables:

| Variable | Description | Example / Default |
|---|---|---|
| `SECRET_KEY` | Flask session secret key | *A long random secret string* |
| `MYSQL_HOST` | Database host (TiDB / MySQL) | `gateway01.ap-southeast-1.prod.aws.tidbcloud.com` |
| `MYSQL_PORT` | Database port | `4000` (TiDB) or `3306` (MySQL) |
| `MYSQL_USER` | Database username | `xxxxxx.root` |
| `MYSQL_PASSWORD` | Database password | *Your DB password* |
| `MYSQL_DB` | Database name | `storybook_db` |
| `CLOUDINARY_URL` | Cloudinary connection string *(optional)* | `cloudinary://api_key:api_secret@cloud_name` |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | `your_cloud_name` |
| `CLOUDINARY_API_KEY` | Cloudinary API key | `your_api_key` |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | `your_api_secret` |

---

## 🚀 Running Locally

### 1. Clone the repository
```bash
git clone https://github.com/RishikaSunil/once-upon-a-page.git
cd once-upon-a-page
```

### 2. Set up virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Create a `.env` file in the root directory with your database and Cloudinary credentials:
```env
SECRET_KEY=your-magical-secret-key
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=storybook_db
```

### 5. Launch the application
```bash
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

---

## ☁️ Deployment on Vercel

The project is configured for serverless deployment on Vercel via [`vercel.json`](vercel.json):
1. Connect the GitHub repository in the **Vercel Dashboard**.
2. Set the Framework Preset to **Other** (or Flask).
3. Add the required Environment Variables in **Project Settings > Environment Variables**.
4. Every push to the `main` branch triggers an automated build and deployment.
