# Prana AI 🏥✨

<p align="center">
  <img src="static/images/logo.png" alt="Prana AI Logo" width="150">
</p>

**Prana AI** is an intelligent, beautifully designed healthcare companion web application. Built with a premium "glassmorphism" aesthetic and powered by modern AI, it empowers users to digitize their medical records, extract insights from handwritten prescriptions, and converse with a smart health assistant.

<p align="center">
  <img src="static/images/hero-screenshot.png" alt="Prana AI Hero Section" width="800" style="border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
</p>

---

## 🌟 Key Features

### 🎨 Premium User Interface
- **Glassmorphism Design:** Frosted glass cards, fluid gradients, and refined typography (Plus Jakarta Sans).
- **Responsive Dashboard:** A comprehensive, color-coded dashboard summarizing your health profile and reminders.
<br>
<p align="center">
  <img src="static/images/dashboard-screenshot.png" alt="Prana AI Dashboard" width="700" style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 10px;">
</p>
<br>
- **Micro-Interactions:** Smooth `fadeInUp` animations, interactive hover states, and dynamic status indicators.

### 🤖 AI-Powered Chatbot
- **Gemini AI Integration:** Consult our smart health assistant for queries regarding symptoms, general well-being, and medical advice.
- **Modern Chat Interface:** Modeled after premium messaging apps with dynamic typing indicators and clickable suggestion pills.

### 📸 Prescription Scanner (OCR)
- **Live Camera & Upload:** Seamlessly digitize handwritten prescriptions by taking a live photo or uploading a document.
- **Smart Data Extraction:** Automatically reads and extracts medicine names, dosages, and schedules.

### 💊 Medication Reminders
- **Smart Tracking:** Keep track of all your active medications.
- **Full CRUD Support:** Easily add, edit, and safely delete your medication reminders.

### 📄 Intelligent Health Reports (PDF)
- **Premium PDF Generation:** Download beautifully formatted PDF reports summarizing your patient profile and active medications.
- **Custom Branding:** Features transparent alternating row colors, premium typography, and an ultra-subtle, non-intrusive watermark of the Prana AI logo.

---

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| **Backend Framework** | Python, Django 6.0 |
| **Database** | SQLite3 (Configurable to PostgreSQL) |
| **Frontend Styling** | HTML5, Vanilla CSS3 (Custom Glassmorphism Tokens), Bootstrap 5 |
| **Icons & Fonts** | Bootstrap Icons, Inter, Plus Jakarta Sans |
| **AI Integration** | Google Gemini API (Chatbot) |
| **PDF Generation** | ReportLab |

---

## 🚀 Getting Started

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
   Create a `.env` file in the root directory and add your Google Gemini API Key:
   ```env
   GEMINI_API_KEY=your_api_key_here
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

---

<p align="center">
  <i>Made with <span style="color: #F43F5E;">❤️</span> for better health</i>
</p>
