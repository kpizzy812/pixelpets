# 07. UI & Frontend Module

[← Назад к PROGRESS.md](../PROGRESS.md)

---

## Описание

Next.js приложение + Telegram Mini App SDK. Все экраны и компоненты.

---

## Прогресс

### Setup

- [x] **7.1** Project Setup
  - [x] Next.js 16 с App Router
  - [x] TypeScript
  - [x] Tailwind CSS v4
  - [x] Telegram Mini App SDK (@telegram-apps/sdk-react@3.3.9)

- [x] **7.2** Project Structure
  - [x] /app - pages
  - [x] /components - UI компоненты
  - [x] /lib - утилиты, API клиент
  - [x] /hooks - кастомные хуки
  - [x] /store - состояние (React hooks)

- [ ] **7.3** API Client
  - [ ] Axios/fetch wrapper
  - [ ] Interceptors для токена
  - [ ] Error handling

- [x] **7.4** Telegram Integration
  - [x] Инициализация SDK (TelegramProvider)
  - [x] Получение initData (useTelegram hook)
  - [x] Theme colors (CSS vars binding)
  - [ ] Haptic feedback
  - [x] Dev mock для разработки вне Telegram

### Layout & Navigation

- [x] **7.5** Root Layout
  - [x] Telegram WebApp viewport
  - [x] Safe areas (viewport meta)
  - [x] Theme provider (Providers wrapper)

- [~] **7.6** Tab Bar (BottomNav)
  - [x] 4 таба: Home, Shop, Tasks, Referrals
  - [x] Иконки и активное состояние
  - [ ] Telegram MainButton интеграция

- [x] **7.7** Header (HeaderBalance)
  - [x] Баланс
  - [x] Кнопка кошелька
  - [x] Настройки

### Pages

- [~] **7.8** Home Page
  - [x] Баланс (HeaderBalance)
  - [x] 3 слота с петами (PetCarousel)
  - [x] Пустые слоты → CTA
  - [ ] Интеграция с реальным API

- [ ] **7.9** Shop Page
  - [ ] Каталог петов
  - [ ] Карточки с ценами
  - [ ] Модалка покупки

- [ ] **7.10** Tasks Page
  - [ ] Список задач
  - [ ] Go/Check buttons
  - [ ] Completed section

- [ ] **7.11** Referrals Page
  - [ ] Реф-ссылка
  - [ ] Copy/Share
  - [ ] Статистика
  - [ ] Уровни

- [ ] **7.12** Wallet Page/Modal
  - [ ] Баланс
  - [ ] Deposit flow
  - [ ] Withdraw flow
  - [ ] История

- [ ] **7.13** Settings Page
  - [ ] Язык
  - [ ] Тема (если поддержим)
  - [ ] About

### Components

- [x] **7.14** PetCard Component
  - [x] Аватар пета (emoji + gradient)
  - [x] Level pill
  - [x] Rarity indicator
  - [x] Action buttons (Train/Claim)

- [x] **7.15** PetSlot Component (PetCarousel)
  - [x] Карточка пета или пустой слот
  - [x] CTA для пустого (To Shop)
  - [x] Горизонтальный carousel со snap

- [x] **7.16** Timer Component (useCountdown)
  - [x] Countdown 24h
  - [x] Форматирование HH:MM:SS
  - [x] Progress calculation

- [x] **7.17** Balance Display (HeaderBalance)
  - [x] Формат $XXX.XX
  - [x] Available label

- [ ] **7.18** Modal Component
  - [ ] Переиспользуемая модалка
  - [ ] Подтверждения, формы

- [ ] **7.19** Toast/Notification
  - [ ] Success/Error/Info
  - [ ] Auto-dismiss

- [x] **7.20** Button Component
  - [x] Primary (lime), Cyan, Amber variants
  - [x] Ghost variant
  - [x] Disabled state
  - [ ] Loading state

### State Management

- [ ] **7.21** Auth Store
  - [ ] User data
  - [ ] Token
  - [ ] Login/Logout

- [ ] **7.22** Pets Store
  - [ ] My pets
  - [ ] Catalog
  - [ ] Actions (buy, train, claim, sell)

