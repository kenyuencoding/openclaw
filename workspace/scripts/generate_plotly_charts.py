import yfinance as yf
from pathlib import Path
import plotly.graph_objects as go

out_dir = Path(__file__).resolve().parent.parent / 'output' / 'charts'
out_dir.mkdir(parents=True, exist_ok=True)
TOP10 = ['NVDA','MSFT','AAPL','AMZN','GOOG','TSLA','META','JPM','UNH','MRVL']

for t in TOP10:
    tk = yf.Ticker(t)
    # daily
    hist_d = tk.history(period='30d', interval='1d')
    if not hist_d.empty:
        fig = go.Figure(data=[
            go.Candlestick(x=hist_d.index, open=hist_d['Open'], high=hist_d['High'], low=hist_d['Low'], close=hist_d['Close'],
                           increasing=dict(line=dict(color='#1f9d3a', width=2)), decreasing=dict(line=dict(color='#d62728', width=2)),
                           whiskerwidth=0.5),
            go.Bar(x=hist_d.index, y=hist_d['Volume'], marker_color='rgba(100,100,150,0.6)', yaxis='y2')
        ])
        fig.update_layout(xaxis_rangeslider_visible=False, template='plotly_white', height=480,
                          yaxis=dict(domain=[0.25,1]), yaxis2=dict(domain=[0,0.2], anchor='x'))
        png = out_dir / f'{t}_1d.png'
        html = out_dir / f'{t}_1d.html'
        fig.write_image(str(png), scale=2)
        fig.write_html(str(html), include_plotlyjs='cdn')
        print('WROTE',png, html)
    else:
        print('NO DAILY', t)
    # 1m
    hist_m = tk.history(period='1d', interval='1m')
    if not hist_m.empty:
        fig = go.Figure(data=[
            go.Candlestick(x=hist_m.index, open=hist_m['Open'], high=hist_m['High'], low=hist_m['Low'], close=hist_m['Close'],
                           increasing=dict(line=dict(color='#1f9d3a', width=1.5)), decreasing=dict(line=dict(color='#d62728', width=1.5)),
                           whiskerwidth=0.3),
            go.Bar(x=hist_m.index, y=hist_m['Volume'], marker_color='rgba(100,100,150,0.6)', yaxis='y2')
        ])
        fig.update_layout(xaxis_rangeslider_visible=False, template='plotly_white', height=480,
                          yaxis=dict(domain=[0.25,1]), yaxis2=dict(domain=[0,0.2], anchor='x'))
        png = out_dir / f'{t}_1m.png'
        html = out_dir / f'{t}_1m.html'
        fig.write_image(str(png), scale=2)
        fig.write_html(str(html), include_plotlyjs='cdn')
        print('WROTE',png, html)
    else:
        print('NO 1M', t)

print('done')
