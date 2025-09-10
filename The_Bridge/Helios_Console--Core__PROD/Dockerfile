# Dockerfile for Helios Console - Development & Production Ready
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --omit=dev --no-audit --no-fund

# Development dependencies (for dev builds)
FROM base AS dev-deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json ./
# Generate clean package-lock.json inside container to avoid WSL corruption
RUN npm install --package-lock-only --no-audit --no-fund
RUN npm ci --no-audit --no-fund

# Development stage
FROM base AS dev
WORKDIR /app
COPY --from=dev-deps /app/node_modules ./node_modules
COPY . .

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Start development server
CMD ["npm", "run", "dev"]

# Production builder
FROM base AS builder
WORKDIR /app
COPY --from=dev-deps /app/node_modules ./node_modules
COPY . .

# Build environment variables (required for Next.js build)
ENV NEXT_PUBLIC_DEMO_MODE=true
ENV NEXT_PUBLIC_SITE_ENV=production
ENV NEXT_PUBLIC_API_BASE_URL=https://cn-dev-api.greenstemglobal.com

# Build application
RUN npm run build

# Production stage
FROM base AS production
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]