"use client";

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

/**
 * The one right-side detail panel.
 *
 * There were four hand-rolled versions of this — three inside StateDetailDialog (main,
 * coverage-gap, no-detail) and one in TagBreakdownSheet — with three different widths,
 * two different header treatments, and only some of them setting up the flex column that
 * makes the body scroll independently of the header. Nothing enforced that a new panel
 * would look like the existing ones.
 *
 * Width is a named choice rather than a class string, so "how wide is a detail panel"
 * has an answer instead of being re-decided per call site:
 *   narrow — a summary or a single list (tag breakdown, coverage gap)
 *   wide   — evidence side by side with statute text (the per-state Sheet)
 *
 * `children` is the body, and is NOT wrapped in a scroll container here: the per-state
 * Sheet needs its own body (search snippets, collapse toggle). Callers that just want a
 * plain scrolling body can use SheetScrollBody below.
 */
export type DetailSheetWidth = "narrow" | "wide";

const WIDTH_CLASS: Record<DetailSheetWidth, string> = {
  narrow: "w-full sm:max-w-md lg:max-w-xl",
  // The base SheetContent ships `data-[side=right]:sm:max-w-sm` (~384px), far too narrow
  // for evidence + statute side by side (Atharv's issue #12). `!` beats the base default.
  wide: "w-full sm:!max-w-2xl lg:!max-w-[65vw] xl:!max-w-[60vw]",
};

export function DetailSheet({
  open,
  onOpenChange,
  title,
  description,
  headerExtra,
  width = "narrow",
  children,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: React.ReactNode;
  description?: React.ReactNode;
  /** Actions or badges under the description (copy button, source links). */
  headerExtra?: React.ReactNode;
  width?: DetailSheetWidth;
  children?: React.ReactNode;
}) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className={`${WIDTH_CLASS[width]} p-0 gap-0 flex flex-col`}
      >
        <SheetHeader className="border-b px-6 py-4 flex-shrink-0 bg-background">
          <SheetTitle className={width === "wide" ? "text-xl" : "text-lg"}>
            {title}
          </SheetTitle>
          {description && <SheetDescription>{description}</SheetDescription>}
          {headerExtra}
        </SheetHeader>
        {children}
      </SheetContent>
    </Sheet>
  );
}

/** Plain scrolling body — the default when a panel has no special body behavior. */
export function SheetScrollBody({ children }: { children: React.ReactNode }) {
  return <div className="flex-1 overflow-auto px-6 py-4 space-y-6">{children}</div>;
}
