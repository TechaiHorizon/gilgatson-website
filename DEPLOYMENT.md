# GilGatson.com Deployment Guide

## Quick Deploy to Netlify (Recommended)

1. **Push to GitHub:**
   ```bash
   cd /home/ubuntu/gilgatson-website
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/gilgatson-website.git
   git push -u origin main
   ```

2. **Deploy on Netlify:**
   - Go to https://app.netlify.com
   - Click "Add new site" → "Import an existing project"
   - Connect your GitHub account
   - Select the `gilgatson-website` repository
   - Build settings (auto-detected):
     - Build command: `pnpm build`
     - Publish directory: `dist`
   - Click "Deploy site"

3. **Add Custom Domain:**
   - In Netlify dashboard, go to "Domain settings"
   - Click "Add custom domain"
   - Enter `gilgatson.com`
   - Follow DNS configuration instructions

## Alternative: Deploy to Vercel

1. **Push to GitHub** (same as above)

2. **Deploy on Vercel:**
   - Go to https://vercel.com
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Vercel auto-detects Astro settings
   - Click "Deploy"

3. **Add Custom Domain:**
   - In Vercel dashboard, go to "Settings" → "Domains"
   - Add `gilgatson.com`
   - Configure DNS records as instructed

## DNS Configuration

Once you have your deployment URL, configure your domain:

1. **Buy domain** (if you haven't):
   - GoDaddy, Namecheap, or Google Domains

2. **Add DNS records:**
   - For Netlify/Vercel, add their nameservers or A/CNAME records
   - Follow the specific instructions provided by your hosting platform

## Post-Deployment Checklist

- [ ] Test all pages load correctly
- [ ] Verify book cover images display
- [ ] Check mobile responsiveness
- [ ] Test all navigation links
- [ ] Verify sitemap.xml is accessible
- [ ] Submit sitemap to Google Search Console
- [ ] Update Amazon links with real ASINs
- [ ] Set up Google Analytics (optional)

## Update Book Links

Before going live, update these placeholder links:

**In `src/pages/index.astro`:**
- Replace `YOUR_KINDLE_ASIN` with actual Kindle ASIN
- Replace `YOUR_PAPERBACK_ASIN` with actual paperback ASIN
- Replace `YOUR_AUDIOBOOK_ASIN` with actual Audible ASIN

**In `src/pages/books.astro`:**
- Update all Amazon/Audible links with real ASINs

## Local Development

```bash
cd /home/ubuntu/gilgatson-website
pnpm dev
```

Visit http://localhost:4321

## Build for Production

```bash
pnpm build
```

Output will be in `dist/` directory.

## Adding Blog Posts

Create new markdown files in `src/pages/blog/`:

```markdown
---
layout: ../../layouts/BaseLayout.astro
title: "Your Blog Post Title"
description: "Brief description"
---

# Your Blog Post Title

Your content here...
```

The file will be automatically available at `/blog/filename`.
