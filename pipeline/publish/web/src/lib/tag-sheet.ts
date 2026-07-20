// Shared shapes + helpers for the tag sheet (/data/tag_sheet.json), consumed by
// both the home Field Tag Sheet report and the per-profession Tags tab. One
// definition so the two views can't drift.

export type Tag = { label: string; count: number; states?: number };
export type Assignment = { state: string; bucket: string; text: string };
export type SubField = {
  field_name: string;
  kind: "scalar" | "per_item";
  unit: string;
  rationale: string;
  tags: Tag[];
  assignments: Assignment[];
};
export type Field = {
  label: string;
  priority: boolean;
  present: boolean;
  subfields: SubField[];
};
export type ProfData = { profession: string; fields: Field[] };

// Group a subfield's per-state assignments by their bucket (tag).
export function groupByBucket(sf: SubField): Map<string, Assignment[]> {
  const byBucket = new Map<string, Assignment[]>();
  for (const a of sf.assignments) {
    const arr = byBucket.get(a.bucket);
    if (arr) arr.push(a);
    else byBucket.set(a.bucket, [a]);
  }
  return byBucket;
}

// One-line summary of a tag. `noun` names the per-item unit — "items" generically,
// "grounds" in the discipline (profile) context.
export function tagSummary(
  tag: Tag,
  kind: SubField["kind"],
  noun = "items",
): string {
  return kind === "per_item" && tag.states !== undefined
    ? `${tag.count} ${noun} across ${tag.states} states`
    : `${tag.count} states`;
}

// Plain-text dump of a field's whole breakdown for copy-paste. `header` (when
// given) is appended to the field label as a first line, e.g. the profession name.
export function breakdownText(
  field: Field,
  opts?: { header?: string; noun?: string },
): string {
  const lines: string[] = [
    opts?.header ? `${field.label} — ${opts.header}` : field.label,
  ];
  for (const sf of field.subfields) {
    lines.push("", sf.field_name);
    const byBucket = groupByBucket(sf);
    for (const tag of sf.tags) {
      lines.push(`  ${tag.label} (${tagSummary(tag, sf.kind, opts?.noun)})`);
      for (const m of byBucket.get(tag.label) ?? []) {
        lines.push(`    ${m.state}  ${m.text}`);
      }
    }
  }
  return lines.join("\n");
}
