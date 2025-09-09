# GreenStemGlobal Production Website

Production website for GreenStemGlobal - connecting EU buyers to verified East African farms with real-time traceability and compliance.

## 🚀 Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS + Custom Design System
- **Components:** shadcn/ui components
- **Forms:** Zod validation
- **Analytics:** Plausible Analytics (privacy-friendly)
- **Deployment:** AWS Amplify
- **SEO:** next-sitemap, structured metadata

## 📁 Project Structure

```
Site--GreenStemGlobal__PROD@v1.0.0/
├── src/
│   ├── app/
│   │   ├── page.tsx                # Home page
│   │   ├── buyers/page.tsx         # Buyers information
│   │   ├── investors/page.tsx      # Investor information
│   │   ├── trace/page.tsx          # Supply chain traceability
│   │   ├── about/page.tsx          # About us
│   │   ├── contact/page.tsx        # Contact form
│   │   ├── legal/
│   │   │   ├── imprint/page.tsx    # Legal imprint
│   │   │   └── privacy/page.tsx    # Privacy policy
│   │   └── api/
│   │       └── contact/route.ts    # Contact form API
│   ├── components/                 # Reusable components
│   └── lib/                        # Utility functions
├── public/                         # Static assets
├── amplify.yml                     # AWS Amplify config
└── next-sitemap.config.js          # Sitemap configuration
```

## 🎨 Design System

### Colors
- **Leaf:** #10b981 (Primary green)
- **Stem:** #065f46 (Dark green)
- **Soil:** #111827 (Dark text)
- **Light:** #f9fafb (Background)
- **Accent:** #f59e0b (Orange accent)

### Typography
- **Body:** Inter
- **Display:** DM Sans

### Components
- NavBar with mobile responsive menu
- Footer with sitemap and legal links
- Hero sections with CTAs
- Product cards with specifications
- Contact form with GDPR compliance

## 🔧 Environment Variables

Create a `.env.local` file with:

```env
# Site Configuration
NEXT_PUBLIC_SITE_ENV=DEV|STAGE|PROD
NEXT_PUBLIC_SITE_URL=https://greenstemglobal.com

# API Configuration
NEXT_PUBLIC_API_BASE_URL=https://api.greenstemglobal.com

# Analytics (Optional)
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=greenstemglobal.com

# Contact Form (Server-side)
CONTACT_EMAIL=info@greenstemglobal.com
SENDGRID_API_KEY=your-sendgrid-key
```

## 📦 Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🚢 Deployment

### AWS Amplify Branch Mapping

- `dev` branch → DEV environment
- `stage` branch → STAGE environment
- `main` branch → PROD environment

### Deploy Commands

```bash
# Deploy to DEV
git push origin dev

# Deploy to STAGE
git push origin stage

# Deploy to PRODUCTION
git push origin main
```

## ✅ Quality Checklist

### Performance
- [ ] Lighthouse Performance ≥ 95
- [ ] Images optimized (WebP/AVIF)
- [ ] Code splitting implemented
- [ ] Critical CSS inlined

### SEO
- [ ] All pages have unique meta titles/descriptions
- [ ] Open Graph tags configured
- [ ] Sitemap generated automatically
- [ ] Robots.txt configured

### Accessibility
- [ ] Lighthouse Accessibility = 100
- [ ] WCAG 2.1 AA compliant
- [ ] Keyboard navigation works
- [ ] Screen reader tested
- [ ] Focus indicators visible
- [ ] Color contrast ≥ 4.5:1

### Security
- [ ] Content Security Policy configured
- [ ] HTTPS enforced
- [ ] Security headers set
- [ ] No client-side secrets
- [ ] Form validation on client and server

## 📊 Features

### For Buyers
- Product specifications (French beans, chili, passion fruit, macadamia)
- Quality assurance information
- Partnership process outline
- Sample shipment requests

### For Investors
- Investment thesis
- Use of funds breakdown
- Governance structure
- Transparency commitments
- Data room access

### Traceability
- Public trace highlights (24-48h delay)
- Real-time access for active buyers
- Supply chain event timeline
- Integration with backend API

### Contact
- GDPR-compliant contact form
- Server-side validation with Zod
- Email integration ready
- Spam protection

## 🔐 Security Headers

Configured in `amplify.yml`:
- Strict-Transport-Security
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Content Security Policy
- Referrer-Policy

## 📝 Content Guidelines

**CRITICAL:** No unverifiable claims or placeholder data
- All numbers must be backed by real data
- All certifications must be documented
- Product specs from actual operations
- No "coming soon" or placeholder text

## 🧪 Testing

```bash
# Run linter
npm run lint

# Type checking
npx tsc --noEmit

# Lighthouse audit
npx lighthouse https://localhost:3000
```

## 📚 Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [AWS Amplify](https://docs.amplify.aws)
- [Zod Validation](https://zod.dev)

## 👥 Team

- **Executor:** Cursor AI
- **Reviewer:** Claude
- **PM:** Naivasha

## 📄 License

© 2025 GreenStemGlobal. All rights reserved.

---

**Note:** This is a production website with real content only. No placeholders, no unverifiable claims, no mock data.