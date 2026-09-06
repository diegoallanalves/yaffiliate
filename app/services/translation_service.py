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
        "signed_in": "SIGNED IN",
        "sign_out": "🚪 Sign Out",

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
        "signed_in": "CONECTADO",
        "sign_out": "🚪 Sair",

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
        "signed_in": "SESIÓN INICIADA",
        "sign_out": "🚪 Cerrar sesión",

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
        "signed_in": "已登录",
        "sign_out": "🚪 退出登录",

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

# Page-header translations for legacy pages that still pass English copy
# directly to the shared page_header component. This lets every page header
# follow the selected interface language while the remaining page controls
# are migrated incrementally to key-based translations.
LITERAL_TRANSLATIONS = {
    "pt_BR": {
        "Product catalogue": "Catálogo de produtos",
        "Manage your affiliate shortlist.": "Gerencie sua lista de produtos afiliados.",
        "Portfolio view of researched, tested and active products.": "Visão do portfólio de produtos pesquisados, testados e ativos.",
        "AI workspace": "Espaço de trabalho com IA",
        "Turn structured research into better decisions.": "Transforme pesquisas estruturadas em decisões melhores.",
        "Analysis and drafting with human review before publication or spending.": "Análise e criação com revisão humana antes de publicar ou investir.",
        "Performance intelligence": "Inteligência de desempenho",
        "Understand your modelled campaign economics.": "Entenda a economia projetada das suas campanhas.",
        "Later this will combine ad-platform, network and website data.": "No futuro, esta área combinará dados de anúncios, redes e do site.",
        "Campaign Generator": "Gerador de Campanhas",
        "Create coordinated marketing assets from one product.": "Crie materiais de marketing coordenados a partir de um produto.",
        "My Campaigns": "Minhas Campanhas",
        "Access every marketing campaign you've created.": "Acesse todas as campanhas de marketing que você criou.",
        "Review, open, download and manage campaigns generated with YAffiliate.": "Revise, abra, baixe e gerencie campanhas criadas com o YAffiliate.",
        "AI Content Studio": "Estúdio de Conteúdo com IA",
        "Generate structured content from product intelligence.": "Gere conteúdo estruturado a partir da inteligência de produtos.",
        "Choose a product, select a content template and create an editable marketing asset.": "Escolha um produto, selecione um modelo e crie um material de marketing editável.",
        "Command Centre": "Central de Comando",
        "Turn research into campaigns that can make money.": "Transforme pesquisa em campanhas com potencial de gerar receita.",
        "Lifecycle messaging": "Mensagens de relacionamento",
        "Draft useful email sequences without spam.": "Crie sequências úteis de e-mails sem spam.",
        "Build permission-based educational and promotional campaigns.": "Crie campanhas educativas e promocionais baseadas em permissão.",
        "Paid acquisition": "Aquisição paga",
        "Prepare Google Ads assets before launch.": "Prepare materiais para Google Ads antes do lançamento.",
        "Draft ad groups and negatives, then review platform and network rules.": "Crie grupos de anúncios e negativas e revise as regras da plataforma e da rede.",
        "Search intelligence": "Inteligência de busca",
        "Build a commercial keyword database.": "Crie uma base comercial de palavras-chave.",
        "Capture intent, volume, CPC and competition before connecting approved keyword APIs.": "Registre intenção, volume, CPC e concorrência antes de conectar APIs de palavras-chave aprovadas.",
        "Conversion studio": "Estúdio de conversão",
        "Create compliant affiliate landing pages.": "Crie páginas de destino de afiliados em conformidade.",
        "Generate clean HTML while keeping claims truthful and relationships transparent.": "Gere HTML limpo mantendo alegações verdadeiras e relações transparentes.",
        "Mission Center": "Central de Missões",
        "Your affiliate execution dashboard.": "Seu painel de execução de afiliados.",
        "Turn product intelligence into daily actions.": "Transforme inteligência de produtos em ações diárias.",
        "Portfolio Intelligence": "Inteligência de Portfólio",
        "See which products deserve your attention today.": "Veja quais produtos merecem sua atenção hoje.",
        "Rank and filter every saved product by opportunity score, commercial potential and recommended next action.": "Classifique e filtre produtos por oportunidade, potencial comercial e próxima ação recomendada.",
        "Product Discovery": "Descoberta de Produtos",
        "Find new affiliate opportunities.": "Encontre novas oportunidades de afiliados.",
        "Search available affiliate networks, compare products and identify the strongest opportunities.": "Pesquise redes de afiliados, compare produtos e identifique as melhores oportunidades.",
        "Product Intelligence": "Inteligência de Produtos",
        "Understand which affiliate products deserve your attention.": "Entenda quais produtos afiliados merecem sua atenção.",
        "Select a saved product and review its latest metrics, recommendation, history and commercial potential.": "Selecione um produto salvo e analise métricas, recomendação, histórico e potencial comercial.",
        "Product Research": "Pesquisa de Produtos",
        "Build and maintain your affiliate product database.": "Crie e mantenha sua base de produtos afiliados.",
        "Unit economics": "Economia unitária",
        "Know your break-even point before spending.": "Conheça seu ponto de equilíbrio antes de investir.",
        "Model profitability using CPC, conversion rate and commission assumptions.": "Modele a lucratividade usando CPC, taxa de conversão e comissão.",
        "Organic growth": "Crescimento orgânico",
        "Plan helpful search content.": "Planeje conteúdo útil para buscas.",
        "Create article briefs around real intent instead of low-value pages.": "Crie pautas com base em intenção real, evitando páginas de baixo valor.",
        "Account & Billing": "Conta e Cobrança",
        "Manage your YAffiliate account and subscription.": "Gerencie sua conta e assinatura YAffiliate.",
    },
    "es": {
        "Product catalogue": "Catálogo de productos",
        "Manage your affiliate shortlist.": "Gestiona tu selección de productos afiliados.",
        "Portfolio view of researched, tested and active products.": "Vista del portafolio de productos investigados, probados y activos.",
        "AI workspace": "Espacio de trabajo con IA",
        "Turn structured research into better decisions.": "Convierte la investigación estructurada en mejores decisiones.",
        "Analysis and drafting with human review before publication or spending.": "Análisis y creación con revisión humana antes de publicar o invertir.",
        "Performance intelligence": "Inteligencia de rendimiento",
        "Understand your modelled campaign economics.": "Comprende la economía proyectada de tus campañas.",
        "Later this will combine ad-platform, network and website data.": "Más adelante combinará datos de anuncios, redes y sitios web.",
        "Campaign Generator": "Generador de Campañas",
        "Create coordinated marketing assets from one product.": "Crea materiales de marketing coordinados a partir de un producto.",
        "My Campaigns": "Mis Campañas",
        "Access every marketing campaign you've created.": "Accede a todas las campañas de marketing que has creado.",
        "Review, open, download and manage campaigns generated with YAffiliate.": "Revisa, abre, descarga y gestiona campañas creadas con YAffiliate.",
        "AI Content Studio": "Estudio de Contenido con IA",
        "Generate structured content from product intelligence.": "Genera contenido estructurado a partir de inteligencia de productos.",
        "Choose a product, select a content template and create an editable marketing asset.": "Elige un producto, selecciona una plantilla y crea un material de marketing editable.",
        "Command Centre": "Centro de Control",
        "Turn research into campaigns that can make money.": "Convierte la investigación en campañas con potencial de generar ingresos.",
        "Lifecycle messaging": "Mensajería de ciclo de vida",
        "Draft useful email sequences without spam.": "Crea secuencias útiles de correo sin spam.",
        "Build permission-based educational and promotional campaigns.": "Crea campañas educativas y promocionales basadas en permiso.",
        "Paid acquisition": "Adquisición de pago",
        "Prepare Google Ads assets before launch.": "Prepara materiales de Google Ads antes del lanzamiento.",
        "Draft ad groups and negatives, then review platform and network rules.": "Crea grupos de anuncios y negativas y revisa las reglas de la plataforma y la red.",
        "Search intelligence": "Inteligencia de búsqueda",
        "Build a commercial keyword database.": "Crea una base comercial de palabras clave.",
        "Capture intent, volume, CPC and competition before connecting approved keyword APIs.": "Registra intención, volumen, CPC y competencia antes de conectar APIs aprobadas.",
        "Conversion studio": "Estudio de conversión",
        "Create compliant affiliate landing pages.": "Crea páginas de destino de afiliados conformes.",
        "Generate clean HTML while keeping claims truthful and relationships transparent.": "Genera HTML limpio manteniendo afirmaciones veraces y relaciones transparentes.",
        "Mission Center": "Centro de Misiones",
        "Your affiliate execution dashboard.": "Tu panel de ejecución de afiliados.",
        "Turn product intelligence into daily actions.": "Convierte la inteligencia de productos en acciones diarias.",
        "Portfolio Intelligence": "Inteligencia de Portafolio",
        "See which products deserve your attention today.": "Descubre qué productos merecen tu atención hoy.",
        "Rank and filter every saved product by opportunity score, commercial potential and recommended next action.": "Clasifica y filtra productos por oportunidad, potencial comercial y próxima acción recomendada.",
        "Product Discovery": "Descubrimiento de Productos",
        "Find new affiliate opportunities.": "Encuentra nuevas oportunidades de afiliación.",
        "Search available affiliate networks, compare products and identify the strongest opportunities.": "Busca redes de afiliados, compara productos e identifica las mejores oportunidades.",
        "Product Intelligence": "Inteligencia de Productos",
        "Understand which affiliate products deserve your attention.": "Comprende qué productos afiliados merecen tu atención.",
        "Select a saved product and review its latest metrics, recommendation, history and commercial potential.": "Selecciona un producto guardado y revisa sus métricas, recomendación, historial y potencial comercial.",
        "Product Research": "Investigación de Productos",
        "Build and maintain your affiliate product database.": "Crea y mantén tu base de productos afiliados.",
        "Unit economics": "Economía unitaria",
        "Know your break-even point before spending.": "Conoce tu punto de equilibrio antes de invertir.",
        "Model profitability using CPC, conversion rate and commission assumptions.": "Modela la rentabilidad usando CPC, tasa de conversión y comisión.",
        "Organic growth": "Crecimiento orgánico",
        "Plan helpful search content.": "Planifica contenido útil para búsquedas.",
        "Create article briefs around real intent instead of low-value pages.": "Crea briefs basados en intención real en lugar de páginas de poco valor.",
        "Account & Billing": "Cuenta y Facturación",
        "Manage your YAffiliate account and subscription.": "Gestiona tu cuenta y suscripción de YAffiliate.",
    },
    "zh_CN": {
        "Product catalogue": "产品目录",
        "Manage your affiliate shortlist.": "管理您的联盟产品候选列表。",
        "Portfolio view of researched, tested and active products.": "查看已研究、测试和正在推广的产品组合。",
        "AI workspace": "AI 工作空间",
        "Turn structured research into better decisions.": "将结构化研究转化为更好的决策。",
        "Analysis and drafting with human review before publication or spending.": "在发布或投入资金前，通过人工审核完成分析和内容创建。",
        "Performance intelligence": "绩效智能分析",
        "Understand your modelled campaign economics.": "了解营销活动的模拟经济表现。",
        "Later this will combine ad-platform, network and website data.": "未来这里将整合广告平台、联盟网络和网站数据。",
        "Campaign Generator": "营销活动生成器",
        "Create coordinated marketing assets from one product.": "从一个产品创建完整协调的营销素材。",
        "My Campaigns": "我的营销活动",
        "Access every marketing campaign you've created.": "访问您创建的所有营销活动。",
        "Review, open, download and manage campaigns generated with YAffiliate.": "查看、打开、下载和管理由 YAffiliate 创建的营销活动。",
        "AI Content Studio": "AI 内容工作室",
        "Generate structured content from product intelligence.": "根据产品智能分析生成结构化内容。",
        "Choose a product, select a content template and create an editable marketing asset.": "选择产品和内容模板，创建可编辑的营销素材。",
        "Command Centre": "指挥中心",
        "Turn research into campaigns that can make money.": "将研究转化为具有创收潜力的营销活动。",
        "Lifecycle messaging": "客户生命周期邮件",
        "Draft useful email sequences without spam.": "创建有价值且非垃圾邮件式的邮件序列。",
        "Build permission-based educational and promotional campaigns.": "创建基于用户许可的教育和推广活动。",
        "Paid acquisition": "付费获客",
        "Prepare Google Ads assets before launch.": "在发布前准备 Google Ads 素材。",
        "Draft ad groups and negatives, then review platform and network rules.": "创建广告组和否定关键词，并检查平台及联盟网络规则。",
        "Search intelligence": "搜索智能分析",
        "Build a commercial keyword database.": "建立商业关键词数据库。",
        "Capture intent, volume, CPC and competition before connecting approved keyword APIs.": "在连接获批的关键词 API 前记录意图、搜索量、CPC 和竞争度。",
        "Conversion studio": "转化工作室",
        "Create compliant affiliate landing pages.": "创建合规的联盟营销落地页。",
        "Generate clean HTML while keeping claims truthful and relationships transparent.": "生成简洁 HTML，同时确保宣传真实并保持联盟关系透明。",
        "Mission Center": "任务中心",
        "Your affiliate execution dashboard.": "您的联盟营销执行面板。",
        "Turn product intelligence into daily actions.": "将产品智能分析转化为每日行动。",
        "Portfolio Intelligence": "产品组合智能分析",
        "See which products deserve your attention today.": "查看今天最值得关注的产品。",
        "Rank and filter every saved product by opportunity score, commercial potential and recommended next action.": "根据机会评分、商业潜力和建议的下一步行动筛选产品。",
        "Product Discovery": "产品发现",
        "Find new affiliate opportunities.": "发现新的联盟营销机会。",
        "Search available affiliate networks, compare products and identify the strongest opportunities.": "搜索可用联盟网络、比较产品并识别最佳机会。",
        "Product Intelligence": "产品智能分析",
        "Understand which affiliate products deserve your attention.": "了解哪些联盟产品最值得关注。",
        "Select a saved product and review its latest metrics, recommendation, history and commercial potential.": "选择已保存产品，查看最新指标、建议、历史和商业潜力。",
        "Product Research": "产品研究",
        "Build and maintain your affiliate product database.": "建立并维护您的联盟产品数据库。",
        "Unit economics": "单位经济模型",
        "Know your break-even point before spending.": "投入资金前了解盈亏平衡点。",
        "Model profitability using CPC, conversion rate and commission assumptions.": "使用 CPC、转化率和佣金假设模拟盈利能力。",
        "Organic growth": "自然流量增长",
        "Plan helpful search content.": "规划有价值的搜索内容。",
        "Create article briefs around real intent instead of low-value pages.": "围绕真实搜索意图创建文章方案，避免低价值页面。",
        "Account & Billing": "账户与账单",
        "Manage your YAffiliate account and subscription.": "管理您的 YAffiliate 账户和订阅。",
    },
}



