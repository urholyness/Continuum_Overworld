import { NextRequest, NextResponse } from 'next/server';
import { logger } from '@/lib/utils/logger';

export async function authMiddleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Skip middleware for static files, API routes, and auth callbacks
  if (
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/api/') ||
    pathname.startsWith('/auth/') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // Get JWT token from cookie or Authorization header
  const token = request.cookies.get('auth-token')?.value ||
    request.headers.get('authorization')?.replace('Bearer ', '');

  // Check if accessing admin routes
  const isAdminRoute = pathname.startsWith('/admin');
  
  if (!token) {
    logger.warn('Unauthenticated request', { pathname });
    
    // Redirect to login for admin routes
    if (isAdminRoute) {
      const loginUrl = new URL('/auth/login', request.url);
      loginUrl.searchParams.set('redirect', pathname);
      return NextResponse.redirect(loginUrl);
    }
    
    // Allow access to other routes but without auth
    return NextResponse.next();
  }

  try {
    // TODO: Implement JWT validation
    // const decoded = jwt.verify(token, process.env.JWT_SECRET!);
    // const groups = decoded['cognito:groups'] || [];
    
    // For now, assume valid token
    const groups = ['ops', 'trace']; // Mock groups - replace with actual JWT parsing
    
    // Check admin access
    if (isAdminRoute && !groups.includes('admin')) {
      logger.warn('Insufficient permissions for admin route', { 
        pathname, 
        groups 
      });
      return new NextResponse('Forbidden', { status: 403 });
    }
    
    // Check ops access
    if (pathname.startsWith('/ops') && !groups.includes('ops') && !groups.includes('admin')) {
      logger.warn('Insufficient permissions for ops route', { 
        pathname, 
        groups 
      });
      return new NextResponse('Forbidden', { status: 403 });
    }
    
    // Check trace access
    if (pathname.startsWith('/trace') && !groups.includes('trace') && !groups.includes('admin')) {
      logger.warn('Insufficient permissions for trace route', { 
        pathname, 
        groups 
      });
      return new NextResponse('Forbidden', { status: 403 });
    }

    return NextResponse.next();
    
  } catch (error) {
    logger.error('Auth middleware error', { 
      pathname, 
      error: error instanceof Error ? error.message : 'Unknown error' 
    });
    
    const loginUrl = new URL('/auth/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }
}