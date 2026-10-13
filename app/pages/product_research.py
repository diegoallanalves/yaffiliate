
"""Product Research workspace for YAffiliate."""

from __future__ import annotations

from decimal import Decimal

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components.layout import page_header
from app.repositories.product_repository import ProductRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.opportunity_history_repository import OpportunityHistoryRepository
from app.services.opportunity_score_service import (
    OpportunityFactors,
    OpportunityScoreService,
)
from app.services.recommendation_service import RecommendationService
from app.services.translation_service import get_language, ui


# Database values must remain in English.
STATUS_OPTIONS = [
    "Research",
    "Shortlist",
    "Testing",
    "Active",
    "Paused",
    "Rejected",
    "Archived",
]

# Additional Product Research translations not yet in the shared service.
# Other languages continue to use the shared ui() dictionary where available.
PAGE_TRANSLATIONS = {
    "pt_BR": {
        "Research workspace": "Espaço de pesquisa",
        "Find and compare affiliate opportunities.": "Encontre e compare oportunidades de afiliados.",
        "Research products, analyse opportunities and prepare your affiliate marketing shortlist.": "Pesquise produtos, analise oportunidades e prepare sua lista de produtos afiliados.",
        "Your research workflow": "Seu fluxo de pesquisa",
        "Add product → Analyse opportunity → Review saved products → Prepare campaign": "Adicionar produto → Analisar oportunidade → Revisar produtos salvos → Preparar campanha",
        "1. Add an affiliate product": "1. Adicionar um produto afiliado",
        "Start with the product details and commission. Advanced market metrics are optional for your research.": "Comece pelos detalhes do produto e pela comissão. As métricas avançadas de mercado são opcionais.",
        "Basic product information": "Informações básicas do produto",
        "Product name *": "Nome do produto *",
        "Example: English Online Course": "Exemplo: Curso de Inglês Online",
        "Not selected": "Não selecionado",
        "Example: Education": "Exemplo: Educação",
        "Research": "Pesquisa",
        "Shortlist": "Lista de seleção",
        "Testing": "Em teste",
        "Active": "Ativo",
        "Paused": "Pausado",
        "Rejected": "Rejeitado",
        "Archived": "Arquivado",
        "All": "Todos",
        "Product economics": "Dados financeiros do produto",
        "Product price (R$)": "Preço do produto (R$)",
        "Commission per sale (R$)": "Comissão por venda (R$)",
        "Commission (%)": "Comissão (%)",
        "Enter the actual commission offered by your affiliate network. A default of zero means no amount has been entered.": "Informe a comissão real oferecida pela rede de afiliados. O valor inicial zero significa que nenhuma quantia foi informada.",
        "Product sales page URL": "URL da página de vendas",
        "Your affiliate tracking URL": "Seu link de rastreamento de afiliado",
        "This must be your own affiliate link from the network, not simply the product website.": "Use seu próprio link de afiliado fornecido pela rede, não apenas o site do produto.",
        "Advanced market metrics — optional": "Métricas avançadas de mercado — opcionais",
        "Only enter figures you have researched. Blank research represented by default zeros is not evidence of zero demand or zero advertising cost.": "Informe apenas números pesquisados. Valores iniciais iguais a zero não comprovam ausência de demanda nem custo zero de publicidade.",
        "EPC (earnings per click)": "EPC (ganhos por clique)",
        "Estimated CPC (cost per click)": "CPC estimado (custo por clique)",
        "Google Trends score": "Pontuação do Google Trends",
        "Refund rate (%)": "Taxa de reembolso (%)",
        "Research notes": "Observações da pesquisa",
        "Target audience, product benefits, competition, sources of market data...": "Público-alvo, benefícios, concorrência, fontes dos dados de mercado...",
        "Save product and analyse opportunity": "Salvar produto e analisar oportunidade",
        "Please enter a product name.": "Informe o nome do produto.",
        "Sales page": "Página de vendas",
        "Affiliate link": "Link de afiliado",
        "must begin with https:// or http://": "deve começar com https:// ou http://",
        "The product could not be saved completely.": "Não foi possível salvar o produto completamente.",
        "Product saved successfully.": "Produto salvo com sucesso.",
        "Your latest product recommendation": "Sua recomendação mais recente",
        "Product ID": "ID do produto",
        "Recommendation ID": "ID da recomendação",
        "Risk level": "Nível de risco",
        "Recommended channel": "Canal recomendado",
        "Difficulty": "Dificuldade",
        "Why YAffiliate recommends this": "Por que o YAffiliate recomenda isso",
        "Suggested next actions": "Próximas ações sugeridas",
        "AI recommendations and expected ROI are estimates. They are not verified sales results or guaranteed returns.": "As recomendações de IA e o ROI esperado são estimativas, não resultados de vendas verificados nem retornos garantidos.",
        "2. Opportunity analysis": "2. Análise de oportunidade",
        "3. Your saved products": "3. Seus produtos salvos",
        "Example: Excel course": "Exemplo: Curso de Excel",
        "Unable to load saved products": "Não foi possível carregar os produtos salvos",
        "No products match your search.": "Nenhum produto corresponde à sua pesquisa.",
        "Not provided": "Não informado",
        "Not scored": "Sem pontuação",
        "Compare commissions and advertising costs": "Comparar comissões e custos de publicidade",
        "Add researched commission and CPC values for at least two products to generate a useful comparison.": "Informe comissões e valores de CPC pesquisados para pelo menos dois produtos para gerar uma comparação útil.",
        "Commission versus estimated CPC": "Comissão versus CPC estimado",
        "Estimated CPC (R$)": "CPC estimado (R$)",
        "Delete a saved product": "Excluir um produto salvo",
        "Deleting a product may also remove related records. This action cannot be undone.": "Excluir um produto também pode remover registros relacionados. Esta ação não pode ser desfeita.",
        "Select product to delete": "Selecione o produto para excluir",
        "I understand this deletion is permanent.": "Entendo que esta exclusão é permanente.",
        "Unable to delete product": "Não foi possível excluir o produto",
        "4. Prepare your next campaign": "4. Prepare sua próxima campanha",
        "Choose a product from your shortlist and verify its affiliate link and commission before creating a campaign.": "Escolha um produto da sua lista e confirme o link de afiliado e a comissão antes de criar uma campanha.",
        "Your saved products are available in Campaign Generator. Open that page to create your marketing assets.": "Seus produtos salvos estão disponíveis no Gerador de Campanhas. Abra essa página para criar seus materiais de marketing.",
        "Affiliate networks could not be loaded": "Não foi possível carregar as redes de afiliados",
        "Leave optional metrics blank when unknown. Enter 0 only when verified.": "Deixe as métricas opcionais em branco quando desconhecidas. Informe 0 apenas quando confirmado.",
        "Research coverage": "Cobertura da pesquisa",
        "Provisional score — insufficient research data.": "Pontuação provisória — dados de pesquisa insuficientes.",
        "No advertising budget can be recommended yet.": "Ainda não é possível recomendar um orçamento de publicidade.",
        "Commission values of zero are treated as unverified for scoring.": "Valores de comissão iguais a zero são considerados não verificados na pontuação.",
    },
}


