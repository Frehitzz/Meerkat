# Run both the frontend and backend concurrently in the same terminal
npx concurrently -c "cyan.bold,green.bold" -n "FRONTEND,BACKEND" "cd meerkat-frontend && npm run dev" "cd meerkat-backend && .\venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

