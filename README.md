# Prana AI — Swasthya Sahayak 🏥✨

<p align="center">
  <img src="static/images/logo.png" alt="Prana AI Logo" width="150">
</p>

**Prana AI (Swasthya Sahayak)** is an intelligent, beautifully designed healthcare companion web application. Built with a premium "glassmorphism" aesthetic and powered by modern AI, it empowers users to digitize their medical records, extract insights from handwritten prescriptions, track their vitals, and converse with a smart health assistant.

<p align="center">
  <img src="static/images/hero-screenshot.png" alt="Prana AI Hero Section" width="800" style="border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
</p>

---

## 🌟 Key Features

### 🤖 AI-Powered Chat Assistant
- **Gemini & Groq AI Engines:** High-availability dual-engine setup. If Gemini hits a rate limit, the system instantly and transparently falls back to Groq's high-speed LLaMA 3 models.
- **Real-Time Streaming:** Enjoy an instant, ChatGPT-like experience with real-time token streaming to the browser.
- **Modern Interface:** Dynamic typing indicators, suggested questions, and a premium chat UI.
<br>
<p align="center">
  <img src="static/images/chatbot-screenshot.png" alt="Prana AI Chatbot" width="700" style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 10px;">
</p>
<br>

### 🩺 AI Symptom Checker
- **Intelligent Diagnosis:** Input your symptoms and let the AI analyze them to provide a preliminary diagnosis.
- **Next Steps:** Get immediate recommendations on whether you should rest at home or consult a doctor.

### 📸 Smart Prescription Scanner (OCR)
- **Live Camera & Upload:** Seamlessly digitize handwritten prescriptions by taking a live photo or uploading a document.
- **Data Extraction & Fallbacks:** Automatically reads and extracts medicine names, dosages, and schedules. If Gemini Vision fails, instantly falls back to Groq's LLaMA 3.2 Vision model.
- **Dynamic Loading UX:** Elegant client-side loading overlays provide immediate feedback during heavy image processing.
<br>
<p align="center">
  <img src="static/images/scan-screenshot.png" alt="Prana AI Prescription OCR Scanner" width="48%" style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 10px;">
  <img src="static/images/ocr-results-screenshot.png" alt="Prana AI OCR Results" width="48%" style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 10px; margin-left: 2%;">
</p>
<br>

### 🫁 AI Disease Detection
- **Medical Imaging:** Upload Chest X-Rays for instant deep learning analysis.
- **Tuberculosis & Pneumonia:** Detects signs of severe respiratory diseases and provides actionable insights.

### 🗺️ Nearby Healthcare (100% Free Open-Source)
- **OpenStreetMap & Leaflet.js:** Locate emergency services, hospitals, clinics, and pharmacies around you without any paid Google API dependencies.
- **Overpass API Integration:** Live querying of nearby healthcare facilities with instant turn-by-turn routing links.

### 👨‍⚕️ Doctor Appointments
- **Browse Specialists:** View detailed doctor profiles including specialties, experience, and consultation fees.
- **Unified Booking Dashboard:** A complete portal for patients to book visits and doctors to manage and confirm appointments.

### 📊 Health Analytics & PDF Reports
- **Vital Tracking:** Log your weight, blood pressure, blood sugar, heart rate, temperature, and SpO2.
- **Interactive Charts:** Visualize your health trends over time using Chart.js.
- **AI Health Score:** Get an AI-generated health score based on your recent vitals.
- **Premium PDF Reports:** Download beautifully formatted PDF reports summarizing your health profile.

### 🚨 Emergency SOS Panic Button
- **One-Tap SOS:** Trigger an emergency alert to instantly notify your designated emergency contacts.
- **Live GPS Tracking:** Emails sent to emergency contacts include an OpenStreetMap link to your exact live GPS location using the HTML5 Geolocation API.

### 🎨 Premium User Interface
- **Glassmorphism Design:** Frosted glass cards, fluid gradients, and refined typography (Plus Jakarta Sans).
- **Responsive Dashboard:** A comprehensive, color-coded dashboard summarizing your health profile.
<br>
<p align="center">
  <img src="static/images/dashboard-screenshot.png" alt="Prana AI Dashboard" width="700" style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 10px;">
</p>
<br>
- **Micro-Interactions:** Smooth `fadeInUp` animations, interactive hover states, and dynamic status indicators.

---

## 🌍 Our Mission

Healthcare should be accessible, intelligent, and effortless. Prana AI was built with a core vision: to bridge the gap between complex medical data and patient understanding. We believe that by providing you with the right tools, you can take control of your health journey with confidence.

### Why Choose Prana AI?

- **Privacy First:** Your health data is your own. We prioritize secure, localized handling of your medical records.
- **Accessible AI:** Complex medical jargon is simplified instantly by our fine-tuned health assistant, making healthcare universally understandable.
- **Beautifully Simple:** Managing your health shouldn't feel like a chore. Our soothing, premium interface is designed to reduce anxiety and create a calming user experience.

---

## 🚀 Experience the Future of Healthcare

Prana AI is more than just an app; it's your personal health advocate available 24/7. From digitizing your latest doctor's visit to ensuring you never miss a dose of medication, we are here to support your well-being every step of the way.

<p align="center">
  <i>Swasthya Sahayak — Your Health, Made Intelligent & Simple.</i><br>
  <i>Made with <span style="color: #F43F5E;">❤️</span> by the Prana AI Team</i>
</p>

---

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| **Backend Framework** | Python, Django |
| **Database** | SQLite3 (Configurable to PostgreSQL) |
| **Frontend Styling** | HTML5, Vanilla CSS3 (Custom Glassmorphism Tokens), Bootstrap 5 |
| **Maps & Routing** | OpenStreetMap, Leaflet.js, Overpass API, Nominatim |
| **Icons & Fonts** | Bootstrap Icons, Inter, Plus Jakarta Sans |
| **AI Integration** | Google Gemini API (Primary) & Groq API (Fallback) with LLaMA 3 |
| **Data Visualization**| Chart.js |
| **PDF Generation** | ReportLab |

---

## 💻 Getting Started (For Developers)

### Prerequisites
Make sure you have Python 3.x installed on your machine.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/veereshawaralli/MediBuddy.git
   cd MediBuddy
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your API Keys and Email Settings (required for SOS Alerts):
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   
   # Email Settings (for SOS Alerts) - e.g., using Gmail
   EMAIL_HOST="smtp.gmail.com"
   EMAIL_PORT="587"
   EMAIL_HOST_USER="your-email@gmail.com"
   EMAIL_HOST_PASSWORD="your-16-char-app-password"
   EMAIL_USE_TLS="True"
   ```

5. **Run Database Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```
   Navigate to `http://localhost:8000` in your web browser.

---

## 👨‍💻 Contributing

Contributions are welcome! If you'd like to improve the UI, add new AI capabilities, or fix bugs, please fork the repository and submit a pull request.
