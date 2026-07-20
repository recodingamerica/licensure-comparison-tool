import type { ElementType, ReactNode } from "react";

import { cn } from "@/lib/utils";

/** The shared eyebrow class string — small mono uppercase tracking-widest muted label. */
export const EYEBROW = "text-xs font-mono uppercase tracking-widest text-muted-foreground";

/**
 * The repeated uppercase-tracking-widest label. Renders a `<p>` by default; pass
 * `as` for a heading/span and `className` to add trailing utilities (margins,
 * `border-b`, an explicit size like `text-[10px]`, etc.) — merged via twMerge so
 * an override wins.
 */
export function Eyebrow({
  as: Tag = "p",
  className,
  children,
}: {
  as?: ElementType;
  className?: string;
  children: ReactNode;
}) {
  return <Tag className={cn(EYEBROW, className)}>{children}</Tag>;
}
