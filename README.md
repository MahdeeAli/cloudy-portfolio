# Video Editor Portfolio & Admin Management System

A sleek, dark-themed, high-performance portfolio website designed for a video editor and motion graphics artist. It features a fully integrated Python backend that handles client booking inquiries, automated email routing, and a secure, drag-and-drop Kanban dashboard for project management.

## 🚀 Features

### Frontend (Client-Facing)
* **Cinematic UI/UX:** Responsive, dark-mode design with glowing accents and a custom grid background.
* **Dynamic Video Gallery:** Custom YouTube video embeds featuring high-quality animated thumbnails and a seamless modal playback system.
* **Direct Booking Form:** Allows clients to submit project details, which automatically routes to the database and triggers email notifications.

### Backend (Admin Dashboard)
* **Secure Authentication:** Session-based login system with automatic timeout for security.
* **Kanban Project Management:** Drag-and-drop interface to move client inquiries between `Pending`, `In Progress`, and `Done`.
* **Live Search & Filtering:** Instantly filter projects across all columns by name, email, or keyword.
* **Soft-Delete & Trash System:** Custom confirmation modals for deleting projects, which moves them to a Recycle Bin page for recovery or permanent deletion.
* **Custom Toast Notifications:** Sleek, slide-in alerts for user actions (moving, recovering, or deleting projects) without relying on clunky browser alerts.

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Backend:** Python, Flask
* **Database:** MySQL
* **Email Automation:** `smtplib` (Python Standard Library)

## 📁 Project Structure

```text
your_project_folder/
├── app.py                  # Main Flask application and API routes
├── requirements.txt        # Python dependencies
└── templates/              # HTML files (must remain in this folder)
    ├── index.html          # Main public portfolio
    ├── login.html          # Admin authentication page
    ├── admin.html          # Kanban dashboard
    └── trash.html          # Recycle bin for deleted projects