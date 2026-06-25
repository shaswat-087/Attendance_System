# Smart Attendance System 🚀

A production-grade web application that automates the corporate or academic attendance pipeline using real-time facial recognition and advanced data analytics. Built over a month of intense, continuous development in June, this full-stack application bridges the gap between high-accuracy computer vision models and an interactive web interface.

The system features a robust multi-tier web application, deep statistical analysis dashboards for monitoring attendance, and custom business logic tailored for academic accountability.

---

## 🛠️ The Tech Stack

The application is structured into a clean, decoupled architecture utilizing industry-standard libraries:

* **Backend Framework:** `Flask` (Python)
* **Database & ORM Layer:** `PostgreSQL` powered by `SQLAlchemy` for structured, transactional database operations.
* **Security & Gatekeeping:** `Werkzeug` for cryptographically secure password hashing and stateful session tracking.
* **AI & Computer Vision Engine:** `face_recognition` (built on top of `dlib`), `PIL` (Pillow), and `NumPy` for generating and comparing 128-dimensional facial landmark vectors in real-time.
* **Analytics Pipeline:** `Dash`, `Plotly`, and `Pandas` to map raw, time-stamped attendance matrices into real-time interactive analytical curves and metrics.
* **Frontend System:** Clean, responsive UI featuring 10 individual webpages engineered entirely from scratch using `HTML5` and `CSS3`.

---

## ✨ Special & Advanced Features

### 1. Personal Attendance Analytics (The 75% Safety Margin)
Designed explicitly to solve a massive pain point for university students navigating strict attendance criteria. The student portal runs an integrated analytical dashboard that tracks an individual's attendance percentage over time, displaying probability curves and projecting exactly how many classes they can afford to miss—or must attend—to maintain their academic standing safely above the 75% threshold.

### 2. Isolated Admin Command Center & Advanced Auth
A comprehensive administrative hub providing macro-level visual data on total student registration, daily trends, and direct control over the underlying PostgreSQL schemas. 
* *The Security Challenge:* The admin module implements a secure, custom-engineered multi-tier authentication guard. It completely separates administrative roles from standard student pathways, ensuring that data records cannot be manipulated or accessed without explicit authorization.

### 3. Dynamic Late Entry Engine
Instead of utilizing binary "Present" or "Absent" metrics, the core camera route evaluates time-deltas based on class commencement. 
* If a student is recognized within a 10-minute grace window, they are flagged as `Present`.
* Arrival past the 10-minute threshold automatically registers their state as `Late` in the database. This holds individuals strictly accountable while preserving their numerical presence in the data tables.

---

