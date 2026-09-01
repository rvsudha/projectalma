export type SearchParams = Record<string, string | string[] | undefined>;

/** Collapse Next's `string | string[] | undefined` to a single trimmed string. */
export function one(value: string | string[] | undefined): string | undefined {
  const v = Array.isArray(value) ? value[0] : value;
  const trimmed = v?.trim();
  return trimmed ? trimmed : undefined;
}

/** Flatten search params to a plain string map (first value wins). */
export function flatten(params: SearchParams): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [key, value] of Object.entries(params)) {
    const v = one(value);
    if (v) out[key] = v;
  }
  return out;
}