def tr(text: str) -> str:
    """Translate customer-facing copy, never database identifiers."""
    language = get_language()
    local = PAGE_TRANSLATIONS.get(language, {})
    return local.get(text, ui(text))


def to_float(value, default=None):
    """Convert Supabase numeric values safely."""
    if value is None or value == "":
        return default

    try:
        result = float(value)
        return result if pd.notna(result) else default
    except (TypeError, ValueError):
        return default


def money(value):
    """Format BRL without treating missing data as a verified zero."""
    number = to_float(value)
    if number is None:
        return tr("Not provided")
    return f"R$ {number:,.2f}"


def show_latest_recommendation():
    """Display the recommendation generated after saving a product."""
    recommendation = st.session_state.get("latest_recommendation")

    if recommendation is None:
        return

    st.success(tr("Product saved successfully."))
    st.markdown(f"### {tr('Your latest product recommendation')}")

    product_id = st.session_state.get("latest_product_id")
    recommendation_id = st.session_state.get("latest_recommendation_id")

    if product_id is not None:
        st.caption(f"{tr('Product ID')}: {product_id}")

    if recommendation_id is not None:
        st.caption(f"{tr('Recommendation ID')}: {recommendation_id}")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        tr("Opportunity score"),
        f"{recommendation.opportunity_score:.1f}/100",
    )
    c2.metric(tr("Risk level"), recommendation.risk_level)
    c3.metric(tr("Expected ROI"), recommendation.expected_roi)

    coverage = st.session_state.get("latest_research_coverage")
    if coverage is not None:
        st.metric(tr("Research coverage"), f"{coverage:.0f}%")
        if coverage < 70:
            st.warning(tr("Provisional score — insufficient research data."))

    st.write(
        f"**{tr('Recommended channel')}:** "
        f"{recommendation.recommended_channel}"
    )
    st.write(
        f"**{tr('Difficulty')}:** {recommendation.difficulty}"
    )
    if recommendation.recommended_budget == 0 and (
        coverage is None or coverage < 70 or recommendation.risk_level == "Unknown"
    ):
        st.write(
            f"**{tr('Suggested test budget')}:** "
            f"{tr('No advertising budget can be recommended yet.')}"
        )
    else:
        st.write(
            f"**{tr('Suggested test budget')}:** "
            f"{money(recommendation.recommended_budget)}"
        )

    with st.expander(
        tr("Why YAffiliate recommends this"),
        expanded=True,
    ):
        for reason in recommendation.reasoning:
            st.write(f"• {reason}")

        st.markdown(f"**{tr('Suggested next actions')}**")

        for action in recommendation.next_actions:
            st.write(f"• {action}")

    st.caption(
        tr(
            "AI recommendations and expected ROI are estimates. "
            "They are not verified sales results or guaranteed returns."
        )
    )


