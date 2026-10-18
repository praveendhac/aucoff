import { FindingsView } from "@/components/lists/findings-view";
import { PageHeader } from "@/components/shell/page-header";

export default function Page() {
  return (
    <>
      <PageHeader title="Findings" crumbs={["Findings"]} />
      <FindingsView />
    </>
  );
}
