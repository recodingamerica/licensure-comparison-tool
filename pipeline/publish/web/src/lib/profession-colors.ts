// One consistent color + abbreviation per profession, used by the browse
// view's tree leaves (applies_to chips) and the state-browse filter chip
// bar. Same color in the filter bar and on each row tells the reader
// "this row applies to that profession."

export type ProfessionStyle = {
  bg: string;        // background — light tint for badge
  text: string;      // foreground text class for the badge
  border: string;    // optional border class
  dot: string;       // solid color class for inline dots
  abbr: string;      // 3-letter abbreviation
};

export const PROFESSION_STYLE: Record<string, ProfessionStyle> = {
  podiatry: {
    bg: "bg-sky-100",
    text: "text-sky-800",
    border: "border-sky-300",
    dot: "bg-sky-500",
    abbr: "POD",
  },
  nursing: {
    bg: "bg-emerald-100",
    text: "text-emerald-800",
    border: "border-emerald-300",
    dot: "bg-emerald-500",
    abbr: "NUR",
  },
  medicine: {
    bg: "bg-rose-100",
    text: "text-rose-800",
    border: "border-rose-300",
    dot: "bg-rose-500",
    abbr: "MED",
  },
  dentistry: {
    bg: "bg-amber-100",
    text: "text-amber-800",
    border: "border-amber-300",
    dot: "bg-amber-500",
    abbr: "DEN",
  },
  optometry: {
    bg: "bg-violet-100",
    text: "text-violet-800",
    border: "border-violet-300",
    dot: "bg-violet-500",
    abbr: "OPT",
  },
  public_accountancy: {
    bg: "bg-slate-200",
    text: "text-slate-700",
    border: "border-slate-300",
    dot: "bg-slate-500",
    abbr: "ACT",
  },
};

export function professionStyle(key: string): ProfessionStyle {
  return (
    PROFESSION_STYLE[key] ?? {
      bg: "bg-muted",
      text: "text-foreground",
      border: "border-border",
      dot: "bg-muted-foreground",
      abbr: key.slice(0, 3).toUpperCase(),
    }
  );
}
