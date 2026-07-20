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
