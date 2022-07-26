import pandas
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

class OEModelMaker():
  ###take data, parameters as input and return full model simulation
  ###want output to be a list of subplots, indexed by period, showing the line in each period but that's a lot of memory
  #website will instead request a period specific subplot and server backend (or for streamlit, server frontend) runs code

  def __init__(self, df, shocksizepct=3, temporary=True, demandshock=True, supplyshock=False, inflationshock=False,
               flexiblerate=True, worldrate=3, inflationsensitivitytooutputgap=1, expendituresensitivitytointerestrate=0.75, CBcredibility=1,
               expendituresensitivitytorealer=0.1, worldinflationtarget=2, domesticinflationtarget=2, CBbeta=1,
               taxrate=0.2, publicexpenditurepct=0.2, publicdebt=0, equilibriumrealer=1, equilibriumnomer=1, equilibriumoutput=100):

               self.df = df
               self.shocksize = shocksizepct
               self.temporary = temporary
               self.multiplier = (0.01 * self.shocksize) + 1
               self.demandshock = demandshock
               self.supplyshock = supplyshock
               self.inflationshock = inflationshock
               self.flexiblerate = flexiblerate
               self.rstar = worldrate
               self.alpha = inflationsensitivitytooutputgap
               self.a = expendituresensitivitytointerestrate
               self.CBcredibility = CBcredibility
               self.b = expendituresensitivitytorealer
               self.adb = expendituresensitivitytorealer * 100
               #self.adb = np.log(expendituresensitivitytorealer)
               self.worldinflationtarget = worldinflationtarget
               self.piT = domesticinflationtarget
               self.beta = CBbeta
               self.t = taxrate
               self.publicexpenditurepct = publicexpenditurepct
               self.publicdebt = publicdebt
               self.qbar = 0
               self.ebar = 1
               self.ye = equilibriumoutput
               self.A = self.df['A'].values[0]
               self.adA = self.ye + (self.a * self.rstar) - (self.adb * self.qbar)

               if self.shocksize > 0:
                 #self.x = np.arange(self.ye - (0.5 * self.shocksize), self.df.iloc[5]['GDP'] + 1.5, 1)
                 self.x = np.arange(self.ye - (0.75 * self.shocksize), self.df['GDP'].values.max() + 1.5, 0.25)

               elif self.shocksize < 0: 
                 #self.x = np.arange(self.df.iloc[5]['GDP'] - 1.5, self.ye - (0.5 * self.shocksize), 1)
                 self.x = np.arange(self.df['GDP'].values.min() - 1.5, self.ye - (0.75 * self.shocksize), 0.25)
               


               self.cols = ['Periods', 'Output Gap', 'GDP', 'Inflation', 'Lending real i.r.', 'Real exchange rate', 'q', 'A']

               if self.supplyshock:
                 self.newye = self.ye * self.multiplier

  def Modelpoints(self):
    #this is finding the POIs from the actual model and outputting them for drawing
    #A and Z represent initial and final equilibriums so p1, p25
    #B represents the shock - it uses the period 5 data point because that isn't actually affected by period 5 rates
    #C represents where the central bank aims to move the economy post shock (the optimals in the sim, period 6 values)
    #using i-1 as the indexer to make the periods we're using clearer

    ys = [self.df.iloc[(i-1)]['GDP'] for i in [1, 5, 6, 25]]
    rs = [self.df.iloc[(i-1)]['Lending real i.r.'] for i in [1, 4, 5, 24]] # these need to be time bumped by one I think !!!!
    qs = [self.df.iloc[(i-1)]['q'] for i in [1, 5, 6, 25]] # I would think these would be time bumped too but i guess not? need to check
    pis = [self.df.iloc[(i-1)]['Inflation'] for i in [1, 5, 6, 25]]

    #I'm not gonna bother with the 'only' stuff I did for other plots - I think it would make debugging even less clear. Just gonna
    #add to the graph drawing functions and pray it works
    #the most likely bugs are time lags, which are pretty easy to fix in the code above so hope it all works lmao    
    return ys, rs, qs, pis

  def ISCurve(self, period, only=True):
    #y = A - a r + b q
    #use last period's r, q, any new A
    #if self.demandshock == False:
    #  q = self.qbar
    #  r = self.rstar
    #  A = self.A

    #else:
    periodslice = self.df.loc[self.df['Periods'] == period]
    a = self.a
    b = self.b
    if period < 5:
      q = self.qbar
      r = self.rstar
      A = self.A
    else:
      lastperiodslice = self.df.loc[self.df['Periods'] == (period-1)]
      q = lastperiodslice['Real exchange rate'].values[0]
      r = lastperiodslice['Lending real i.r.'].values[0]
      A = periodslice['A'].values[0]

    r = []
    for i in self.x:
      r.append(round((A - i + (b * q)) / a, 2))

    if only:
      fig1 = go.Figure()
      fig1.add_trace(go.Scatter(
          x=self.x, y=r, name='IS Curve', mode='lines', line={'color': 'blue'}
      ))
      fig1.update_layout(template='plotly_white', title=f'IS Curve - Period: {period}', height=700, width=700, showlegend=True)
      fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
      fig1.update_yaxes(title_text='Real lending rate r', showline=True, linecolor='black', linewidth=1)
      fig1.add_vline(self.ye)
      fig1.add_hline(self.rstar)
      # fig1.show()
      return fig1.to_html()
      
    else:
      return r

  def RXResponses(self, only=True):
    #this is making rx from visible central bank actions, which I guess was how we were taught at first to derive it
    ys = []
    for yentry in self.df['GDP']:
      ys.append(yentry)
    rs = [self.rstar]
    for rentry in self.df['Lending real i.r.'][:-1]:
      rs.append(round(rentry, 2))

    if only:
      fig1 = go.Figure(data=[
                      go.Scatter(x=ys, y=rs, name='POIs', mode='markers',
                                 marker={'color': '#000000', 'size': 7, 'symbol': 'square'})
                        ],
                       )
      fig1.update_layout(template='plotly_white', title='POIs', height=700, width=700, showlegend=True)
      fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
      fig1.update_yaxes(title_text='Real lending rate r', showline=True, linecolor='black', linewidth=1)
      fig1.add_vline(self.ye)
      fig1.add_hline(self.rstar)
      # fig1.show()
      return fig1.to_html()
      
    else:
      return ys, rs

  def RXCurve(self, only=True):
    r = []
    for i in self.x:
      r.append(((self.ye - i) / ((self.a) + (self.b / (1 - (1 / (1 + ((self.alpha ** 2) * self.beta))))))) + self.rstar)

    newr=[]
    if self.supplyshock and not self.temporary:
      for i in self.x:
        newr.append(((self.newye - i) / ((self.a) + (self.b / (1 - (1 / (1 + ((self.alpha ** 2) * self.beta))))))) + self.rstar)

    if only:
      fig1 = go.Figure()
      fig1.add_trace(go.Scatter(
          x=self.x, y=r, name='RX Curve', mode='lines', line={'color': 'red'}
      ))
      if self.supplyshock and not self.temporary:
        fig1.add_trace(go.Scatter(
          x=self.x, y=newr, name='New RX Curve', mode='lines', line={'color': 'maroon'}
          ))
        fig1.add_vline(self.newye, line={'color': 'lightgrey'})
      fig1.update_layout(template='plotly_white', title='RX Curve', height=700, width=700, showlegend=True)
      fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
      fig1.update_yaxes(title_text='Real lending rate r', showline=True, linecolor='black', linewidth=1)
      fig1.add_vline(self.ye, line={'color': 'lightgrey'})
      fig1.add_hline(self.rstar)
      # fig1.show()
      return fig1.to_html()
      
    else:
      return r, newr



  def ISRXDiagram(self, period):
    IS = self.ISCurve(period, only=False)
    RXys, RXrs = self.RXResponses(only=False)
    RXCurvers, NewRXCurvers = self.RXCurve(only=False)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
          x=self.x, y=IS, name='IS Curve', mode='lines', line={'color': 'blue'}
      ))
    fig1.add_trace(go.Scatter(
          x=self.x, y=RXCurvers, name='RX Curve', mode='lines', line={'color': 'red'}
      ))
    if self.supplyshock and not self.temporary and period >= 5:
        fig1.add_trace(go.Scatter(
          x=self.x, y=NewRXCurvers, name='New RX Curve', mode='lines', line={'color': 'maroon'}
          ))
        fig1.add_vline(self.newye, line={'color': 'lightgrey'})
    fig1.add_trace(go.Scatter(x=RXys, y=RXrs, name='POIs', mode='markers',
                                 marker={'color': '#000000', 'size': 7, 'symbol': 'square'}))
    fig1.update_layout(template='plotly_white', title=f'IS-RX Diagram - Period: {period}', height=700, width=700, showlegend=True)
    fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
    fig1.update_yaxes(title_text='Real lending rate r', showline=True, linecolor='black', linewidth=1)
    fig1.add_vline(self.ye, line={'color': 'lightgrey'})
    fig1.add_hline(self.rstar, line={'color': 'lightgrey'})

    # fig1.show()
    return fig1.to_html()
    

  def ADCurve(self, period, only=True):
    #y = A - a rstar + b q
    #use df A, rstar 
    periodslice = self.df.loc[self.df['Periods'] == period]
    
    a = self.a
    b = self.adb
    A = periodslice['A'].values[0]
    r = self.rstar

    qlist = []
    for i in self.x:
      q = (A - i - (a * r)) / (b * -1)
      qlist.append(round(q, 4))

    if only:
      fig1 = go.Figure()
      fig1.add_trace(go.Scatter(
          x=self.x, y=qlist, name='AD Curve', mode='lines', line={'color': 'green'}
      ))
      fig1.update_layout(template='plotly_white', title=f'AD Curve - Period: {period}', height=700, width=700, showlegend=True)
      fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
      fig1.update_yaxes(title_text='Real exchange rate q', showline=True, linecolor='black', linewidth=1)
      fig1.add_vline(self.ye)
      fig1.add_hline(self.qbar)
      # fig1.show()
      return fig1.to_html()
      
    else:
      return qlist

  def ERPoints(self, only=True):
    ys = []
    for yentry in self.df['GDP']:
      ys.append(yentry)
    qs = []
    for qentry in self.df['q']:
      qs.append(qentry)

    if only:
      fig1 = go.Figure()
      fig1.add_trace(go.Scatter(x=ys, y=qs, name='POIs', mode='markers',
                                 marker={'color': '#000000', 'size': 7, 'symbol': 'hexagon'}))
      fig1.update_layout(template='plotly_white', title='POIs', height=700, width=700, showlegend=True)
      fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
      fig1.update_yaxes(title_text='Real exchange rate q', showline=True, linecolor='black', linewidth=1)
      fig1.add_vline(self.ye)
      fig1.add_hline(self.qbar)
      # fig1.show()
      return fig1.to_html()
      
    else:
      return ys, qs


  def ADERUDiagram(self, period):
    AD = self.ADCurve(period, only=False)
    ERys, ERqs = self.ERPoints(only=False)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
          x=self.x, y=AD, name='AD Curve', mode='lines', line={'color': 'green'}
      ))
    fig1.add_trace(go.Scatter(x=ERys, y=ERqs, name='POIs', mode='markers',
                                 marker={'color': '#000000', 'size': 7, 'symbol': 'hexagon'}))
    fig1.update_layout(template='plotly_white', title=f'AD-ERU Diagram - Period: {period}', height=700, width=700, showlegend=True)
    fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
    fig1.update_yaxes(title_text='Real exchange rate q', showline=True, linecolor='black', linewidth=1)
    fig1.add_hline(self.qbar, line={'color': 'lightgrey'})
    fig1.add_vline(self.ye, line={'color': 'violet'})
    if self.supplyshock and not self.temporary:
      fig1.add_vline(self.newye, line={'color': 'darkviolet'})

    # fig1.show()
    return fig1.to_html()
    

  def MRCurve(self, only=True):
    pi = []
    for i in self.x:
      pi.append(round(((self.ye - i) / (self.alpha * self.beta)) + self.piT, 2))

    newpi=[]
    if self.supplyshock and not self.temporary:
      for i in self.x:
        newpi.append(round(((self.newye - i) / (self.alpha * self.beta)) + self.piT, 2))

    if only:
      fig1 = go.Figure()
      fig1.add_trace(go.Scatter(
          x=self.x, y=pi, name='MR Curve', mode='lines', line={'color': 'orange'}
      ))
      if self.supplyshock and not self.temporary:
        fig1.add_trace(go.Scatter(
          x=self.x, y=newpi, name='New RX Curve', mode='lines', line={'color': 'tan'}
          ))
        fig1.add_vline(self.newye, line={'color': 'lightgrey'})
      fig1.update_layout(template='plotly_white', title='MR Curve', height=700, width=700, showlegend=True)
      fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
      fig1.update_yaxes(title_text='Inflation pi', showline=True, linecolor='black', linewidth=1)
      fig1.add_vline(self.ye)
      fig1.add_hline(self.piT)
      # fig1.show()
      return fig1.to_html()
      
    else:
      return pi, newpi

  def PhillipsCurve(self, period, only=True):
    periodslice = self.df.loc[self.df['Periods'] == period]
    piE = periodslice['Expected Inflation'].values[0]

    pi = []
    if self.supplyshock and not self.temporary and not period <= 5:
      for i in self.x:
        pi.append(round((piE + (self.alpha * (i - self.newye))), 2))
    else:
      for i in self.x:
        pi.append(round((piE + (self.alpha * (i - self.ye))), 2))

    if only:
      fig1 = go.Figure()
      fig1.add_trace(go.Scatter(
          x=self.x, y=pi, name='Phillips Curve', mode='lines', line={'color': 'purple'}
      ))
      fig1.update_layout(template='plotly_white', title=f'Phillips Curve - Period: {period}', height=700, width=700, showlegend=True)
      fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
      fig1.update_yaxes(title_text='Inflation pi', showline=True, linecolor='black', linewidth=1)
      fig1.add_vline(self.ye, line={'color': 'lightgrey'})
      fig1.add_hline(self.piT, line={'color': 'lightgrey'})
      if self.supplyshock and not self.temporary:
        fig1.add_vline(self.newye, line={'color': 'lightgrey'})
      # fig1.show()
      return fig1.to_html()
      
    else:
      return pi

  def PhillipsCurvePoints(self, only=True):
    ys = []
    for yentry in self.df['GDP']:
      ys.append(yentry)

    pis = []
    for pientry in self.df['Inflation']:
      pis.append(pientry)

    if only:
      fig1 = go.Figure()
      fig1.add_trace(go.Scatter(x=ys, y=pis, name='POIs', mode='markers',
                                 marker={'color': '#000000', 'size': 7, 'symbol': 'triangle-up'}))
      fig1.update_layout(template='plotly_white', title='Points', height=700, width=700, showlegend=True)
      fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
      fig1.update_yaxes(title_text='Inflation pi', showline=True, linecolor='black', linewidth=1)
      fig1.add_vline(self.ye)
      fig1.add_hline(self.piT)
      # fig1.show()
      return fig1.to_html()
      
    else:
      return ys, pis


  def MRPCDiagram(self, period):
    PC = self.PhillipsCurve(period, only=False)
    PCpointys, PCpointpis = self.PhillipsCurvePoints(only=False)
    MR, NewMR = self.MRCurve(only=False)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=PCpointys, y=PCpointpis, name='POIs', mode='markers',
                               marker={'color': '#000000', 'size': 7, 'symbol': 'triangle-up'}))
    fig1.add_trace(go.Scatter(
          x=self.x, y=PC, name='Phillips Curve', mode='lines', line={'color': 'purple'}
      ))
    fig1.add_trace(go.Scatter(
          x=self.x, y=MR, name='MR Curve', mode='lines', line={'color': 'orange'}
      ))
    if self.supplyshock and not self.temporary and period >= 5:
        fig1.add_trace(go.Scatter(
          x=self.x, y=NewMR, name='New MR Curve', mode='lines', line={'color': 'tan'}
          ))
        fig1.add_vline(self.newye, line={'color': 'lightgrey'})
    fig1.update_layout(template='plotly_white', title=f'MR-PC Diagram - Period: {period}', height=700, width=700, showlegend=True)
    fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
    fig1.update_yaxes(title_text='Inflation pi', showline=True, linecolor='black', linewidth=1)
    fig1.add_vline(self.ye)
    fig1.add_hline(self.piT)
    # fig1.show()
    return fig1.to_html()
    


  def ThreeEquationsPeriod(self, period):
    IS = self.ISCurve(period, only=False)
    #RXys, RXrs = self.RXResponses(only=False)
    RXCurvers, NewRXCurvers = self.RXCurve(only=False)
    AD = self.ADCurve(period, only=False)
    #ERys, ERqs = self.ERPoints(only=False)
    PC = self.PhillipsCurve(period, only=False)
    #PCpointys, PCpointpis = self.PhillipsCurvePoints(only=False)
    MR, NewMR = self.MRCurve(only=False)
    ys, RXrs, ERqs, PCpointpis = self.Modelpoints()


    fig1 = make_subplots(rows=3, cols=1, vertical_spacing=0.05, shared_xaxes=True,
                         subplot_titles=['IS-RX Diagram', 'AD-ERU Diagram', 'MR-PC Curve'])

    fig1.add_trace(go.Scatter(
          x=self.x, y=IS, name='IS Curve', mode='lines', line={'color': 'blue'}
      ), row=1, col=1)
    fig1.add_trace(go.Scatter(
          x=self.x, y=RXCurvers, name='RX Curve', mode='lines', line={'color': 'red'}
      ), row=1, col=1)
    fig1.add_trace(go.Scatter(x=ys, y=RXrs, name='POIs', mode='markers', hovertext=['Point A', 'Point B', 'Point C', 'Point Z'], 
                                 marker={'color': '#000000', 'size': 7, 'symbol': ['square', 'hexagon', 'triangle-up', 'square']}
      ), row=1, col=1)
    fig1.add_trace(go.Scatter(
          x=self.x, y=AD, name='AD Curve', mode='lines', line={'color': 'green'}
      ), row=2, col=1)
    fig1.add_trace(go.Scatter(x=ys, y=ERqs, name='POIs', mode='markers', hovertext=['Point A', 'Point B', 'Point C', 'Point Z'], showlegend=False, 
                                 marker={'color': '#000000', 'size': 7, 'symbol': ['square', 'hexagon', 'triangle-up', 'square']}
      ), row=2, col=1)
    fig1.add_trace(go.Scatter(
          x=self.x, y=PC, name='Phillips Curve', mode='lines', line={'color': 'purple'}
      ), row=3, col=1)
    fig1.add_trace(go.Scatter(
          x=self.x, y=MR, name='MR Curve', mode='lines', line={'color': 'orange'}
      ), row=3, col=1)
    fig1.add_trace(go.Scatter(x=ys, y=PCpointpis, name='POIs', mode='markers', hovertext=['Point A', 'Point B', 'Point C', 'Point Z'], showlegend=False, 
                               marker={'color': '#000000', 'size': 7, 'symbol': ['square', 'hexagon', 'triangle-up', 'square']}
      ), row=3, col=1)

    if self.supplyshock and not self.temporary and period >= 5:
        fig1.add_trace(go.Scatter(
          x=self.x, y=NewRXCurvers, name='New RX Curve', mode='lines', line={'color': 'maroon'}
          ), row=1, col=1)
        fig1.add_trace(go.Scatter(
          x=self.x, y=NewMR, name='New MR Curve', mode='lines', line={'color': 'tan'}
          ), row=3, col=1)
        fig1.add_vline(self.newye, row=2, line={'color': 'darkviolet'})
    fig1.add_vline(self.ye, row=[1, 3], line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.add_vline(self.ye, row=2, line={'color': 'violet', 'dash': 'solid', 'width': 1})
    fig1.add_hline(self.rstar, row=1, col=1, line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.add_hline(self.qbar, row=2, col=1, line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.add_hline(self.piT, row=3, col=1, line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.update_layout(template='plotly_white', title=f'Period: {period}', height=1000, width=500, margin={'l': 20, 'r': 20, 'b': 25, 't': 35},
                       xaxis_showticklabels=True, xaxis2_showticklabels=True, xaxis3_showticklabels=True,
                       yaxis_showticklabels=True, yaxis2_showticklabels=True, yaxis3_showticklabels=True)
    fig1.update_xaxes(showline=True, linecolor='darkgray', linewidth=1)
    fig1.update_yaxes(title_text='Real Interest Rate r', showline=True, linecolor='darkgray', linewidth=1, row=1, col='all')
    fig1.update_yaxes(title_text='Real Exchange Rate q', showline=True, linecolor='darkgray', linewidth=1, row=2, col='all')
    fig1.update_yaxes(title_text='Inflation pi', showline=True, linecolor='darkgray', linewidth=1, row=3, col='all')
    fig1.update_yaxes(showline=True, linecolor='darkgray', linewidth=1)
    # fig1.show()
    return fig1.to_html()
    


  def ThreeEquationsOverTime(self):
    fig1 = make_subplots(rows=3, cols=4, vertical_spacing=0.05, horizontal_spacing=0.05, shared_xaxes=True, shared_yaxes=True,
                         row_titles=['IS-RX Diagram', 'AD-ERU Diagram', 'MR-PC Curve'],
                         column_titles=['Period1 / Point A', 'Period5 / Shock', 'Period6 / Recovery', 'Period25 / Point Z'])

    #RXys, RXrs = self.RXResponses(only=False)
    RXCurvers, NewRXCurvers = self.RXCurve(only=False)
    #ERys, ERqs = self.ERPoints(only=False)
    #PCpointys, PCpointpis = self.PhillipsCurvePoints(only=False)
    MR, NewMR = self.MRCurve(only=False)
    ys, RXrs, ERqs, PCpointpis = self.Modelpoints()

    fig1.add_trace(go.Scatter(x=ys, y=RXrs, name='POIs', mode='markers', hovertext=['Point A', 'Point B', 'Point C', 'Point Z'], 
                                 marker={'color': '#000000', 'size': 7, 'symbol': ['square', 'hexagon', 'triangle-up', 'square']}
      ), row=1, col=1)
    fig1.add_trace(go.Scatter(x=ys, y=RXrs, name='POIs', mode='markers', hovertext=['Point A', 'Point B', 'Point C', 'Point Z'], 
                                 marker={'color': '#000000', 'size': 7, 'symbol': ['square', 'hexagon', 'triangle-up', 'square']}, showlegend=False
      ), row=1, col='all')
    fig1.add_trace(go.Scatter(x=ys, y=ERqs, name='POIs', mode='markers', hovertext=['Point A', 'Point B', 'Point C', 'Point Z'], 
                                 marker={'color': '#000000', 'size': 7, 'symbol': ['square', 'hexagon', 'triangle-up', 'square']}, showlegend=False
      ), row=2, col='all')
    fig1.add_trace(go.Scatter(x=ys, y=PCpointpis, name='POIs', mode='markers', hovertext=['Point A', 'Point B', 'Point C', 'Point Z'], 
                               marker={'color': '#000000', 'size': 7, 'symbol': ['square', 'hexagon', 'triangle-up', 'square']}, showlegend=False
      ), row=3, col='all')

    periods = [1, 5, 6, 25]
    for period in periods:
      IS = self.ISCurve(period, only=False)
      AD = self.ADCurve(period, only=False)
      PC = self.PhillipsCurve(period, only=False)
      onlegend = False if period !=5 else True

      column = periods.index(period) + 1

      fig1.add_trace(go.Scatter(
          x=self.x, y=IS, name='IS Curve', mode='lines', line={'color': 'blue'}, showlegend=onlegend 
      ), row=1, col=column)
      fig1.add_trace(go.Scatter(
          x=self.x, y=RXCurvers, name='RX Curve', mode='lines', line={'color': 'red'}, showlegend=onlegend
      ), row=1, col=column)
      fig1.add_trace(go.Scatter(
          x=self.x, y=AD, name='AD Curve', mode='lines', line={'color': 'green'}, showlegend=onlegend
      ), row=2, col=column)

      fig1.add_trace(go.Scatter(
          x=self.x, y=PC, name='Phillips Curve', mode='lines', line={'color': 'purple'}, showlegend=onlegend
      ), row=3, col=column)
      fig1.add_trace(go.Scatter(
          x=self.x, y=MR, name='MR Curve', mode='lines', line={'color': 'orange'}, showlegend=onlegend
      ), row=3, col=column)

      if self.supplyshock and not self.temporary and period >= 5:
        fig1.add_trace(go.Scatter(
          x=self.x, y=NewRXCurvers, name='New RX Curve', mode='lines', line={'color': 'maroon'}, showlegend=onlegend
          ), row=1, col=column)
        fig1.add_trace(go.Scatter(
          x=self.x, y=NewMR, name='New MR Curve', mode='lines', line={'color': 'tan'}, showlegend=onlegend
          ), row=3, col=column)
        fig1.add_vline(self.newye, row=2, col=column, line={'color': 'darkviolet'})


    fig1.add_vline(self.ye, row=[1, 3], col='all', line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.add_vline(self.ye, row=2, col='all', line={'color': 'violet', 'dash': 'solid', 'width': 1})
    fig1.add_hline(self.rstar, row=1, col='all', line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.add_hline(self.qbar, row=2, col='all', line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.add_hline(self.piT, row=3, col='all', line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.update_layout(template='plotly_white', margin={'l': 20, 'r': 20, 'b': 25, 't': 35},
                       xaxis_showticklabels=True, xaxis2_showticklabels=True, xaxis3_showticklabels=True, xaxis4_showticklabels=True,
                       xaxis5_showticklabels=True, xaxis6_showticklabels=True, xaxis7_showticklabels=True, xaxis8_showticklabels=True,
                       xaxis9_showticklabels=True, xaxis10_showticklabels=True, xaxis11_showticklabels=True, xaxis12_showticklabels=True,
                       yaxis_showticklabels=True, yaxis2_showticklabels=True, yaxis3_showticklabels=True, yaxis4_showticklabels=True,
                       yaxis5_showticklabels=True, yaxis6_showticklabels=True, yaxis7_showticklabels=True, yaxis8_showticklabels=True,
                       yaxis9_showticklabels=True, yaxis10_showticklabels=True, yaxis11_showticklabels=True, yaxis12_showticklabels=True)
    fig1.update_xaxes(showline=True, linecolor='darkgray', linewidth=1)
    fig1.update_yaxes(title_text='Real Interest Rate r', showline=True, linecolor='darkgray', linewidth=1, row=1, col='all')
    fig1.update_yaxes(title_text='Real Exchange Rate q', showline=True, linecolor='darkgray', linewidth=1, row=2, col='all')
    fig1.update_yaxes(title_text='Inflation pi', showline=True, linecolor='darkgray', linewidth=1, row=3, col='all')
    fig1.update_yaxes(showline=True, linecolor='darkgray', linewidth=1)
    #print(fig1.layout)
    # fig1.show()
    return fig1.to_html(div_id='summary', default_height='97.5vh', default_width='97.5vw', include_plotlyjs=False)
    


class CEModelMaker():
  def __init__(self, df, shocksizepct=3, temporary=True, demandshock=True, supplyshock=False, inflationshock=False,
               rstar = 4, inflationsensitivitytooutputgap=1, expendituresensitivitytointerestrate=2, CBcredibility=0,
               domesticinflationtarget=2, CBbeta=1, equilibriumoutput=100):

               self.df = df
               self.shocksize = shocksizepct
               self.temporary = temporary
               self.multiplier = (0.01 * self.shocksize) + 1
               self.demandshock = demandshock
               self.supplyshock = supplyshock
               self.inflationshock = inflationshock
               self.rstar = rstar
               self.alpha = inflationsensitivitytooutputgap
               self.a = expendituresensitivitytointerestrate
               self.CBcredibility = CBcredibility
               #self.adb = np.log(expendituresensitivitytorealer)
               self.piT = domesticinflationtarget
               self.beta = CBbeta


               self.ye = equilibriumoutput
               self.A = self.df['A'].values[0]

               if self.shocksize > 0:
                 #self.x = np.arange(self.ye - (0.5 * self.shocksize), self.df.iloc[5]['GDP'] + 1.5, 1)
                 self.x = np.arange(self.ye - (0.75 * self.shocksize), self.df['GDP'].values.max() + 1.5, 0.25)

               elif self.shocksize < 0: 
                 #self.x = np.arange(self.df.iloc[5]['GDP'] - 1.5, self.ye - (0.5 * self.shocksize), 1)
                 self.x = np.arange(self.df['GDP'].values.min() - 1.5, self.ye - (0.75 * self.shocksize), 0.25)
              
               


               self.cols = ['Periods', 'Output Gap', 'GDP', 'Inflation', 'Lending real i.r.', 'A']

               if self.supplyshock:
                 self.newye = self.ye * self.multiplier

  def Modelpoints(self):
    #this is finding the POIs from the actual model and outputting them for drawing
    #A and Z represent initial and final equilibriums so p1, p25
    #B represents the shock - it uses the period 5 data point because that isn't actually affected by period 5 rates
    #C represents where the central bank aims to move the economy post shock (the optimals in the sim, period 6 values)
    #using i-1 as the indexer to make the periods we're using clearer

    ys = [self.df.iloc[(i-1)]['GDP'] for i in [1, 5, 6, 25]]
    rs = [self.df.iloc[(i-1)]['Lending real i.r.'] for i in [1, 4, 5, 24]] # these need to be time bumped by one I think !!!!
    #qs = [self.df.iloc[(i-1)]['q'] for i in [1, 5, 6, 25]] # I would think these would be time bumped too but i guess not? need to check
    pis = [self.df.iloc[(i-1)]['Inflation'] for i in [1, 5, 6, 25]]

    #I'm not gonna bother with the 'only' stuff I did for other plots - I think it would make debugging even less clear. Just gonna
    #add to the graph drawing functions and pray it works
    #the most likely bugs are time lags, which are pretty easy to fix in the code above so hope it all works lmao    
    return ys, rs, pis


  def ISCurve(self, period, only=True):
    #y = A - a r
    #use last period's r, any new A

    periodslice = self.df.loc[self.df['Periods'] == period]
    a = self.a
    if period < 5:
      r = self.rstar
      A = self.A
    else:
      lastperiodslice = self.df.loc[self.df['Periods'] == (period-1)]
      r = lastperiodslice['Lending real i.r.'].values[0]
      A = periodslice['A'].values[0]

    r = []
    for i in self.x:
      r.append(round((A - i) / a, 2))

    if only:
      fig1 = go.Figure()
      fig1.add_trace(go.Scatter(
          x=self.x, y=r, name='IS Curve', mode='lines', line={'color': 'blue'}
      ))
      fig1.update_layout(template='plotly_white', title=f'IS Curve - Period: {period}', height=700, width=700, showlegend=True)
      fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
      fig1.update_yaxes(title_text='Real lending rate r', showline=True, linecolor='black', linewidth=1)
      fig1.add_vline(self.ye)
      fig1.add_hline(self.rstar)
      # fig1.show()
      return fig1.to_html()
      
    else:
      return r

  def MRCurve(self, only=True):
    pi = []
    for i in self.x:
      pi.append(round(((self.ye - i) / (self.alpha * self.beta)) + self.piT, 2))

    newpi=[]
    if self.supplyshock and not self.temporary:
      for i in self.x:
        newpi.append(round(((self.newye - i) / (self.alpha * self.beta)) + self.piT, 2))

    if only:
      fig1 = go.Figure()
      fig1.add_trace(go.Scatter(
          x=self.x, y=pi, name='MR Curve', mode='lines', line={'color': 'orange'}
      ))
      if self.supplyshock and not self.temporary:
        fig1.add_trace(go.Scatter(
          x=self.x, y=newpi, name='New RX Curve', mode='lines', line={'color': 'tan'}
          ))
        fig1.add_vline(self.newye, line={'color': 'lightgrey'})
      fig1.update_layout(template='plotly_white', title='MR Curve', height=700, width=700, showlegend=True)
      fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
      fig1.update_yaxes(title_text='Inflation pi', showline=True, linecolor='black', linewidth=1)
      fig1.add_vline(self.ye)
      fig1.add_hline(self.piT)
      # fig1.show()
      return fig1.to_html()
      
    else:
      return pi, newpi


  def PhillipsCurve(self, period, only=True):
    periodslice = self.df.loc[self.df['Periods'] == period]
    piE = periodslice['Expected Inflation'].values[0]

    pi = []
    if self.supplyshock and not self.temporary and not period <= 5:
      for i in self.x:
        pi.append(round((piE + (self.alpha * (i - self.newye))), 2))
    else:
      for i in self.x:
        pi.append(round((piE + (self.alpha * (i - self.ye))), 2))

    if only:
      fig1 = go.Figure()
      fig1.add_trace(go.Scatter(
          x=self.x, y=pi, name='Phillips Curve', mode='lines', line={'color': 'purple'}
      ))
      fig1.update_layout(template='plotly_white', title=f'Phillips Curve - Period: {period}', height=700, width=700, showlegend=True)
      fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
      fig1.update_yaxes(title_text='Inflation pi', showline=True, linecolor='black', linewidth=1)
      fig1.add_vline(self.ye, line={'color': 'lightgrey'})
      fig1.add_hline(self.piT, line={'color': 'lightgrey'})
      if self.supplyshock and not self.temporary:
        fig1.add_vline(self.newye, line={'color': 'lightgrey'})
      # fig1.show()
      return fig1.to_html()
      
    else:
      return pi

  def MRPCDiagram(self, period):
    PC = self.PhillipsCurve(period, only=False)
    PCpointys, PCpointpis = self.PhillipsCurvePoints(only=False)
    MR, NewMR = self.MRCurve(only=False)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=PCpointys, y=PCpointpis, name='POIs', mode='markers',
                               marker={'color': '#000000', 'size': 7, 'symbol': 'triangle-up'}))
    fig1.add_trace(go.Scatter(
          x=self.x, y=PC, name='Phillips Curve', mode='lines', line={'color': 'purple'}
      ))
    fig1.add_trace(go.Scatter(
          x=self.x, y=MR, name='MR Curve', mode='lines', line={'color': 'orange'}
      ))
    if self.supplyshock and not self.temporary and period >= 5:
        fig1.add_trace(go.Scatter(
          x=self.x, y=NewMR, name='New MR Curve', mode='lines', line={'color': 'tan'}
          ))
        fig1.add_vline(self.newye, line={'color': 'lightgrey'})
    fig1.update_layout(template='plotly_white', title=f'MR-PC Diagram - Period: {period}', height=700, width=700, showlegend=True)
    fig1.update_xaxes(title_text='Output y', showline=True, linecolor='black', linewidth=1)
    fig1.update_yaxes(title_text='Inflation pi', showline=True, linecolor='black', linewidth=1)
    fig1.add_vline(self.ye)
    fig1.add_hline(self.piT)
    # fig1.show()
    return fig1.to_html()
      

  def ThreeEquationsPeriod(self, period):
    IS = self.ISCurve(period, only=False)
    PC = self.PhillipsCurve(period, only=False)
    MR, NewMR = self.MRCurve(only=False)
    ys, ISrs, PCpointpis = self.Modelpoints()


    fig1 = make_subplots(rows=2, cols=1, vertical_spacing=0.05, shared_xaxes=True,
                         subplot_titles=['IS Diagram', 'AD-ERU Diagram', 'MR-PC Curve'])

    fig1.add_trace(go.Scatter(
          x=self.x, y=IS, name='IS Curve', mode='lines', line={'color': 'blue'}
      ), row=1, col=1)
    fig1.add_trace(go.Scatter(x=ys, y=ISrs, name='POIs', mode='markers', hovertext=['Point A', 'Point B', 'Point C', 'Point Z'], 
                                 marker={'color': '#000000', 'size': 7, 'symbol': ['square', 'hexagon', 'triangle-up', 'square']}
      ), row=1, col=1)
    fig1.add_trace(go.Scatter(
          x=self.x, y=PC, name='Phillips Curve', mode='lines', line={'color': 'purple'}
      ), row=2, col=1)
    fig1.add_trace(go.Scatter(
          x=self.x, y=MR, name='MR Curve', mode='lines', line={'color': 'orange'}
      ), row=2, col=1)
    fig1.add_trace(go.Scatter(x=ys, y=PCpointpis, name='POIs', mode='markers', hovertext=['Point A', 'Point B', 'Point C', 'Point Z'], showlegend=False, 
                               marker={'color': '#000000', 'size': 7, 'symbol': ['square', 'hexagon', 'triangle-up', 'square']}
      ), row=2, col=1)

    if self.supplyshock and not self.temporary and period >= 5:
        fig1.add_trace(go.Scatter(
          x=self.x, y=NewMR, name='New MR Curve', mode='lines', line={'color': 'tan'}
          ), row=2, col=1)
        fig1.add_vline(self.newye, row=2, line={'color': 'darkviolet'})
    fig1.add_vline(self.ye, row=[1, 2], line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.add_hline(self.rstar, row=1, col=1, line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.add_hline(self.piT, row=2, col=1, line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.update_layout(template='plotly_white', title=f'Period: {period}', height=1000, width=500, margin={'l': 20, 'r': 20, 'b': 25, 't': 35},
                       xaxis_showticklabels=True, xaxis2_showticklabels=True,
                       yaxis_showticklabels=True, yaxis2_showticklabels=True,)
    fig1.update_xaxes(showline=True, linecolor='darkgray', linewidth=1)
    fig1.update_yaxes(title_text='Real Interest Rate r', showline=True, linecolor='darkgray', linewidth=1, row=1, col='all')
    fig1.update_yaxes(title_text='Inflation pi', showline=True, linecolor='darkgray', linewidth=1, row=2, col='all')
    fig1.update_yaxes(showline=True, linecolor='darkgray', linewidth=1)
    # fig1.show()
    return fig1.to_html()
    

  def ThreeEquationsOverTime(self):
    fig1 = make_subplots(rows=2, cols=4, vertical_spacing=0.05, horizontal_spacing=0.05, shared_xaxes=True, shared_yaxes=True,
                         row_titles=['IS Diagram', 'MR-PC Curve'],
                         column_titles=['Period1 / Point A', 'Period5 / Shock', 'Period6 / Recovery', 'Period25 / Point Z'])

    MR, NewMR = self.MRCurve(only=False)
    ys, ISrs, PCpointpis = self.Modelpoints()

    fig1.add_trace(go.Scatter(x=ys, y=ISrs, name='POIs', mode='markers', hovertext=['Point A', 'Point B', 'Point C', 'Point Z'], 
                                 marker={'color': '#000000', 'size': 7, 'symbol': ['square', 'hexagon', 'triangle-up', 'square']}
      ), row=1, col=1)
    fig1.add_trace(go.Scatter(x=ys, y=ISrs, name='POIs', mode='markers', hovertext=['Point A', 'Point B', 'Point C', 'Point Z'], 
                                 marker={'color': '#000000', 'size': 7, 'symbol': ['square', 'hexagon', 'triangle-up', 'square']}, showlegend=False
      ), row=1, col='all')
    fig1.add_trace(go.Scatter(x=ys, y=PCpointpis, name='POIs', mode='markers', hovertext=['Point A', 'Point B', 'Point C', 'Point Z'], 
                               marker={'color': '#000000', 'size': 7, 'symbol': ['square', 'hexagon', 'triangle-up', 'square']}, showlegend=False
      ), row=2, col='all')

    periods = [1, 5, 6, 25]
    for period in periods:
      IS = self.ISCurve(period, only=False)
      PC = self.PhillipsCurve(period, only=False)
      onlegend = False if period !=5 else True
      column = periods.index(period) + 1

      fig1.add_trace(go.Scatter(
          x=self.x, y=IS, name='IS Curve', mode='lines', line={'color': 'blue'}, showlegend=onlegend 
      ), row=1, col=column)

      fig1.add_trace(go.Scatter(
          x=self.x, y=PC, name='Phillips Curve', mode='lines', line={'color': 'purple'}, showlegend=onlegend
      ), row=2, col=column)
      fig1.add_trace(go.Scatter(
          x=self.x, y=MR, name='MR Curve', mode='lines', line={'color': 'orange'}, showlegend=onlegend
      ), row=2, col=column)

      if self.supplyshock and not self.temporary and period >= 5:
        fig1.add_trace(go.Scatter(
          x=self.x, y=NewMR, name='New MR Curve', mode='lines', line={'color': 'tan'}, showlegend=onlegend
          ), row=2, col=column)


    fig1.add_vline(self.ye, row=[1, 2], col='all', line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.add_hline(self.rstar, row=1, col='all', line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.add_hline(self.piT, row=2, col='all', line={'color': 'lightgrey', 'dash': 'solid', 'width': 1})
    fig1.update_layout(template='plotly_white', margin={'l': 20, 'r': 20, 'b': 25, 't': 35},
                       xaxis_showticklabels=True, xaxis2_showticklabels=True, xaxis3_showticklabels=True, xaxis4_showticklabels=True,
                       xaxis5_showticklabels=True, xaxis6_showticklabels=True, xaxis7_showticklabels=True, xaxis8_showticklabels=True,
                       yaxis_showticklabels=True, yaxis2_showticklabels=True, yaxis3_showticklabels=True, yaxis4_showticklabels=True,
                       yaxis5_showticklabels=True, yaxis6_showticklabels=True, yaxis7_showticklabels=True, yaxis8_showticklabels=True,
                       )
    fig1.update_xaxes(showline=True, linecolor='darkgray', linewidth=1)
    fig1.update_yaxes(title_text='Real Interest Rate r', showline=True, linecolor='darkgray', linewidth=1, row=1, col='all')
    fig1.update_yaxes(title_text='Inflation pi', showline=True, linecolor='darkgray', linewidth=1, row=2, col='all')
    fig1.update_yaxes(showline=True, linecolor='darkgray', linewidth=1)
    #print(fig1.layout)
    # fig1.show()
    return fig1.to_html(div_id='summary', default_height='65vh', default_width='97.5vw', include_plotlyjs=False)
      