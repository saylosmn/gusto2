# Gusto Restaurant — multi-branch website

An Italian-leaning restaurant group in Ulaanbaatar with **three branches**, a fully
**database-driven** public site, and **six languages** (mn, en, ru, zh, ko, ja).

Built on the project's Next.js (App Router) + MongoDB stack.

## What's in this slice (A — public site)

- **Group home** with hero, live open/closed status strip, signature dishes, wine & bar, and per-branch Google ratings.
- **Locations index** — a real three-way comparison (photo, neighbourhood, price range, rating, today's hours, distance).
- **Branch home / menu / reserve** routes, per branch.
- **Branch switcher that retints the whole page** (basil / ochre / barolo) — the signature design element.
- **Menu with per-branch prices** (read-only overrides), sold-out greying, dietary filters, search, and a *compare across branches* toggle.
- **Reservations**: form -> DB, validated against that branch's hours in **Asia/Ulaanbaatar** (rejects past / before-open / after-close). No inbox; nothing exposes other guests' data.
- **i18n** everywhere: nav, buttons, live-status (ICU message formatting), footer in all six locales, one fully-translated menu category, mn+en long-form. Fallback chain: requested -> mn -> en.
- Per-locale font stacks (Playfair Display + Inter for Latin/Cyrillic; Noto Serif/Sans SC/JP/KR for CJK & Hangul).

## Data model (MongoDB collections)

`branches` (soft-delete via `isDeleted`, `needsVerification` flag), `opening_hours`,
`categories`, `menu_items` (per-branch pricing embedded on each item as
`branchOverrides: [{ branchId, priceOverride, isAvailable, isServed }]`),
`reservations`, `testimonials`, `gallery_images`, `settings`.
All translated text is a locale-keyed subdocument `{ mn, en, ru, zh, ko, ja }` — all six
keys always present, empty allowed. Adding a seventh language = add a key, no schema change.

## Local setup

1. `yarn install`
2. Copy `.env.example` to `.env` and set `MONGO_URL`, `DB_NAME`.
3. Seed the database: `node scripts/seed.js`  (the app also auto-seeds on first request if empty)
4. `yarn dev` and open the app. `/` redirects to the detected locale.

## Routing

`/[locale]` group home · `/[locale]/branches` · `/[locale]/[branch]` ·
`/[locale]/[branch]/menu` · `/[locale]/[branch]/reserve` · `/[locale]/about` · `/[locale]/contact`.

## Seed facts

Only the **three Google-verified branches** are seeded (Seoul Street — default, White Gate,
Tenger), each with `needsVerification: true`. Closing hours and Tenger's opening time are left
empty (unknown) on purpose — never invented. The Facebook/Instagram locations are **not** seeded.

## Render дээр deploy хийх

Энэ repo-д `render.yaml` (Blueprint) бэлэн байгаа — Render build/start командыг өөрөө уншина.

**1. MongoDB бэлдэх.** Render дээр Mongo байхгүй тул [MongoDB Atlas](https://www.mongodb.com/atlas)
дээр үнэгүй cluster үүсгэ. Network Access → `0.0.0.0/0` (эсвэл Render-ийн static outbound IP)
нэмж, connection string-ээ ав.

**2. Repo-г GitHub-д түлх.**

```bash
git init && git add -A && git commit -m "Gusto site" && git branch -M main
```

Дараа нь GitHub дээр repo үүсгээд `git remote add origin <url> && git push -u origin main`.

**3. Render дээр.** Dashboard → **New → Blueprint** → энэ repo-г сонго. `render.yaml`-аас
`gusto` нэртэй web service үүснэ. `sync: false` гэсэн хувьсагчдыг гараар бөглөнө:

| Хувьсагч | Утга |
|---|---|
| `MONGO_URL` | Atlas connection string |
| `NEXT_PUBLIC_BASE_URL` | `https://gusto.onrender.com` (эхний deploy-ийн дараа) |
| `DB_NAME` | `gusto` (blueprint-д бэлэн) |
| `CORS_ORIGINS` | `*` (blueprint-д бэлэн) |

**4. Seed.** Тусад нь юу ч ажиллуулах шаардлагагүй — `branches` collection хоосон бол
API анхны хүсэлт дээр өөрөө seed хийнэ. Гараар дахин seed хийх бол: `yarn seed`.

**5. `NEXT_PUBLIC_BASE_URL`-г тавьсны дараа дахин deploy хий** — энэ хувьсагч build үед
кодод шингэдэг тул зөвхөн дараагийн build-д нөлөөлнө.

### Анхаарах зүйлс

- **Free plan** 15 минут идэвхгүй байвал унтарч, дараагийн хүсэлт дээр ~50 секунд сэрнэ.
- Build-д `devDependencies` (tailwind, postcss, autoprefixer) хэрэгтэй тул
  `NODE_ENV=production`-г Render-ийн environment дээр **бүү нэм**.
- Node хувилбар `.node-version` болон `render.yaml`-д 22.11.0 гэж тогтоосон.
