# Render Deployment Checklist

## Pre-Deployment
- [ ] Code committed to GitHub repository
- [ ] All deployment files created (`render.yaml`, `Dockerfile`s)
- [ ] Environment variables configured
- [ ] CORS settings updated for production

## Deployment Steps
1. [ ] Push code to GitHub
2. [ ] Create new Blueprint on Render
3. [ ] Connect GitHub repository
4. [ ] Wait for automatic deployment
5. [ ] Verify both services are running

## Post-Deployment Verification
- [ ] Backend health check: `https://your-backend.onrender.com/`
- [ ] Frontend accessible: `https://your-frontend.onrender.com/`
- [ ] API communication working
- [ ] Database initialized with seed data
- [ ] Admin features working (create alerts)
- [ ] User features working (view/snooze alerts)

## Environment Variables to Set
### Backend Service
- `FRONTEND_URL`: Your frontend Render URL
- `RENDER`: `true` (for production CORS)

### Frontend Service  
- `NEXT_PUBLIC_API_URL`: Your backend Render URL

## Quick Test
1. Access frontend URL
2. Navigate to "Manage Alerts" 
3. Create a test alert
4. Switch to "My Alerts" to verify it appears
5. Test read/snooze functionality

Your alerting platform is now live on Render! 🚀