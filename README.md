# Restaurant UI - Fullstack Application

## Overview

This is a full-stack restaurant management application featuring a React frontend and a Python/Flask API backend with an SQLite relational database. It provides essential features to view a menu, place orders, and manage order statuses, serving as a comprehensive foundational project for a modern restaurant POS (Point of Sale) or self-service system.

## Key Technical Decisions

### 1. Essential Tech Stack Selection

- **Frontend (React)**: Chosen for its dynamic component-based architecture, making UI state management straightforward and the overall interface very resilient. We deliberately avoided extra abstractions like Vite, ensuring a highly standardized build process.
- **Backend (Python + Flask)**: A lightweight but powerful API framework. Flask is easy to read, configure, and maintain, which aligns nicely with the goal of writing clear, human-readable code.
- **Database (SQLite with SQLAlchemy)**: SQLite operates as our relational database, making setup frictionless. SQLAlchemy is the ORM, abstracting pure SQL into Python classes which prevents SQL injection and significantly streamlines database operations.

### 2. Architecture & Design Patterns

- **RESTful API Design**: We adhere to standard REST principles using intuitive resource paths (`/api/menu`, `/api/orders`) and standard HTTP verbs (GET, POST, PUT), enabling any client (web, mobile, or Postman) to cleanly interact with backend data.
- **Entity Relationships**: We utilize a `One-to-Many` and `Many-to-Many` (via associative entity) design between `Order` and `MenuItem` by introducing an `OrderItem` model. This correctly structures cart data without redundancy.

---

## Walkthrough

### Project Structure

- **/frontend**: React client application.
  - `src/App.js` & `src/App.css`: Defines the global structure and styles.
  - `src/components/`: Modular React components (`Menu`, `OrderList`, etc.).
- **/backend**: Python Flask server.
  - `app.py`: Central hub defining the SQLite DB connection, ORM models (`MenuItem`, `Order`, `OrderItem`), and all API endpoints.
  - `requirements.txt`: Project dependencies.
- **Restaurant_API.postman_collection.json**: A Postman collection for independently testing all API paths.

### AI Usage

AI was instrumental in scaffolding the foundational blocks of this application quickly, ensuring modern standard practices for React file organization and Flask boilerplate.

- **Brainstorming Data Models**: AI helped rapidly ideate the best relational layout between Orders and Menu Items without over-engineering complex schema setups initially.

### Risks

- **Concurrency in SQLite**: SQLite locks the database file when writing. In a highly active restaurant where multiple waiters are submitting orders concurrently, write-locks could cause API timeouts.
- **State Management**: The frontend relies on standard React state. As the app grows (e.g., adding user auth, analytics dashboards), standard state might become cumbersome.

### Extension Approach

Moving forward, this project acts as a sturdy baseline meant to be expanded:

1. **Migration to PostgreSQL**: To mitigate the SQLite concurrency risk, the SQLAlchemy URI can be swapped out to a robust PostgreSQL cluster without changing any Python query code.
2. **WebSocket Integration for Real-time Updates**: Orders placed by customers could instantly appear on a kitchen display system without needing to poll the backend.
3. **Redux / Context for Frontend**: Introducing a global state manager for the React app to cleanly separate the "cart" logic away from UI components.

---

## Setup & Running Locally

### Backend Setup

1. Open a terminal and navigate to the `backend` folder.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   python app.py
   ```
   _Note: This automatically provisions the `restaurant.db` with sample menu items._

### Frontend Setup

1. Open another terminal and navigate to the `frontend` folder.
2. Install dependencies (if not already done via create-react-app):
   ```bash
   npm install
   ```
3. Start the React server (starts on typically `http://localhost:3000`):
   ```bash
   npm start
   ```

### Postman Testing

1. Open Postman.
2. Import `Restaurant_API.postman_collection.json`.
3. Test out all the included requests (ensure your backend is actively running on `localhost:5000`).
