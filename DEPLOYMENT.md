# Deployment Guide for Render

## Option 1: Blueprint Deployment (Recommended)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file and deploy both services

## Option 2: Manual Deployment

### Backend Deployment

1. **Create Web Service**:
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Set root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `python main.py`
   - Environment variables:
     - `PYTHON_VERSION`: `3.11.0`
     - `PORT`: `8000` (auto-set by Render)

### Frontend Deployment

1. **Create Web Service**:
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Set root directory: `frontend`
   - Build command: `npm install && npm run build`
   - Start command: `npm start`
   - Environment variables:
     - `NODE_VERSION`: `18.17.0`
     - `NEXT_PUBLIC_API_URL`: `https://your-backend-service.onrender.com`

## Environment Variables

### Backend
- `PORT`: Automatically set by Render
- `FRONTEND_URL`: Set to your frontend URL for CORS

### Frontend
- `NEXT_PUBLIC_API_URL`: Set to your backend service URL

## Post-Deployment

1. **Database Initialization**: The SQLite database will be created automatically on first run
2. **CORS Configuration**: Update the backend CORS settings if needed
3. **Health Checks**: Both services include health check endpoints

## Important Notes

- **Free Tier Limitations**: Render free tier services sleep after 15 minutes of inactivity
- **Database Persistence**: SQLite data persists on Render's disk storage
- **HTTPS**: All Render services get automatic HTTPS
- **Custom Domains**: Available on paid plans

## Troubleshooting

1. **Build Failures**: Check build logs in Render dashboard
2. **CORS Issues**: Verify `NEXT_PUBLIC_API_URL` is set correctly
3. **Database Issues**: Check if database initialization completed successfully
4. **Service Communication**: Ensure backend URL is correctly configured in frontend