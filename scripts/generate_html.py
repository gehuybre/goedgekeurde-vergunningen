#!/usr/bin/env python3
"""
Generate HTML Dashboard for Bouwvergunningen België

This script generates a complete HTML dashboard with interactive charts,
downloadable CSV files, and iframe embed codes.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
import json
import sys
from datetime import datetime
import base64

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from config import DUTCH_COLUMN_NAMES, COLUMN_DESCRIPTIONS

# Set plotly template
pio.templates.default = "plotly_white"

class DashboardGenerator:
    def __init__(self):
        self.data_dir = Path("data")
        self.docs_dir = Path("docs")
        self.charts_dir = self.docs_dir / "charts"
        self.tables_dir = self.docs_dir / "tables"
        self.csv_dir = self.docs_dir / "csv"
        
        # Create directories
        for dir_path in [self.docs_dir, self.charts_dir, self.tables_dir, self.csv_dir]:
            dir_path.mkdir(exist_ok=True, parents=True)
        
        self.gewest_colors = {
            'Vlaams Gewest': '#1f77b4',
            'Waals Gewest': '#ff7f0e', 
            'Brussels Hoofdstedelijk Gewest': '#2ca02c'
        }
        
    def load_and_prepare_data(self):
        """Load and prepare the building permits data"""
        print("📊 Loading and preparing data...")
        
        # Load the data
        df = pd.read_csv(self.data_dir / "building_permits.csv")
        
        # Filter for gewest level and quarterly data
        df_gewest = df[
            (df['geografisch_niveau'] == 2) & 
            (df['periode'].isin([1, 2, 3, 4]))
        ].copy()
        
        # Create date column
        df_gewest['datum'] = pd.to_datetime(
            df_gewest['jaar'].astype(str) + '-' + 
            ((df_gewest['periode'] * 3) - 2).astype(str).str.zfill(2) + '-01'
        )
        
        # Calculate aandeel flats
        df_gewest['aandeel_flats'] = (
            df_gewest['nieuwbouw_appartementen'] / 
            df_gewest['nieuwbouw_woningen_totaal'] * 100
        ).round(1)
        
        # Fill NaN with 0
        numeric_cols = ['nieuwbouw_woningen_totaal', 'renovatie_gebouwen_wonen', 'aandeel_flats']
        df_gewest[numeric_cols] = df_gewest[numeric_cols].fillna(0)
        
        # Transform gewest names to proper capitalization
        gewest_mapping = {
            'VLAAMS GEWEST': 'Vlaams Gewest',
            'WAALS GEWEST': 'Waals Gewest', 
            'BRUSSELS HOOFDSTEDELIJK GEWEST': 'Brussels Hoofdstedelijk Gewest'
        }
        df_gewest['gemeente_naam_nl'] = df_gewest['gemeente_naam_nl'].map(gewest_mapping)
        
        self.df = df
        self.df_gewest = df_gewest
        self.gewesten = df_gewest['gemeente_naam_nl'].unique()
        
        print(f"✅ Data loaded: {df.shape[0]:,} rows, {len(self.gewesten)} gewesten")
        
    def create_trend_chart(self, data, metric, title, y_label, filename):
        """Create trend chart with monthly data and moving average"""
        fig = go.Figure()
        
        for gewest in self.gewesten:
            gewest_data = data[data['gemeente_naam_nl'] == gewest].sort_values('datum')
            
            if len(gewest_data) == 0:
                continue
                
            # Calculate 4-quarter moving average
            gewest_data = gewest_data.copy()
            gewest_data[f'{metric}_12m'] = gewest_data[metric].rolling(window=4, min_periods=1).mean()
            
            color = self.gewest_colors[gewest]
            
            # Monthly data (dotted line)
            fig.add_trace(go.Scatter(
                x=gewest_data['datum'],
                y=gewest_data[metric],
                mode='lines+markers',
                name=f'{gewest} (maand)',
                line=dict(color=color, dash='dot', width=2),
                marker=dict(size=4),
                opacity=0.7,
                showlegend=True
            ))
            
            # Moving average (solid line)
            fig.add_trace(go.Scatter(
                x=gewest_data['datum'],
                y=gewest_data[f'{metric}_12m'],
                mode='lines',
                name=f'{gewest} (trend)',
                line=dict(color=color, width=3),
                showlegend=True
            ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=18, family="Arial, sans-serif"),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title=dict(text="Datum", font=dict(size=14)),
                tickfont=dict(size=12),
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            yaxis=dict(
                title=dict(text=y_label, font=dict(size=14)),
                tickfont=dict(size=12),
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(size=12)
            ),
            height=650,
            margin=dict(t=80, b=150, l=80, r=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12)
        )
        
        # Save as HTML
        chart_html = fig.to_html(include_plotlyjs='cdn', div_id=f"chart-{filename}")
        (self.charts_dir / f"{filename}.html").write_text(chart_html, encoding='utf-8')
        
        # Save as standalone HTML for iframe
        standalone_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ margin: 0; padding: 10px; font-family: Arial, sans-serif; }}
        .chart-container {{ width: 100%; height: 100vh; }}
    </style>
</head>
<body>
    <div class="chart-container">
        {fig.to_html(include_plotlyjs=False, div_id=f"chart-{filename}")}
    </div>
</body>
</html>
"""
        (self.charts_dir / f"{filename}_standalone.html").write_text(standalone_html, encoding='utf-8')
        
        return fig
        
    def create_data_table(self, data, filename, title):
        """Create HTML table with download and embed options"""
        # Save CSV
        csv_path = self.csv_dir / f"{filename}.csv"
        data.to_csv(csv_path, index=False)
        
        # Create HTML table
        table_html = data.tail(30).to_html(
            escape=False, 
            index=False, 
            table_id=f"table-{filename}",
            classes="data-table"
        )
        
        # Create standalone table HTML for iframe
        standalone_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <link rel="stylesheet" href="../css/dashboard.css">
    <style>
        body {{ margin: 0; padding: 10px; }}
        .table-scroll {{ max-height: none; border: none; }}
    </style>
