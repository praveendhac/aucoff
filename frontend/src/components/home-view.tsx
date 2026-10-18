export function HomeView({ tenantId, signOut }: { tenantId?: string; signOut: React.ReactNode }) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-3 p-8">
      <h1 className="text-3xl font-semibold tracking-tight">AUCoFF</h1>
      <p className="text-zinc-600 dark:text-zinc-400">
        AgenticAI Unified Compliance Framework for Fintechs. Application shell coming soon.
      </p>
      {tenantId ? <p className="font-mono text-sm text-zinc-500">tenant {tenantId}</p> : null}
      {signOut}
    </main>
  );
}
