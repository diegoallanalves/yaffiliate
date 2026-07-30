from pathlib import Path

from app.collectors.hotmart_collector import HotmartCollector
from app.services.business_consultant_service import (
    BusinessConsultantService,
)
from app.services.comparison_service import ComparisonService
from app.services.pdf_report_service import PdfReportService
from app.services.product_analysis_service import (
    ProductAnalysisService,
)
from app.services.report_builder_service import (
    ReportBuilderService,
)


def main() -> None:
    collector = HotmartCollector()
    comparison_service = ComparisonService()
    analysis_service = ProductAnalysisService()
    consultant_service = BusinessConsultantService()
    report_builder = ReportBuilderService()
    pdf_service = PdfReportService()

    products = collector.search_products(
        keyword="Excel",
        country_code="BR",
        language_code="pt-BR",
        limit=10,
    )

    if not products:
        print("No products were found.")
        return

    comparison = comparison_service.compare(products)

    selected_product = products[0]

    selected_comparison = next(
        (
            item
            for item in comparison.products
            if (
                item.product.product_name
                == selected_product.product_name
            )
        ),
        None,
    )

    analysis = analysis_service.analyse(
        product=selected_product,
        comparison=selected_comparison,
    )

    consultant = consultant_service.generate(
        product=selected_product,
        analysis=analysis,
    )

    report = report_builder.build(
        product=selected_product,
        analysis=analysis,
        consultant=consultant,
        generated_for="Diego Alves",
    )

    output_directory = Path("reports")
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_directory
        / "filtrify_excel_masterclass_report.pdf"
    )

    pdf_service.save(
        report=report,
        file_path=str(output_path),
    )

    print("PDF generated successfully:")
    print(output_path.resolve())


if __name__ == "__main__":
    main()