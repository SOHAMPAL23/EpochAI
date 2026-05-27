Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Launching PortfolioOS AI Workspace" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Start Express API Backend on Port 8000
Write-Host "📡 Starting Core API Server (Express/TypeScript)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '📡 Express API Server Running on Port 8000' -ForegroundColor Yellow; cd apps/api; npm run dev"

# 2. Start Vite React Frontend on Port 5173
Write-Host "🎨 Starting Frontend Dev Server (React/Vite)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '🎨 React Dev Server (Vite) Running on Port 5173' -ForegroundColor Green; npm run dev"

Write-Host ""
Write-Host "✅ Both servers have been successfully dispatched in separate terminal windows!" -ForegroundColor Green
Write-Host "🔗 Frontend Interface: http://localhost:5173" -ForegroundColor Cyan
Write-Host "🔗 Backend Health Diagnostic: http://localhost:8000/api/health" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
