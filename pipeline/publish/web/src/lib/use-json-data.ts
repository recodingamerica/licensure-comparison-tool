import { useEffect, useState } from "react";

/**
 * Fetch a JSON payload whenever `url` changes and expose `{ data, error }`.
 * Covers only the plain shape: GET the url, `json()` on 2xx, else surface the
 * error as a string. Pass `notFoundMessage` for a friendlier non-2xx message
 * than the default `HTTP <status>`.
 *
 * Views with richer semantics (404-as-absent, an enum load state, parallel
 * fetches) keep their own effect on purpose — don't force them through here.
 */
export function useJsonData<T>(
  url: string,
  notFoundMessage?: string,
): { data: T | null; error: string | null } {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setData(null);
    setError(null);
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(notFoundMessage ?? `HTTP ${r.status}`);
        return r.json();
      })
      .then((d: T) => {
        if (!cancelled) setData(d);
      })
      .catch((e) => {
        if (!cancelled) setError(String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [url, notFoundMessage]);

  return { data, error };
}
