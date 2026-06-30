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

## Planned Modules
1. **Prescription OCR**: EasyOCR for reading handwritten meds.
2. **AI Health Chatbot**: Gemini/OpenAI integration.
3. **Health Reports Generation**: ReportLab PDF.

## Note for AI Assistant
- Instead of scanning directories, read this file for a high-level overview.
- Keep this file updated as new apps and major features are added.
