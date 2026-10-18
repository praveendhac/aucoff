import { getServerSession } from "next-auth";
import { AppShell } from "@/components/shell/app-shell";
import { buildAuthOptions } from "@/lib/auth";

export const dynamic = "force-dynamic";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const session = await getServerSession(buildAuthOptions());
  return (
    <AppShell roles={session?.roles ?? []} tenantId={session?.tenantId}>
      {children}
    </AppShell>
  );
}
