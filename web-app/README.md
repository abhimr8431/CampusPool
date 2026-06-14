# CampusPool Web Rebuild

This folder contains a React + Vite web rebuild of the CampusPool app.

## Setup

1. Open a terminal in `web-app`.
2. Run `npm install`.
3. Run `npm run dev`.

The web app will start on `http://localhost:4173`.

## Backend

The app expects the existing backend API to be available at `http://127.0.0.1:5000/api`.

If you want to use the existing Python backend, start it from the repository root:

```bash
cd backend
python app.py
```

## Notes

- Login uses the same `auth/login` API as the original app.
- The frontend avoids Android/iOS and targets a browser-based experience.
- You can extend the rebuild with verification upload and improved route handling later.
