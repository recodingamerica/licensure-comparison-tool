"use client";

// Legacy /profile?p=<id> → /professions/<id> redirect.
//
// The old route used a query parameter for the profession; the unified
// /professions/[id] route uses a path segment. next.config.ts can't match
// query params cleanly, so we redirect client-side here.

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

function Redirector() {
  const router = useRouter();
  const params = useSearchParams();
  useEffect(() => {
    const p = params.get("p");
    router.replace(p ? `/professions/${encodeURIComponent(p)}` : "/");
  }, [params, router]);
  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <p className="text-sm text-muted-foreground">Redirecting…</p>
    </main>
  );
}

export default function LegacyProfile() {
  return (
    <Suspense fallback={<main className="mx-auto max-w-2xl px-6 py-12"><p className="text-sm text-muted-foreground">Loading…</p></main>}>
      <Redirector />
    </Suspense>
  );
}
