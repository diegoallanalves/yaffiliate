from pprint import pprint

from app.services.portfolio_service import PortfolioService


def main() -> None:
    service = PortfolioService()

    summary = service.get_portfolio_summary()

    pprint(summary)


if __name__ == "__main__":
    main()