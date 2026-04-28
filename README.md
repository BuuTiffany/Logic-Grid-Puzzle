# Logic Grid Puzzle

A web app for solving logic/zebra puzzles. Built with SvelteKit (frontend) and Django (backend), with Supabase as the database.

---

## Project Structure

```
Logic-Grid-Puzzle/
├── frontend/          # SvelteKit app
├── server/            # Django REST API
└── README.md
```

---

## Prerequisites

- Python 3.11+
- Node.js 18+

---

## Running Locally

### 1. Backend (Django)

```bash
cd server

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the dev server
python manage.py runserver
```

Django will be available at `http://localhost:8000`.

### 2. Frontend (SvelteKit)

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

SvelteKit will be available at `http://localhost:5173`.

### Seeding Puzzles

Generate and store puzzles in Supabase:

```bash
cd server
source .venv/bin/activate

# Seed 10 of every grid/difficulty combination
python manage.py seed_puzzles --count 10

# Seed a specific grid and difficulty
python manage.py seed_puzzles --grid 4x5 --difficulty moderate --count 20

# Seed all grids at a specific difficulty
python manage.py seed_puzzles --difficulty easy --count 15
```

### Clean Up Used Puzzles

Remove puzzles that have already been served to users:

```bash
# Preview how many would be deleted (safe to run anytime)
python manage.py cleanup_puzzles --dry-run

# Actually delete them
python manage.py cleanup_puzzles
```