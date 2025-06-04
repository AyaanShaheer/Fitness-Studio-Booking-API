
---

# 🧘‍♀️ Fitness Studio Booking API

## 📌 Overview

This is a Python-based REST API for a fictional fitness studio, built with **FastAPI** and **SQLite (in-memory)**.
It supports:

* Viewing upcoming classes
* Booking classes
* Retrieving bookings by email
  All with proper **timezone management**.

---

## ⚙️ Setup Instructions

### ✅ Prerequisites

* Python 3.8+
* Git (optional)

---

### 📥 Clone the Repository (if applicable)

```bash
git clone <your-repo-url>
cd fitness_studio_api
```

---

### 🧪 Set Up a Virtual Environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

---

### 📦 Install Dependencies

```bash
pip install fastapi uvicorn pydantic pytest pytz
```

#### Dependency Summary:

* `fastapi` – Web framework for the API
* `uvicorn` – ASGI server
* `pydantic` – Request/response validation
* `pytest` – Unit testing
* `pytz` – Timezone support

---

### 🚀 Running the API

```bash
uvicorn fitness_studio_api:app --reload
```

* API available at: `http://localhost:8000`
* Interactive docs: `http://localhost:8000/docs`

---

### 🧪 Running Tests

```bash
pytest tests.py
```

---

## 📡 API Endpoints

### 🔍 `GET /classes`

* **Query parameter**: `timezone` (default: `Asia/Kolkata`)
* **Returns**: List of upcoming classes with name, datetime (converted to the timezone), instructor, and available slots

#### Example:

```bash
curl http://localhost:8000/classes?timezone=Asia/Kolkata
```

#### Sample Response:

```json
[
  {
    "id": "<uuid>",
    "name": "Yoga",
    "datetime": "2025-06-05T10:00:00+05:30",
    "instructor": "Alice",
    "available_slots": 10
  }
]
```

---

### 📝 `POST /book`

* **Body**:

```json
{
  "class_id": "uuid",
  "client_name": "string",
  "client_email": "email"
}
```

* **Books a class** if slots are available.

#### Example:

```bash
curl -X POST http://localhost:8000/book \
  -H "Content-Type: application/json" \
  -d '{"class_id": "<class_id>", "client_name": "John Doe", "client_email": "john@example.com"}'
```

#### Sample Response:

```json
{
  "id": "<booking_id>",
  "class_id": "<class_id>",
  "client_name": "John Doe",
  "client_email": "john@example.com"
}
```

---

### 📬 `GET /bookings`

* **Query parameter**: `client_email`
* **Returns**: All bookings for the specified email.

> Note: You must create a booking in the same session (POST /book) before using this.

#### Example:

```bash
curl http://localhost:8000/bookings?client_email=john@example.com
```

#### Sample Response:

```json
[
  {
    "id": "<booking_id>",
    "class_id": "<class_id>",
    "client_name": "John Doe",
    "client_email": "john@example.com"
  }
]
```

---

## ✨ Features

* **🕒 Timezone Management**: Converts class datetime from IST to requested timezone.
* **✅ Input Validation**: Ensures correct formats (e.g., email) using Pydantic.
* **❌ Error Handling**: Detects overbooking, invalid class IDs, and bad timezones.
* **🧾 Logging**: Logs requests and booking events.
* **🧪 Unit Testing**: Validates all functionalities using `pytest`.

---

## ⚠️ Notes

* Uses **in-memory SQLite DB** seeded with sample classes (Yoga, Zumba, HIIT) on startup.
* ⚠️ **Data resets on server restart** — Bookings must be recreated every session.

---


## 🛠️ Troubleshooting

### 🚫 Missing Dependencies

```bash
pip install fastapi uvicorn pydantic pytest pytz
```

### 🔎 Empty GET /bookings Response

* Ensure you’ve booked with the same `client_email` **in the current session**.

### 🕐 Timezone Conversion Errors

* Use valid timezones (e.g., `Asia/Kolkata`, `America/New_York`)
  Invalid values return `400 Bad Request`.

### 📄 Check Logs

* `uvicorn` console logs will show API activity and errors
  (e.g., `INFO: Booking created: <booking_id>`)

---

Let me know if you want this in a downloadable file (`README.md`).
