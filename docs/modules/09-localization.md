# 09. Localization Module

[← Назад к PROGRESS.md](../PROGRESS.md)

---

## Описание

Мультиязычность: EN, RU + EU языки (DE, ES, FR, PT, IT).

---

## Прогресс

### Setup

- [ ] **9.1** i18n Library Setup
  - [ ] Выбор библиотеки (next-intl / react-i18next)
  - [ ] Конфигурация
  - [ ] Middleware для определения языка

- [ ] **9.2** Language Detection
  - [ ] Из Telegram initData.user.language_code
  - [ ] Fallback: localStorage
  - [ ] Default: EN

- [ ] **9.3** Language Switcher
  - [ ] UI компонент
  - [ ] Сохранение в localStorage
  - [ ] Перезагрузка контекста

### Translations

- [ ] **9.4** English (EN) - Base
  - [ ] common.json
  - [ ] pet.json
  - [ ] shop.json
  - [ ] tasks.json
  - [ ] ref.json
  - [ ] wallet.json
  - [ ] errors.json

- [ ] **9.5** Russian (RU)
  - [ ] Все файлы переведены

- [ ] **9.6** German (DE)
  - [ ] Все файлы переведены

- [ ] **9.7** Spanish (ES)
  - [ ] Все файлы переведены

- [ ] **9.8** French (FR)
  - [ ] Все файлы переведены

- [ ] **9.9** Portuguese (PT)
  - [ ] Все файлы переведены

- [ ] **9.10** Italian (IT)
  - [ ] Все файлы переведены

### Integration

- [ ] **9.11** Component Integration
  - [ ] useTranslation hook во всех компонентах
  - [ ] Проверка всех строк

- [ ] **9.12** Date/Number Formatting
  - [ ] Локализация дат
  - [ ] Локализация чисел/валюты

- [ ] **9.13** RTL Support (опционально)
  - [ ] Для будущих языков (AR, HE)

### QA

- [ ] **9.14** Translation Review
  - [ ] Проверка всех языков
  - [ ] Consistency check
  - [ ] Context validation

---

## Supported Languages

| Code | Language | Status | Priority |
|------|----------|--------|----------|
| en | English | Required | 1 |
| ru | Russian | Required | 1 |
| de | German | EU | 2 |
| es | Spanish | EU | 2 |
| fr | French | EU | 2 |
| pt | Portuguese | EU | 2 |
| it | Italian | EU | 2 |

---

## File Structure

```
/i18n
  /locales
    /en
      common.json
      pet.json
      shop.json
      tasks.json
      ref.json
      wallet.json
      errors.json
    /ru
      ...
    /de
      ...
    /es
      ...
    /fr
      ...
    /pt
      ...
    /it
      ...
  config.ts
  client.ts
```

---

## Translation Files

### common.json (EN - Base)

```json
{
  "balance": "Balance",
  "upgrade": "Upgrade",
  "start": "Start",
  "claim": "Claim",
  "release": "Release",
  "ok": "OK",
  "cancel": "Cancel",
  "confirm": "Confirm",
  "back": "Back",
  "loading": "Loading...",
  "error": "Error",
  "success": "Success"
}
```

### pet.json (EN)

```json
{
  "train_24h": "Train 24h",
  "training": "Training…",
  "time_left": "Time left:",
  "mission_complete": "Mission complete",
  "claim_loot": "Claim Loot",
  "loot_collected": "Loot collected.",
  "on_mission": "Your pet is on a mission.",
  "evolved": "Evolved",
  "full_potential": "This pet has reached its full potential.",
  "total_farmed": "Total loot farmed:",
  "lifetime": "Lifetime:",
  "final_class": "Final class:",
  "slot_cleared": "Slot cleared.",
  "upgrade_success": "Pet upgraded.",
  "max_level": "Max level reached.",
  "release_confirm": "Release this pet early?\nYou will get 85% of invested XPET.\nUnclaimed loot will be lost.",
  "released": "Pet released.",
  "levels": {
    "baby": "Baby",
    "teen": "Teen",
    "adult": "Adult",
    "mythic": "Mythic"
  },
  "invested": "Invested",
  "daily": "Daily"
}
```

### shop.json (EN)

```json
{
  "title": "Shop",
  "buy_pet": "Recruit",
  "recruited": "New pet recruited.",
  "no_slots": "No free slots.",
  "not_enough_balance": "Not enough XPET.",
  "roi_cap": "ROI cap",
  "daily_rate": "daily",
  "confirm_buy": "Buy {{name}} for {{price}} XPET?"
}
```

### tasks.json (EN)

