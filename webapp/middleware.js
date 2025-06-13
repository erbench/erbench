import {NextResponse} from 'next/server'

const publicRoutes = ['/api/jobs']
const API_KEY = process.env.APP_API_KEY // Read APP_API_KEY from .env

export default async function middleware(req) {
  // Allow GET requests to pass through without authentication
  if (req.method === 'GET') {
    return NextResponse.next()
  }

  // Allow POST requests to /query methods
  if (req.nextUrl.pathname.endsWith('/query') && req.method === 'POST') {
    return NextResponse.next()
  }

  // Allow specific public routes
  if (publicRoutes.includes(req.nextUrl.pathname)) {
    return NextResponse.next()
  }

  const authHeader = req.headers.get('Authorization')

  if (!API_KEY || !authHeader || authHeader !== `Bearer ${API_KEY}`) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
  }

  return NextResponse.next()
}

// Routes Middleware should not run on
export const config = {
  matcher: ['/api/:path*'],
}
