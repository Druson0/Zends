TRANSLATIONS = {
    "English": {
        "nav_title": "System Navigation",
        "nav_analyst": "Telecom Brand Analyst Dashboard",
        "nav_customer": "Customer User Interface",
        "nav_rag": "RAG Document Management",
        "theme_toggle": "🌙 Dark / ☀️ Light",
        "lang_select": "🌐 Language",
        "btn_analyze": "🔍 Analyze My Feedback",
        "btn_resolved": "✅ Mark Resolved",
        "btn_callback": "📞 Request Callback",
        "btn_email": "📧 Email Transcript",
        "feedback_placeholder": "Describe your experience with our telecom services...",
        "ai_assistant": "🤖 TelecomAI Assistant",
        "ai_response_title": "✦ AI-Generated Response",
        "system_instruction": "You MUST generate your final response entirely in English."
    },
    "Español": {
        "nav_title": "Navegación del Sistema",
        "nav_analyst": "Panel de Analista de Marca",
        "nav_customer": "Interfaz de Usuario",
        "nav_rag": "Gestión de Documentos RAG",
        "theme_toggle": "🌙 Oscuro / ☀️ Claro",
        "lang_select": "🌐 Idioma",
        "btn_analyze": "🔍 Analizar Mi Comentario",
        "btn_resolved": "✅ Marcar Resuelto",
        "btn_callback": "📞 Solicitar Llamada",
        "btn_email": "📧 Enviar Transcripción",
        "feedback_placeholder": "Describa su experiencia con nuestros servicios de telecomunicaciones...",
        "ai_assistant": "🤖 Asistente TelecomAI",
        "ai_response_title": "✦ Respuesta Generada por IA",
        "system_instruction": "Debes generar tu respuesta final completamente en Español (Spanish)."
    },
    "Français": {
        "nav_title": "Navigation du Système",
        "nav_analyst": "Tableau de Bord Analyste",
        "nav_customer": "Interface Utilisateur",
        "nav_rag": "Gestion des Documents RAG",
        "theme_toggle": "🌙 Sombre / ☀️ Clair",
        "lang_select": "🌐 Langue",
        "btn_analyze": "🔍 Analyser Mon Commentaire",
        "btn_resolved": "✅ Marquer Résolu",
        "btn_callback": "📞 Demander un Rappel",
        "btn_email": "📧 Envoyer la Transcription",
        "feedback_placeholder": "Décrivez votre expérience avec nos services télécom...",
        "ai_assistant": "🤖 Assistant TelecomAI",
        "ai_response_title": "✦ Réponse Générée par IA",
        "system_instruction": "Vous DEVEZ générer votre réponse finale entièrement en Français (French)."
    }
}

def t(key, lang="English"):
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"]).get(key, key)
