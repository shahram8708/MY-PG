# MY PG – Backend Service

This project is a Flask-based backend application that powers the **MY PG** accommodation platform. It handles OTP authentication, PG and food service applications, email notifications, owner approval workflows, user requests, and submission handling. The server integrates with Gmail SMTP to send automated transactional emails to users, PG owners, food service owners, and administrators.

---

## Overview

The application provides:

* OTP-based login flow
* PG and food accommodation application submission
* Owner approval and rejection workflow via email links
* Email-based confirmations and notifications
* PG and food detail submission for owners
* User accommodation request submission
* Support for uploading documents and attachments
* Application expiry handling (48-hour approval window)
* Persistent application storage using `applications.json`

The backend renders a primary index page interface and exposes multiple JSON-based REST endpoints consumed by the MY PG frontend website.

---

## Features

* OTP verification via email
* Secure login confirmation emails to users and admin
* Apply for PG with document uploads
* Apply for food service
* Owner approval and rejection actions
* Applicant status email notifications
* Upload PG details (including images)
* Upload food details (including images)
* Leave PG / Leave Food submission workflow
* PG and food availability request submission
* 48-hour application validation mechanism
* CORS enabled

---

## Tech Stack

* **Backend:** Python, Flask
* **Email:** Gmail SMTP
* **CORS:** Flask-CORS
* **Data Handling:** JSON storage
* **Utilities:** smtplib, MIME handling, datetime

---

## Project Structure

```
MY-PG-main/
│
├── app.py                 # Flask backend and all routes
├── requirements.txt       # Dependencies
│
└── templates/
    └── index.html         # Main UI page
```

---

## Installation

1. Ensure Python is installed.
2. Extract the project folder.
3. Open a terminal in the project directory.
4. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

The application uses Gmail SMTP to send emails.
SMTP details are configured inside `app.py`:

```python
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'mypghelp@gmail.com'
SMTP_PASSWORD = '...'
```

If required, update these values with your credentials.

The backend also stores application records in:

```
applications.json
```

This file is automatically created and updated by the application.

Internet connection is required for email delivery.

---

## Running the Application

Start the Flask server:

```bash
python app.py
```

The server runs in debug mode.
Open the browser and visit:

```
http://127.0.0.1:5000
```

---

## Major Endpoints

### Authentication

* `POST /send-otp`
* `POST /login`

### Applications

* `POST /apply`
* `POST /food_apply`
* `GET /confirm_application`
* `GET /reject_application`
* `GET /view_application/<app_id>`

### Uploads

* `POST /upload-pg-details`
* `POST /upload-food-details`

### Requests

* `POST /pg-accommodation-request`
* `POST /food-accommodation-request`

### Leaving Services

* `POST /submit-leave-pg`
* `POST /submit-leave-food`

All submission endpoints return JSON responses.

---

## Notes

* Email notifications are automatically sent to users, owners, and admin.
* Attachments (user photos, IDs, documents, and images) are supported in applicable routes.
* Application approval links are time-bound to **48 hours**.
* CORS is enabled to support external frontend integration.
* The backend expects the MY PG frontend to supply correct form field names.

---

## License

No license file is included in this project.
