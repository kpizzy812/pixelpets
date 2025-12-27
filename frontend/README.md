# Pixel Pets Frontend

Telegram Mini App built with Next.js 16 and React 19.

## Tech Stack

- **Framework:** Next.js 16 (App Router)
- **UI:** React 19 + Tailwind CSS 4
- **State:** Zustand
- **i18n:** next-intl (7 languages)
- **Telegram:** @telegram-apps/sdk-react

## Pages

| Route | Description |
|-------|-------------|
| `/` | Home — pet carousel, training actions |
| `/shop` | Pet catalog with buy modal |
| `/tasks` | Task list with rewards |
| `/referrals` | Referral stats, invite link |
| `/settings` | Language selector, support |
| `/hall-of-fame` | Evolved pets showcase |
| `/spin` | Lucky spin wheel |

## Development

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Build

```bash
npm run build
npm start
```

## Deploy

Deployed via Vercel:

```bash
vercel --prod
```
