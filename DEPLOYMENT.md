# AI Travel Agent - Vercel Deployment Guide

This guide will help you deploy the AI Travel Agent application to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Environment Variables**: Prepare your API keys and configuration

## Required Environment Variables

Set these environment variables in your Vercel dashboard:

```bash
# Google AI API Key (required for AI functionality)
GOOGLE_API_KEY=your_google_api_key_here

# SerpAPI Key (for search functionality)
SERPAPI_API_KEY=your_serpapi_key_here

# Mailgun API Key (for email notifications)
MAILGUN_API_KEY=your_mailgun_key_here
MAILGUN_DOMAIN=your_mailgun_domain_here

# Optional: Custom configuration
FLASK_ENV=production
```

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Connect Repository**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project**:
   - Framework Preset: "Other"
   - Root Directory: Leave empty (use root)
   - Build Command: Leave empty (Vercel will auto-detect)
   - Output Directory: Leave empty
   - Install Command: `pip install -r requirements.txt`

3. **Set Environment Variables**:
   - In project settings, go to "Environment Variables"
   - Add all required environment variables listed above

4. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from Project Directory**:
   ```bash
   cd your-project-directory
   vercel
   ```

4. **Follow the prompts**:
   - Link to existing project or create new one
   - Confirm settings
   - Deploy

## Project Structure for Vercel

The project is configured with the following structure:

```
ai-travel-agent/
├── api/
│   └── index.py          # Serverless function entry point
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
├── .vercelignore        # Files to exclude from deployment
├── chat.html            # Frontend HTML
├── script.js            # Frontend JavaScript
├── styles.css           # Frontend CSS
├── app.py               # Backend logic
└── agents/              # AI agent modules
```

## Configuration Files

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  },
  "env": {
    "PYTHON_VERSION": "3.11"
  }
}
```

### .vercelignore
Key files excluded from deployment:
- Development files (.env, .vscode/, etc.)
- Python cache (__pycache__/, *.pyc)
- Documentation files
- Local development server (api_server.py)

## API Endpoints

After deployment, your API will be available at:

- **Health Check**: `https://your-app.vercel.app/api/health`
- **Chat**: `https://your-app.vercel.app/api/chat` (POST)
- **Feedback**: `https://your-app.vercel.app/api/feedback` (POST)

## Frontend Access

Your frontend will be available at: `https://your-app.vercel.app`

## Testing the Deployment

1. **Health Check**:
   ```bash
   curl https://your-app.vercel.app/api/health
   ```

2. **Chat API**:
   ```bash
   curl -X POST https://your-app.vercel.app/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, I need help planning a trip"}'
   ```

3. **Frontend**: Open `https://your-app.vercel.app` in your browser

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check that all dependencies are in requirements.txt
   - Verify Python version compatibility (3.11)
   - Check Vercel build logs for specific errors

2. **Runtime Errors**:
   - Verify environment variables are set correctly
   - Check function logs in Vercel dashboard
   - Ensure API keys are valid

3. **Import Errors**:
   - Verify all required modules are installed
   - Check that relative imports work correctly
   - Ensure the api/index.py can import from parent directories

4. **Timeout Issues**:
   - Function timeout is set to 30 seconds
   - For longer operations, consider implementing async processing
   - Check if external API calls are causing delays

### Debugging

1. **Check Logs**:
   - Go to Vercel dashboard → Your Project → Functions
   - Click on a function to see logs and errors

2. **Local Testing**:
   ```bash
   # Test the serverless function locally
   cd api
   python index.py
   ```

3. **Environment Variables**:
   - Verify all required environment variables are set
   - Check for typos in variable names
   - Ensure sensitive values are not exposed in logs

## Performance Optimization

1. **Cold Start Optimization**:
   - The backend is initialized on first request
   - Subsequent requests will be faster
   - Consider implementing connection pooling for databases

2. **Caching**:
   - Implement response caching for frequently requested data
   - Use Vercel's Edge Caching for static assets

3. **Bundle Size**:
   - Keep dependencies minimal
   - Use .vercelignore to exclude unnecessary files

## Security Considerations

1. **Environment Variables**:
   - Never commit API keys to the repository
   - Use Vercel's environment variable system
   - Rotate keys regularly

2. **CORS Configuration**:
   - The API includes CORS headers for frontend access
   - Adjust CORS settings if needed for production

3. **Input Validation**:
   - All API endpoints include input validation
   - Sanitize user inputs to prevent injection attacks

## Monitoring and Maintenance

1. **Vercel Analytics**:
   - Enable Vercel Analytics for performance monitoring
   - Monitor function execution times and error rates

2. **Logging**:
   - Application logs are available in Vercel dashboard
   - Implement structured logging for better debugging

3. **Updates**:
   - Vercel automatically deploys on git push to main branch
   - Test changes in preview deployments before merging

## Support

For deployment issues:
1. Check Vercel documentation: [vercel.com/docs](https://vercel.com/docs)
2. Review function logs in Vercel dashboard
3. Test locally before deploying
4. Ensure all environment variables are properly configured

## Next Steps

After successful deployment:
1. Set up custom domain (optional)
2. Configure monitoring and alerts
3. Implement CI/CD workflows
4. Set up staging environment for testing
5. Configure backup and disaster recovery