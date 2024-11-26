
# Online Career Counselling Service (OCCS)

## Overview
The **Online Career Counselling Service (OCCS)** is a web platform designed to bridge the gap between students' career aspirations and accessible professional guidance. It provides:
- Personalized career recommendations based on aptitude and interests.
- Scheduling and management of counselor sessions.
- Access to curated resources for various career paths.

---

## Features

### For Students:
- **Sign Up/Login**: Secure user authentication.
- **Career Recommendations**: Personalized suggestions based on interest quizzes.
- **Appointment Booking**: Easy scheduling and rescheduling of sessions.
- **Resource Exploration**: Explore degree programs, job roles, salaries, and more.

### For Counselors:
- **Manage Availability**: Add or edit available time slots.
- **View Appointments**: Access upcoming and past bookings.
- **Student Interaction**: Review student quizzes and provide feedback.
- **Session Management**: Approve, reschedule, or cancel sessions.

---

## Project Structure
```plaintext
── ccservice \
│   ├── admin.py                # Django admin customization \
│   ├── apps.py                 # Application configuration \
│   ├── models.py               # Database models for the app \
│   ├── scrapers.py             # Custom scripts for scraping external data \
│   ├── urls.py                 # URL configuration for the app \
│   ├── utils.py                # Utility functions used across the app \
│   └── views.py                # View functions for handling web requests \
├── db.sqlite3                  # SQLite database file \
├── manage.py                   # Django project management script \
├── OCCS \
│   ├── settings.py             # Django project settings \
│   ├── urls.py                 # Root URL configuration \
│   └── wsgi.py                 # Web Server Gateway Interface for deployment \
├── static \
│   ├── css                     # CSS stylesheets for the application \
│   │   ├── counsellorIndex.css \
│   │   ├── counsellorLogin.css \
│   │   ├── counsellorRegistration.css \
│   │   ├── studentIndex.css \
│   │   ├── studentLogin.css \
│   │   ├── studentRegistration.css \
│   │   └── styles.css \
│   ├── images                  # Static images used in the application \
│   │   ├── counsellor.png \
│   │   ├── discussion.png \
│   │   ├── logo.png \
│   │   └── student.png \
│   └── js                      # JavaScript files for client-side interactivity \
│       ├── booking.js \
│       ├── counselorIndex.js \
│       └── studentIndex.js \
└── templates \
    ├── career_base.html        # Base template for career-related pages \
    ├── career_colleges.html    # Template for college recommendations \
    ├── career_field_detail.html # Details about specific career fields \
    ├── career.html             # Overview of career options \
    ├── college_rankings.html   # Displays rankings of colleges \
    ├── counsellorIndex.html    # Dashboard for counselors \
    ├── counsellorLogin.html    # Login page for counselors \
    ├── counsellorRegistration.html # Registration form for counselors \
    ├── index.html              # Homepage of the application \
    ├── studentIndex.html       # Dashboard for students \
    ├── studentLogin.html       # Login page for students \
    ├── studentRegistration.html # Registration form for students \
    └── update_career_data.html # Admin interface to update career data \

```

---

## Installation

### Prerequisites:
- Python 3.8+
- Django 3.x
- SQLite3
- Git

### Steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/VedantK11/Counselling-Service.git
   cd OCCS
   ```
2. Install dependencies:
   ```bash
   pip install django
   pip install pandas
   pip install beautifulsoup4
   pip install selenium
   ```
3. Run migrations:
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```
4. Scrape the Career opportunities:
   ```bash
   python3 manage.py scrape_nirf
   ```

5. Start the development server:
   ```bash
   python3 manage.py runserver
   ```
6. Access the application at `http://127.0.0.1:8000/`.

---

## Tools and Technologies
- **Frontend**: HTML, CSS, Bootstrap.
- **Backend**: Django Framework.
- **Database**: SQLite.
- **Web Scraping**: BeautifulSoup, Selenium.

---

## Challenges and Solutions
1. **Real-Time Booking Updates**:
   - **Challenge**: Synchronizing booking changes between students and counselors.
   - **Solution**: Implemented real-time updates using WebSockets.

2. **Dynamic Career Suggestions**:
   - **Challenge**: Adapting scraping logic for different websites.
   - **Solution**: Developed custom scripts for each data source.

---

## Contribution
- **UI and Exploration Module**: Naman.
- **Student and Counselor Modules**: Mriganko.
- **Booking System**: Vedant.

---

## Future Enhancements
- AI-driven career guidance.
- Integration with external calendars for session reminders.
- Support for mobile platforms.

---



## Contact
For queries, please reach out to:
- **Vedant**: [vedantk@iitb.ac.in](mailto:vedantk@iitb.ac.in)
- **Mriganko**: [24m2134@iitb.ac.in](mailto:24m2134@iitb.ac.in)
- **Naman**: [namansharma@iitb.ac.in](mailto:namansharma@iitb.ac.in)