# -----------------------------------------------------------------------------
# Phase 2: customer-facing page controls
# -----------------------------------------------------------------------------
# These exact-literal translations are intentionally kept separate from
# internal identifiers, database values, routes and API parameters.
UI_LITERAL_TRANSLATIONS = {
    "pt_BR": {
        "Select a product": "Selecione um produto",
        "🚀 Generate Campaign": "🚀 Gerar Campanha",
        "Campaign assets": "Materiais da campanha",
        "Estimated words": "Palavras estimadas",
        "Average quality": "Qualidade média",
        "📰 SEO Article": "📰 Artigo de SEO",
        "🌐 Landing Page": "🌐 Página de Destino",
        "📧 Email Sequence": "📧 Sequência de E-mails",
        "🎯 Google Ads": "🎯 Google Ads",
        "SEO score": "Pontuação de SEO",
        "SEO article content": "Conteúdo do artigo de SEO",
        "Conversion score": "Pontuação de conversão",
        "Landing-page content": "Conteúdo da página de destino",
        "Emails": "E-mails",
        "Headlines": "Títulos",
        "Descriptions": "Descrições",
        "Keywords": "Palavras-chave",
        "Export complete campaign": "Exportar campanha completa",
        "Download the campaign as structured JSON or as a complete ZIP package.": "Baixe a campanha em JSON estruturado ou como um pacote ZIP completo.",
        "Saved campaign loaded from Campaign History.": "Campanha salva carregada do Histórico de Campanhas.",
        "← Back to Campaign History": "← Voltar ao Histórico de Campanhas",
        "Clear loaded campaign": "Limpar campanha carregada",
        "No products are currently available for campaign generation.": "Nenhum produto está disponível no momento para geração de campanha.",
        "Target keyword": "Palavra-chave alvo",
        "Target audience": "Público-alvo",
        "Campaign name": "Nome da campanha",
        "Writing tone": "Tom de escrita",
        "SEO article length": "Tamanho do artigo de SEO",
        "Campaign goal": "Objetivo da campanha",
        "Email sequence length": "Tamanho da sequência de e-mails",
        "Choose a product and generate a campaign to view the campaign assets.": "Escolha um produto e gere uma campanha para visualizar os materiais.",
        "Campaign generated and saved to Campaign History.": "Campanha gerada e salva no Histórico de Campanhas.",
        "The saved campaign settings were loaded, but its assets could not be reconstructed.": "As configurações da campanha foram carregadas, mas seus materiais não puderam ser reconstruídos.",
        "You must be signed in to save a campaign.": "Você precisa estar conectado para salvar uma campanha.",
        "Product": "Produto", "Audience": "Público", "Verified offer details": "Detalhes verificados da oferta",
        "Sequence": "Sequência", "Generate email sequence": "Gerar sequência de e-mails",
        "Products analysed": "Produtos analisados", "Average score": "Pontuação média",
        "High opportunity": "Alta oportunidade", "Needs attention": "Precisa de atenção",
        "Portfolio filters": "Filtros do portfólio", "Affiliate network": "Rede de afiliados",
        "Product status": "Status do produto", "Minimum opportunity score": "Pontuação mínima de oportunidade",
        "Decision": "Decisão", "Ranked portfolio": "Portfólio classificado",
        "No products are available yet. Add products in Product Research first.": "Ainda não há produtos disponíveis. Adicione produtos primeiro em Pesquisa de Produtos.",
        "No products match the selected filters.": "Nenhum produto corresponde aos filtros selecionados.",
        "Export keywords CSV": "Exportar palavras-chave em CSV", "Keyword ID to delete": "ID da palavra-chave para excluir",
        "Keyword": "Palavra-chave", "Intent": "Intenção", "Related product": "Produto relacionado",
        "Monthly volume": "Volume mensal", "Estimated CPC": "CPC estimado", "Competition 0-100": "Concorrência 0-100",
        "Status": "Status", "Save keyword": "Salvar palavra-chave", "No keywords saved yet.": "Nenhuma palavra-chave salva ainda.",
        "Delete selected keyword": "Excluir palavra-chave selecionada", "Keyword is required.": "A palavra-chave é obrigatória.",
        "Campaigns": "Campanhas", "Choose a campaign": "Escolha uma campanha", "Overview": "Visão geral",
        "**Product:**": "**Produto:**", "**Created:**": "**Criada em:**", "Download JSON": "Baixar JSON",
        "📂 Open Campaign": "📂 Abrir Campanha", "Delete Campaign": "Excluir Campanha",
        "Your authenticated user ID could not be found. Please sign in again.": "Seu ID de usuário autenticado não foi encontrado. Entre novamente.",
        "You have no saved campaigns yet.": "Você ainda não possui campanhas salvas.", "Campaign JSON": "JSON da campanha",
        "Advanced": "Avançado", "Delete ALL Campaigns": "Excluir TODAS as Campanhas", "Campaign history could not be loaded.": "O histórico de campanhas não pôde ser carregado.",
        "This campaign could not be opened.": "Esta campanha não pôde ser aberta.", "Campaign deleted.": "Campanha excluída.", "History cleared.": "Histórico limpo.",
        "Products researched": "Produtos pesquisados", "Saved campaigns": "Campanhas salvas", "Modelled profit": "Lucro projetado", "Average ROAS": "ROAS médio",
        "Next revenue actions": "Próximas ações de receita", "Recent campaigns": "Campanhas recentes", "Top opportunities": "Melhores oportunidades",
        "Research products before spending money on traffic.": "Pesquise produtos antes de investir dinheiro em tráfego.",
        "Product Discovery": "Descoberta de Produtos", "Generate SEO, landing page, emails and Google Ads.": "Gere SEO, página de destino, e-mails e Google Ads.",
        "Quick Generate": "Geração Rápida", "Reopen campaigns and continue from where you stopped.": "Reabra campanhas e continue de onde parou.",
        "Campaign History": "Histórico de Campanhas", "Dashboard data could not be loaded.": "Os dados do painel não puderam ser carregados.",
        "Generate your first campaign to see it here.": "Gere sua primeira campanha para vê-la aqui.", "Add products in Product Research.": "Adicione produtos em Pesquisa de Produtos.", "Open campaign": "Abrir campanha",
        "Tasks": "Tarefas", "Estimated Time": "Tempo estimado", "Mission Tasks": "Tarefas da Missão", "Filter by status": "Filtrar por status", "Add products in Product Research.": "Adicione produtos em Pesquisa de Produtos.",
        "Products found": "Produtos encontrados", "Best score": "Melhor pontuação", "Average commission": "Comissão média",
        "Inspect a discovered product": "Inspecionar produto descoberto", "Opportunity score": "Pontuação de oportunidade", "Commission": "Comissão", "Monthly searches": "Pesquisas mensais",
        "AI Product Analyst": "Analista de Produtos com IA", "Probability of success": "Probabilidade de sucesso", "Confidence": "Confiança", "Commercial potential": "Potencial comercial",
        "Channel potential": "Potencial por canal", "⭐ Save selected product to portfolio": "⭐ Salvar produto selecionado no portfólio",
        "Search keyword": "Palavra-chave de pesquisa", "Affiliate networks": "Redes de afiliados", "Country": "País", "Language": "Idioma", "Results per network": "Resultados por rede", "Discover products": "Descobrir produtos",
        "Best opportunity": "Melhor oportunidade", "Product comparison": "Comparação de produtos", "Category winners": "Destaques por categoria",
        "SEO potential": "Potencial de SEO", "Google Ads potential": "Potencial no Google Ads", "Email marketing potential": "Potencial de e-mail marketing", "Landing-page potential": "Potencial da página de destino",
        "Enter a keyword before searching.": "Digite uma palavra-chave antes de pesquisar.", "Select at least one affiliate network.": "Selecione pelo menos uma rede de afiliados.",
        "Search for a keyword to discover affiliate products.": "Pesquise uma palavra-chave para descobrir produtos afiliados.", "Rank": "Posição", "Score": "Pontuação", "SEO rating": "Avaliação de SEO",
        "No duplicate product, metric, recommendation or history snapshot was created.": "Nenhum produto, métrica, recomendação ou registro histórico duplicado foi criado.",
        "Strengths": "Pontos fortes", "Weaknesses": "Pontos fracos",
        "Assistant mode": "Modo do assistente", "Context": "Contexto", "Generate analysis": "Gerar análise", "Provide context first.": "Forneça o contexto primeiro.",
        "The Artificial Intelligence provider returned an empty response.": "O provedor de Inteligência Artificial retornou uma resposta vazia.",
        "Landing-page URL": "URL da página de destino", "Verified product facts": "Fatos verificados do produto", "Target keywords": "Palavras-chave alvo", "Draft campaign structure": "Criar estrutura da campanha",
        "Scenarios": "Cenários", "Budget": "Orçamento", "Profit": "Lucro", "Weighted ROAS": "ROAS ponderado", "Export analytics CSV": "Exportar análises em CSV", "Save calculator scenarios first.": "Salve primeiro os cenários da calculadora.",
        "Clicks": "Cliques", "Expected sales": "Vendas esperadas", "Revenue": "Receita", "ROAS": "ROAS", "ROI": "ROI", "Break-even conversion": "Conversão de equilíbrio",
        "Modelled estimates, not guaranteed results.": "Estimativas modeladas, não resultados garantidos.", "Save scenario": "Salvar cenário", "Budget (R$)": "Orçamento (R$)", "Average CPC": "CPC médio", "Conversion rate %": "Taxa de conversão %", "Calculate scenario": "Calcular cenário", "Scenario saved.": "Cenário salvo.", "Custom product name": "Nome do produto personalizado",
        "Content template": "Modelo de conteúdo", "No products are available for content generation.": "Nenhum produto está disponível para geração de conteúdo.", "No content templates are currently available.": "Nenhum modelo de conteúdo está disponível no momento.",
        "Choose a product and generate content to open the editor.": "Escolha um produto e gere conteúdo para abrir o editor.", "An editor has not yet been configured for this content type.": "Ainda não há um editor configurado para este tipo de conteúdo.", "The selected content generator is not available yet.": "O gerador de conteúdo selecionado ainda não está disponível.",
        "Primary keyword": "Palavra-chave principal", "Verified facts and sources": "Fatos e fontes verificados", "Content type": "Tipo de conteúdo", "Generate SEO brief": "Gerar briefing de SEO",
        "Google Trend": "Google Trends", "Recommended channel": "Canal recomendado", "Risk": "Risco", "Expected ROI": "ROI esperado", "Suggested test budget": "Orçamento de teste sugerido",
        "Opportunity timeline": "Linha do tempo da oportunidade", "Current score": "Pontuação atual", "Score change": "Variação da pontuação", "Trend": "Tendência", "Snapshots": "Registros", "Trend analyst": "Analista de tendências",
        "No products are available yet. Add one in Product Research first.": "Ainda não há produtos disponíveis. Adicione um primeiro em Pesquisa de Produtos.", "The selected product could not be loaded.": "O produto selecionado não pôde ser carregado.",
        "At least two historical snapshots are required to calculate meaningful analytics.": "São necessários pelo menos dois registros históricos para calcular análises relevantes.",
        "Improving signals": "Sinais de melhora", "Score movement": "Movimento da pontuação", "Market status": "Status de mercado", "Why this product": "Por que este produto", "Recommended next actions": "Próximas ações recomendadas",
        "No saved recommendation is available.": "Nenhuma recomendação salva está disponível.", "No saved next actions are available.": "Nenhuma próxima ação salva está disponível.", "The opportunity score has remained stable.": "A pontuação de oportunidade permaneceu estável.", "No recommendation reasoning is available.": "Nenhuma justificativa de recomendação está disponível.", "No next actions are available.": "Nenhuma próxima ação está disponível.",
        "Do not invent testimonials, guarantees, scarcity, medical outcomes, income claims or discounts.": "Não invente depoimentos, garantias, escassez, resultados médicos, alegações de renda ou descontos.",
        "Product name": "Nome do produto", "Main truthful benefit": "Principal benefício verdadeiro", "Call to action": "Chamada para ação", "Affiliate URL": "URL de afiliado", "Generate landing page": "Gerar página de destino", "Download HTML": "Baixar HTML", "Complete product, audience and benefit.": "Preencha produto, público e benefício.",
        "Workspace": "Espaço de trabalho", "💳 YAffiliate Pro": "💳 YAffiliate Pro", "Integration status": "Status das integrações", "OpenAI:": "OpenAI:", "Database:": "Banco de dados:", "Authentication:": "Autenticação:", "Stripe payments:": "Pagamentos Stripe:",
        "Workspace name": "Nome do espaço de trabalho", "Default reporting currency": "Moeda padrão dos relatórios", "Default monthly testing budget": "Orçamento mensal padrão para testes", "Save settings": "Salvar configurações", "Settings saved.": "Configurações salvas.",
        "Current plan: YAffiliate Pro": "Plano atual: YAffiliate Pro", "**Current plan:** Free": "**Plano atual:** Gratuito", "Your supported local subscription price and checkout language will be presented automatically by Stripe.": "O preço local compatível e o idioma do checkout serão apresentados automaticamente pelo Stripe.",
        "🚀 Upgrade to YAffiliate Pro": "🚀 Assinar YAffiliate Pro", "Payments are processed securely by Stripe. YAFFiliate does not store your card details.": "Os pagamentos são processados com segurança pelo Stripe. O YAffiliate não armazena os dados do seu cartão.",
        "You must be signed in before starting a subscription.": "Você precisa estar conectado antes de iniciar uma assinatura.", "Stripe did not return a Checkout URL.": "O Stripe não retornou uma URL de Checkout.",
        "AI Marketing Platform": "Plataforma de Marketing com IA", "Sign in to create, save and manage your affiliate campaigns.": "Entre para criar, salvar e gerenciar suas campanhas de afiliados.",
        "Sign In": "Entrar", "Create Account": "Criar Conta", "Email": "E-mail", "Password": "Senha", "🔐 Sign In": "🔐 Entrar", "Signed in successfully.": "Login realizado com sucesso.", "Confirm password": "Confirmar senha", "✨ Create Account": "✨ Criar Conta",
        "Passwords do not match.": "As senhas não coincidem.", "Password must contain at least 8 characters.": "A senha deve conter pelo menos 8 caracteres.", "Account created successfully.": "Conta criada com sucesso.",
        "Sign in did not return an authenticated session.": "O login não retornou uma sessão autenticada.", "Account could not be created.": "A conta não pôde ser criada.", "Account created. Check your email, confirm your address, then return and sign in.": "Conta criada. Verifique seu e-mail, confirme seu endereço e depois volte para entrar.", "Account was created but the authenticated session could not be stored. Please sign in.": "A conta foi criada, mas a sessão autenticada não pôde ser salva. Entre novamente.",
        "This feature is available with YAffiliate Pro.": "Este recurso está disponível no YAffiliate Pro.", "Upgrade to unlock YAffiliate's advanced AI marketing, research, campaign and analytics tools.": "Assine o Pro para desbloquear as ferramentas avançadas de IA, marketing, pesquisa, campanhas e análises do YAffiliate.", "Open Settings to start a secure Stripe subscription.": "Abra Configurações para iniciar uma assinatura segura pelo Stripe.", "💳 View YAffiliate Pro": "💳 Ver YAffiliate Pro",
    },
    "es": {},
    "zh_CN": {},
}

