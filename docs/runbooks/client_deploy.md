# Publishing to the live website (one-time setup + deploy)

`publish` (no flag) rebuilds an occupation's data payload and uploads it to the
blob store. That's free and safe. Adding `--deploy` also **pushes the public live
site** (utah-licensing.vercel.app) so it picks up the new data — that step needs a
one-time Vercel setup and asks for a typed "yes" before it runs.

> If the maintainer handles deploys, you never need this — just run `publish`
> without `--deploy` and tell them there's new data to push.

## One-time setup (once per machine)

You need Node.js installed, then, from the repo root:

```bash
cd pipeline/publish/web
npm install                              # install the site's build deps
npx vercel login                         # sign in to the Vercel account that owns the site
npx vercel link --yes --project utah-licensing   # connect this folder to the project
npx vercel env pull .env.local           # pull BLOB_READ_WRITE_TOKEN + SITE_PASSWORD
cd ../../..                              # back to repo root
```

`vercel link` must target the **same Vercel project/org that hosts the live site** —
if you're not sure which account that is, ask the maintainer before linking.

## Deploying

From the repo root, after you've built data for the occupations you want live:

```bash
pipeline/.venv/bin/python -m pipeline.client.run publish --professions dentistry,nursing --deploy
```

It prints exactly what will go live and waits for you to type `yes`. Pass `--yes`
to skip the prompt only in an automated/trusted context.

Publishing without deploying (safe anytime, no setup needed):

```bash
pipeline/.venv/bin/python -m pipeline.client.run publish --professions dentistry,nursing
```

## Notes

- The site is behind HTTP Basic Auth (password `SITE_PASSWORD`, set on Vercel and
  in `.env.local`). Deploying doesn't change that.
- A deploy rebuilds the whole site from the current blob payloads, so it also
  reflects any other occupations already uploaded — not just the ones you named.
