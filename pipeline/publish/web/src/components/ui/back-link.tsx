import type { ReactNode } from "react";
import Link from "next/link";

import { cn } from "@/lib/utils";
import { EYEBROW } from "./eyebrow";

/** The repeated "← label" back link — an eyebrow-styled Link with a hover reveal. */
export function BackLink({
  href,
  className,
  children,
}: {
  href: string;
  className?: string;
  children: ReactNode;
}) {
  return (
    <Link href={href} className={cn(EYEBROW, "hover:text-foreground", className)}>
      ← {children}
    </Link>
  );
}