# Spanish and Simplified Chinese inherit complete customer-facing coverage.
# Explicit dictionaries below are generated from the English UI literals, while
# brands, currencies, technical codes and network names remain untouched.


# Complete Phase 2 translations for remaining customer-facing controls.
UI_LITERAL_TRANSLATIONS["pt_BR"].update({
    "Add a product": "Adicionar produto",
    "Best opportunity score": "Melhor pontuação de oportunidade",
    "Category": "Categoria",
    "Commission %": "Comissão %",
    "Commission per sale": "Comissão por venda",
    "Competition score": "Pontuação de concorrência",
    "Country code": "Código do país",
    "Delete a product": "Excluir produto",
    "Delete selected product": "Excluir produto selecionado",
    "EPC": "EPC",
    "Export products as CSV": "Exportar produtos em CSV",
    "Google Trend score": "Pontuação do Google Trends",
    "Gravity score": "Pontuação de Gravity",
    "I understand that this will delete the product and its related records.": "Entendo que isso excluirá o produto e seus registros relacionados.",
    "Language code": "Código do idioma",
    "Latest Filtrify Recommendation": "Recomendação mais recente do YAffiliate",
    "Market metrics": "Métricas de mercado",
    "Monthly search volume": "Volume mensal de buscas",
    "No products found yet.": "Nenhum produto encontrado ainda.",
    "Notes": "Observações",
    "Opportunity": "Oportunidade",
    "Price": "Preço",
    "Product deleted.": "Produto excluído.",
    "Product name is required.": "O nome do produto é obrigatório.",
    "Product was not found.": "O produto não foi encontrado.",
    "Products": "Produtos",
    "Refund rate %": "Taxa de reembolso %",
    "Sales-page URL": "URL da página de vendas",
    "Save product": "Salvar produto",
    "Saved products": "Produtos salvos",
    "Search by product name": "Pesquisar pelo nome do produto",
    "Select product": "Selecionar produto",
    "🔒 YAffiliate Pro": "🔒 YAffiliate Pro",
    "🚀 YAffiliate": "🚀 YAffiliate",
})

