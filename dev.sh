#!/bin/bash

# Development startup script for Elephant Recruitment System
# Starts both backend API and frontend dev server

echo ""
echo "===================================="
echo "  ELEPHANT RECRUITMENT - Dev Mode"
echo "===================================="
echo ""

export BACKEND_PORT=3002

echo "Starting backend on port $BACKEND_PORT..."
(cd backend-api && npm start) &
BACKEND_PID=$!

sleep 3

echo "Starting frontend on port 5173..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

echo ""
echo "✓ Both services starting:"
echo "  - Backend:  http://localhost:$BACKEND_PORT/api/chat"
echo "  - Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
