export function humanize(s: string | null | undefined): string {
  if (!s) return "";
  return String(s).replace(/_/g, " ").trim();
}

// Wrap matched substring in <mark>; allow whitespace flexibility for source
// line breaks. Returns React-renderable parts (string or marked span).
export function highlightInText(
  text: string,
  quote: string
): Array<{ kind: "text" | "mark"; value: string }> {
  if (!quote) return [{ kind: "text", value: text }];
  const trimmed = quote.trim();
  if (!trimmed) return [{ kind: "text", value: text }];
  const escaped = trimmed
    .replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
    .replace(/\s+/g, "\\s+");
  let pattern: RegExp;
  try {
    pattern = new RegExp(escaped, "i");
  } catch {
    return [{ kind: "text", value: text }];
  }
  const m = text.match(pattern);
  if (!m) return [{ kind: "text", value: text }];
  const i = text.indexOf(m[0]);
  return [
    { kind: "text", value: text.slice(0, i) },
    { kind: "mark", value: m[0] },
    { kind: "text", value: text.slice(i + m[0].length) },
  ];
}
