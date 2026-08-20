import { NextResponse } from 'next/server'

// Rewrite every non-API, non-asset path to '/', so the client SPA in app/page.js
// can own locale + branch routing (e.g. /ko/seoul-street/menu) and deep links /
// refreshes still resolve. The browser URL is preserved; only the served page is '/'.
export function middleware(request) {
  return NextResponse.rewrite(new URL('/', request.url))
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|.*\\.).*)'],
}
