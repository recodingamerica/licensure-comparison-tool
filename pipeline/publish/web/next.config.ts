import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  trailingSlash: true,
  images: { unoptimized: true },

  // Old URLs → new unified routes. The /profile?p=X case is handled at the
  // page level (see /profile/page.tsx) since Next's redirects() can't match
  // on query parameters as cleanly as path segments.
  async redirects() {
    return [
      // NOTE: /browse/<state> and /browse/<state>/<prof> are intentionally
      // NOT redirected — they are the canonical "full statute tree" views
      // (whole state and per-(state, profession) respectively), linked from
      // the /states/<state> portfolio.
      {
        // /umbrella/<state> is now the state portfolio; the tree is one
        // click away via the "Open full statute tree" button on the
        // portfolio, so the legacy URL just lands on the portfolio.
        source: "/umbrella/:state",
        destination: "/states/:state",
        permanent: true,
      },
      {
        source: "/umbrella/profession/:id",
        // The merged /professions/[id] uses ?view=statutes (one tab for
        // practice-act + umbrella). The redirect lands users there since the
        // umbrella content now lives inside that combined view.
        destination: "/professions/:id?view=statutes",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
