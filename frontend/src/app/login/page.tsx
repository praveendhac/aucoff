import { SignInButton } from "@/components/auth-buttons";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-3xl font-semibold tracking-tight">AUCoFF</h1>
      <p className="text-zinc-600 dark:text-zinc-400">Sign in to continue.</p>
      <SignInButton />
    </main>
  );
}