```json
{
  "title": "Tasks",
  "go": "Go",
  "check": "Check",
  "completed": "Completed",
  "reward": "+{{amount}} XPET",
  "no_tasks": "No tasks available.",
  "task_completed": "Task completed!"
}
```

### ref.json (EN)

```json
{
  "title": "Referrals",
  "invite": "Invite Friends",
  "copy_link": "Copy link",
  "share": "Share",
  "link_copied": "Link copied!",
  "ref_levels": "Referral Levels",
  "unlock_requirement": "Unlock: {{count}} active partners",
  "earned": "Earned from referrals:",
  "active_partners": "Active partners:",
  "reward_received": "Referral loot received.",
  "level": "Level {{num}}",
  "locked": "Locked"
}
```

### wallet.json (EN)

```json
{
  "title": "Wallet",
  "balance": "Balance",
  "deposit": "Deposit XPET",
  "withdraw": "Withdraw",
  "fee": "Fee: $1 + 2%",
  "minimum": "Minimum: {{amount}} XPET",
  "enter_amount": "Enter amount",
  "select_network": "Select network",
  "your_address": "Send USDT to:",
  "wallet_address": "Your wallet address",
  "pending": "Pending",
  "confirmed": "Confirmed",
  "history": "Transaction History",
  "no_transactions": "No transactions yet"
}
```

### errors.json (EN)

```json
{
  "generic": "Something went wrong.",
  "try_again": "Try again.",
  "not_enough_xpet": "Not enough XPET.",
  "no_free_slots": "No free slots.",
  "already_training": "Already training.",
  "action_unavailable": "Action unavailable.",
  "network_error": "Network error. Check your connection.",
  "session_expired": "Session expired. Please reload."
}
```

---

## Russian Translations (RU)

### common.json (RU)

```json
{
  "balance": "Баланс",
  "upgrade": "Улучшить",
  "start": "Старт",
  "claim": "Забрать",
  "release": "Отпустить",
  "ok": "ОК",
  "cancel": "Отмена",
  "confirm": "Подтвердить",
  "back": "Назад",
  "loading": "Загрузка...",
  "error": "Ошибка",
  "success": "Успешно"
}
```

### pet.json (RU)

```json
{
  "train_24h": "Тренировка 24ч",
  "training": "Тренируется…",
  "time_left": "Осталось:",
  "mission_complete": "Миссия выполнена",
  "claim_loot": "Забрать добычу",
  "loot_collected": "Добыча собрана.",
  "on_mission": "Питомец на миссии.",
  "evolved": "Эволюционировал",
  "full_potential": "Питомец достиг максимума.",
  "total_farmed": "Всего добыто:",
  "lifetime": "Время жизни:",
  "final_class": "Финальный класс:",
  "slot_cleared": "Слот освобождён.",
  "upgrade_success": "Питомец улучшен.",
  "max_level": "Максимальный уровень.",
  "release_confirm": "Отпустить питомца раньше времени?\nВы получите 85% от вложенных XPET.\nНесобранная добыча будет потеряна.",
  "released": "Питомец отпущен.",
  "levels": {
    "baby": "Малыш",
    "teen": "Подросток",
    "adult": "Взрослый",
    "mythic": "Мифический"
  },
  "invested": "Вложено",
  "daily": "В день"
}
```

---

## Implementation

### next-intl Config

```typescript
// i18n/config.ts
export const locales = ['en', 'ru', 'de', 'es', 'fr', 'pt', 'it'] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = 'en';

// Telegram language code mapping
export const telegramToLocale: Record<string, Locale> = {
  'en': 'en',
  'ru': 'ru',
  'de': 'de',
  'es': 'es',
  'fr': 'fr',
  'pt-br': 'pt',
  'pt': 'pt',
  'it': 'it',
};
```

### Usage in Components

```tsx
import { useTranslations } from 'next-intl';

function PetCard({ pet }) {
  const t = useTranslations('pet');

  return (
    <div>
      <span>{t('invested')}: {pet.invested_total} XPET</span>
      <span>{t('daily')}: {pet.daily_rate}%</span>
      <button>{t('claim_loot')}</button>
    </div>
  );
}
```

### Language Detection

```typescript
// hooks/useLanguage.ts
import { useEffect } from 'react';
import { useTelegram } from './useTelegram';
import { telegramToLocale, defaultLocale } from '@/i18n/config';

export function useLanguageDetection() {
  const { initData } = useTelegram();

  useEffect(() => {
    const tgLang = initData?.user?.language_code;
    const savedLang = localStorage.getItem('language');

    let locale = savedLang || telegramToLocale[tgLang] || defaultLocale;

    // Set locale
    document.documentElement.lang = locale;
    localStorage.setItem('language', locale);
  }, [initData]);
}
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
