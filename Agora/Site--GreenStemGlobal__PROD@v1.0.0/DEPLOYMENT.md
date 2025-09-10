# GreenStemGlobal Website Deployment Guide

## 🚀 AWS Amplify Deployment

### Prerequisites
- AWS Account with Amplify access
- Git repository with code
- Environment variables configured

### Environment Variables

Set these in AWS Amplify Console:

```bash
# Site Configuration
NEXT_PUBLIC_SITE_ENV=production
NEXT_PUBLIC_SITE_URL=https://www.greenstemglobal.com

# API Configuration
NEXT_PUBLIC_API_BASE_URL=https://cn-api.greenstemglobal.com

# Cache Configuration
NEXT_PUBLIC_CACHE_REVALIDATE_TRACE=300
NEXT_PUBLIC_CACHE_REVALIDATE_HIGHLIGHTS=60

# Feature Flags
NEXT_PUBLIC_ENABLE_BLOCKCHAIN_VIEW=true
NEXT_PUBLIC_ENABLE_SATELLITE_DATA=true
NEXT_PUBLIC_ENABLE_WEATHER_DATA=true

# Analytics
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=greenstemglobal.com
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX

# Sitemap Configuration
SITE_URL=https://www.greenstemglobal.com
```

### Branch Mapping
- `dev` → DEV environment
- `stage` → STAGE environment  
- `main` → PROD environment

### Build Settings

The `amplify.yml` file is configured with:
- Node.js 18+ runtime
- npm ci for dependency installation
- Next.js build with sitemap generation
- Security headers (CSP, HSTS, etc.)
- Cache optimization

### Dependencies Verification

All required packages are installed:
- ✅ Next.js 14.2.5
- ✅ React 18.3.1
- ✅ TypeScript 5.9.2
- ✅ Tailwind CSS 3.4.17
- ✅ next-sitemap 4.2.3
- ✅ @vercel/analytics 1.5.0
- ✅ plausible-tracker 0.3.9
- ✅ lucide-react 0.543.0
- ✅ zod 3.23.8

### Security Headers

Configured in `amplify.yml`:
- Strict-Transport-Security
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Content-Security-Policy
- Referrer-Policy

### Performance Optimization

- Image optimization (WebP/AVIF)
- Static asset caching (1 year)
- Next.js automatic code splitting
- Sitemap generation on build

### Monitoring

- Vercel Analytics integration
- Plausible Analytics (privacy-friendly)
- CloudWatch logs via Amplify
- Error tracking and performance metrics

## 🔧 Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Generate sitemap
npm run postbuild
```

## 📁 Project Structure

```
src/
├── app/
│   ├── page.tsx              # Home page
│   ├── buyers/page.tsx       # Buyers page
│   ├── investors/page.tsx    # Investors page
│   ├── trace/page.tsx        # Trace page
│   ├── about/page.tsx        # About page
│   ├── contact/page.tsx      # Contact page
│   ├── legal/
│   │   ├── imprint/page.tsx  # Legal imprint
│   │   └── privacy/page.tsx  # Privacy policy
│   └── api/contact/route.ts  # Contact form API
├── components/
│   ├── NavBar.tsx            # Navigation
│   ├── Footer.tsx            # Footer
│   └── Hero.tsx              # Hero component
└── lib/
    └── utils.ts              # Utility functions
```

## 🎯 Deployment Checklist

- [ ] Environment variables set in Amplify
- [ ] Branch mapping configured
- [ ] Build settings verified
- [ ] Security headers active
- [ ] Analytics configured
- [ ] Sitemap generation working
- [ ] All pages accessible
- [ ] Contact form functional
- [ ] API endpoints responding
- [ ] Performance metrics acceptable

## 🚨 Troubleshooting

### Build Failures
- Check Node.js version (18+ required)
- Verify all dependencies installed
- Check environment variables
- Review build logs in Amplify console

### Runtime Issues
- Verify API endpoints are accessible
- Check CORS configuration
- Review browser console for errors
- Validate environment variables

### Performance Issues
- Enable CloudFront caching
- Optimize images
- Check bundle size
- Review Core Web Vitals

## 📞 Support

For deployment issues:
1. Check Amplify build logs
2. Review environment variables
3. Verify API connectivity
4. Contact DevOps team

---

**Last Updated:** September 9, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
