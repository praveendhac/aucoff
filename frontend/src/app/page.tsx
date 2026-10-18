import { getServerSession } from "next-auth";
import { SignOutButton } from "@/components/auth-buttons";
import { HomeView } from "@/components/home-view";
import { buildAuthOptions } from "@/lib/auth";

export const dynamic = "force-dynamic";

export default async function Home() {
  const session = await getServerSession(buildAuthOptions());
  return <HomeView tenantId={session?.tenantId} signOut={<SignOutButton />} />;
}
