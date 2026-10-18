import type { JWT } from "next-auth/jwt";
import type { NextAuthOptions } from "next-auth";

// Auth.js (NextAuth v4) in the BFF pattern: the authorization-code flow with PKCE and state runs on
// the server; the tokens live only inside the encrypted, httpOnly session cookie and are never
// handed to browser code (constitution ZT-2, frontend-spec section 5).

function required(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is not set; the web app refuses to start without it`);
  return value;
}

const REFRESH_MARGIN_MS = 30_000;

function claimsOf(accessToken: string): Record<string, unknown> {
  // The token came straight from the token endpoint over TLS; the gateway validates it again.
  const payload = accessToken.split(".")[1] ?? "";
  return JSON.parse(Buffer.from(payload, "base64url").toString("utf8")) as Record<string, unknown>;
}

async function refresh(token: JWT, issuerBackchannel: string): Promise<JWT> {
  try {
    const response = await fetch(`${issuerBackchannel}/protocol/openid-connect/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "refresh_token",
        client_id: required("OIDC_CLIENT_ID"),
        client_secret: required("OIDC_CLIENT_SECRET"),
        refresh_token: String(token.refreshToken),
      }),
    });
    if (!response.ok) throw new Error("refresh refused");
    const fresh = (await response.json()) as {
      access_token: string;
      refresh_token?: string;
      expires_in: number;
    };
    return {
      ...token,
      accessToken: fresh.access_token,
      refreshToken: fresh.refresh_token ?? token.refreshToken,
      expiresAt: Date.now() + fresh.expires_in * 1000,
      error: undefined,
    };
  } catch {
    return { ...token, error: "RefreshFailed" };
  }
}

export function buildAuthOptions(): NextAuthOptions {
  const issuer = required("OIDC_ISSUER"); // public issuer, as in every token
  const backchannel = required("OIDC_BACKCHANNEL_ISSUER"); // in-cluster URL for discovery/tokens
  return {
    secret: required("NEXTAUTH_SECRET"),
    session: { strategy: "jwt", maxAge: 8 * 60 * 60 },
    pages: { signIn: "/login", error: "/login" },
    providers: [
      {
        id: "keycloak",
        name: "Keycloak",
        type: "oauth",
        wellKnown: `${backchannel}/.well-known/openid-configuration`,
        issuer,
        clientId: required("OIDC_CLIENT_ID"),
        clientSecret: required("OIDC_CLIENT_SECRET"),
        authorization: { params: { scope: "openid profile email" } },
        checks: ["pkce", "state"],
        idToken: true,
        profile(profile: {
          sub: string;
          name?: string;
          email?: string;
          preferred_username?: string;
        }) {
          return {
            id: profile.sub,
            name: profile.name ?? profile.preferred_username ?? null,
            email: profile.email ?? null,
          };
        },
      },
    ],
    callbacks: {
      async jwt({ token, account }) {
        if (account?.access_token) {
          const claims = claimsOf(account.access_token);
          return {
            ...token,
            accessToken: account.access_token,
            refreshToken: account.refresh_token,
            expiresAt: (account.expires_at ?? 0) * 1000,
            tenantId: typeof claims.tenant_id === "string" ? claims.tenant_id : undefined,
          };
        }
        const expiresAt = typeof token.expiresAt === "number" ? token.expiresAt : 0;
        if (Date.now() < expiresAt - REFRESH_MARGIN_MS) return token;
        return refresh(token, backchannel);
      },
      async session({ session, token }) {
        // Only what the UI needs. The access and refresh tokens are NOT exposed to the browser.
        return {
          ...session,
          tenantId: token.tenantId,
          error: token.error,
        };
      },
    },
  };
}
