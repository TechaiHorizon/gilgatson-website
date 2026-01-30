# Cloudflare Pages Environment Variables Setup

To complete the Kit (ConvertKit) newsletter integration, you need to add environment variables to your Cloudflare Pages project.

## Steps to Add Environment Variables

1. **Go to Cloudflare Pages Dashboard**
   - Visit: https://dash.cloudflare.com/
   - Navigate to: **Workers & Pages** → **gilgatson-website** (or your project name)

2. **Access Settings**
   - Click on the **Settings** tab
   - Scroll down to **Environment variables** section

3. **Add the Following Variables**

   For **Production** environment:
   
   | Variable Name | Value |
   |--------------|-------|
   | `KIT_API_KEY` | `upylj_EGT-d6I4VoUHieGg` |
   | `KIT_API_SECRET` | `LFhEQlAxT4NJcw5O_2MVdLcRhMwy8BI3p2EayFXp0zg` |

4. **Save and Redeploy**
   - Click **Save** after adding each variable
   - The next deployment will automatically use these variables
   - You can trigger a redeploy by pushing a commit to GitHub

## How It Works

1. User enters email on gilgatson.com newsletter form
2. Form submits to `/api/subscribe` (Cloudflare Pages Function)
3. Function uses environment variables to authenticate with Kit API
4. Kit API adds subscriber to your newsletter list
5. User receives confirmation message

## Testing

After setting up environment variables and deploying:

1. Visit: https://gilgatson.com
2. Scroll to newsletter signup section
3. Enter a test email address
4. Click "Subscribe"
5. Check Kit dashboard for new subscriber: https://app.kit.com/subscribers

## Security Notes

- Environment variables are encrypted and not exposed to the client
- API credentials are only accessible in the serverless function
- CORS is configured to only allow requests from gilgatson.com

## Troubleshooting

If subscriptions aren't working:

1. **Check Cloudflare Pages deployment logs**
   - Go to: Deployments → Latest deployment → View details
   - Look for errors in function logs

2. **Verify environment variables are set**
   - Settings → Environment variables
   - Make sure both `KIT_API_KEY` and `KIT_API_SECRET` are present

3. **Test the API endpoint directly**
   ```bash
   curl -X POST https://gilgatson.com/api/subscribe \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com"}'
   ```

4. **Check Kit API status**
   - Visit: https://status.kit.com/
   - Ensure Kit API is operational

## Kit Dashboard

Access your Kit account to manage subscribers:
- Dashboard: https://app.kit.com/dashboard
- Subscribers: https://app.kit.com/subscribers
- Email: massappealnow@gmail.com
- Password: Trevamir76$

## API Documentation

- Kit API Docs: https://developers.kit.com/
- Cloudflare Pages Functions: https://developers.cloudflare.com/pages/functions/
