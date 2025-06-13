import {NextResponse} from 'next/server'

const publicRoutes = ['/api/jobs/submit', '/api/jobs/query']
const API_KEY = process.env.APP_API_KEY // Read APP_API_KEY from .env

export default async function middleware(req) {
  // Allow specific public routes
  if (publicRoutes.includes(req.nextUrl.pathname)) {
    return NextResponse.next()
  }

  // Exception for a route with jobId in the middle
  if (req.nextUrl.pathname.endsWith('/predictions/query') || req.nextUrl.pathname.endsWith('/predictions/csv')) {
    return NextResponse.next()
  }

  const authHeader = req.headers.get('Authorization')

  if (!API_KEY) {
    return NextResponse.json({error: 'Auth is not configured on the server'}, {status: 409})
  }

  if (!API_KEY || !authHeader || authHeader !== `Bearer ${API_KEY}`) {
    return NextResponse.json({error: 'Forbidden'}, {status: 403})
  }

  return NextResponse.next()
}

// Routes Middleware should not run on
export const config = {
  matcher: ['/api/:path*'],
}
