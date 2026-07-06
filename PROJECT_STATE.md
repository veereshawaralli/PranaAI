# Project State & Architecture

**Project Name**: Prana AI (formerly CuraVision / MediBuddy)
**Framework**: Django 5.0.6
**Database**: SQLite (Development) -> PostgreSQL (Production Planned)

## Current Features Implemented
1. **CustomUser Model** (`accounts.models.CustomUser`)
   - Extended fields: `phone_number`, `date_of_birth`, `blood_group`, `address`, `is_patient`, `is_doctor`
2. **Authentication Flow** (`accounts` app)
   - Registration (`/accounts/register/`)
   - Login (`/accounts/login/`) - built-in view
   - Logout (`/accounts/logout/`) - built-in view
   - Crispy Forms integrated with Bootstrap 5
3. **Templates & UI**
   - Base template `templates/base.html` (Bootstrap 5)
   - Home landing page `templates/home.html`
   - Accounts templates in `templates/accounts/`
4. **Dashboard & Medicine Reminders** (`dashboard` app)
   - Home Dashboard (`/dashboard/`) displaying user profile and reminders.
   - `MedicineReminder` model linked to user.
   - Add Reminder flow (`/dashboard/add-reminder/`).
5. **AI Disease Detection** (`disease_detection` app)
   - Image upload for X-Rays and MRIs.
   - Integration with Gemini AI for medical image analysis.

6. **Prescription OCR** (`ocr` app)
   - Integration with Gemini AI for reading handwritten meds.
7. **AI Health Chatbot** (`chatbot` app)
   - Gemini integration for conversational health assistant.
8. **Health Reports Generation** (`reports` app)
   - ReportLab PDF generation for patient data.
9. **Locator** (`locator` app)
   - Uses OpenStreetMap, Leaflet.js, and Overpass API.
   - Finds nearby hospitals, clinics, and pharmacies.
   - Opens turn-by-route routing in OpenStreetMap.
10. **Appointments** (`appointments` app)
    - Allows users to book, manage, and cancel appointments with healthcare providers.
    - Features a clean table view for all upcoming and past appointments.
11. **Emergency SOS** (`emergency` app)
    - One-tap panic button with pulsing red animation.
    - HTML5 Geolocation captures live GPS coordinates.
    - Sends email alerts to all emergency contacts with Google Maps link.
    - Emergency contact CRUD management.
    - SOS alert history log.
12. **Health Analytics** (`analytics` app)
    - Track vital signs: Weight, Blood Pressure, Blood Sugar, Heart Rate, Temperature, SpO2.
    - Interactive Chart.js line/area charts with 30-day trends.
    - AI-powered Health Score (0-100) via Gemini analysis.
    - Metric summary cards with latest readings.
13. **AI Symptom Checker** (`symptom_checker` app)
    - Multi-step wizard: Body Area → Symptom Selection → Details → AI Analysis.
    - Categorized symptom checkboxes per body area.
    - Severity slider (1-10) and duration picker.
    - Gemini AI analysis returning possible conditions, urgency level (Low/Medium/High/Emergency), recommendations, and home remedies.
    - Symptom check history log.
14. **Pharmacy Store** (`pharmacy` app)
    - Browse medicines by category.
    - Shopping cart functionality.
    - Simulated checkout and order history tracking.

## Planned Modules
*(All modules are now complete! 13 features implemented. Please suggest new features to add to the roadmap.)*

## Note for AI Assistant
- Instead of scanning directories, read this file for a high-level overview.
- Keep this file updated as new apps and major features are added.
