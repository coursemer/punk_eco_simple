import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from datetime import datetime

def init_dash(server):
    """Initialise l'application Dash."""
    dash_app = dash.Dash(
        __name__,
        server=server,
        routes_pathname_prefix='/ma-economy/',
        external_stylesheets=['/static/css/ma_economy.css']
    )
    
    # Layout du tableau de bord
    dash_app.layout = html.Div([
        # En-tête
        html.Div([
            html.H1("📊 Tableau de Bord Économique du Maroc", className="dashboard-header"),
            html.P("Dernière mise à jour: " + datetime.now().strftime("%d/%m/%Y %H:%M"), 
                  id='last-update')
        ], className='header-container'),
        
        # Indicateurs clés
        html.Div([
            # PIB
            html.Div([
                html.Div([
                    html.Div("PIB", className='indicator-title'),
                    html.Div(id='pib-value', className='indicator-value'),
                    html.Div(id='pib-change', className='indicator-change')
                ], className='indicator-card', id='pib-indicator'),
                
                # Inflation
                html.Div([
                    html.Div("Inflation", className='indicator-title'),
                    html.Div(id='inflation-value', className='indicator-value'),
                    html.Div(id='inflation-change', className='indicator-change')
                ], className='indicator-card', id='inflation-indicator'),
                
                # Chômage
                html.Div([
                    html.Div("Chômage", className='indicator-title'),
                    html.Div(id='chomage-value', className='indicator-value'),
                    html.Div(id='chomage-change', className='indicator-change')
                ], className='indicator-card', id='chomage-indicator'),
                
                # TMM
                html.Div([
                    html.Div("TMM", className='indicator-title'),
                    html.Div(id='tmm-value', className='indicator-value'),
                    html.Div(id='tmm-change', className='indicator-change')
                ], className='indicator-card', id='tmm-indicator'),
            ], className='indicators-row'),
            
            # Graphiques
            html.Div([
                dcc.Graph(id='pib-chart', className='chart'),
                dcc.Graph(id='inflation-chart', className='chart')
            ], className='charts-row'),
            
            # Données détaillées
            html.Div([
                html.H2("Indicateurs détaillés"),
                html.Div(id='indicators-table')
            ], className='data-table')
            
        ], className='dashboard-container'),
        
        # Actualisation automatique
        dcc.Interval(
            id='interval-component',
            interval=3600*1000,  # 1 heure
            n_intervals=0
        )
    ])
    
    # Callbacks pour la mise à jour des indicateurs
    @dash_app.callback(
        [Output('pib-value', 'children'),
         Output('pib-change', 'children'),
         Output('inflation-value', 'children'),
         Output('inflation-change', 'children'),
         Output('chomage-value', 'children'),
         Output('chomage-change', 'children'),
         Output('tmm-value', 'children'),
         Output('tmm-change', 'children')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_indicators(n):
        from app.models.ma_economy import EconomicIndicator
        
        indicators = {
            'hcp_pib': {'value': None, 'change': None},
            'hcp_inflation': {'value': None, 'change': None},
            'hcp_chomage': {'value': None, 'change': None},
            'bam_tmm': {'value': None, 'change': None}
        }
        
        for indicator_id in indicators.keys():
            # Dernière valeur
            last = EconomicIndicator.query.filter_by(
                indicator_id=indicator_id
            ).order_by(EconomicIndicator.date.desc()).first()
            
            if last:
                indicators[indicator_id]['value'] = f"{last.value}%"
                
                # Calcul de la variation
                previous = EconomicIndicator.query.filter_by(
                    indicator_id=indicator_id
                ).order_by(EconomicIndicator.date.desc()).offset(1).first()
                
                if previous and previous.value != 0:
                    change = ((last.value - previous.value) / previous.value) * 100
                    indicators[indicator_id]['change'] = f"{change:+.1f}%"
        
        return [
            indicators['hcp_pib']['value'] or 'N/A',
            indicators['hcp_pib']['change'] or '',
            indicators['hcp_inflation']['value'] or 'N/A',
            indicators['hcp_inflation']['change'] or '',
            indicators['hcp_chomage']['value'] or 'N/A',
            indicators['hcp_chomage']['change'] or '',
            indicators['bam_tmm']['value'] or 'N/A',
            indicators['bam_tmm']['change'] or ''
        ]
    
    # Callback pour le graphique PIB
    @dash_app.callback(
        Output('pib-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_pib_chart(n):
        from app.models.ma_economy import EconomicIndicator
        
        data = EconomicIndicator.query.filter_by(indicator_id='hcp_pib')\
            .order_by(EconomicIndicator.date).limit(24).all()
        
        if not data:
            return go.Figure()
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[d.date for d in data],
            y=[d.value for d in data],
            mode='lines+markers',
            name='PIB (%)',
            line=dict(color='#2ecc71', width=3)
        ))
        
        fig.update_layout(
            title='Évolution du PIB (Taux de croissance annuel %)',
            xaxis_title='Date',
            yaxis_title='Taux de croissance (%)',
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    # Callback pour le graphique d'inflation
    @dash_app.callback(
        Output('inflation-chart', 'figure'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_inflation_chart(n):
        from app.models.ma_economy import EconomicIndicator
        
        inflation = EconomicIndicator.query.filter_by(indicator_id='hcp_inflation')\
            .order_by(EconomicIndicator.date).limit(24).all()
            
        if not inflation:
            return go.Figure()
            
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=[d.date for d in inflation],
            y=[d.value for d in inflation],
            mode='lines+markers',
            name='Inflation (%)',
            line=dict(color='#e74c3c', width=3)
        ))
        
        fig.update_layout(
            title='Évolution du Taux d\'Inflation (%)',
            xaxis_title='Date',
            yaxis_title='Taux d\'inflation (%)',
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    # Callback pour le tableau des indicateurs
    @dash_app.callback(
        Output('indicators-table', 'children'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_indicators_table(n):
        from app.models.ma_economy import EconomicIndicator
        
        indicators = EconomicIndicator.query\
            .order_by(EconomicIndicator.date.desc(), EconomicIndicator.source)\
            .limit(50).all()
            
        if not indicators:
            return "Aucune donnée disponible"
            
        rows = []
        for i, ind in enumerate(indicators):
            rows.append(html.Tr([
                html.Td(ind.name),
                html.Td(f"{ind.value} {ind.unit}"),
                html.Td(ind.date.strftime("%d/%m/%Y")),
                html.Td(ind.source)
            ]))
            
        return html.Table([
            html.Thead(html.Tr([
                html.Th('Indicateur'),
                html.Th('Valeur'),
                html.Th('Date'),
                html.Th('Source')
            ])),
            html.Tbody(rows)
        ], className='data-table')
    
    return dash_app.server
