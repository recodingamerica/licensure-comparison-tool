"use client";

// Reusable US state choropleth.
//
// Owns the react-simple-maps geography fetch, the FIPS→USPS mapping, and
// the floating tooltip that follows the cursor. Callers pass:
//   - `fillFor(state)` to pick a color per USPS code
//   - `renderTooltip(state)` for hover content (null = no tooltip for that state)
//   - optional `onClick(state)` for navigation / drill-down
//
// Both /professions/<X>?view=map (MapView) and the homepage "by state" mode
// use this. Keeps the geography fetch + FIPS lookup in one place.

import { useState, type ReactNode } from "react";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import { COLOR_TOKENS } from "@/lib/web-colors";

const GEO_URL = "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json";

// FIPS → USPS. us-atlas keys state features by FIPS id; the rest of the
// pipeline (and our state-keyed payloads) uses USPS two-letter codes.
const FIPS_TO_USPS: Record<string, string> = {
  "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
  "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
  "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
  "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
  "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
  "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
  "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
  "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
  "54": "WV", "55": "WI", "56": "WY",
};

// Fill for a state with no value — from the token source (config/web_colors.yaml).
export const NO_DATA_FILL = COLOR_TOKENS.light["map-no-data"];

export type UsMapProps = {
  fillFor: (state: string) => string;
  renderTooltip: (state: string) => ReactNode;
  onClick?: (state: string) => void;
  // Width × height SVG box. Defaults match the AlbersUSA layout MapView uses.
  width?: number;
  height?: number;
  // Drop the bordered frame (the map sits inline in the page).
  bare?: boolean;
  // Outline one state (e.g. the focus state, Utah) with a colored stroke.
  highlightState?: string;
  highlightColor?: string;
};

export function UsMap({
  fillFor,
  renderTooltip,
  onClick,
  width = 975,
  height = 610,
  bare = false,
  highlightState,
  highlightColor = "#111827",
}: UsMapProps) {
  const [hover, setHover] = useState<{ state: string; x: number; y: number } | null>(null);
  const tip = hover ? renderTooltip(hover.state) : null;

  return (
    <>
      <div className={bare ? "" : "rounded-lg border bg-white"}>
        <ComposableMap
          projection="geoAlbersUsa"
          projectionConfig={{ scale: 1000 }}
          width={width}
          height={height}
          style={{ width: "100%", height: "auto" }}
        >
          <Geographies geography={GEO_URL}>
            {({ geographies }) =>
              geographies.map((geo) => {
                const fips = String(geo.id).padStart(2, "0");
                const usps = FIPS_TO_USPS[fips];
                const fill = usps ? fillFor(usps) : NO_DATA_FILL;
                const clickable = !!(usps && onClick);
                const highlighted = !!usps && usps === highlightState;
                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill={fill}
                    stroke={highlighted ? highlightColor : "#ffffff"}
                    strokeWidth={highlighted ? 2 : 0.5}
                    onMouseEnter={(e) => {
                      if (usps)
                        setHover({ state: usps, x: e.clientX, y: e.clientY });
                    }}
                    onMouseMove={(e) => {
                      if (usps)
                        setHover((h) =>
                          h && h.state === usps
                            ? { ...h, x: e.clientX, y: e.clientY }
                            : h,
                        );
                    }}
                    onMouseLeave={() => setHover(null)}
                    onClick={() => {
                      if (usps && onClick) onClick(usps);
                    }}
                    style={{
                      default: { outline: "none", cursor: clickable ? "pointer" : "default" },
                      hover: { outline: "none", opacity: 0.85, cursor: clickable ? "pointer" : "default" },
                      pressed: { outline: "none" },
                    }}
                  />
                );
              })
            }
          </Geographies>
        </ComposableMap>
      </div>

      {hover && tip && (() => {
        // Flip the tooltip to the left / above the cursor when it would overflow
        // the viewport edge (otherwise far-right states like NY/ME clip).
        const pad = 12;
        const TW = 340, TH = 300; // approx tooltip footprint
        const vw = typeof window !== "undefined" ? window.innerWidth : 1280;
        const vh = typeof window !== "undefined" ? window.innerHeight : 800;
        const left = hover.x + pad + TW > vw ? Math.max(8, hover.x - pad - TW) : hover.x + pad;
        const top = hover.y + pad + TH > vh ? Math.max(8, hover.y - pad - TH) : hover.y + pad;
        return (
          <div
            className="pointer-events-none fixed z-50 max-w-lg rounded-md border bg-popover px-4 py-3 text-sm shadow-md"
            style={{ left, top }}
          >
            {tip}
          </div>
        );
      })()}
    </>
  );
}
