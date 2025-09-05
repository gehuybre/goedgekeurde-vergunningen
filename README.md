# Goedgekeurde Bouwvergunningen België - Data Analyse

Dit project analyseert de bouwvergunningsdata van België per gewest, gebaseerd op open data van Statbel.

## 📊 Projectomschrijving

Het project bevat interactieve analyses van bouwvergunningen in België, gefocust op:
- **Nieuwbouw woningen totaal** per gewest
- **Renovatie gebouwen wonen** per gewest  
- **Aandeel flats** (appartementen percentage) per gewest

Voor elk gewest worden lijngrafieken gemaakt met:
- Maanddata in stippellijn (korte termijn evolutie)
- 12-maands gemiddelde in volle lijn (trend)

## 🗂️ Projectstructuur

```
goedgekeurde_vergunningen/
├── data/                    # Data bestanden
│   └── building_permits.csv # Verwerkte bouwvergunningsdata
├── notebooks/               # Jupyter notebooks voor analyse
│   ├── download.ipynb      # Data download en preprocessing
│   └── analyse.ipynb       # Hoofdanalyse met visualisaties
├── src/                    # Python broncode
│   ├── config.py          # Nederlandse kolomnamen en configuratie
│   └── data_utils.py      # Data utility functies
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Project configuratie
└── README.md              # Dit bestand
```

## 🚀 Aan de slag

### 1. Omgeving opzetten
```bash
# Virtual environment activeren
source .venv/bin/activate

# Dependencies installeren (indien nodig)
pip install -r requirements.txt
```

### 2. Data downloaden
```bash
# Start Jupyter notebook
jupyter notebook

# Open notebooks/download.ipynb en voer uit om data te downloaden
```

### 3. Analyse uitvoeren
```bash
# Open notebooks/analyse.ipynb voor de hoofdanalyse
```

## 📈 Analyses

### Gewestelijke Analyse
Het project analyseert drie gewesten:
- **Vlaams Gewest**
- **Waals Gewest**  
- **Brussels Hoofdstedelijk Gewest**

### Visualisaties
- Interactieve Plotly grafieken
- Professionele HTML tabellen met scrollfunctie
- Export naar CSV voor verdere analyse

### Output Bestanden
- `analyse_nieuwbouw_woningen_per_gewest.csv`
- `analyse_renovatie_gebouwen_per_gewest.csv`  
- `analyse_aandeel_flats_per_gewest.csv`

## 🛠️ Technologieën

- **Python 3.11+**
- **Pandas**: Data manipulatie en analyse
- **Plotly**: Interactieve visualisaties
- **Jupyter**: Notebook omgeving
- **Requests**: Data download

## 📊 Databron

Data afkomstig van **Statbel** (Belgisch Statistiekbureau):
- Bestand: `TF_BUILDING_PERMITS.zip`
- Bron: https://statbel.fgov.be/sites/default/files/files/opendata/Building%20permits/
- Periode: 1996-2025
- Records: ~237,604 rijen

## 🎯 Features

- ✅ Automatische data download en preprocessing
- ✅ Nederlandse kolomnamen en beschrijvingen
- ✅ Interactieve Plotly visualisaties
- ✅ HTML tabellen met professionele styling
- ✅ CSV export voor alle analyses
- ✅ Vlaamse hoofdletterregels toegepast

## 📋 Licentie

Dit project is open source en vrij te gebruiken voor educatieve en onderzoeksdoeleinden.

## 🤝 Bijdragen

Bijdragen zijn welkom! Open een issue of pull request voor verbeteringen.
