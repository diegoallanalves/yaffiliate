"""Multilingual translation service for YAffiliate."""

from __future__ import annotations

import streamlit as st


LANGUAGES = {
    "English": "en",
    "Português": "pt_BR",
    "Español": "es",
    "简体中文": "zh_CN",
}


TRANSLATIONS = {
    # =========================================================
    # ENGLISH
    # =========================================================
    "en": {
        # General
        "language": "Language",
        "navigation": "Navigation",
        "welcome": "Welcome",
        "settings": "Settings",
        "logout": "Logout",

        # Navigation
        "quick_generate": "Quick Generate",
        "dashboard": "Dashboard",
        "mission_center": "Mission Center",
        "product_intelligence": "Product Intelligence",
        "portfolio_intelligence": "Portfolio Intelligence",
        "product_research": "Product Research",
        "product_discovery": "Product Discovery",
        "content_studio": "AI Content Studio",
        "campaign_generator": "Campaign Generator",
        "campaign_history": "Campaign History",
        "keyword_research": "Keyword Research",
        "ai_assistant": "AI Assistant",
        "profit_calculator": "Profit Calculator",
        "analytics": "Analytics",
        "landing_pages": "Landing Pages",
        "email_marketing": "Email Marketing",
        "seo": "SEO",
        "google_ads": "Google Ads",
        "affiliate_products": "Affiliate Products",

        # Subscription
        "pro_active": "YAffiliate Pro active",
        "pro_required": "PRO features require an active subscription.",

        # Branding
        "platform_tagline": "AI Marketing Platform",
        "beta_tagline": (
            "YAffiliate Beta · Build your marketing kit in minutes"
        ),

        # Common actions
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "search": "Search",
        "generate": "Generate",
        "download": "Download",
        "continue": "Continue",
        "back": "Back",
        "upgrade_to_pro": "Upgrade to Pro",

        # Quick Generate
        "qg_eyebrow": "START HERE",
        "qg_title": (
            "From One Product to a Complete Marketing Campaign in Minutes."
        ),
        "qg_subtitle": (
            "Search for a product, generate the campaign, "
            "and download the complete ZIP package."
        ),
        "qg_info": (
            "Search any product and YAffiliate will create a complete "
            "marketing campaign in minutes."
        ),
        "qg_product_question": "What product do you want to promote?",
        "qg_product_placeholder": (
            "Examples: Excel Masterclass, English Course"
        ),
        "qg_generate": "🚀 Generate My Campaign",
        "qg_enter_product": "Enter a product name.",
        "qg_generating": "Generating campaign...",
        "qg_session_expired": (
            "Your login session has expired. Please sign in again."
        ),
        "qg_generated": "Marketing kit generated and saved.",
        "qg_kit_include": "Your marketing kit will include",
        "qg_seo_article": "SEO article",
        "qg_landing_page": "Landing page",
        "qg_email_sequence": "Email sequence",
        "qg_google_ads": "Google Ads",
        "qg_campaign_summary": "Campaign summary",
        "qg_zip_package": "Complete ZIP package",
        "qg_ready": "Marketing Kit Ready",
        "qg_placeholder_warning": (
            "This campaign used estimated placeholder product data "
            "because the product was not found in the catalogue."
        ),
        "qg_product": "Product",
        "qg_campaign": "Campaign",
        "qg_files_ready": "Files ready",
        "qg_marketing_content": "Marketing content",
        "qg_words": "words",
        "qg_average_quality": "Average quality",
        "qg_included": "Included",
        "qg_saved_id": "Saved Campaign ID",
        "qg_zip_unavailable": (
            "The ZIP file is not available. Generate the kit again."
        ),
        "qg_download": "📦 Download My Complete Marketing Kit",
        "qg_zip_caption": (
            "The ZIP includes the campaign assets and summary files "
            "created by YAffiliate."
        ),
    },

    # =========================================================
    # PORTUGUÊS — BRASIL
    # =========================================================
    "pt_BR": {
        # Geral
        "language": "Idioma",
        "navigation": "Navegação",
        "welcome": "Bem-vindo",
        "settings": "Configurações",
        "logout": "Sair",

        # Navegação
        "quick_generate": "Geração Rápida",
        "dashboard": "Painel",
        "mission_center": "Central de Missões",
        "product_intelligence": "Inteligência de Produtos",
        "portfolio_intelligence": "Inteligência de Portfólio",
        "product_research": "Pesquisa de Produtos",
        "product_discovery": "Descoberta de Produtos",
        "content_studio": "Estúdio de Conteúdo com IA",
        "campaign_generator": "Gerador de Campanhas",
        "campaign_history": "Histórico de Campanhas",
        "keyword_research": "Pesquisa de Palavras-chave",
        "ai_assistant": "Assistente de IA",
        "profit_calculator": "Calculadora de Lucro",
        "analytics": "Análises",
        "landing_pages": "Páginas de Destino",
        "email_marketing": "E-mail Marketing",
        "seo": "SEO",
        "google_ads": "Google Ads",
        "affiliate_products": "Produtos de Afiliados",

        # Assinatura
        "pro_active": "YAffiliate Pro ativo",
        "pro_required": (
            "Os recursos PRO exigem uma assinatura ativa."
        ),

        # Marca
        "platform_tagline": "Plataforma de Marketing com IA",
        "beta_tagline": (
            "YAffiliate Beta · Crie seu kit de marketing em minutos"
        ),

        # Ações
        "save": "Salvar",
        "cancel": "Cancelar",
        "delete": "Excluir",
        "search": "Pesquisar",
        "generate": "Gerar",
        "download": "Baixar",
        "continue": "Continuar",
        "back": "Voltar",
        "upgrade_to_pro": "Assinar o Pro",

        # Geração Rápida
        "qg_eyebrow": "COMECE AQUI",
        "qg_title": (
            "De Um Produto a Uma Campanha de Marketing Completa em Minutos."
        ),
        "qg_subtitle": (
            "Pesquise um produto, gere a campanha "
            "e baixe o pacote ZIP completo."
        ),
        "qg_info": (
            "Pesquise qualquer produto e o YAffiliate criará uma "
            "campanha de marketing completa em minutos."
        ),
        "qg_product_question": "Qual produto você deseja promover?",
        "qg_product_placeholder": (
            "Exemplos: Curso de Excel, Curso de Inglês"
        ),
        "qg_generate": "🚀 Gerar Minha Campanha",
        "qg_enter_product": "Digite o nome de um produto.",
        "qg_generating": "Gerando campanha...",
        "qg_session_expired": (
            "Sua sessão expirou. Entre novamente."
        ),
        "qg_generated": "Kit de marketing gerado e salvo.",
        "qg_kit_include": "Seu kit de marketing incluirá",
        "qg_seo_article": "Artigo de SEO",
        "qg_landing_page": "Página de destino",
        "qg_email_sequence": "Sequência de e-mails",
        "qg_google_ads": "Google Ads",
        "qg_campaign_summary": "Resumo da campanha",
        "qg_zip_package": "Pacote ZIP completo",
        "qg_ready": "Kit de Marketing Pronto",
        "qg_placeholder_warning": (
            "Esta campanha utilizou dados estimados porque o produto "
            "não foi encontrado no catálogo."
        ),
        "qg_product": "Produto",
        "qg_campaign": "Campanha",
        "qg_files_ready": "Arquivos prontos",
        "qg_marketing_content": "Conteúdo de marketing",
        "qg_words": "palavras",
        "qg_average_quality": "Qualidade média",
        "qg_included": "Incluído",
        "qg_saved_id": "ID da campanha salva",
        "qg_zip_unavailable": (
            "O arquivo ZIP não está disponível. "
            "Gere o kit novamente."
        ),
        "qg_download": "📦 Baixar Meu Kit de Marketing Completo",
        "qg_zip_caption": (
            "O ZIP contém os materiais da campanha e os arquivos "
            "de resumo criados pelo YAffiliate."
        ),
    },

    # =========================================================
    # ESPAÑOL
    # =========================================================
    "es": {
        # General
        "language": "Idioma",
        "navigation": "Navegación",
        "welcome": "Bienvenido",
        "settings": "Configuración",
        "logout": "Cerrar sesión",

        # Navegación
        "quick_generate": "Generación Rápida",
        "dashboard": "Panel",
        "mission_center": "Centro de Misiones",
        "product_intelligence": "Inteligencia de Productos",
        "portfolio_intelligence": "Inteligencia de Portafolio",
        "product_research": "Investigación de Productos",
        "product_discovery": "Descubrimiento de Productos",
        "content_studio": "Estudio de Contenido con IA",
        "campaign_generator": "Generador de Campañas",
        "campaign_history": "Historial de Campañas",
        "keyword_research": "Investigación de Palabras Clave",
        "ai_assistant": "Asistente de IA",
        "profit_calculator": "Calculadora de Beneficios",
        "analytics": "Analítica",
        "landing_pages": "Páginas de Destino",
        "email_marketing": "Email Marketing",
        "seo": "SEO",
        "google_ads": "Google Ads",
        "affiliate_products": "Productos de Afiliados",

        # Suscripción
        "pro_active": "YAffiliate Pro activo",
        "pro_required": (
            "Las funciones PRO requieren una suscripción activa."
        ),

        # Marca
        "platform_tagline": "Plataforma de Marketing con IA",
        "beta_tagline": (
            "YAffiliate Beta · Crea tu kit de marketing en minutos"
        ),

        # Acciones
        "save": "Guardar",
        "cancel": "Cancelar",
        "delete": "Eliminar",
        "search": "Buscar",
        "generate": "Generar",
        "download": "Descargar",
        "continue": "Continuar",
        "back": "Volver",
        "upgrade_to_pro": "Actualizar a Pro",

        # Generación Rápida
        "qg_eyebrow": "EMPIEZA AQUÍ",
        "qg_title": (
            "De Un Producto a Una Campaña de Marketing Completa en Minutos."
        ),
        "qg_subtitle": (
            "Busca un producto, genera la campaña "
            "y descarga el paquete ZIP completo."
        ),
        "qg_info": (
            "Busca cualquier producto y YAffiliate creará una "
            "campaña de marketing completa en minutos."
        ),
        "qg_product_question": "¿Qué producto quieres promocionar?",
        "qg_product_placeholder": (
            "Ejemplos: Curso de Excel, Curso de Inglés"
        ),
        "qg_generate": "🚀 Generar Mi Campaña",
        "qg_enter_product": "Introduce el nombre de un producto.",
        "qg_generating": "Generando campaña...",
        "qg_session_expired": (
            "Tu sesión ha caducado. Inicia sesión de nuevo."
        ),
        "qg_generated": "Kit de marketing generado y guardado.",
        "qg_kit_include": "Tu kit de marketing incluirá",
        "qg_seo_article": "Artículo SEO",
        "qg_landing_page": "Página de destino",
        "qg_email_sequence": "Secuencia de emails",
        "qg_google_ads": "Google Ads",
        "qg_campaign_summary": "Resumen de la campaña",
        "qg_zip_package": "Paquete ZIP completo",
        "qg_ready": "Kit de Marketing Listo",
        "qg_placeholder_warning": (
            "Esta campaña utilizó datos estimados porque el producto "
            "no se encontró en el catálogo."
        ),
        "qg_product": "Producto",
        "qg_campaign": "Campaña",
        "qg_files_ready": "Archivos listos",
        "qg_marketing_content": "Contenido de marketing",
        "qg_words": "palabras",
        "qg_average_quality": "Calidad media",
        "qg_included": "Incluido",
        "qg_saved_id": "ID de campaña guardada",
        "qg_zip_unavailable": (
            "El archivo ZIP no está disponible. "
            "Genera el kit nuevamente."
        ),
        "qg_download": "📦 Descargar Mi Kit de Marketing Completo",
        "qg_zip_caption": (
            "El ZIP incluye los materiales de la campaña y los "
            "archivos de resumen creados por YAffiliate."
        ),
    },

    # =========================================================
    # 简体中文
    # =========================================================
    "zh_CN": {
        # 通用
        "language": "语言",
        "navigation": "导航",
        "welcome": "欢迎",
        "settings": "设置",
        "logout": "退出登录",

        # 导航
        "quick_generate": "快速生成",
        "dashboard": "控制面板",
        "mission_center": "任务中心",
        "product_intelligence": "产品智能分析",
        "portfolio_intelligence": "产品组合分析",
        "product_research": "产品研究",
        "product_discovery": "产品发现",
        "content_studio": "AI 内容工作室",
        "campaign_generator": "营销活动生成器",
        "campaign_history": "营销活动历史",
        "keyword_research": "关键词研究",
        "ai_assistant": "AI 助手",
        "profit_calculator": "利润计算器",
        "analytics": "数据分析",
        "landing_pages": "落地页",
        "email_marketing": "电子邮件营销",
        "seo": "SEO",
        "google_ads": "Google 广告",
        "affiliate_products": "联盟产品",

        # 订阅
        "pro_active": "YAffiliate Pro 已激活",
        "pro_required": "PRO 功能需要有效订阅。",

        # 品牌
        "platform_tagline": "AI 营销平台",
        "beta_tagline": (
            "YAffiliate Beta · 几分钟内创建您的营销工具包"
        ),

        # 操作
        "save": "保存",
        "cancel": "取消",
        "delete": "删除",
        "search": "搜索",
        "generate": "生成",
        "download": "下载",
        "continue": "继续",
        "back": "返回",
        "upgrade_to_pro": "升级到 Pro",

        # 快速生成
        "qg_eyebrow": "从这里开始",
        "qg_title": "几分钟内，从一个产品生成完整的营销活动。",
        "qg_subtitle": (
            "搜索产品、生成营销活动并下载完整的 ZIP 文件包。"
        ),
        "qg_info": (
            "搜索任何产品，YAffiliate 将在几分钟内为您创建"
            "完整的营销活动。"
        ),
        "qg_product_question": "您想推广什么产品？",
        "qg_product_placeholder": (
            "例如：Excel 课程、英语课程"
        ),
        "qg_generate": "🚀 生成我的营销活动",
        "qg_enter_product": "请输入产品名称。",
        "qg_generating": "正在生成营销活动...",
        "qg_session_expired": (
            "您的登录会话已过期，请重新登录。"
        ),
        "qg_generated": "营销工具包已生成并保存。",
        "qg_kit_include": "您的营销工具包将包括",
        "qg_seo_article": "SEO 文章",
        "qg_landing_page": "落地页",
        "qg_email_sequence": "电子邮件序列",
        "qg_google_ads": "Google 广告",
        "qg_campaign_summary": "营销活动摘要",
        "qg_zip_package": "完整 ZIP 文件包",
        "qg_ready": "营销工具包已准备就绪",
        "qg_placeholder_warning": (
            "由于目录中未找到该产品，此营销活动使用了"
            "估算的产品数据。"
        ),
        "qg_product": "产品",
        "qg_campaign": "营销活动",
        "qg_files_ready": "已准备文件",
        "qg_marketing_content": "营销内容",
        "qg_words": "字",
        "qg_average_quality": "平均质量",
        "qg_included": "包含内容",
        "qg_saved_id": "已保存的营销活动 ID",
        "qg_zip_unavailable": (
            "ZIP 文件不可用，请重新生成营销工具包。"
        ),
        "qg_download": "📦 下载完整营销工具包",
        "qg_zip_caption": (
            "ZIP 文件包含由 YAffiliate 创建的营销活动素材"
            "和摘要文件。"
        ),
    },
}


def get_language() -> str:
    """Return the currently selected interface language."""

    language = st.session_state.get("language", "en")

    if language not in TRANSLATIONS:
        return "en"

    return language


def set_language(language: str) -> None:
    """Set the interface language for the current Streamlit session."""

    if language not in TRANSLATIONS:
        language = "en"

    st.session_state["language"] = language


def get_language_name() -> str:
    """Return the customer-facing name of the selected language."""

    current_language = get_language()

    for name, code in LANGUAGES.items():
        if code == current_language:
            return name

    return "English"


def t(key: str) -> str:
    """
    Translate a UI key.

    Falls back to English when a translation is missing.
    If the key does not exist in English, return the key itself.
    """

    language = get_language()

    return TRANSLATIONS.get(
        language,
        TRANSLATIONS["en"],
    ).get(
        key,
        TRANSLATIONS["en"].get(key, key),
    )