- [ ] **7.23** Wallet Store
  - [ ] Balance
  - [ ] Transactions

---

## Tech Stack

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "typescript": "^5.0.0",
    "@telegram-apps/sdk-react": "^1.0.0",
    "tailwindcss": "^3.0.0",
    "zustand": "^4.0.0",
    "axios": "^1.0.0",
    "date-fns": "^3.0.0",
    "framer-motion": "^11.0.0"
  }
}
```

---

## File Structure

```
/app
  /layout.tsx
  /page.tsx (Home)
  /shop/page.tsx
  /tasks/page.tsx
  /referrals/page.tsx
  /wallet/page.tsx
  /settings/page.tsx

/components
  /ui
    /Button.tsx
    /Modal.tsx
    /Toast.tsx
    /ProgressBar.tsx
  /pet
    /PetCard.tsx
    /PetSlot.tsx
    /PetAvatar.tsx
    /LevelProgress.tsx
  /layout
    /TabBar.tsx
    /Header.tsx
    /BalanceDisplay.tsx
  /wallet
    /DepositForm.tsx
    /WithdrawForm.tsx
    /TransactionList.tsx
  /tasks
    /TaskItem.tsx
    /TaskList.tsx
  /referrals
    /RefLink.tsx
    /RefLevels.tsx
    /RefStats.tsx

/lib
  /api.ts
  /telegram.ts
  /utils.ts
  /constants.ts

/hooks
  /useAuth.ts
  /usePets.ts
  /useWallet.ts
  /useTelegram.ts
  /useCountdown.ts

/stores
  /authStore.ts
  /petsStore.ts
  /walletStore.ts

/i18n
  /en.json
  /ru.json
  ...
```

---

## Design Tokens

```css
:root {
  /* Colors - Telegram Theme */
  --tg-theme-bg-color: #ffffff;
  --tg-theme-text-color: #000000;
  --tg-theme-hint-color: #999999;
  --tg-theme-link-color: #2481cc;
  --tg-theme-button-color: #2481cc;
  --tg-theme-button-text-color: #ffffff;
  --tg-theme-secondary-bg-color: #f1f1f1;

  /* Custom Colors */
  --color-xpet: #FFD700;
  --color-success: #22C55E;
  --color-warning: #F59E0B;
  --color-danger: #EF4444;

  /* Pet Rarity Colors */
  --rarity-common: #9CA3AF;
  --rarity-rare: #3B82F6;
  --rarity-epic: #8B5CF6;
  --rarity-legendary: #F59E0B;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
}
```

---

## Screen Mockups (ASCII)

### Home
```
┌─────────────────────────────────────┐
│  💰 $150.50           [💳] [⚙️]    │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐    │
│  │  🫧 Bubble Slime            │    │
│  │  ████████░░ Teen            │    │
│  │  Invested: 15 XPET          │    │
│  │  Daily: 1.0%                │    │
│  │  ⏱ 12:34:56                 │    │
│  │           [⬆️] [🗑️]         │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │  🦊 Pixel Fox               │    │
│  │  ████░░░░░░ Baby            │    │
│  │  [Claim Loot]               │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │        Empty Slot           │    │
│  │       [Buy Pet →]           │    │
│  └─────────────────────────────┘    │
│                                     │
├─────────────────────────────────────┤
│  [🏠]    [🏪]    [📋]    [👥]     │
└─────────────────────────────────────┘
```

### Shop
```
┌─────────────────────────────────────┐
│  🏪 Shop                            │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐    │
│  │  🫧 Bubble Slime            │    │
│  │  ░░░░░░░░░░ Common          │    │
│  │  5 XPET | 1.0% | 150% cap   │    │
│  │              [Buy]          │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │  🦊 Pixel Fox               │    │
│  │  ██░░░░░░░░ Rare            │    │
│  │  50 XPET | 1.2% | 160% cap  │    │
│  │              [Buy]          │    │
│  └─────────────────────────────┘    │
│                                     │
│  ...                                │
│                                     │
└─────────────────────────────────────┘
```

---

## Заметки

```
(пусто)
```

---

## Блокеры

```
(нет)
```
