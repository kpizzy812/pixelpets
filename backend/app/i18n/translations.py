"""
Translation service for backend messages.
"""

from contextvars import ContextVar
from typing import Literal

SUPPORTED_LOCALES = ('en', 'ru', 'de', 'es', 'fr', 'pt', 'it')
Locale = Literal['en', 'ru', 'de', 'es', 'fr', 'pt', 'it']

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
TRANSLATIONS: dict[str, dict[str, str]] = {
    # === Errors ===
    "error.pet_not_found": {
        "en": "Pet not found",
        "ru": "Питомец не найден",
        "de": "Haustier nicht gefunden",
        "es": "Mascota no encontrada",
        "fr": "Animal non trouvé",
        "pt": "Pet não encontrado",
        "it": "Pet non trovato"
    },
    "error.pet_type_not_found": {
        "en": "Pet type not found",
        "ru": "Тип питомца не найден",
        "de": "Tierart nicht gefunden",
        "es": "Tipo de mascota no encontrado",
        "fr": "Type d'animal non trouvé",
        "pt": "Tipo de pet não encontrado",
        "it": "Tipo di pet non trovato"
    },
    "error.pet_type_not_available": {
        "en": "Pet type is not available",
        "ru": "Этот тип питомца недоступен",
        "de": "Tierart nicht verfügbar",
        "es": "Tipo de mascota no disponible",
        "fr": "Type d'animal non disponible",
        "pt": "Tipo de pet não disponível",
        "it": "Tipo di pet non disponibile"
    },
    "error.insufficient_balance": {
        "en": "Insufficient balance",
        "ru": "Недостаточно средств",
        "de": "Unzureichendes Guthaben",
        "es": "Saldo insuficiente",
        "fr": "Solde insuffisant",
        "pt": "Saldo insuficiente",
        "it": "Saldo insufficiente"
    },
    "error.no_free_slots": {
        "en": "No free slots available",
        "ru": "Нет свободных слотов",
        "de": "Keine freien Plätze verfügbar",
        "es": "No hay espacios disponibles",
        "fr": "Pas d'emplacement disponible",
        "pt": "Sem espaços disponíveis",
        "it": "Nessuno slot disponibile"
    },
    "error.pet_not_idle": {
        "en": "Pet is not idle",
        "ru": "Питомец не готов",
        "de": "Haustier ist nicht bereit",
        "es": "Mascota no está lista",
        "fr": "Animal non disponible",
        "pt": "Pet não está pronto",
        "it": "Pet non pronto"
    },
    "error.pet_not_training": {
        "en": "Pet is not training",
        "ru": "Питомец не тренируется",
        "de": "Haustier trainiert nicht",
        "es": "Mascota no está entrenando",
        "fr": "Animal ne s'entraîne pas",
        "pt": "Pet não está treinando",
        "it": "Pet non in allenamento"
    },
    "error.training_not_complete": {
        "en": "Training is not complete yet",
        "ru": "Тренировка ещё не завершена",
        "de": "Training noch nicht abgeschlossen",
        "es": "Entrenamiento aún no completado",
        "fr": "Entraînement non terminé",
        "pt": "Treino ainda não concluído",
        "it": "Allenamento non ancora completato"
    },
    "error.pet_already_max_level": {
        "en": "Pet is already at maximum level",
        "ru": "Питомец уже максимального уровня",
        "de": "Haustier ist bereits auf Maximum",
        "es": "Mascota ya está al nivel máximo",
        "fr": "Animal déjà au niveau maximum",
        "pt": "Pet já está no nível máximo",
        "it": "Pet già al livello massimo"
    },
    "error.pet_cannot_sell": {
        "en": "Cannot sell this pet",
        "ru": "Невозможно продать этого питомца",
        "de": "Kann dieses Haustier nicht verkaufen",
        "es": "No se puede vender esta mascota",
        "fr": "Impossible de vendre cet animal",
        "pt": "Não é possível vender este pet",
        "it": "Impossibile vendere questo pet"
    },
    "error.task_not_found": {
        "en": "Task not found",
        "ru": "Задание не найдено",
        "de": "Aufgabe nicht gefunden",
        "es": "Tarea no encontrada",
        "fr": "Tâche non trouvée",
        "pt": "Tarefa não encontrada",
        "it": "Attività non trovata"
    },
    "error.task_already_completed": {
        "en": "Task already completed",
        "ru": "Задание уже выполнено",
        "de": "Aufgabe bereits erledigt",
        "es": "Tarea ya completada",
        "fr": "Tâche déjà terminée",
        "pt": "Tarefa já concluída",
        "it": "Attività già completata"
    },
    "error.withdrawal_not_found": {
        "en": "Withdrawal request not found",
        "ru": "Запрос на вывод не найден",
        "de": "Auszahlungsanfrage nicht gefunden",
        "es": "Solicitud de retiro no encontrada",
        "fr": "Demande de retrait non trouvée",
        "pt": "Solicitação de saque não encontrada",
        "it": "Richiesta di prelievo non trovata"
    },
    "error.deposit_not_found": {
        "en": "Deposit request not found",
        "ru": "Запрос на пополнение не найден",
        "de": "Einzahlungsanfrage nicht gefunden",
        "es": "Solicitud de depósito no encontrada",
        "fr": "Demande de dépôt non trouvée",
        "pt": "Solicitação de depósito não encontrada",
        "it": "Richiesta di deposito non trovata"
    },
    "error.invalid_amount": {
        "en": "Invalid amount",
        "ru": "Неверная сумма",
        "de": "Ungültiger Betrag",
        "es": "Cantidad inválida",
        "fr": "Montant invalide",
        "pt": "Valor inválido",
        "it": "Importo non valido"
    },
    "error.min_deposit": {
        "en": "Minimum deposit is {min} USDT",
        "ru": "Минимальное пополнение — {min} USDT",
        "de": "Mindesteinzahlung ist {min} USDT",
        "es": "Depósito mínimo es {min} USDT",
        "fr": "Dépôt minimum est {min} USDT",
        "pt": "Depósito mínimo é {min} USDT",
        "it": "Deposito minimo è {min} USDT"
    },
    "error.min_withdrawal": {
        "en": "Minimum withdrawal is {min} USDT",
        "ru": "Минимальный вывод — {min} USDT",
        "de": "Mindestauszahlung ist {min} USDT",
        "es": "Retiro mínimo es {min} USDT",
        "fr": "Retrait minimum est {min} USDT",
        "pt": "Saque mínimo é {min} USDT",
        "it": "Prelievo minimo è {min} USDT"
    },
    "error.balance_negative": {
        "en": "Resulting balance cannot be negative",
        "ru": "Итоговый баланс не может быть отрицательным",
        "de": "Endguthaben kann nicht negativ sein",
        "es": "El saldo resultante no puede ser negativo",
        "fr": "Le solde résultant ne peut pas être négatif",
        "pt": "O saldo resultante não pode ser negativo",
        "it": "Il saldo risultante non può essere negativo"
    },

    # === Success messages ===
    "success.task_completed": {
        "en": "Task completed!",
        "ru": "Задание выполнено!",
        "de": "Aufgabe erledigt!",
        "es": "¡Tarea completada!",
        "fr": "Tâche terminée !",
        "pt": "Tarefa concluída!",
        "it": "Attività completata!"
    },
    "success.pet_purchased": {
        "en": "Pet purchased successfully!",
        "ru": "Питомец успешно куплен!",
        "de": "Haustier erfolgreich gekauft!",
        "es": "¡Mascota comprada con éxito!",
        "fr": "Animal acheté avec succès !",
        "pt": "Pet comprado com sucesso!",
        "it": "Pet acquistato con successo!"
    },
    "success.training_started": {
        "en": "Training started!",
        "ru": "Тренировка началась!",
        "de": "Training gestartet!",
        "es": "¡Entrenamiento iniciado!",
        "fr": "Entraînement démarré !",
        "pt": "Treino iniciado!",
        "it": "Allenamento iniziato!"
    },
    "success.reward_claimed": {
        "en": "Reward claimed!",
        "ru": "Награда получена!",
        "de": "Belohnung erhalten!",
        "es": "¡Recompensa reclamada!",
        "fr": "Récompense réclamée !",
        "pt": "Recompensa resgatada!",
        "it": "Ricompensa riscossa!"
    },
    "success.pet_upgraded": {
        "en": "Pet upgraded!",
        "ru": "Питомец улучшен!",
        "de": "Haustier aufgewertet!",
        "es": "¡Mascota mejorada!",
        "fr": "Animal amélioré !",
        "pt": "Pet melhorado!",
        "it": "Pet potenziato!"
    },
    "success.pet_sold": {
        "en": "Pet sold!",
        "ru": "Питомец продан!",
        "de": "Haustier verkauft!",
        "es": "¡Mascota vendida!",
        "fr": "Animal vendu !",
        "pt": "Pet vendido!",
        "it": "Pet venduto!"
    },
    "success.deposit_created": {
        "en": "Deposit request created",
        "ru": "Запрос на пополнение создан",
        "de": "Einzahlungsanfrage erstellt",
        "es": "Solicitud de depósito creada",
        "fr": "Demande de dépôt créée",
        "pt": "Solicitação de depósito criada",
        "it": "Richiesta di deposito creata"
    },
    "success.withdrawal_created": {
        "en": "Withdrawal request created",
        "ru": "Запрос на вывод создан",
        "de": "Auszahlungsanfrage erstellt",
        "es": "Solicitud de retiro creada",
        "fr": "Demande de retrait créée",
        "pt": "Solicitação de saque criada",
        "it": "Richiesta di prelievo creata"
    },

    # === Bot messages ===
    "bot.welcome": {
        "en": "Welcome to Pixel Pets! 🎮\n\nBuy virtual pets, train them daily, and earn USDT rewards!\n\n🐾 Each pet has a unique daily rate\n💰 Train 24h to collect earnings\n🚀 Upgrade pets for higher rewards\n\nTap the button below to start!",
        "ru": "Добро пожаловать в Pixel Pets! 🎮\n\nПокупайте виртуальных питомцев, тренируйте их каждый день и зарабатывайте USDT!\n\n🐾 Каждый питомец имеет уникальную ставку\n💰 Тренируйте 24ч, чтобы собрать доход\n🚀 Улучшайте питомцев для большего дохода\n\nНажмите кнопку ниже, чтобы начать!",
        "de": "Willkommen bei Pixel Pets! 🎮\n\nKaufe virtuelle Haustiere, trainiere sie täglich und verdiene USDT!\n\n🐾 Jedes Tier hat eine einzigartige Tagesrate\n💰 24h trainieren um Einnahmen zu sammeln\n🚀 Tiere aufwerten für höhere Belohnungen\n\nTippe auf den Button um zu starten!",
        "es": "¡Bienvenido a Pixel Pets! 🎮\n\nCompra mascotas virtuales, entrénalas diariamente y gana USDT!\n\n🐾 Cada mascota tiene una tasa diaria única\n💰 Entrena 24h para recolectar ganancias\n🚀 Mejora mascotas para mayores recompensas\n\n¡Toca el botón para comenzar!",
        "fr": "Bienvenue dans Pixel Pets ! 🎮\n\nAchetez des animaux virtuels, entraînez-les quotidiennement et gagnez des USDT !\n\n🐾 Chaque animal a un taux journalier unique\n💰 Entraînez 24h pour collecter les gains\n🚀 Améliorez les animaux pour plus de récompenses\n\nAppuyez sur le bouton pour commencer !",
        "pt": "Bem-vindo ao Pixel Pets! 🎮\n\nCompre pets virtuais, treine-os diariamente e ganhe USDT!\n\n🐾 Cada pet tem uma taxa diária única\n💰 Treine 24h para coletar ganhos\n🚀 Melhore pets para maiores recompensas\n\nToque no botão para começar!",
        "it": "Benvenuto in Pixel Pets! 🎮\n\nAcquista pet virtuali, allenali ogni giorno e guadagna USDT!\n\n🐾 Ogni pet ha un tasso giornaliero unico\n💰 Allena 24h per raccogliere i guadagni\n🚀 Potenzia i pet per ricompense più alte\n\nTocca il pulsante per iniziare!"
    },
    "bot.welcome_back": {
        "en": "Welcome back! 👋\n\nYour balance: {balance} USDT\n\nTap the button to continue playing!",
        "ru": "С возвращением! 👋\n\nВаш баланс: {balance} USDT\n\nНажмите кнопку, чтобы продолжить!",
        "de": "Willkommen zurück! 👋\n\nDein Guthaben: {balance} USDT\n\nTippe auf den Button um weiterzuspielen!",
        "es": "¡Bienvenido de nuevo! 👋\n\nTu saldo: {balance} USDT\n\n¡Toca el botón para seguir jugando!",
        "fr": "Bon retour ! 👋\n\nVotre solde : {balance} USDT\n\nAppuyez sur le bouton pour continuer !",
        "pt": "Bem-vindo de volta! 👋\n\nSeu saldo: {balance} USDT\n\nToque no botão para continuar jogando!",
        "it": "Bentornato! 👋\n\nIl tuo saldo: {balance} USDT\n\nTocca il pulsante per continuare a giocare!"
    },
    "bot.play_button": {
        "en": "🎮 Play Pixel Pets",
        "ru": "🎮 Играть в Pixel Pets",
        "de": "🎮 Pixel Pets spielen",
        "es": "🎮 Jugar Pixel Pets",
        "fr": "🎮 Jouer à Pixel Pets",
        "pt": "🎮 Jogar Pixel Pets",
        "it": "🎮 Gioca a Pixel Pets"
    },
    "bot.help": {
        "en": "🆘 Need help?\n\nJoin our support chat: @pixelpets_support\nFollow updates: @pixelpets_channel",
        "ru": "🆘 Нужна помощь?\n\nПрисоединяйтесь к чату поддержки: @pixelpets_support\nСледите за обновлениями: @pixelpets_channel",
        "de": "🆘 Hilfe benötigt?\n\nTrete unserem Support-Chat bei: @pixelpets_support\nFolge Updates: @pixelpets_channel",
        "es": "🆘 ¿Necesitas ayuda?\n\nÚnete a nuestro chat de soporte: @pixelpets_support\nSigue las actualizaciones: @pixelpets_channel",
        "fr": "🆘 Besoin d'aide ?\n\nRejoignez notre chat de support : @pixelpets_support\nSuivez les mises à jour : @pixelpets_channel",
        "pt": "🆘 Precisa de ajuda?\n\nEntre no chat de suporte: @pixelpets_support\nSiga as atualizações: @pixelpets_channel",
        "it": "🆘 Hai bisogno di aiuto?\n\nUnisciti al nostro chat di supporto: @pixelpets_support\nSegui gli aggiornamenti: @pixelpets_channel"
    },
    "bot.unknown_command": {
        "en": "Unknown command. Use /start to open the game.",
        "ru": "Неизвестная команда. Используйте /start, чтобы открыть игру.",
        "de": "Unbekannter Befehl. Nutze /start um das Spiel zu öffnen.",
        "es": "Comando desconocido. Usa /start para abrir el juego.",
        "fr": "Commande inconnue. Utilisez /start pour ouvrir le jeu.",
        "pt": "Comando desconhecido. Use /start para abrir o jogo.",
        "it": "Comando sconosciuto. Usa /start per aprire il gioco."
    },

    # === Notifications ===
    "notify.training_complete": {
        "en": "🎉 {pet_name} finished training!\n\n💰 Reward ready: +{reward} USDT\n\nOpen the app to claim your earnings!",
        "ru": "🎉 {pet_name} завершил тренировку!\n\n💰 Награда готова: +{reward} USDT\n\nОткройте приложение, чтобы забрать доход!",
        "de": "🎉 {pet_name} hat das Training beendet!\n\n💰 Belohnung bereit: +{reward} USDT\n\nÖffne die App um deine Einnahmen abzuholen!",
        "es": "🎉 ¡{pet_name} terminó el entrenamiento!\n\n💰 Recompensa lista: +{reward} USDT\n\n¡Abre la app para reclamar tus ganancias!",
        "fr": "🎉 {pet_name} a terminé l'entraînement !\n\n💰 Récompense prête : +{reward} USDT\n\nOuvrez l'app pour récupérer vos gains !",
        "pt": "🎉 {pet_name} terminou o treino!\n\n💰 Recompensa pronta: +{reward} USDT\n\nAbra o app para resgatar seus ganhos!",
        "it": "🎉 {pet_name} ha finito l'allenamento!\n\n💰 Ricompensa pronta: +{reward} USDT\n\nApri l'app per riscuotere i tuoi guadagni!"
    },
    "notify.pet_evolved": {
        "en": "⭐ {pet_name} has evolved!\n\nYour pet reached max ROI and moved to the Hall of Fame!\n\nTotal earned: {total} USDT",
        "ru": "⭐ {pet_name} эволюционировал!\n\nВаш питомец достиг максимального ROI и попал в Зал славы!\n\nВсего заработано: {total} USDT",
        "de": "⭐ {pet_name} hat sich entwickelt!\n\nDein Haustier hat max ROI erreicht und ist in der Ruhmeshalle!\n\nGesamt verdient: {total} USDT",
        "es": "⭐ ¡{pet_name} ha evolucionado!\n\n¡Tu mascota alcanzó el ROI máximo y está en el Salón de la Fama!\n\nTotal ganado: {total} USDT",
        "fr": "⭐ {pet_name} a évolué !\n\nVotre animal a atteint le ROI max et est au Temple de la Renommée !\n\nTotal gagné : {total} USDT",
        "pt": "⭐ {pet_name} evoluiu!\n\nSeu pet atingiu o ROI máximo e está no Hall da Fama!\n\nTotal ganho: {total} USDT",
        "it": "⭐ {pet_name} si è evoluto!\n\nIl tuo pet ha raggiunto il ROI massimo ed è nella Hall of Fame!\n\nTotale guadagnato: {total} USDT"
    },
    "notify.deposit_approved": {
        "en": "✅ Deposit approved!\n\n+{amount} USDT added to your balance.",
        "ru": "✅ Пополнение подтверждено!\n\n+{amount} USDT добавлено на ваш баланс.",
        "de": "✅ Einzahlung genehmigt!\n\n+{amount} USDT zu deinem Guthaben hinzugefügt.",
        "es": "✅ ¡Depósito aprobado!\n\n+{amount} USDT añadidos a tu saldo.",
        "fr": "✅ Dépôt approuvé !\n\n+{amount} USDT ajoutés à votre solde.",
        "pt": "✅ Depósito aprovado!\n\n+{amount} USDT adicionados ao seu saldo.",
        "it": "✅ Deposito approvato!\n\n+{amount} USDT aggiunti al tuo saldo."
    },
    "notify.deposit_rejected": {
        "en": "❌ Deposit rejected.\n\nPlease contact support if you believe this is an error.",
        "ru": "❌ Пополнение отклонено.\n\nСвяжитесь с поддержкой, если считаете это ошибкой.",
        "de": "❌ Einzahlung abgelehnt.\n\nKontaktiere den Support wenn du glaubst dass dies ein Fehler ist.",
        "es": "❌ Depósito rechazado.\n\nContacta soporte si crees que es un error.",
        "fr": "❌ Dépôt refusé.\n\nContactez le support si vous pensez que c'est une erreur.",
        "pt": "❌ Depósito rejeitado.\n\nEntre em contato com o suporte se acredita ser um erro.",
        "it": "❌ Deposito rifiutato.\n\nContatta il supporto se pensi sia un errore."
    },
    "notify.withdrawal_approved": {
        "en": "✅ Withdrawal approved!\n\n{amount} USDT sent to your wallet.\nTx: {tx_hash}",
        "ru": "✅ Вывод подтверждён!\n\n{amount} USDT отправлено на ваш кошелёк.\nTx: {tx_hash}",
        "de": "✅ Auszahlung genehmigt!\n\n{amount} USDT an deine Wallet gesendet.\nTx: {tx_hash}",
        "es": "✅ ¡Retiro aprobado!\n\n{amount} USDT enviados a tu billetera.\nTx: {tx_hash}",
        "fr": "✅ Retrait approuvé !\n\n{amount} USDT envoyés à votre portefeuille.\nTx : {tx_hash}",
        "pt": "✅ Saque aprovado!\n\n{amount} USDT enviados para sua carteira.\nTx: {tx_hash}",
        "it": "✅ Prelievo approvato!\n\n{amount} USDT inviati al tuo portafoglio.\nTx: {tx_hash}"
    },
    "notify.withdrawal_rejected": {
        "en": "❌ Withdrawal rejected.\n\n{amount} USDT returned to your balance.\n\nReason: {reason}",
        "ru": "❌ Вывод отклонён.\n\n{amount} USDT возвращено на ваш баланс.\n\nПричина: {reason}",
        "de": "❌ Auszahlung abgelehnt.\n\n{amount} USDT zurück auf dein Guthaben.\n\nGrund: {reason}",
        "es": "❌ Retiro rechazado.\n\n{amount} USDT devueltos a tu saldo.\n\nRazón: {reason}",
        "fr": "❌ Retrait refusé.\n\n{amount} USDT retournés à votre solde.\n\nRaison : {reason}",
        "pt": "❌ Saque rejeitado.\n\n{amount} USDT devolvidos ao seu saldo.\n\nMotivo: {reason}",
        "it": "❌ Prelievo rifiutato.\n\n{amount} USDT restituiti al tuo saldo.\n\nMotivo: {reason}"
    },
    "notify.ref_reward": {
        "en": "💎 Referral reward!\n\n+{amount} USDT from level {level} referral.",
        "ru": "💎 Реферальная награда!\n\n+{amount} USDT от реферала уровня {level}.",
        "de": "💎 Empfehlungsbelohnung!\n\n+{amount} USDT von Level {level} Empfehlung.",
        "es": "💎 ¡Recompensa de referido!\n\n+{amount} USDT de referido nivel {level}.",
        "fr": "💎 Récompense de parrainage !\n\n+{amount} USDT du parrainage niveau {level}.",
        "pt": "💎 Recompensa de indicação!\n\n+{amount} USDT de indicação nível {level}.",
        "it": "💎 Ricompensa referral!\n\n+{amount} USDT da referral livello {level}."
    },

    # === Share text ===
    "share.invite_text": {
        "en": "🎮 Join me in Pixel Pets!\n\nBuy cute pets, train them daily, and earn real USDT rewards!\n\n💰 Use my link to get a bonus:",
        "ru": "🎮 Присоединяйся ко мне в Pixel Pets!\n\nПокупай милых питомцев, тренируй их каждый день и зарабатывай реальные USDT!\n\n💰 Используй мою ссылку для бонуса:",
        "de": "🎮 Spiele mit mir Pixel Pets!\n\nKaufe süße Haustiere, trainiere sie täglich und verdiene echte USDT!\n\n💰 Nutze meinen Link für einen Bonus:",
        "es": "🎮 ¡Únete a mí en Pixel Pets!\n\n¡Compra mascotas, entrénalas diario y gana USDT reales!\n\n💰 Usa mi enlace para un bono:",
        "fr": "🎮 Rejoins-moi dans Pixel Pets !\n\nAchète des animaux mignons, entraîne-les et gagne des vrais USDT !\n\n💰 Utilise mon lien pour un bonus :",
        "pt": "🎮 Junte-se a mim no Pixel Pets!\n\nCompre pets fofos, treine-os diariamente e ganhe USDT reais!\n\n💰 Use meu link para um bônus:",
        "it": "🎮 Unisciti a me in Pixel Pets!\n\nAcquista pet carini, allenali ogni giorno e guadagna veri USDT!\n\n💰 Usa il mio link per un bonus:"
    },
}


def get_text(key: str, locale: str | None = None, **kwargs) -> str:
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
