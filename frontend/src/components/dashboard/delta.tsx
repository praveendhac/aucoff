import { ArrowDown, ArrowUp, Minus } from "lucide-react";
import { deltaTone } from "@/lib/dashboard";

// Arrow + signed number + word, so direction and good/bad never rely on colour alone.
export function Delta({
  value,
  lowerIsBetter = false,
  unit = "",
  onDark = false,
}: {
  value: number;
  lowerIsBetter?: boolean;
  unit?: string;
  onDark?: boolean;
}) {
  const tone = deltaTone(value, lowerIsBetter);
  const Icon = value > 0 ? ArrowUp : value < 0 ? ArrowDown : Minus;
  const word = tone === "better" ? "better" : tone === "worse" ? "worse" : "unchanged";
  const colour = onDark
    ? "#ffffff"
    : tone === "better"
      ? "var(--pass)"
      : tone === "worse"
        ? "var(--fail)"
        : "var(--text-muted)";
  const sign = value > 0 ? "+" : "";
  return (
    <span className="inline-flex items-center gap-1 text-xs font-medium" style={{ color: colour }}>
      <Icon size={14} aria-hidden />
      <span className="tabular">
        {sign}
        {value}
        {unit}
      </span>
      <span>{word} vs previous scan</span>
    </span>
  );
}
