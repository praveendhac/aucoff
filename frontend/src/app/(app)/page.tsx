import { PostureDashboardView } from "@/components/dashboard/posture-dashboard";
import { PageHeader } from "@/components/shell/page-header";

export default function Home() {
  return (
    <>
      <PageHeader title="Compliance posture" crumbs={["Dashboard"]} />
      <PostureDashboardView />
    </>
  );
}
