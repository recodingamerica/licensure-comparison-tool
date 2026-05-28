"use client";

// MultiCheckPopover — generic multi-select dropdown.
//
// One button at the top showing "Label (selected/total) ▾", popover with
// search + checkbox list + bulk show all / clear actions. Same idiom as
// ColumnVisibilityPopover on /professions/<X> Table tab; suitable for
// profession filters on /browse/<state> and any other multi-pick UI.

import { useEffect, useMemo, useRef, useState } from "react";
import { Button } from "@/components/ui/button";

export type MultiCheckItem = {
  id: string;
  label: string;
  // Optional small colored swatch rendered before the label (e.g. profession
  // family dot). Pass a tailwind class like "bg-emerald-500".
  swatchClass?: string;
};

export function MultiCheckPopover({
  label,
  items,
  selected,
  onChange,
  buttonClassName,
}: {
  label: string;
  items: MultiCheckItem[];
  selected: Set<string>;
  onChange: (next: Set<string>) => void;
  buttonClassName?: string;
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  useEffect(() => {
    if (open) searchRef.current?.focus();
    else setQuery("");
  }, [open]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const sorted = [...items].sort((a, b) => a.label.localeCompare(b.label));
    if (!q) return sorted;
    return sorted.filter((i) => i.label.toLowerCase().includes(q));
  }, [items, query]);

  const toggle = (id: string) => {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    onChange(next);
  };

  const summary =
    selected.size === 0 || selected.size === items.length
      ? "all"
      : `${selected.size} of ${items.length}`;

  return (
    <div ref={ref} className="relative inline-block">
      <Button
        variant="outline"
        size="sm"
        className={`font-mono text-xs ${buttonClassName ?? ""}`}
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        {label} ({summary}) ▾
      </Button>
      {open && (
        <div
          role="menu"
          className="absolute left-0 top-full mt-1 w-80 max-h-[70vh] flex flex-col rounded-md border bg-popover text-popover-foreground shadow-md z-50"
        >
          <div className="px-2 pt-2 pb-1.5 text-xs font-mono uppercase tracking-widest text-muted-foreground">
            {label}
          </div>
          <div className="px-2 pb-2">
            <input
              ref={searchRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search…"
              className="w-full rounded border bg-background px-2 py-1 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>
          <div className="px-2 pb-1.5 text-xs text-muted-foreground flex items-center justify-between gap-2">
            <span>
              {filtered.length === items.length
                ? `${items.length} items`
                : `${filtered.length} of ${items.length} match`}
            </span>
            <div className="flex gap-1">
              <button
                type="button"
                className="hover:text-foreground underline"
                onClick={() => onChange(new Set(filtered.map((i) => i.id)))}
              >
                select all
              </button>
              <span>·</span>
              <button
                type="button"
                className="hover:text-foreground underline"
                onClick={() => onChange(new Set())}
              >
                clear
              </button>
            </div>
          </div>
          <div className="my-1 h-px bg-border" />
          <div className="overflow-y-auto p-1">
            {filtered.length === 0 ? (
              <div className="px-2 py-3 text-sm text-muted-foreground text-center">
                no matches
              </div>
            ) : (
              filtered.map((it) => (
                <label
                  key={it.id}
                  className="flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-accent hover:text-accent-foreground cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selected.has(it.id)}
                    onChange={() => toggle(it.id)}
                    className="h-4 w-4 rounded border-input"
                  />
                  {it.swatchClass && (
                    <span className={`w-2 h-2 rounded-full ${it.swatchClass}`} />
                  )}
                  <span>{it.label}</span>
                </label>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
