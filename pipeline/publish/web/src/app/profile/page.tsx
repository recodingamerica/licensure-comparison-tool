"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import type { ProfilePayload } from "@/lib/types";
import { ProfileView } from "@/components/profile-view";

function ProfileInner() {
  const params = useSearchParams();
  const prof = params.get("p") || "podiatry";
  const [payload, setPayload] = useState<ProfilePayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setPayload(null);
    setError(null);
    fetch(`/data/${encodeURIComponent(prof)}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`No data for "${prof}"`);
        return r.json();
      })
      .then((d: ProfilePayload) => setPayload(d))
      .catch((e) => setError(String(e)));
  }, [prof]);

  if (error) {
    return (
      <main className="mx-auto max-w-2xl px-6 py-12">
        <Link
          href="/"
          className="text-xs font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground"
        >
          ← all professions
        </Link>
        <div className="mt-6 rounded border border-destructive bg-destructive/5 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      </main>
    );
  }

  if (!payload) {
    return (
      <main className="mx-auto max-w-7xl px-6 py-12">
        <p className="text-sm text-muted-foreground">Loading…</p>
      </main>
    );
  }

  return <ProfileView payload={payload} />;
}

export default function ProfilePage() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto max-w-7xl px-6 py-12">
          <p className="text-sm text-muted-foreground">Loading…</p>
        </main>
      }
    >
      <ProfileInner />
    </Suspense>
  );
}
