import Link from "next/link";

// The error/loading chrome shared by the two browse routes (/browse/[state] and
// /browse/[state]/[prof]) — identical in both, and BrowseLoadingMain doubles as
// the Suspense fallback.

const WRAP = "mx-auto max-w-2xl px-6 py-12";

export function BrowseLoadingMain() {
  return (
    <main className={WRAP}>
      <p className="text-xs text-muted-foreground">Loading…</p>
    </main>
  );
}

export function BrowseErrorMain({ error }: { error: string }) {
  return (
    <main className={WRAP}>
      <p className="text-sm text-destructive">{error}</p>
      <Link href="/" className="text-xs underline mt-4 block">
        ← home
      </Link>
    </main>
  );
}
