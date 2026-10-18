import { getToken } from "next-auth/jwt";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { isPublicPath } from "@/lib/public-paths";

// Default-deny for the whole web app (constitution ZT-1, ZT-2): nothing is served without a valid
// session except the paths in `isPublicPath`.
export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (isPublicPath(pathname)) return NextResponse.next();

  const token = await getToken({ req: request });
  if (token?.accessToken && !token.error) return NextResponse.next();

  if (pathname.startsWith("/bff/") || pathname.startsWith("/api/")) {
    return Response.json(
      { type: "about:blank", title: "Authentication required", status: 401 },
      { status: 401, headers: { "Content-Type": "application/problem+json" } },
    );
  }
  return NextResponse.redirect(new URL("/login", request.url));
}

export const config = { matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"] };
