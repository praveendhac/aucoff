import NextAuth from "next-auth";
import { buildAuthOptions } from "@/lib/auth";

// The OIDC login, callback and logout handlers: the only unauthenticated route handlers (ZT-2).
const handler = (request: Request, context: unknown) =>
  (NextAuth(buildAuthOptions()) as (r: Request, c: unknown) => Promise<Response>)(request, context);

export { handler as GET, handler as POST };
