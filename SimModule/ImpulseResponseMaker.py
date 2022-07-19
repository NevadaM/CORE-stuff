from re import template
import pandas
import numpy
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#import Simulator #for example dataframe

####Take df from simulator, create impulse response funcs using plotly
#get example df

#sim = Simulator.Simulator()
#df = sim.DemandShock(3, temporary=True)

class ImpulseResponses():

    def __init__(self, df, ye=100, rstar=3, piT=2, ebar=1):
        self.df = df
        self.ye = ye
        self.rstar = rstar
        self.piT = piT
        self.ebar = ebar


    def GDP(self, html=True):
        fig = go.Figure()
        scatter = go.Scatter(
            x=self.df['Periods'], y = self.df['GDP'], 
            name='GDP', mode='lines+markers', line={'color': 'blue'}, marker={'color': 'purple'}
        )
        fig.add_trace(scatter)
        fig.update_layout(
            template='plotly_white', title='GDP / y', 
            height=450, width=800
            )
        fig.update_xaxes(
            title_text='Periods', showline=True, 
            linecolor='black', linewidth=1
        )
        fig.update_yaxes(
            title_text='GDP (y)', showline=True, 
            linecolor='black', linewidth=1
        )

        fig.add_hline(self.ye)
        # fig.show()
        if html:
            return fig.to_html()
        else:
            return scatter
        

    def Inflation(self, html=True):
        fig = go.Figure()
        scatter = go.Scatter(
            x=self.df['Periods'], y = self.df['Inflation'], 
            name='Inflation', mode='lines+markers', line={'color': 'blue'}, marker={'color': 'purple'}
            )
        fig.add_trace(scatter)
        fig.update_layout(
            template='plotly_white', title='Inflation / pi', 
            height=450, width=800
            )
        fig.update_xaxes(
            title_text='Periods', showline=True, 
            linecolor='black', linewidth=1
        )
        fig.update_yaxes(
            title_text='Inflation (pi)', showline=True, 
            linecolor='black', linewidth=1
        )

        fig.add_hline(self.piT)
        # fig.show()
        if html:
            return fig.to_html()
        else:
            return scatter
        

    def RealInterestRate(self, html=True):
        fig = go.Figure()
        scatter = go.Scatter(
            x=self.df['Periods'], y = self.df['Lending real i.r.'], 
            name='Interest Rate', mode='lines+markers', line={'color': 'blue'}, marker={'color': 'purple'}
        )
        fig.add_trace(scatter)
        fig.update_layout(
            template='plotly_white', title='Interest Rate / r', 
            height=450, width=800
            )
        fig.update_xaxes(
            title_text='Periods', showline=True, 
            linecolor='black', linewidth=1
        )
        fig.update_yaxes(
            title_text='Interest Rate (r)', showline=True, 
            linecolor='black', linewidth=1
        )

        fig.add_hline(self.rstar)
        # fig.show()
        if html:
            return fig.to_html()
        else:
            return scatter
        

    def RealExchangeRate(self, html=True):
        fig = go.Figure()
        scatter = go.Scatter(
            x=self.df['Periods'], y = self.df['Real exchange rate'], 
            name='Real Exchange Rate', mode='lines+markers', line={'color': 'blue'}, marker={'color': 'purple'}
        )
        fig.add_trace(scatter)
        fig.update_layout(
            template='plotly_white', title='Real Exchange Rate / Q', 
            height=450, width=800
            )
        fig.update_xaxes(
            title_text='Periods', showline=True, 
            linecolor='black', linewidth=1
        )
        fig.update_yaxes(
            title_text='Real Exchange Rate (Q)', showline=True, 
            linecolor='black', linewidth=1
        )

        fig.add_hline(self.ebar)
        # fig.show()
        if html:
            return fig.to_html()
        else:
            return scatter
        
    def AllIRFs(self, open=True):
        if open:
            fig = make_subplots(rows=4, shared_xaxes=True, subplot_titles=['GDP / y', 'Inflation / pi', 'Real Interest Rate / r', 'Real Exchange Rate / Q'], x_title='Periods', 
            vertical_spacing=0.1)
        else: 
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, subplot_titles=['GDP / y', 'Inflation / pi', 'Real Interest Rate / r'], x_title='Periods')

        fig.add_trace(self.GDP(html=False), row=1, col=1)
        fig.add_trace(self.Inflation(html=False), row=2, col=1)
        fig.add_trace(self.RealInterestRate(html=False), row=3, col=1)
        if open:
            fig.add_trace(self.RealExchangeRate(html=False), row=4, col=1)
            fig.add_hline(self.ebar, row=4, col=1)


        fig.update_layout(template='plotly_white', hovermode='x', showlegend=False)
        fig.update_xaxes(showline=True, linecolor='black', linewidth=1)
        fig.update_yaxes(showline=True, linecolor='black', linewidth=1)

        fig.add_hline(y=self.ye, row=1, col=1)
        fig.add_hline(self.piT, row=2, col=1)
        fig.add_hline(self.rstar, row=3, col=1)


        
        return fig.to_html(div_id='irf', default_height='97.5vh', default_width='65vw', include_plotlyjs='cdn') 
            
        
