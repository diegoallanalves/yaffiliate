from dataclasses import dataclass,asdict
@dataclass(frozen=True)
class CampaignResult:
    product_name:str; budget:float; cpc:float; conversion_rate:float; commission:float; clicks:float; sales:float; revenue:float; profit:float; roas:float; roi:float; break_even_conversion_rate:float
    def as_record(self): return asdict(self)

def calculate_campaign(product_name,budget,cpc,conversion_rate_percent,commission):
    if budget<0: raise ValueError('Budget cannot be negative.')
    if cpc<=0: raise ValueError('CPC must be greater than zero.')
    if commission<=0: raise ValueError('Commission must be greater than zero.')
    if not 0<=conversion_rate_percent<=100: raise ValueError('Conversion rate must be between 0 and 100.')
    cr=conversion_rate_percent/100; clicks=budget/cpc; sales=clicks*cr; revenue=sales*commission; profit=revenue-budget
    return CampaignResult(product_name.strip() or 'Unnamed product',round(budget,2),round(cpc,2),cr,round(commission,2),round(clicks,2),round(sales,2),round(revenue,2),round(profit,2),round(revenue/budget if budget else 0,4),round(profit/budget if budget else 0,4),round(cpc/commission,6))
