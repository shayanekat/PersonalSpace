import pandas as pd
import plotly.express as px
import datetime

# initalisation
df = pd.read_csv('apps/nidification/data.csv')
current_day = pd.Timestamp.now().normalize()
current_year = datetime.datetime.now().year

# convertir les dates en format datetime
def parse_date(date_str):
    jour, mois = map(int, date_str.split('/'))
    return pd.Timestamp(year=current_year, month=mois, day=jour)

for col in df.columns:
    if col != 'espece':
        df[col] = df[col].apply(parse_date)
        

# construction des segments
segments = []

phases = [  # (étape début, étape fin, nom de la phase)
    ("parade", "construction nid", "parade"),
    ("construction nid", "ponte", "construction nid"),
    ("ponte", "eclosion", "incubation"),
    ("eclosion", "envol", "élevage")
]

for _, row in df.iterrows():
    for start_col, end_col, label in phases:
        segments.append({
            'espece': row['espece'],
            'phase': label,
            'start': row[start_col],
            'end': row[end_col]
        })

gantt = pd.DataFrame(segments)

# création du graphique
fig = px.timeline(gantt, x_start="start", x_end="end", y="espece", color="phase", title="Nidification par espèce", template="plotly_dark")
fig.update_yaxes(autorange="reversed")  # standard gantt
fig.add_vline(x=current_day, line_width=2, line_dash="dash", line_color="red")
fig.add_annotation(x=current_day, y=1, xref='x', yref="paper", text="Aujourd'hui", showarrow=False, yanchor="bottom", font=dict(color="red"))

fig.show()
