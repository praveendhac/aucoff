import { EvidenceView } from "@/components/lists/evidence-view";
import { PageHeader } from "@/components/shell/page-header";

export default function Page() {
  return (
    <>
      <PageHeader title="Evidence" crumbs={["Evidence"]} />
      <EvidenceView />
    </>
  );
}