def save_product(data):
    """Save product, metrics, history and recommendation."""
    repo = ProductRepository()

    # Missing research must remain None, not a fabricated zero.
    # The products table currently requires numeric commission fields.
    # Its default zero is therefore excluded from scoring unless verified later.
    factors = OpportunityFactors(
        commission_amount=(
            float(data["commission_amount"])
            if data["commission_amount"] > 0 else None
        ),
        commission_percent=(
            float(data["commission_percent"])
            if data["commission_percent"] > 0 else None
        ),
        search_volume=data["search_volume"],
        competition_score=data["competition_score"],
        estimated_cpc=data["estimated_cpc"],
        google_trend_score=data["google_trend_score"],
        refund_rate=data["refund_rate"],
        gravity_score=data["gravity_score"],
        epc=data["epc"],
    )

    score_service = OpportunityScoreService()
    recommendation_service = RecommendationService()
    score_details = score_service.calculate_details(factors)
    opportunity_score = score_details["opportunity_score"]

    product_id = repo.create_product(
        product_name=data["product_name"],
        network_id=data["network_id"],
        category=data["category"] or None,
        language_code=data["language_code"] or None,
        country_code=data["country_code"] or None,
        price=float(data["price"]),
        commission_amount=float(data["commission_amount"]),
        commission_percent=float(data["commission_percent"]),
        sales_page_url=data["sales_page_url"] or None,
        affiliate_url=data["affiliate_url"] or None,
        status=data["status"],
        notes=data["notes"] or None,
    )

    repo.add_product_metric(
        product_id=product_id,
        epc=data["epc"],
        gravity_score=data["gravity_score"],
        search_volume=data["search_volume"],
        competition_score=data["competition_score"],
        estimated_cpc=data["estimated_cpc"],
        google_trend_score=data["google_trend_score"],
        refund_rate=data["refund_rate"],
        opportunity_score=opportunity_score,
        data_source="Manual Streamlit entry",
    )

    OpportunityHistoryRepository().create_snapshot(
        product_id=product_id,
        opportunity_score=opportunity_score,
        epc=data["epc"],
        gravity_score=data["gravity_score"],
        search_volume=data["search_volume"],
        competition_score=data["competition_score"],
        estimated_cpc=data["estimated_cpc"],
        google_trend_score=data["google_trend_score"],
        refund_rate=data["refund_rate"],
    )

    recommendation = recommendation_service.generate(
        opportunity_score=opportunity_score,
        factors=factors,
    )

    recommendation_id = (
        RecommendationRepository().create_recommendation(
            product_id=product_id,
            recommendation=recommendation,
        )
    )

    st.session_state["latest_recommendation"] = recommendation
    st.session_state["latest_recommendation_id"] = recommendation_id
    st.session_state["latest_product_id"] = product_id
    st.session_state["latest_research_coverage"] = score_details["data_coverage"]


