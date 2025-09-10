export async function getJWT(): Promise<string | null> {
  // SSR: read from cookies(); CSR: read from secure storage via API
  // Placeholder implementation - will be implemented based on your auth gateway
  
  if (typeof window === 'undefined') {
    // Server-side: read from cookies
    const { cookies } = await import('next/headers');
    const authCookie = cookies().get('auth-token');
    return authCookie?.value || null;
  } else {
    // Client-side: read from localStorage or make API call
    try {
      const token = localStorage.getItem('auth-token');
      return token;
    } catch {
      return null;
    }
  }
}

export async function setJWT(token: string): Promise<void> {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth-token', token);
  }
}

export async function clearJWT(): Promise<void> {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth-token');
  }
}