UI_LITERAL_TRANSLATIONS["es"].update({
    "**Created:**": "**Creada:**", "**Current plan:** Free": "**Plan actual:** Gratis", "**Product:**": "**Producto:**",
    "AI Marketing Platform": "Plataforma de Marketing con IA", "AI Product Analyst": "Analista de Productos con IA",
    "Account could not be created.": "No se pudo crear la cuenta.", "Account created successfully.": "Cuenta creada correctamente.",
    "Account created. Check your email, confirm your address, then return and sign in.": "Cuenta creada. Revisa tu correo, confirma tu dirección y luego vuelve para iniciar sesión.",
    "Account was created but the authenticated session could not be stored. Please sign in.": "La cuenta fue creada, pero no se pudo guardar la sesión autenticada. Inicia sesión.",
    "Add a product": "Añadir producto", "Add products in Product Research.": "Añade productos en Investigación de Productos.", "Advanced": "Avanzado",
    "Affiliate URL": "URL de afiliado", "Affiliate network": "Red de afiliados", "Affiliate networks": "Redes de afiliados",
    "An editor has not yet been configured for this content type.": "Todavía no se ha configurado un editor para este tipo de contenido.",
    "Assistant mode": "Modo del asistente", "At least two historical snapshots are required to calculate meaningful analytics.": "Se necesitan al menos dos registros históricos para calcular análisis relevantes.",
    "Audience": "Público", "Authentication:": "Autenticación:", "Average CPC": "CPC medio", "Average ROAS": "ROAS medio", "Average commission": "Comisión media", "Average quality": "Calidad media", "Average score": "Puntuación media",
    "Best opportunity": "Mejor oportunidad", "Best opportunity score": "Mejor puntuación de oportunidad", "Best score": "Mejor puntuación", "Break-even conversion": "Conversión de equilibrio",
    "Budget": "Presupuesto", "Budget (R$)": "Presupuesto (R$)", "Calculate scenario": "Calcular escenario", "Call to action": "Llamada a la acción",
    "Campaign History": "Historial de Campañas", "Campaign JSON": "JSON de campaña", "Campaign assets": "Materiales de campaña", "Campaign deleted.": "Campaña eliminada.",
    "Campaign generated and saved to Campaign History.": "Campaña generada y guardada en el Historial de Campañas.", "Campaign goal": "Objetivo de la campaña", "Campaign history could not be loaded.": "No se pudo cargar el historial de campañas.", "Campaign name": "Nombre de la campaña", "Campaigns": "Campañas",
    "Category": "Categoría", "Category winners": "Destacados por categoría", "Channel potential": "Potencial por canal", "Choose a campaign": "Elige una campaña",
    "Choose a product and generate a campaign to view the campaign assets.": "Elige un producto y genera una campaña para ver los materiales.",
    "Choose a product and generate content to open the editor.": "Elige un producto y genera contenido para abrir el editor.", "Clear loaded campaign": "Limpiar campaña cargada",
    "Clicks": "Clics", "Commercial potential": "Potencial comercial", "Commission": "Comisión", "Commission %": "Comisión %", "Commission per sale": "Comisión por venta",
    "Competition 0-100": "Competencia 0-100", "Competition score": "Puntuación de competencia", "Complete product, audience and benefit.": "Completa producto, público y beneficio.", "Confidence": "Confianza", "Confirm password": "Confirmar contraseña",
    "Content template": "Plantilla de contenido", "Content type": "Tipo de contenido", "Context": "Contexto", "Conversion rate %": "Tasa de conversión %", "Conversion score": "Puntuación de conversión",
    "Country": "País", "Country code": "Código de país", "Create Account": "Crear Cuenta", "Current plan: YAffiliate Pro": "Plan actual: YAffiliate Pro", "Current score": "Puntuación actual", "Custom product name": "Nombre de producto personalizado",
    "Dashboard data could not be loaded.": "No se pudieron cargar los datos del panel.", "Database:": "Base de datos:", "Decision": "Decisión", "Default monthly testing budget": "Presupuesto mensual predeterminado para pruebas", "Default reporting currency": "Moneda predeterminada de informes",
    "Delete ALL Campaigns": "Eliminar TODAS las Campañas", "Delete Campaign": "Eliminar Campaña", "Delete a product": "Eliminar producto", "Delete selected keyword": "Eliminar palabra clave seleccionada", "Delete selected product": "Eliminar producto seleccionado",
    "Descriptions": "Descripciones", "Discover products": "Descubrir productos", "Do not invent testimonials, guarantees, scarcity, medical outcomes, income claims or discounts.": "No inventes testimonios, garantías, escasez, resultados médicos, promesas de ingresos ni descuentos.",
    "Download HTML": "Descargar HTML", "Download JSON": "Descargar JSON", "Download the campaign as structured JSON or as a complete ZIP package.": "Descarga la campaña como JSON estructurado o como un paquete ZIP completo.", "Draft campaign structure": "Crear estructura de campaña",
    "EPC": "EPC", "Email": "Correo electrónico", "Email marketing potential": "Potencial de email marketing", "Email sequence length": "Longitud de la secuencia de correos", "Emails": "Correos",
    "Enter a keyword before searching.": "Introduce una palabra clave antes de buscar.", "Estimated CPC": "CPC estimado", "Estimated Time": "Tiempo estimado", "Estimated words": "Palabras estimadas", "Expected ROI": "ROI esperado", "Expected sales": "Ventas esperadas",
    "Export analytics CSV": "Exportar análisis CSV", "Export complete campaign": "Exportar campaña completa", "Export keywords CSV": "Exportar palabras clave CSV", "Export products as CSV": "Exportar productos como CSV",
    "Filter by status": "Filtrar por estado", "Generate SEO brief": "Generar brief SEO", "Generate SEO, landing page, emails and Google Ads.": "Genera SEO, página de destino, correos y Google Ads.", "Generate analysis": "Generar análisis", "Generate email sequence": "Generar secuencia de correos", "Generate landing page": "Generar página de destino", "Generate your first campaign to see it here.": "Genera tu primera campaña para verla aquí.",
    "Google Ads potential": "Potencial de Google Ads", "Google Trend": "Google Trends", "Google Trend score": "Puntuación de Google Trends", "Gravity score": "Puntuación Gravity", "Headlines": "Titulares", "High opportunity": "Alta oportunidad", "History cleared.": "Historial limpiado.",
    "I understand that this will delete the product and its related records.": "Entiendo que esto eliminará el producto y sus registros relacionados.", "Improving signals": "Señales de mejora", "Inspect a discovered product": "Inspeccionar producto descubierto", "Integration status": "Estado de integraciones", "Intent": "Intención",
    "Keyword": "Palabra clave", "Keyword ID to delete": "ID de palabra clave para eliminar", "Keyword is required.": "La palabra clave es obligatoria.", "Keywords": "Palabras clave",
    "Landing-page URL": "URL de página de destino", "Landing-page content": "Contenido de la página de destino", "Landing-page potential": "Potencial de la página de destino", "Language": "Idioma", "Language code": "Código de idioma",
    "Latest Filtrify Recommendation": "Recomendación más reciente de YAffiliate", "Main truthful benefit": "Principal beneficio veraz", "Market metrics": "Métricas de mercado", "Market status": "Estado del mercado", "Minimum opportunity score": "Puntuación mínima de oportunidad", "Mission Tasks": "Tareas de la Misión",
    "Modelled estimates, not guaranteed results.": "Estimaciones modeladas, no resultados garantizados.", "Modelled profit": "Beneficio proyectado", "Monthly search volume": "Volumen mensual de búsquedas", "Monthly searches": "Búsquedas mensuales", "Monthly volume": "Volumen mensual", "Needs attention": "Necesita atención", "Next revenue actions": "Próximas acciones de ingresos",
    "No content templates are currently available.": "No hay plantillas de contenido disponibles actualmente.", "No duplicate product, metric, recommendation or history snapshot was created.": "No se creó ningún producto, métrica, recomendación o registro histórico duplicado.", "No keywords saved yet.": "Todavía no hay palabras clave guardadas.", "No next actions are available.": "No hay próximas acciones disponibles.",
    "No products are available for content generation.": "No hay productos disponibles para generar contenido.", "No products are available yet. Add one in Product Research first.": "Todavía no hay productos disponibles. Añade uno primero en Investigación de Productos.", "No products are available yet. Add products in Product Research first.": "Todavía no hay productos disponibles. Añade productos primero en Investigación de Productos.", "No products are currently available for campaign generation.": "No hay productos disponibles actualmente para generar campañas.",
    "No products found yet.": "Todavía no se encontraron productos.", "No products match the selected filters.": "Ningún producto coincide con los filtros seleccionados.", "No recommendation reasoning is available.": "No hay una justificación de recomendación disponible.", "No saved next actions are available.": "No hay próximas acciones guardadas disponibles.", "No saved recommendation is available.": "No hay una recomendación guardada disponible.", "Notes": "Notas",
    "Open Settings to start a secure Stripe subscription.": "Abre Configuración para iniciar una suscripción segura con Stripe.", "Open campaign": "Abrir campaña", "OpenAI:": "OpenAI:", "Opportunity": "Oportunidad", "Opportunity score": "Puntuación de oportunidad", "Opportunity timeline": "Cronología de oportunidad", "Overview": "Resumen",
    "Password": "Contraseña", "Password must contain at least 8 characters.": "La contraseña debe contener al menos 8 caracteres.", "Passwords do not match.": "Las contraseñas no coinciden.", "Payments are processed securely by Stripe. YAFFiliate does not store your card details.": "Los pagos se procesan de forma segura con Stripe. YAffiliate no almacena los datos de tu tarjeta.",
    "Portfolio filters": "Filtros del portafolio", "Price": "Precio", "Primary keyword": "Palabra clave principal", "Probability of success": "Probabilidad de éxito", "Product": "Producto", "Product comparison": "Comparación de productos", "Product deleted.": "Producto eliminado.", "Product name": "Nombre del producto", "Product name is required.": "El nombre del producto es obligatorio.", "Product status": "Estado del producto", "Product was not found.": "No se encontró el producto.", "Products": "Productos", "Products analysed": "Productos analizados", "Products found": "Productos encontrados", "Products researched": "Productos investigados", "Profit": "Beneficio",
    "Provide context first.": "Proporciona contexto primero.", "Quick Generate": "Generación Rápida", "ROAS": "ROAS", "ROI": "ROI", "Rank": "Posición", "Ranked portfolio": "Portafolio clasificado", "Recent campaigns": "Campañas recientes", "Recommended channel": "Canal recomendado", "Recommended next actions": "Próximas acciones recomendadas", "Refund rate %": "Tasa de reembolso %", "Related product": "Producto relacionado",
    "Reopen campaigns and continue from where you stopped.": "Vuelve a abrir campañas y continúa desde donde lo dejaste.", "Research products before spending money on traffic.": "Investiga productos antes de gastar dinero en tráfico.", "Results per network": "Resultados por red", "Revenue": "Ingresos", "Risk": "Riesgo",
    "SEO article content": "Contenido del artículo SEO", "SEO article length": "Longitud del artículo SEO", "SEO potential": "Potencial SEO", "SEO rating": "Valoración SEO", "SEO score": "Puntuación SEO", "Sales-page URL": "URL de página de ventas",
    "Save calculator scenarios first.": "Guarda primero los escenarios de la calculadora.", "Save keyword": "Guardar palabra clave", "Save product": "Guardar producto", "Save scenario": "Guardar escenario", "Save settings": "Guardar configuración", "Saved campaign loaded from Campaign History.": "Campaña guardada cargada desde el Historial de Campañas.", "Saved campaigns": "Campañas guardadas", "Saved products": "Productos guardados", "Scenario saved.": "Escenario guardado.", "Scenarios": "Escenarios", "Score": "Puntuación", "Score change": "Cambio de puntuación", "Score movement": "Movimiento de puntuación",
    "Search by product name": "Buscar por nombre del producto", "Search for a keyword to discover affiliate products.": "Busca una palabra clave para descubrir productos afiliados.", "Search keyword": "Palabra clave de búsqueda", "Select a product": "Selecciona un producto", "Select at least one affiliate network.": "Selecciona al menos una red de afiliados.", "Select product": "Seleccionar producto", "Sequence": "Secuencia", "Settings saved.": "Configuración guardada.",
    "Sign In": "Iniciar Sesión", "Sign in did not return an authenticated session.": "El inicio de sesión no devolvió una sesión autenticada.", "Sign in to create, save and manage your affiliate campaigns.": "Inicia sesión para crear, guardar y gestionar tus campañas de afiliados.", "Signed in successfully.": "Sesión iniciada correctamente.", "Snapshots": "Registros", "Status": "Estado", "Strengths": "Fortalezas", "Stripe did not return a Checkout URL.": "Stripe no devolvió una URL de Checkout.", "Stripe payments:": "Pagos con Stripe:", "Suggested test budget": "Presupuesto de prueba sugerido",
    "Target audience": "Público objetivo", "Target keyword": "Palabra clave objetivo", "Target keywords": "Palabras clave objetivo", "Tasks": "Tareas", "The Artificial Intelligence provider returned an empty response.": "El proveedor de Inteligencia Artificial devolvió una respuesta vacía.", "The opportunity score has remained stable.": "La puntuación de oportunidad se ha mantenido estable.", "The saved campaign settings were loaded, but its assets could not be reconstructed.": "Se cargó la configuración de la campaña guardada, pero no se pudieron reconstruir sus materiales.", "The selected content generator is not available yet.": "El generador de contenido seleccionado todavía no está disponible.", "The selected product could not be loaded.": "No se pudo cargar el producto seleccionado.", "This campaign could not be opened.": "No se pudo abrir esta campaña.", "This feature is available with YAffiliate Pro.": "Esta función está disponible con YAffiliate Pro.", "Top opportunities": "Mejores oportunidades", "Trend": "Tendencia", "Trend analyst": "Analista de tendencias",
    "Upgrade to unlock YAffiliate's advanced AI marketing, research, campaign and analytics tools.": "Actualiza a Pro para desbloquear las herramientas avanzadas de IA, marketing, investigación, campañas y análisis de YAffiliate.", "Verified facts and sources": "Hechos y fuentes verificados", "Verified offer details": "Detalles verificados de la oferta", "Verified product facts": "Datos verificados del producto", "Weaknesses": "Debilidades", "Weighted ROAS": "ROAS ponderado", "Why this product": "Por qué este producto", "Workspace": "Espacio de trabajo", "Workspace name": "Nombre del espacio de trabajo", "Writing tone": "Tono de escritura",
    "You have no saved campaigns yet.": "Todavía no tienes campañas guardadas.", "You must be signed in before starting a subscription.": "Debes iniciar sesión antes de comenzar una suscripción.", "You must be signed in to save a campaign.": "Debes iniciar sesión para guardar una campaña.", "Your authenticated user ID could not be found. Please sign in again.": "No se pudo encontrar tu ID de usuario autenticado. Inicia sesión de nuevo.", "Your supported local subscription price and checkout language will be presented automatically by Stripe.": "Stripe mostrará automáticamente el precio local compatible y el idioma del checkout.",
    "← Back to Campaign History": "← Volver al Historial de Campañas", "✨ Create Account": "✨ Crear Cuenta", "⭐ Save selected product to portfolio": "⭐ Guardar producto seleccionado en el portafolio", "🌐 Landing Page": "🌐 Página de Destino", "🎯 Google Ads": "🎯 Google Ads", "💳 View YAffiliate Pro": "💳 Ver YAffiliate Pro", "💳 YAffiliate Pro": "💳 YAffiliate Pro", "📂 Open Campaign": "📂 Abrir Campaña", "📧 Email Sequence": "📧 Secuencia de Correos", "📰 SEO Article": "📰 Artículo SEO", "🔐 Sign In": "🔐 Iniciar Sesión", "🔒 YAffiliate Pro": "🔒 YAffiliate Pro", "🚀 Generate Campaign": "🚀 Generar Campaña", "🚀 Upgrade to YAffiliate Pro": "🚀 Actualizar a YAffiliate Pro", "🚀 YAffiliate": "🚀 YAffiliate",
})