def render_add_product():
    """Show the translated product creation form."""

    st.markdown(f"### {tr('1. Add an affiliate product')}")
    st.caption(
        tr(
            "Start with the product details and commission. "
            "Advanced market metrics are optional for your research."
        )
    )

    try:
        networks = ProductRepository().list_affiliate_networks()
    except Exception as exc:
        st.warning(
            f"{tr('Affiliate networks could not be loaded')}: {exc}"
        )
        networks = []

    network_options = {
        int(network["NetworkID"]): str(network["NetworkName"])
        for network in networks
    }

    with st.form("add_product_form", clear_on_submit=True):
        st.markdown(f"#### {tr('Basic product information')}")

        product_name = st.text_input(
            tr("Product name *"),
            placeholder=tr("Example: English Online Course"),
        )

        c1, c2 = st.columns(2)

        network_id = c1.selectbox(
            tr("Affiliate network"),
            options=[None] + list(network_options),
            format_func=lambda value: (
                tr("Not selected")
                if value is None
                else network_options[value]
            ),
        )

        category = c2.text_input(
            tr("Category"),
            placeholder=tr("Example: Education"),
        )

        c3, c4, c5 = st.columns(3)

        country_code = c3.text_input(
            tr("Country code"),
            value="BR",
            max_chars=10,
        )

        language_code = c4.text_input(
            tr("Language code"),
            value="pt-BR",
            max_chars=20,
        )

        status = c5.selectbox(
            tr("Product status"),
            STATUS_OPTIONS,
            format_func=tr,
        )

        st.markdown(f"#### {tr('Product economics')}")

        c1, c2, c3 = st.columns(3)

        price = c1.number_input(
            tr("Product price (R$)"),
            min_value=0.0,
            step=10.0,
        )

        commission_amount = c2.number_input(
            tr("Commission per sale (R$)"),
            min_value=0.0,
            step=10.0,
        )

        commission_percent = c3.number_input(
            tr("Commission (%)"),
            min_value=0.0,
            max_value=100.0,
            step=1.0,
        )

        st.caption(tr("Commission values of zero are treated as unverified for scoring."))

        sales_page_url = st.text_input(
            tr("Product sales page URL"),
            placeholder="https://...",
        )

        affiliate_url = st.text_input(
            tr("Your affiliate tracking URL"),
            placeholder="https://...",
            help=tr(
                "This must be your own affiliate link from the network, "
                "not simply the product website."
            ),
        )

        with st.expander(tr("Advanced market metrics — optional")):
            st.caption(tr("Leave optional metrics blank when unknown. Enter 0 only when verified."))

            c1, c2, c3 = st.columns(3)

            epc = c1.number_input(
                tr("EPC (earnings per click)"),
                min_value=0.0,
                step=0.1,
                value=None,
            )

            gravity_score = c2.number_input(
                tr("Gravity score"),
                min_value=0.0,
                step=1.0,
                value=None,
            )

            search_volume = c3.number_input(
                tr("Monthly search volume"),
                min_value=0,
                step=100,
                value=None,
            )

            c4, c5, c6 = st.columns(3)

            competition_score = c4.number_input(
                tr("Competition score"),
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                value=None,
            )

            estimated_cpc = c5.number_input(
                tr("Estimated CPC (cost per click)"),
                min_value=0.0,
                step=0.1,
                value=None,
            )

            google_trend_score = c6.number_input(
                tr("Google Trends score"),
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                value=None,
            )

            refund_rate = st.number_input(
                tr("Refund rate (%)"),
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                value=None,
            )

        notes = st.text_area(
            tr("Research notes"),
            placeholder=tr(
                "Target audience, product benefits, "
                "competition, sources of market data..."
            ),
        )

        submitted = st.form_submit_button(
            tr("Save product and analyse opportunity"),
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    if not product_name.strip():
        st.error(tr("Please enter a product name."))
        return

    for label, url in [
        ("Sales page", sales_page_url),
        ("Affiliate link", affiliate_url),
    ]:
        if url.strip() and not url.strip().startswith(
            ("https://", "http://")
        ):
            st.error(
                f"{tr(label)} "
                f"{tr('must begin with https:// or http://')}"
            )
            return

    data = {
        "product_name": product_name.strip(),
        "network_id": network_id,
        "category": category.strip(),
        "country_code": country_code.strip(),
        "language_code": language_code.strip(),
        "status": status,
        "price": price,
        "commission_amount": commission_amount,
        "commission_percent": commission_percent,
        "sales_page_url": sales_page_url.strip(),
        "affiliate_url": affiliate_url.strip(),
        "epc": epc,
        "gravity_score": gravity_score,
        "search_volume": search_volume,
        "competition_score": competition_score,
        "estimated_cpc": estimated_cpc,
        "google_trend_score": google_trend_score,
        "refund_rate": refund_rate,
        "notes": notes.strip(),
    }

    try:
        save_product(data)
        st.rerun()
    except Exception as exc:
        st.error(tr("The product could not be saved completely."))
        st.exception(exc)


def render_saved_products():
    """Show saved Supabase products without changing stored data."""

    st.markdown(f"### {tr('3. Your saved products')}")

    c1, c2 = st.columns(2)

    search_text = c1.text_input(
        tr("Search by product name"),
        placeholder=tr("Example: Excel course"),
    )

    status_filter = c2.selectbox(
        tr("Filter by status"),
        ["All"] + STATUS_OPTIONS,
        format_func=tr,
    )

    try:
        products = ProductRepository().list_products(
            status=(
                None if status_filter == "All" else status_filter
            ),
            search=search_text.strip() or None,
        )
    except Exception as exc:
        st.error(
            f"{tr('Unable to load saved products')}: {exc}"
        )
        return

    if not products:
        st.info(tr("No products match your search."))
        return

    df = pd.DataFrame(products)

    numeric_columns = [
        "Price",
        "CommissionAmount",
        "CommissionPercent",
        "EPC",
        "GravityScore",
        "SearchVolume",
        "CompetitionScore",
        "EstimatedCPC",
        "GoogleTrendScore",
        "RefundRate",
        "OpportunityScore",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    c1, c2, c3 = st.columns(3)

    c1.metric(tr("Saved products"), len(df))

    commissions = df["CommissionAmount"].dropna()
    scores = df["OpportunityScore"].dropna()

    c2.metric(
        tr("Average commission"),
        money(commissions.mean())
        if not commissions.empty
        else tr("Not provided"),
    )

    c3.metric(
        tr("Best opportunity score"),
        f"{scores.max():.1f}/100"
        if not scores.empty
        else tr("Not scored"),
    )

    st.markdown(f"#### {tr('Product comparison')}")

    display_columns = [
        "ProductID",
        "ProductName",
        "NetworkName",
        "Category",
        "Status",
        "Price",
        "CommissionAmount",
        "CommissionPercent",
        "SearchVolume",
        "EstimatedCPC",
        "OpportunityScore",
    ]

    st.dataframe(
        df[[col for col in display_columns if col in df.columns]],
        hide_index=True,
        use_container_width=True,
    )

    chart_columns = [
        "EstimatedCPC",
        "CommissionAmount",
        "OpportunityScore",
    ]

    chart_df = df.dropna(subset=chart_columns).copy()

    # Zero placeholders are not evidence of genuine market data.
    chart_df = chart_df[
        (chart_df["EstimatedCPC"] > 0)
        & (chart_df["CommissionAmount"] > 0)
    ]

    with st.expander(
        tr("Compare commissions and advertising costs")
    ):
        if len(chart_df) < 2:
            st.info(
                tr(
                    "Add researched commission and CPC values for at "
                    "least two products to generate a useful comparison."
                )
            )
        else:
            chart = px.scatter(
                chart_df,
                x="EstimatedCPC",
                y="CommissionAmount",
                color="OpportunityScore",
                hover_name="ProductName",
                title=tr("Commission versus estimated CPC"),
                labels={
                    "EstimatedCPC": tr("Estimated CPC (R$)"),
                    "CommissionAmount": tr(
                        "Commission per sale (R$)"
                    ),
                    "OpportunityScore": tr("Opportunity score"),
                },
            )
            st.plotly_chart(
                chart,
                use_container_width=True,
            )

    st.download_button(
        tr("Export products as CSV"),
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="yaffiliate_products.csv",
        mime="text/csv",
    )

    with st.expander(tr("Delete a saved product")):
        st.warning(
            tr(
                "Deleting a product may also remove related records. "
                "This action cannot be undone."
            )
        )

        labels = {
            int(row["ProductID"]): (
                f"{row['ProductID']} — {row['ProductName']}"
            )
            for _, row in df.iterrows()
        }

        selected_id = st.selectbox(
            tr("Select product to delete"),
            options=list(labels),
            format_func=lambda value: labels[value],
        )

        confirmed = st.checkbox(
            tr("I understand this deletion is permanent.")
        )

        if st.button(
            tr("Delete selected product"),
            disabled=not confirmed,
        ):
            try:
                deleted = ProductRepository().delete_product(
                    int(selected_id)
                )

                if deleted:
                    st.success(tr("Product deleted."))
                    st.rerun()
                else:
                    st.warning(tr("Product was not found."))

            except Exception as exc:
                st.error(
                    f"{tr('Unable to delete product')}: {exc}"
                )


def render():
    """Main Product Research page."""

    page_header(
        tr("Research workspace"),
        tr("Find and compare affiliate opportunities."),
        tr(
            "Research products, analyse opportunities and "
            "prepare your affiliate marketing shortlist."
        ),
    )

    st.markdown(f"### {tr('Your research workflow')}")

    st.caption(
        tr(
            "Add product → Analyse opportunity → "
            "Review saved products → Prepare campaign"
        )
    )

    st.divider()
    render_add_product()

    if st.session_state.get("latest_recommendation") is not None:
        st.divider()
        st.markdown(f"### {tr('2. Opportunity analysis')}")
        show_latest_recommendation()

    st.divider()
    render_saved_products()

    st.divider()
    st.markdown(f"### {tr('4. Prepare your next campaign')}")

    st.info(
        tr(
            "Choose a product from your shortlist and verify its "
            "affiliate link and commission before creating a campaign."
        )
    )

    st.caption(
        tr(
            "Your saved products are available in Campaign Generator. "
            "Open that page to create your marketing assets."
        )
    )