</head>
<body>
    <div class="table-container">
        <div class="table-scroll">
            {table_html}
        </div>
    </div>
</body>
</html>
"""
        
        table_path = self.tables_dir / f"{filename}.html"
        table_path.write_text(standalone_html, encoding='utf-8')
        
        return table_html, len(data)
        
    def generate_analyses(self):
        """Generate all analyses and save files"""
        print("📈 Generating analyses...")
        
        analyses = []
        
        # Analysis 1: Nieuwbouw woningen totaal
        print("  → Nieuwbouw woningen totaal")
        fig1 = self.create_trend_chart(
            self.df_gewest,
            'nieuwbouw_woningen_totaal',
            'Nieuwbouw woningen totaal per gewest',
            'Aantal woningen',
            'nieuwbouw_woningen'
        )
        
        # Create chart data for table
        chart1_data = []
        for gewest in self.gewesten:
            gewest_data = self.df_gewest[self.df_gewest['gemeente_naam_nl'] == gewest].copy()
            if len(gewest_data) > 0:
                gewest_data = gewest_data.sort_values('datum')
                gewest_data['nieuwbouw_woningen_12m'] = gewest_data['nieuwbouw_woningen_totaal'].rolling(window=4, min_periods=1).mean()
                
                for _, row in gewest_data.iterrows():
                    chart1_data.append({
                        'datum': row['datum'].strftime('%Y-%m-%d'),
                        'gewest': row['gemeente_naam_nl'],
                        'jaar': row['jaar'],
                        'periode': row['periode'],
                        'nieuwbouw_woningen_maand': row['nieuwbouw_woningen_totaal'],
                        'nieuwbouw_woningen_trend': round(row['nieuwbouw_woningen_12m'], 1)
                    })
        
        chart1_df = pd.DataFrame(chart1_data)
        table1_html, table1_rows = self.create_data_table(
            chart1_df, 
            'nieuwbouw_woningen_data',
            'Nieuwbouw woningen data'
        )
        
        analyses.append({
            'id': 'nieuwbouw_woningen',
            'title': 'Nieuwbouw woningen totaal per gewest',
            'description': 'Evolutie van het aantal nieuwbouw woningen per gewest met maandelijkse data en trend.',
            'chart_file': 'nieuwbouw_woningen',
            'table_html': table1_html,
            'table_file': 'nieuwbouw_woningen_data',
            'csv_file': 'nieuwbouw_woningen_data.csv',
            'data_rows': table1_rows
        })
        
        # Analysis 2: Renovatie gebouwen wonen
        print("  → Renovatie gebouwen wonen")
        fig2 = self.create_trend_chart(
            self.df_gewest,
            'renovatie_gebouwen_wonen',
            'Renovatie gebouwen wonen per gewest',
            'Aantal gebouwen',
            'renovatie_gebouwen'
        )
        
        chart2_data = []
        for gewest in self.gewesten:
            gewest_data = self.df_gewest[self.df_gewest['gemeente_naam_nl'] == gewest].copy()
            if len(gewest_data) > 0:
                gewest_data = gewest_data.sort_values('datum')
                gewest_data['renovatie_gebouwen_12m'] = gewest_data['renovatie_gebouwen_wonen'].rolling(window=4, min_periods=1).mean()
                
                for _, row in gewest_data.iterrows():
                    chart2_data.append({
                        'datum': row['datum'].strftime('%Y-%m-%d'),
                        'gewest': row['gemeente_naam_nl'],
                        'jaar': row['jaar'],
                        'periode': row['periode'],
                        'renovatie_gebouwen_maand': row['renovatie_gebouwen_wonen'],
                        'renovatie_gebouwen_trend': round(row['renovatie_gebouwen_12m'], 1)
                    })
        
        chart2_df = pd.DataFrame(chart2_data)
        table2_html, table2_rows = self.create_data_table(
            chart2_df,
            'renovatie_gebouwen_data',
            'Renovatie gebouwen data'
        )
        
        analyses.append({
            'id': 'renovatie_gebouwen',
            'title': 'Renovatie gebouwen wonen per gewest',
            'description': 'Evolutie van het aantal renovaties van woongebouwen per gewest.',
            'chart_file': 'renovatie_gebouwen',
            'table_html': table2_html,
            'table_file': 'renovatie_gebouwen_data',
            'csv_file': 'renovatie_gebouwen_data.csv',
            'data_rows': table2_rows
        })
        
        # Analysis 3: Aandeel flats
        print("  → Aandeel flats")
        fig3 = self.create_trend_chart(
            self.df_gewest,
            'aandeel_flats',
            'Aandeel flats (% van totale nieuwbouw woningen) per gewest',
            'Percentage (%)',
            'aandeel_flats'
        )
        
        # Update y-axis for percentage
        fig3.update_layout(
            yaxis=dict(
                ticksuffix='%',
                range=[0, max(100, self.df_gewest['aandeel_flats'].max() * 1.1)],
                tickformat='.1f'
            )
        )
        
        # Re-save with updated layout
        chart_html = fig3.to_html(include_plotlyjs='cdn', div_id="chart-aandeel_flats")
        (self.charts_dir / "aandeel_flats.html").write_text(chart_html, encoding='utf-8')
        
        chart3_data = []
        for gewest in self.gewesten:
            gewest_data = self.df_gewest[self.df_gewest['gemeente_naam_nl'] == gewest].copy()
            if len(gewest_data) > 0:
                gewest_data = gewest_data.sort_values('datum')
                gewest_data['aandeel_flats_12m'] = gewest_data['aandeel_flats'].rolling(window=4, min_periods=1).mean()
                
                for _, row in gewest_data.iterrows():
                    chart3_data.append({
                        'datum': row['datum'].strftime('%Y-%m-%d'),
                        'gewest': row['gemeente_naam_nl'],
                        'jaar': row['jaar'],
                        'periode': row['periode'],
                        'aandeel_flats_maand': round(row['aandeel_flats'], 1),
                        'aandeel_flats_trend': round(row['aandeel_flats_12m'], 1),
                        'appartementen_absoluut': row['nieuwbouw_appartementen'],
                        'woningen_totaal': row['nieuwbouw_woningen_totaal']
                    })
        
        chart3_df = pd.DataFrame(chart3_data)
        table3_html, table3_rows = self.create_data_table(
            chart3_df,
            'aandeel_flats_data',
            'Aandeel flats data'
        )
        
        analyses.append({
            'id': 'aandeel_flats',
            'title': 'Aandeel flats per gewest',
            'description': 'Percentage appartementen van het totale aantal nieuwbouw woningen per gewest.',
            'chart_file': 'aandeel_flats',
            'table_html': table3_html,
            'table_file': 'aandeel_flats_data',
            'csv_file': 'aandeel_flats_data.csv',
            'data_rows': table3_rows
        })
        
        self.analyses = analyses
        print(f"✅ Generated {len(analyses)} analyses")
        
    def generate_stats(self):
        """Generate summary statistics"""
        stats = {
            'total_records': f"{self.df.shape[0]:,}",
            'total_locations': f"{self.df['refnis_code'].nunique():,}",
            'year_range': f"{self.df['jaar'].min()} - {self.df['jaar'].max()}",
            'gewesten_count': len(self.gewesten),
            'last_updated': datetime.now().strftime('%d %B %Y om %H:%M')
        }
        return stats
        
    def generate_html(self):
        """Generate the main HTML dashboard"""
        print("🌐 Generating HTML dashboard...")
        
        stats = self.generate_stats()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bouwvergunningen België - Dashboard</title>
    <link rel="stylesheet" href="css/dashboard.css">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🏗️ Bouwvergunningen België</h1>
            <p>Interactieve analyse van goedgekeurde bouwvergunningen per gewest</p>
            <div class="subtitle">
                Data van Statbel • Laatst bijgewerkt: {stats['last_updated']}
            </div>
        </header>
        
        <nav class="nav">
            <a href="#nieuwbouw_woningen">Nieuwbouw woningen</a>
            <a href="#renovatie_gebouwen">Renovatie gebouwen</a>
            <a href="#aandeel_flats">Aandeel flats</a>
            <a href="#downloads">Downloads</a>
        </nav>
        
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">{stats['total_records']}</span>
                <span class="stat-label">Totaal records</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{stats['gewesten_count']}</span>
                <span class="stat-label">Gewesten</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{stats['year_range']}</span>
                <span class="stat-label">Periode</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{stats['total_locations']}</span>
                <span class="stat-label">Locaties</span>
            </div>
        </div>
"""
        
        # Add each analysis section
        for analysis in self.analyses:
            iframe_code_chart = f'&lt;iframe src="https://gehuybre.github.io/goedgekeurde-vergunningen/charts/{analysis["chart_file"]}_standalone.html" width="100%" height="650" frameborder="0"&gt;&lt;/iframe&gt;'
            iframe_code_table = f'&lt;iframe src="https://gehuybre.github.io/goedgekeurde-vergunningen/tables/{analysis["table_file"]}.html" width="100%" height="400" frameborder="0"&gt;&lt;/iframe&gt;'
            
            html_content += f"""
        <section class="analysis-section" id="{analysis['id']}">
            <h2>{analysis['title']}</h2>
            <p>{analysis['description']}</p>
            
            <div class="chart-container">
                <div class="chart-actions">
                    <button class="btn btn-small btn-copy" onclick="copyToClipboard('{iframe_code_chart}', 'Grafiek iframe code gekopieerd!')">📋 Kopieer iframe</button>
                </div>
                <div class="chart-wrapper">
                    <iframe src="charts/{analysis['chart_file']}_standalone.html" width="100%" height="650" frameborder="0"></iframe>
                </div>
            </div>
            
            <h3>📋 Data tabel (laatste 30 entries)</h3>
            <div class="table-container">
                <div class="table-actions">
                    <h4 class="table-title">Data: {analysis['title']} ({analysis['data_rows']:,} records)</h4>
                    <div class="table-buttons">
                        <a href="csv/{analysis['csv_file']}" class="btn btn-small btn-download" download>💾 Download CSV</a>
                        <button class="btn btn-small btn-copy" onclick="copyToClipboard('{iframe_code_table}', 'Tabel iframe code gekopieerd!')">📋 Kopieer iframe</button>
                    </div>
                </div>
                <div class="table-scroll">
                    <iframe src="tables/{analysis['table_file']}.html" width="100%" height="400" frameborder="0"></iframe>
                </div>
            </div>
        </section>
"""
        
        # Add downloads section
        html_content += f"""
        <section class="downloads-section" id="downloads">
            <h2>📁 Downloads</h2>
            <p>Download alle data in CSV formaat voor eigen gebruik.</p>
            
            <div class="downloads-grid">
"""
        
        for analysis in self.analyses:
            html_content += f"""
                <div class="download-card">
                    <h4>{analysis['title']}</h4>
                    <p>Complete dataset met {analysis['data_rows']:,} records</p>
                    <a href="csv/{analysis['csv_file']}" class="btn btn-download" download>📥 Download CSV</a>
                </div>
"""
        
        html_content += """
            </div>
        </section>
        
        <footer class="footer">
            <p>
                🔗 <a href="https://github.com/gehuybre/goedgekeurde-vergunningen" target="_blank">GitHub Repository</a> • 
                📊 Data: <a href="https://statbel.fgov.be/" target="_blank">Statbel</a> • 
                🏛️ Gewesten: Vlaams Gewest, Waals Gewest, Brussels Hoofdstedelijk Gewest
            </p>
            <p style="margin-top: 1rem; opacity: 0.8; font-size: 0.9rem;">
                Dashboard automatisch gegenereerd met GitHub Actions
            </p>
        </footer>
    </div>
    
    <div class="copy-notification" id="copyNotification"></div>
    
    <script>
        function copyToClipboard(text, message) {
            // Decode HTML entities
            const decodedText = text.replace(/&lt;/g, '<').replace(/&gt;/g, '>');
            
            navigator.clipboard.writeText(decodedText).then(function() {
                showNotification(message);
            }).catch(function(err) {
                console.error('Failed to copy: ', err);
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = decodedText;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                showNotification(message);
            });
        }
        
        function showNotification(message) {
            const notification = document.getElementById('copyNotification');
            notification.textContent = message;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }
        
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    </script>
</body>
</html>
"""
        
        # Save the HTML file
        (self.docs_dir / "index.html").write_text(html_content, encoding='utf-8')
        print("✅ Generated index.html")

def main():
    """Main function to generate the dashboard"""
    print("🚀 Starting dashboard generation...")
    
    generator = DashboardGenerator()
    generator.load_and_prepare_data()
    generator.generate_analyses()
    generator.generate_html()
    
    print("🎉 Dashboard generation completed!")
    print(f"📁 Files generated in: {generator.docs_dir}")
    print("🌐 Ready for GitHub Pages deployment")

if __name__ == "__main__":
    main()