UI_LITERAL_TRANSLATIONS["zh_CN"].update({
    "**Created:**": "**创建时间：**", "**Current plan:** Free": "**当前方案：** 免费", "**Product:**": "**产品：**",
    "AI Marketing Platform": "AI 营销平台", "AI Product Analyst": "AI 产品分析师",
    "Account could not be created.": "无法创建账户。", "Account created successfully.": "账户创建成功。", "Account created. Check your email, confirm your address, then return and sign in.": "账户已创建。请查看邮箱并确认地址，然后返回登录。", "Account was created but the authenticated session could not be stored. Please sign in.": "账户已创建，但无法保存登录会话。请重新登录。",
    "Add a product": "添加产品", "Add products in Product Research.": "请先在产品研究中添加产品。", "Advanced": "高级", "Affiliate URL": "联盟链接", "Affiliate network": "联盟网络", "Affiliate networks": "联盟网络",
    "An editor has not yet been configured for this content type.": "此内容类型尚未配置编辑器。", "Assistant mode": "助手模式", "At least two historical snapshots are required to calculate meaningful analytics.": "至少需要两个历史快照才能计算有意义的分析。", "Audience": "受众", "Authentication:": "身份验证：", "Average CPC": "平均 CPC", "Average ROAS": "平均 ROAS", "Average commission": "平均佣金", "Average quality": "平均质量", "Average score": "平均评分",
    "Best opportunity": "最佳机会", "Best opportunity score": "最佳机会评分", "Best score": "最高评分", "Break-even conversion": "盈亏平衡转化率", "Budget": "预算", "Budget (R$)": "预算 (R$)", "Calculate scenario": "计算方案", "Call to action": "行动号召",
    "Campaign History": "营销活动历史", "Campaign JSON": "营销活动 JSON", "Campaign assets": "营销素材", "Campaign deleted.": "营销活动已删除。", "Campaign generated and saved to Campaign History.": "营销活动已生成并保存到历史记录。", "Campaign goal": "营销目标", "Campaign history could not be loaded.": "无法加载营销活动历史。", "Campaign name": "营销活动名称", "Campaigns": "营销活动",
    "Category": "类别", "Category winners": "分类最佳产品", "Channel potential": "渠道潜力", "Choose a campaign": "选择营销活动", "Choose a product and generate a campaign to view the campaign assets.": "选择产品并生成营销活动以查看素材。", "Choose a product and generate content to open the editor.": "选择产品并生成内容以打开编辑器。", "Clear loaded campaign": "清除已加载的营销活动",
    "Clicks": "点击", "Commercial potential": "商业潜力", "Commission": "佣金", "Commission %": "佣金 %", "Commission per sale": "每笔销售佣金", "Competition 0-100": "竞争度 0-100", "Competition score": "竞争评分", "Complete product, audience and benefit.": "请完整填写产品、受众和优势。", "Confidence": "置信度", "Confirm password": "确认密码",
    "Content template": "内容模板", "Content type": "内容类型", "Context": "上下文", "Conversion rate %": "转化率 %", "Conversion score": "转化评分", "Country": "国家", "Country code": "国家代码", "Create Account": "创建账户", "Current plan: YAffiliate Pro": "当前方案：YAffiliate Pro", "Current score": "当前评分", "Custom product name": "自定义产品名称",
    "Dashboard data could not be loaded.": "无法加载仪表盘数据。", "Database:": "数据库：", "Decision": "决策", "Default monthly testing budget": "默认每月测试预算", "Default reporting currency": "默认报表货币", "Delete ALL Campaigns": "删除所有营销活动", "Delete Campaign": "删除营销活动", "Delete a product": "删除产品", "Delete selected keyword": "删除所选关键词", "Delete selected product": "删除所选产品",
    "Descriptions": "描述", "Discover products": "发现产品", "Do not invent testimonials, guarantees, scarcity, medical outcomes, income claims or discounts.": "不要虚构评价、保证、稀缺性、医疗结果、收入承诺或折扣。", "Download HTML": "下载 HTML", "Download JSON": "下载 JSON", "Download the campaign as structured JSON or as a complete ZIP package.": "将营销活动下载为结构化 JSON 或完整 ZIP 包。", "Draft campaign structure": "创建营销活动结构",
    "EPC": "EPC", "Email": "电子邮件", "Email marketing potential": "邮件营销潜力", "Email sequence length": "邮件序列长度", "Emails": "邮件", "Enter a keyword before searching.": "搜索前请输入关键词。", "Estimated CPC": "预计 CPC", "Estimated Time": "预计时间", "Estimated words": "预计字数", "Expected ROI": "预计 ROI", "Expected sales": "预计销售量",
    "Export analytics CSV": "导出分析 CSV", "Export complete campaign": "导出完整营销活动", "Export keywords CSV": "导出关键词 CSV", "Export products as CSV": "导出产品 CSV", "Filter by status": "按状态筛选", "Generate SEO brief": "生成 SEO 简报", "Generate SEO, landing page, emails and Google Ads.": "生成 SEO、落地页、邮件和 Google Ads。", "Generate analysis": "生成分析", "Generate email sequence": "生成邮件序列", "Generate landing page": "生成落地页", "Generate your first campaign to see it here.": "生成第一个营销活动后即可在此查看。",
    "Google Ads potential": "Google Ads 潜力", "Google Trend": "Google Trends", "Google Trend score": "Google Trends 评分", "Gravity score": "Gravity 评分", "Headlines": "标题", "High opportunity": "高机会", "History cleared.": "历史记录已清除。", "I understand that this will delete the product and its related records.": "我了解这将删除该产品及其相关记录。", "Improving signals": "改善信号", "Inspect a discovered product": "查看发现的产品", "Integration status": "集成状态", "Intent": "意图",
    "Keyword": "关键词", "Keyword ID to delete": "要删除的关键词 ID", "Keyword is required.": "必须填写关键词。", "Keywords": "关键词", "Landing-page URL": "落地页 URL", "Landing-page content": "落地页内容", "Landing-page potential": "落地页潜力", "Language": "语言", "Language code": "语言代码", "Latest Filtrify Recommendation": "最新 YAffiliate 推荐", "Main truthful benefit": "主要真实优势", "Market metrics": "市场指标", "Market status": "市场状态", "Minimum opportunity score": "最低机会评分", "Mission Tasks": "任务列表",
    "Modelled estimates, not guaranteed results.": "模型估算，不代表保证结果。", "Modelled profit": "模型利润", "Monthly search volume": "月搜索量", "Monthly searches": "每月搜索", "Monthly volume": "月度量", "Needs attention": "需要关注", "Next revenue actions": "下一步营收行动",
    "No content templates are currently available.": "当前没有可用的内容模板。", "No duplicate product, metric, recommendation or history snapshot was created.": "未创建重复的产品、指标、建议或历史快照。", "No keywords saved yet.": "尚未保存关键词。", "No next actions are available.": "没有可用的下一步行动。", "No products are available for content generation.": "没有可用于内容生成的产品。", "No products are available yet. Add one in Product Research first.": "目前没有产品。请先在产品研究中添加一个。", "No products are available yet. Add products in Product Research first.": "目前没有产品。请先在产品研究中添加产品。", "No products are currently available for campaign generation.": "当前没有可用于生成营销活动的产品。", "No products found yet.": "尚未找到产品。", "No products match the selected filters.": "没有产品符合所选筛选条件。", "No recommendation reasoning is available.": "没有可用的推荐理由。", "No saved next actions are available.": "没有已保存的下一步行动。", "No saved recommendation is available.": "没有已保存的推荐。", "Notes": "备注",
    "Open Settings to start a secure Stripe subscription.": "打开设置，通过 Stripe 安全订阅。", "Open campaign": "打开营销活动", "OpenAI:": "OpenAI：", "Opportunity": "机会", "Opportunity score": "机会评分", "Opportunity timeline": "机会时间线", "Overview": "概览", "Password": "密码", "Password must contain at least 8 characters.": "密码至少需要 8 个字符。", "Passwords do not match.": "两次输入的密码不一致。", "Payments are processed securely by Stripe. YAFFiliate does not store your card details.": "付款由 Stripe 安全处理。YAffiliate 不保存您的银行卡信息。",
    "Portfolio filters": "产品组合筛选", "Price": "价格", "Primary keyword": "主要关键词", "Probability of success": "成功概率", "Product": "产品", "Product comparison": "产品对比", "Product deleted.": "产品已删除。", "Product name": "产品名称", "Product name is required.": "必须填写产品名称。", "Product status": "产品状态", "Product was not found.": "未找到产品。", "Products": "产品", "Products analysed": "已分析产品", "Products found": "找到的产品", "Products researched": "已研究产品", "Profit": "利润", "Provide context first.": "请先提供上下文。", "Quick Generate": "快速生成", "ROAS": "ROAS", "ROI": "ROI", "Rank": "排名", "Ranked portfolio": "产品组合排名", "Recent campaigns": "最近的营销活动", "Recommended channel": "推荐渠道", "Recommended next actions": "建议的下一步行动", "Refund rate %": "退款率 %", "Related product": "相关产品",
    "Reopen campaigns and continue from where you stopped.": "重新打开营销活动并从上次停止的位置继续。", "Research products before spending money on traffic.": "投入流量预算前先研究产品。", "Results per network": "每个网络的结果数", "Revenue": "收入", "Risk": "风险", "SEO article content": "SEO 文章内容", "SEO article length": "SEO 文章长度", "SEO potential": "SEO 潜力", "SEO rating": "SEO 评级", "SEO score": "SEO 评分", "Sales-page URL": "销售页 URL",
    "Save calculator scenarios first.": "请先保存计算器方案。", "Save keyword": "保存关键词", "Save product": "保存产品", "Save scenario": "保存方案", "Save settings": "保存设置", "Saved campaign loaded from Campaign History.": "已从营销活动历史加载保存的营销活动。", "Saved campaigns": "已保存的营销活动", "Saved products": "已保存产品", "Scenario saved.": "方案已保存。", "Scenarios": "方案", "Score": "评分", "Score change": "评分变化", "Score movement": "评分趋势", "Search by product name": "按产品名称搜索", "Search for a keyword to discover affiliate products.": "搜索关键词以发现联盟产品。", "Search keyword": "搜索关键词", "Select a product": "选择产品", "Select at least one affiliate network.": "请至少选择一个联盟网络。", "Select product": "选择产品", "Sequence": "序列", "Settings saved.": "设置已保存。",
    "Sign In": "登录", "Sign in did not return an authenticated session.": "登录未返回有效会话。", "Sign in to create, save and manage your affiliate campaigns.": "登录后即可创建、保存和管理联盟营销活动。", "Signed in successfully.": "登录成功。", "Snapshots": "快照", "Status": "状态", "Strengths": "优势", "Stripe did not return a Checkout URL.": "Stripe 未返回 Checkout URL。", "Stripe payments:": "Stripe 支付：", "Suggested test budget": "建议测试预算", "Target audience": "目标受众", "Target keyword": "目标关键词", "Target keywords": "目标关键词", "Tasks": "任务",
    "The Artificial Intelligence provider returned an empty response.": "人工智能服务返回了空响应。", "The opportunity score has remained stable.": "机会评分保持稳定。", "The saved campaign settings were loaded, but its assets could not be reconstructed.": "已加载保存的营销活动设置，但无法重建其素材。", "The selected content generator is not available yet.": "所选内容生成器尚不可用。", "The selected product could not be loaded.": "无法加载所选产品。", "This campaign could not be opened.": "无法打开此营销活动。", "This feature is available with YAffiliate Pro.": "此功能仅适用于 YAffiliate Pro。", "Top opportunities": "最佳机会", "Trend": "趋势", "Trend analyst": "趋势分析师",
    "Upgrade to unlock YAffiliate's advanced AI marketing, research, campaign and analytics tools.": "升级到 Pro，解锁 YAffiliate 的高级 AI 营销、研究、营销活动和分析工具。", "Verified facts and sources": "已验证的事实和来源", "Verified offer details": "已验证的优惠详情", "Verified product facts": "已验证的产品信息", "Weaknesses": "不足", "Weighted ROAS": "加权 ROAS", "Why this product": "为什么选择此产品", "Workspace": "工作空间", "Workspace name": "工作空间名称", "Writing tone": "写作语气",
    "You have no saved campaigns yet.": "您还没有保存的营销活动。", "You must be signed in before starting a subscription.": "开始订阅前必须先登录。", "You must be signed in to save a campaign.": "必须登录后才能保存营销活动。", "Your authenticated user ID could not be found. Please sign in again.": "找不到您的已认证用户 ID。请重新登录。", "Your supported local subscription price and checkout language will be presented automatically by Stripe.": "Stripe 会自动显示受支持的本地订阅价格和结账语言。",
    "← Back to Campaign History": "← 返回营销活动历史", "✨ Create Account": "✨ 创建账户", "⭐ Save selected product to portfolio": "⭐ 将所选产品保存到产品组合", "🌐 Landing Page": "🌐 落地页", "🎯 Google Ads": "🎯 Google Ads", "💳 View YAffiliate Pro": "💳 查看 YAffiliate Pro", "💳 YAffiliate Pro": "💳 YAffiliate Pro", "📂 Open Campaign": "📂 打开营销活动", "📧 Email Sequence": "📧 邮件序列", "📰 SEO Article": "📰 SEO 文章", "🔐 Sign In": "🔐 登录", "🔒 YAffiliate Pro": "🔒 YAffiliate Pro", "🚀 Generate Campaign": "🚀 生成营销活动", "🚀 Upgrade to YAffiliate Pro": "🚀 升级到 YAffiliate Pro", "🚀 YAffiliate": "🚀 YAffiliate",
})

def translate_literal(text: str) -> str:
    """Translate customer-facing literal text when a translation exists."""
    language = get_language()
    if language == "en":
        return text
    if text in UI_LITERAL_TRANSLATIONS.get(language, {}):
        return UI_LITERAL_TRANSLATIONS[language][text]
    return LITERAL_TRANSLATIONS.get(language, {}).get(text, text)


def ui(text: str) -> str:
    """Translate a customer-facing UI literal without changing internal values."""
    return translate_literal(text)
