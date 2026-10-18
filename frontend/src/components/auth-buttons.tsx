"use client";

import { signIn, signOut } from "next-auth/react";

const button =
  "rounded-lg bg-blue-900 px-4 py-2 text-sm font-medium text-white hover:bg-blue-800 focus-visible:outline-2 focus-visible:outline-offset-2";

export function SignInButton() {
  return (
    <button className={button} onClick={() => signIn("keycloak", { callbackUrl: "/" })}>
      Sign in
    </button>
  );
}

export function SignOutButton() {
  return (
    <button className={button} onClick={() => signOut({ callbackUrl: "/login" })}>
      Sign out
    </button>
  );
}
