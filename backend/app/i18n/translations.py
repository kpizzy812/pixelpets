"""
Translation service for backend messages.
"""

from contextvars import ContextVar
from typing import Literal

SUPPORTED_LOCALES = ('en', 'ru')
Locale = Literal['en', 'ru']

# Context variable to store current locale per request
_locale_context: ContextVar[Locale] = ContextVar('locale', default='en')


def get_locale() -> Locale:
    """Get current locale from context."""
    return _locale_context.get()


def set_locale(locale: str) -> None:
    """Set locale for current context."""
    if locale in SUPPORTED_LOCALES:
        _locale_context.set(locale)  # type: ignore
    else:
        _locale_context.set('en')


# Translation dictionaries
TRANSLATIONS: dict[str, dict[Locale, str]] = {
    # === Errors ===
    "error.pet_not_found": {
        "en": "Pet not found",
        "ru": "Питомец не найден"
    },
    "error.pet_type_not_found": {
        "en": "Pet type not found",
        "ru": "Тип питомца не найден"
    },
    "error.pet_type_not_available": {
        "en": "Pet type is not available",
        "ru": "Этот тип питомца недоступен"
    },
    "error.insufficient_balance": {
        "en": "Insufficient balance",
        "ru": "Недостаточно средств"
    },
    "error.no_free_slots": {
        "en": "No free slots available",
        "ru": "Нет свободных слотов"
    },
    "error.pet_not_idle": {
        "en": "Pet is not idle",
        "ru": "Питомец не готов"
    },
    "error.pet_not_training": {
        "en": "Pet is not training",
        "ru": "Питомец не тренируется"
    },
    "error.training_not_complete": {
        "en": "Training is not complete yet",
        "ru": "Тренировка ещё не завершена"
    },
    "error.pet_already_max_level": {
        "en": "Pet is already at maximum level",
        "ru": "Питомец уже максимального уровня"
    },
    "error.pet_cannot_sell": {
        "en": "Cannot sell this pet",
        "ru": "Невозможно продать этого питомца"
    },
    "error.task_not_found": {
        "en": "Task not found",
        "ru": "Задание не найдено"
    },
    "error.task_already_completed": {
        "en": "Task already completed",
        "ru": "Задание уже выполнено"
    },
    "error.withdrawal_not_found": {
        "en": "Withdrawal request not found",
        "ru": "Запрос на вывод не найден"
    },
    "error.deposit_not_found": {
        "en": "Deposit request not found",
        "ru": "Запрос на пополнение не найден"
    },
    "error.invalid_amount": {
        "en": "Invalid amount",
        "ru": "Неверная сумма"
    },
    "error.min_deposit": {
        "en": "Minimum deposit is {min} XPET",
        "ru": "Минимальное пополнение — {min} XPET"
    },
    "error.min_withdrawal": {
        "en": "Minimum withdrawal is {min} XPET",
        "ru": "Минимальный вывод — {min} XPET"
    },
    "error.balance_negative": {
        "en": "Resulting balance cannot be negative",
        "ru": "Итоговый баланс не может быть отрицательным"
    },

    # === Success messages ===
    "success.task_completed": {
        "en": "Task completed!",
        "ru": "Задание выполнено!"
    },
    "success.pet_purchased": {
        "en": "Pet purchased successfully!",
        "ru": "Питомец успешно куплен!"
    },
    "success.training_started": {
        "en": "Training started!",
        "ru": "Тренировка началась!"
    },
    "success.reward_claimed": {
        "en": "Reward claimed!",
        "ru": "Награда получена!"
    },
    "success.pet_upgraded": {
        "en": "Pet upgraded!",
        "ru": "Питомец улучшен!"
    },
    "success.pet_sold": {
        "en": "Pet sold!",
        "ru": "Питомец продан!"
    },
    "success.deposit_created": {
        "en": "Deposit request created",
        "ru": "Запрос на пополнение создан"
    },
    "success.withdrawal_created": {
        "en": "Withdrawal request created",
        "ru": "Запрос на вывод создан"
    },

    # === Bot messages ===
    "bot.welcome": {
        "en": "Welcome to Pixel Pets! 🎮\n\nBuy virtual pets, train them daily, and earn XPET rewards!\n\n🐾 Each pet has a unique daily rate\n💰 Train 24h to collect earnings\n🚀 Upgrade pets for higher rewards\n\nTap the button below to start!",
        "ru": "Добро пожаловать в Pixel Pets! 🎮\n\nПокупайте виртуальных питомцев, тренируйте их каждый день и зарабатывайте XPET!\n\n🐾 Каждый питомец имеет уникальную ставку\n💰 Тренируйте 24ч, чтобы собрать доход\n🚀 Улучшайте питомцев для большего дохода\n\nНажмите кнопку ниже, чтобы начать!"
    },
    "bot.welcome_back": {
        "en": "Welcome back! 👋\n\nYour balance: {balance} XPET\n\nTap the button to continue playing!",
        "ru": "С возвращением! 👋\n\nВаш баланс: {balance} XPET\n\nНажмите кнопку, чтобы продолжить!"
    },
    "bot.play_button": {
        "en": "🎮 Play Pixel Pets",
        "ru": "🎮 Играть в Pixel Pets"
    },
    "bot.help": {
        "en": "🆘 Need help?\n\nJoin our support chat: @pixelpets_support\nFollow updates: @pixelpets_channel",
        "ru": "🆘 Нужна помощь?\n\nПрисоединяйтесь к чату поддержки: @pixelpets_support\nСледите за обновлениями: @pixelpets_channel"
    },
    "bot.unknown_command": {
        "en": "Unknown command. Use /start to open the game.",
        "ru": "Неизвестная команда. Используйте /start, чтобы открыть игру."
    },

    # === Notifications ===
    "notify.training_complete": {
        "en": "🎉 {pet_name} finished training!\n\n💰 Reward ready: +{reward} XPET\n\nOpen the app to claim your earnings!",
        "ru": "🎉 {pet_name} завершил тренировку!\n\n💰 Награда готова: +{reward} XPET\n\nОткройте приложение, чтобы забрать доход!"
    },
    "notify.pet_evolved": {
        "en": "⭐ {pet_name} has evolved!\n\nYour pet reached max ROI and moved to the Hall of Fame!\n\nTotal earned: {total} XPET",
        "ru": "⭐ {pet_name} эволюционировал!\n\nВаш питомец достиг максимального ROI и попал в Зал славы!\n\nВсего заработано: {total} XPET"
    },
    "notify.deposit_approved": {
        "en": "✅ Deposit approved!\n\n+{amount} XPET added to your balance.",
        "ru": "✅ Пополнение подтверждено!\n\n+{amount} XPET добавлено на ваш баланс."
    },
    "notify.deposit_rejected": {
        "en": "❌ Deposit rejected.\n\nPlease contact support if you believe this is an error.",
        "ru": "❌ Пополнение отклонено.\n\nСвяжитесь с поддержкой, если считаете это ошибкой."
    },
    "notify.withdrawal_approved": {
        "en": "✅ Withdrawal approved!\n\n{amount} XPET sent to your wallet.\nTx: {tx_hash}",
        "ru": "✅ Вывод подтверждён!\n\n{amount} XPET отправлено на ваш кошелёк.\nTx: {tx_hash}"
    },
    "notify.withdrawal_rejected": {
        "en": "❌ Withdrawal rejected.\n\n{amount} XPET returned to your balance.\n\nReason: {reason}",
        "ru": "❌ Вывод отклонён.\n\n{amount} XPET возвращено на ваш баланс.\n\nПричина: {reason}"
    },
    "notify.ref_reward": {
        "en": "💎 Referral reward!\n\n+{amount} XPET from level {level} referral.",
        "ru": "💎 Реферальная награда!\n\n+{amount} XPET от реферала уровня {level}."
    },

    # === Share text ===
    "share.invite_text": {
        "en": "🎮 Join me in Pixel Pets!\n\nBuy cute pets, train them daily, and earn real rewards!\n\n💰 Use my link to get a bonus:",
        "ru": "🎮 Присоединяйся ко мне в Pixel Pets!\n\nПокупай милых питомцев, тренируй их каждый день и зарабатывай реальные награды!\n\n💰 Используй мою ссылку для бонуса:"
    },
}


def get_text(key: str, locale: Locale | None = None, **kwargs) -> str:
    """
    Get translated text by key.

    Args:
        key: Translation key (e.g., "error.pet_not_found")
        locale: Override locale (uses context locale if None)
        **kwargs: Format arguments for the string

    Returns:
        Translated string, or key if not found
    """
    if locale is None:
        locale = get_locale()

    translation = TRANSLATIONS.get(key)
    if translation is None:
        return key

    text = translation.get(locale, translation.get('en', key))

    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass

    return text


# Shorthand alias
t = get_text
