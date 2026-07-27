"use client";

import { createContext, useContext } from "react";

/**
 * Opening a state's detail Sheet — as a capability any view can call, rather than a
 * prop each view has to be wired for.
 *
 * A state is the primary object in this app and it appears in almost every view (table,
 * map, scope matrix, similarity, novel policies). Before this, only the table could open
 * the Sheet, so the same gesture on the same object did different things — or nothing —
 * depending on which view you were in. The profile page's map was the clearest case: it
 * rendered the same <UsMap> as the homepage but without a click handler, so clicking a
 * state silently did nothing.
 *
 * Views call `useOpenStateDetail()` and get a function they can call unconditionally.
 * Outside a provider it returns null, so a view can ask "am I able to open detail here?"
 * and render itself non-interactive rather than presenting a dead affordance.
 */
export type OpenStateDetail = (
  state: string,
  opts?: {
    /** Grid colId to focus, when the click came from a specific column. */
    colId?: string | null;
    /** Category chip clicked, when the click came from one. */
    category?: string | null;
  },
) => void;

const StateFocusContext = createContext<OpenStateDetail | null>(null);

export const StateFocusProvider = StateFocusContext.Provider;

/** The opener, or null when no detail Sheet is available in this tree. */
export function useOpenStateDetail(): OpenStateDetail | null {
  return useContext(StateFocusContext);
}
