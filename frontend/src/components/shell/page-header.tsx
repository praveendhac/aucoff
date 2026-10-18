export function PageHeader({
  title,
  crumbs,
  actions,
}: {
  title: string;
  crumbs: string[];
  actions?: React.ReactNode;
}) {
  return (
    <div className="mb-6">
      <nav aria-label="Breadcrumb" className="mb-1 text-xs text-muted">
        <ol className="flex gap-1.5">
          {crumbs.map((c, i) => (
            <li key={c} aria-current={i === crumbs.length - 1 ? "page" : undefined}>
              {i > 0 ? <span aria-hidden> / </span> : null}
              {c}
            </li>
          ))}
        </ol>
      </nav>
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {actions}
      </div>
    </div>
  );
}
