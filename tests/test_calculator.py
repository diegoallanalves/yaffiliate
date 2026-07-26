import pytest
from app.models.calculator import calculate_campaign
def test_profitable_campaign():
 r=calculate_campaign("Test",500,1,2,100); assert r.clicks==500 and r.sales==10 and r.revenue==1000 and r.profit==500 and r.roas==2 and r.roi==1
def test_invalid_cpc():
 with pytest.raises(ValueError):calculate_campaign("Test",500,0,2,100)
