import pandas as pd

def add_opportunity_score(df):
    if df.empty:return df
    r=df.copy()
    cols=['commission','commission_percent','cpc','search_volume','competition','refund_rate']
    for c in cols:r[c]=pd.to_numeric(r[c],errors='coerce').fillna(0)
    def n(s):
        return pd.Series([.5]*len(s),index=s.index) if s.max()==s.min() else (s-s.min())/(s.max()-s.min())
    r['opportunity_score']=(n(r.commission)*30+n(r.commission_percent)*15+n(r.search_volume)*25+(1-n(r.cpc))*15+(1-n(r.competition))*10+(1-n(r.refund_rate))*5).round(1)
    return r
