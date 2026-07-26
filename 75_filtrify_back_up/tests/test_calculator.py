import pytest

from src.features.calculator import calculate_campaign


def test_profitable_campaign():
    result = calculate_campaign(
        product_name="Test",
        budget=500,
        cpc=1,
        conversion_rate_percent=2,
        commission=100,
    )
    assert result.clicks == 500
    assert result.sales == 10
    assert result.revenue == 1000
    assert result.profit == 500
    assert result.roas == 2
    assert result.roi == 1


def test_invalid_cpc():
    with pytest.raises(ValueError):
        calculate_campaign("Test", 500, 0, 2, 100)
