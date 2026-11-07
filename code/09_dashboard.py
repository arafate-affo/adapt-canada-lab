"""
09_dashboard.py
Build a self-contained interactive dashboard (docs/dashboard.html) for GitHub Pages from the
processed files. Data are embedded as JSON; Plotly is loaded from its CDN. The page has:
  1. Adaptation index by province, with a quarter selector
  2. Index series Q2 2025 - Q3 2026 for Canada and the provinces (click legend to toggle)
  3. Industry pillars (Canada, latest quarter)
  4. AI adoption by sector, US vs Canada
  5. Provincial exports to the US, change Jan-Sep 2026 vs 2025
  6. Tariff-response awards by province
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
T = ROOT / "output" / "tables"
OUT = ROOT / "docs" / "dashboard.html"

NAME = {"CA": "Canada", "NL": "Newfoundland and Labrador", "PE": "Prince Edward Island", "NS": "Nova Scotia",
        "NB": "New Brunswick", "QC": "Quebec", "ON": "Ontario", "MB": "Manitoba", "SK": "Saskatchewan",
        "AB": "Alberta", "BC": "British Columbia", "YT": "Yukon", "NT": "Northwest Territories", "NU": "Nunavut"}
PROVS = ["BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL"]

idx = pd.read_csv(P / "adaptation_index_provinces.csv")
idx = idx[idx.geo_code.isin(PROVS + ["CA"])]
quarters = sorted(idx.quarter.unique())
cols = ["P1_core", "P2_supply_reconfiguration", "P3_technology_investment", "P4_financial_buffers",
        "P5_digital_readiness", "D_retrenchment", "N_passivity", "exposure_neg_impact", "exposure_us_sales", "index_raw"]
by_q = {q: idx[idx.quarter == q].set_index("geo_code").reindex(PROVS)[cols].round(1).reset_index()
        .rename(columns={"geo_code": "code"}).assign(name=lambda d: d.code.map(NAME)).to_dict("records") for q in quarters}
series = {c: idx[idx.geo_code == c].set_index("quarter").index_raw.reindex(quarters).round(2).tolist() for c in ["CA"] + PROVS}
horizon = {q: idx[idx.quarter == q].horizon.iloc[0] for q in quarters}

ind = pd.read_csv(P / "adaptation_index_industries_canada.csv")
latest = quarters[-1]
i3 = ind[(ind.quarter == latest) & (ind.naics != "ALL")].copy()
i3["label"] = (i3.breakdown.str.replace(r" \[.*\]$", "", regex=True)
               .str.replace("Administrative and support, waste management and remediation services", "Administrative and support services")
               .str.replace("Mining, quarrying, and oil and gas extraction", "Mining, oil and gas"))
i3 = i3.sort_values("index_raw")
industry = {"labels": i3.label.tolist(),
            "P1": i3.P1_core.fillna(0).round(1).tolist(), "P2": i3.P2_supply_reconfiguration.fillna(0).round(1).tolist(),
            "P3": i3.P3_technology_investment.fillna(0).round(1).tolist(), "P4": i3.P4_financial_buffers.fillna(0).round(1).tolist(),
            "D": i3.D_retrenchment.fillna(0).round(1).tolist(), "exposure": i3.exposure_neg_impact.round(1).tolist()}

ai = pd.read_csv(T / "ai_adoption_us_vs_canada_by_sector.csv").dropna(subset=["us_ai_use_2026_avg", "ca_ai_use_last12m_Q2"])
ai = ai.sort_values("us_ai_use_2026_avg")
ai["label"] = ai.label.str.replace("Administrative and support, waste management and remediation services", "Administrative and support services")
ai_d = {"labels": ai.label.tolist(), "us": ai.us_ai_use_2026_avg.tolist(), "ca": ai.ca_ai_use_last12m_Q2.tolist(),
        "ca_plan": ai.ca_ai_planned_next12m_Q3.tolist()}

trd = pd.read_csv(P / "trade_province_exposure.csv")
trd = trd[trd.napcs == "Total of all merchandise"]
code_of = {v: k for k, v in NAME.items()}
trd["code"] = trd.geo.map(code_of)
trd = trd[trd.code.isin(PROVS)].sort_values("chg_us_exports_ytd_2026_vs_2025_pct")
trade = {"labels": trd.geo.tolist(), "chg26": trd.chg_us_exports_ytd_2026_vs_2025_pct.round(1).tolist(),
         "chg25": trd.chg_us_exports_ytd_2025_vs_2024_pct.round(1).tolist(), "share24": trd.us_share_exports_2024.round(1).tolist()}

prog = pd.read_csv(P / "programs_tariff_by_province.csv")
prog = prog[prog.prov_code.isin(PROVS)].sort_values("value_mcad")
programs = {"labels": [NAME[c] for c in prog.prov_code], "value": prog.value_mcad.round(2).tolist(), "n": prog.n_awards.astype(int).tolist()}

DATA = json.dumps({"quarters": quarters, "horizon": horizon, "by_q": by_q, "series": series, "names": NAME,
                   "industry": industry, "ai": ai_d, "trade": trade, "programs": programs, "latest": latest})

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ADAPT Canada dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root{--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--grid:#e6e5e1;--b:#2a78d6;--o:#eb6834;--a:#1baf7a;--y:#eda100}
body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
header{padding:20px 16px 8px;max-width:1100px;margin:0 auto}
h1{font-size:1.4rem;margin:0 0 4px}h2{font-size:1.05rem;margin:18px 0 6px}
p.sub{color:var(--ink2);margin:0;font-size:.9rem}
main{max-width:1100px;margin:0 auto;padding:0 16px 40px;display:grid;grid-template-columns:1fr;gap:18px}
@media(min-width:900px){main{grid-template-columns:1fr 1fr}.wide{grid-column:1/3}}
.card{background:#fff;border:1px solid var(--grid);border-radius:8px;padding:10px 12px}
.card .note{font-size:.78rem;color:var(--ink2);margin:4px 0 0}
select{font:inherit;padding:3px 6px;border:1px solid var(--grid);border-radius:6px;background:#fff}
table{border-collapse:collapse;font-size:.8rem;width:100%}th,td{border-bottom:1px solid var(--grid);padding:3px 6px;text-align:right}
th:first-child,td:first-child{text-align:left}
footer{max-width:1100px;margin:0 auto;padding:0 16px 30px;font-size:.8rem;color:var(--ink2)}
</style></head><body>
<header><h1>Business adaptation to the 2025-2026 tariff shock: Canada (prototype dashboard)</h1>
<p class="sub">Built from Statistics Canada (CSBC, trade), Elections Canada, open.canada.ca and the US Census BTOS. Prototype index, see methodology in the repository docs.</p></header>
<main>
<div class="card"><h2>1. Adaptation index by province <select id="qsel"></select></h2><div id="p1" style="height:420px"></div><p class="note" id="p1note"></p></div>
<div class="card"><h2>2. Index over the tariff episode (click a province in the legend)</h2><div id="p2" style="height:420px"></div><p class="note">Shaded quarters measure actions taken; the others, actions planned over the next 12 months.</p></div>
<div class="card wide"><h2>3. Planned responses by industry, Canada, latest quarter</h2><div id="p3" style="height:520px"></div><p class="note">Stacked shares of businesses planning each action (next 12 months). Hover for the share reporting a negative tariff impact.</p></div>
<div class="card"><h2>4. Business AI adoption by sector: US vs Canada</h2><div id="p4" style="height:520px"></div><p class="note">US: BTOS 2026 biweekly average, AI used in the last two weeks. Canada: CSBC Q2 2026, AI used in the last 12 months. Definitions differ; indicative.</p></div>
<div class="card"><h2>5. Exports to the United States by province</h2><div id="p5" style="height:520px"></div><p class="note">Domestic exports, customs basis, January-September of each year (StatCan 12-10-0175-01). Hover for the US share of exports in 2024.</p></div>
<div class="card wide"><h2>6. Federal tariff-response awards disclosed by province (lower bound)</h2><div id="p6" style="height:360px"></div><p class="note">Agreements mentioning tariffs in the proactive disclosure of grants and contributions (mostly the Regional Tariff Response Initiative); several agencies have not yet disclosed 2026 awards.</p></div>
<div class="card wide"><h2>Data table, selected quarter</h2><div id="tbl"></div></div>
</main>
<footer>Prototype prepared by Arafate Affo (November 2026) as a starter kit for the Laboratory on adaptation to economic shocks, Maison des affaires publiques et internationales, Université de Montréal. All shares are percentages of businesses; territories are excluded from the charts because of suppression.</footer>
<script>
const D = __DATA__;
const L = {paper_bgcolor:'#fcfcfb',plot_bgcolor:'#fcfcfb',font:{color:'#0b0b0b',size:12},margin:{l:150,r:20,t:10,b:40},
  xaxis:{gridcolor:'#e6e5e1',zeroline:false},yaxis:{gridcolor:'#e6e5e1'},hoverlabel:{bgcolor:'#fff'},legend:{orientation:'h',y:-0.15}};
const sel=document.getElementById('qsel');
D.quarters.forEach(q=>{const o=document.createElement('option');o.value=q;o.textContent=q+' ('+D.horizon[q]+')';sel.appendChild(o)});
sel.value=D.latest;
function p1(){const q=sel.value;const r=D.by_q[q].slice().sort((a,b)=>a.index_raw-b.index_raw);
 Plotly.react('p1',[{type:'bar',orientation:'h',x:r.map(d=>d.index_raw),y:r.map(d=>d.name),marker:{color:'#2a78d6'},
   customdata:r.map(d=>[d.P1_core,d.P2_supply_reconfiguration,d.P3_technology_investment,d.P4_financial_buffers,d.D_retrenchment,d.exposure_neg_impact]),
   hovertemplate:'<b>%{y}</b><br>Index: %{x}<br>Alt. customers: %{customdata[0]}%<br>Supply reconfiguration: %{customdata[1]}%<br>Technology: %{customdata[2]}%<br>Financial buffers: %{customdata[3]}%<br>Retrenchment: %{customdata[4]}%<br>Negative tariff impact: %{customdata[5]}%<extra></extra>'}],
   Object.assign({},L,{xaxis:{title:'Core adaptation index (mean % of businesses per pillar)',gridcolor:'#e6e5e1'}}),{responsive:true,displayModeBar:false});
 document.getElementById('p1note').textContent='Quarter '+q+': '+D.horizon[q]+'.';
 const cols=['name','index_raw','P1_core','P2_supply_reconfiguration','P3_technology_investment','P4_financial_buffers','P5_digital_readiness','D_retrenchment','N_passivity','exposure_neg_impact','exposure_us_sales'];
 const hdr=['Province','Index','Alt. customers','Supply reconfig.','Technology','Financial buffers','Digital readiness','Retrenchment','No action','Neg. impact','Sells to US'];
 let h='<table><tr>'+hdr.map(x=>'<th>'+x+'</th>').join('')+'</tr>';
 D.by_q[q].slice().sort((a,b)=>b.index_raw-a.index_raw).forEach(d=>{h+='<tr>'+cols.map(c=>'<td>'+(d[c]==null?'':d[c])+'</td>').join('')+'</tr>'});
 document.getElementById('tbl').innerHTML=h+'</table>';}
sel.onchange=p1;p1();
const pal={CA:'#0b0b0b',ON:'#2a78d6',QC:'#eb6834',AB:'#1baf7a',BC:'#eda100'};
const tr2=Object.keys(D.series).map(c=>({type:'scatter',mode:'lines+markers',name:D.names[c],x:D.quarters,y:D.series[c],
  line:{width:c==='CA'?3:1.8,color:pal[c]||'#9a9a94'},visible:(c in pal)?true:'legendonly',hovertemplate:'%{x}: %{y}<extra>'+D.names[c]+'</extra>'}));
const shapes=D.quarters.map((q,i)=>D.horizon[q].includes('taken')?{type:'rect',xref:'x',yref:'paper',x0:i-0.5,x1:i+0.5,y0:0,y1:1,fillcolor:'#e6e5e1',opacity:.5,line:{width:0}}:null).filter(Boolean);
Plotly.newPlot('p2',tr2,Object.assign({},L,{margin:{l:50,r:20,t:10,b:70},shapes,yaxis:{title:'Core adaptation index',rangemode:'tozero',gridcolor:'#e6e5e1'}}),{responsive:true,displayModeBar:false});
const I=D.industry;const mk=(k,n,c)=>({type:'bar',orientation:'h',name:n,x:I[k],y:I.labels,marker:{color:c,line:{color:'#fcfcfb',width:1}},customdata:I.exposure,hovertemplate:'<b>%{y}</b><br>'+n+': %{x}%<br>Negative tariff impact: %{customdata}%<extra></extra>'});
Plotly.newPlot('p3',[mk('P1','Alternative customers outside the US','#2a78d6'),mk('P2','Alternative suppliers / domestic sourcing','#eb6834'),mk('P3','Technology investment','#1baf7a'),mk('P4','Financial tools, inventory, hiring','#eda100')],
  Object.assign({},L,{barmode:'stack',margin:{l:260,r:20,t:10,b:60},xaxis:{title:'% of businesses planning each action',gridcolor:'#e6e5e1'}}),{responsive:true,displayModeBar:false});
const A=D.ai;
Plotly.newPlot('p4',[{type:'scatter',mode:'markers',name:'United States (BTOS 2026)',x:A.us,y:A.labels,marker:{color:'#2a78d6',size:10},hovertemplate:'%{y}<br>US: %{x}%<extra></extra>'},
  {type:'scatter',mode:'markers',name:'Canada (CSBC Q2 2026)',x:A.ca,y:A.labels,marker:{color:'#eb6834',size:10},hovertemplate:'%{y}<br>Canada: %{x}%<extra></extra>'},
  {type:'scatter',mode:'markers',name:'Canada, planned next 12 months (Q3 2026)',x:A.ca_plan,y:A.labels,marker:{color:'#eb6834',size:9,symbol:'circle-open'},hovertemplate:'%{y}<br>Canada planned: %{x}%<extra></extra>'}],
  Object.assign({},L,{margin:{l:250,r:20,t:10,b:70},xaxis:{title:'% of businesses using AI',gridcolor:'#e6e5e1'}}),{responsive:true,displayModeBar:false});
const Tr=D.trade;
Plotly.newPlot('p5',[{type:'bar',orientation:'h',name:'Jan-Sep 2026 vs 2025',x:Tr.chg26,y:Tr.labels,marker:{color:Tr.chg26.map(v=>v>=0?'#2a78d6':'#eb6834')},customdata:Tr.share24,hovertemplate:'%{y}<br>2026 vs 2025: %{x}%<br>US share of exports 2024: %{customdata}%<extra></extra>'},
  {type:'scatter',mode:'markers',name:'Jan-Sep 2025 vs 2024',x:Tr.chg25,y:Tr.labels,marker:{color:'#0b0b0b',size:8,symbol:'diamond'},hovertemplate:'%{y}<br>2025 vs 2024: %{x}%<extra></extra>'}],
  Object.assign({},L,{margin:{l:170,r:20,t:10,b:70},xaxis:{title:'Change in domestic exports to the US (%)',gridcolor:'#e6e5e1',zeroline:true,zerolinecolor:'#52514e'}}),{responsive:true,displayModeBar:false});
const Pg=D.programs;
Plotly.newPlot('p6',[{type:'bar',orientation:'h',x:Pg.value,y:Pg.labels,marker:{color:'#1baf7a'},customdata:Pg.n,hovertemplate:'%{y}<br>$%{x} M in %{customdata} agreements<extra></extra>'}],
  Object.assign({},L,{margin:{l:170,r:20,t:10,b:50},xaxis:{title:'Disclosed tariff-response agreements, $ million',gridcolor:'#e6e5e1'}}),{responsive:true,displayModeBar:false});
</script></body></html>
"""
OUT.write_text(HTML.replace("__DATA__", DATA), encoding="utf-8")
print("dashboard written:", OUT, f"({OUT.stat().st_size // 1024} KB)")
