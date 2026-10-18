import { ControlsView } from "@/components/lists/controls-view";
import { PageHeader } from "@/components/shell/page-header";

export default function Page() {
  return (
    <>
      <PageHeader title="Controls" crumbs={["Unified controls"]} />
      <ControlsView />
    </>
  );
}
