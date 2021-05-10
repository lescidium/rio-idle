"""Big container file for all old projects which are obsolete or will soon be obsolete."""
import urllib.request as ur
from urllib.error import HTTPError
import re
import datetime

import pandas_datareader as pdr
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
import yuqi
import soojin
import minnie

def oppa(tick,write):
    """Runs good old Oppa.
    
    First argument is stock symbol, second is true/false argument.
    Put True for an excel report, put False for no excel report."""
    income = minnie.macro_scrape(tick,'income-statement')
    balance = minnie.macro_scrape(tick,'balance-sheet')
    cash = minnie.macro_scrape(tick,'cash-flow-statement')
    yrlab = income.columns
    report = macro_calc(income,balance,cash,yrlab,tick)
    val_report,assum = valeria(tick,yrlab,report,0,10)
    if write == True:
        minnie.write(report, val_report, assum, 'No-URL', tick)
    return report.T

def smallset(tick,yrs_bak,yrs_len):
    """Smallset runs a time dynamic Oppa for a small set of stocks.
    
    The 30 stocks included in this set are the 30 biggest market cap stocks as of 2021Q1.
    Some example include:
    AAPL, T, NKE, KO, ADBE, XOM, VZ, NFLX, HD, BAC
    
    Yrs_bak tells the func how many years back you want to set the present day.
    Yrs_len tells the func how many years of data you want to utilize in calculations.
    """
    
    income = minnie.macro_scrape(tick,'income-statement')
    balance = minnie.macro_scrape(tick,'balance-sheet')
    cash = minnie.macro_scrape(tick,'cash-flow-statement')
    yrlab = income.columns
    report = macro_calc(income,balance,cash,yrlab,tick)
    val_report,assum = valeria(tick,yrlab,report,yrs_bak,yrs_len)
    report = report[report.columns[yrs_bak:yrs_bak+yrs_len]]
    return (report.T,val_report,assum)


def macro_calc(income,balance,cash,yrlab,tick):
    """
    Perform a long list of calculations, and return the financial report we are interested in.

    The output is also a dataframe.
    """
##################################Income####################################
    #Extract Data of Interest for Calculations
    grpr = income.loc['Gross Profit']
    trev = income.loc['Revenue']
    #CoR = income.loc['Cost Of Goods Sold'] Not in use
    sga = income.loc['SG&A Expenses']
    pti = income.loc['Pre-Tax Income']
    dni = income.loc['Net Income']
    rnd = income.loc['Research And Development Expenses']
    ebit = income.loc['EBIT']
    inct = income.loc['Income Taxes']

    #Calculate Financials of Interest
    grm = grpr.divide(trev)
    #Cm = abs(CoR.divide(TR)) not very helpful, just 1-Gm
    sgam = abs(sga.divide(trev))
    plm = dni.divide(trev)
    rndm = abs(rnd.divide(trev))

    intpay = ebit.sub(dni).sub(inct) #Interest Payments Calculation
##################################Balance###################################
    tass = balance.loc['Total Assets']
    rec = balance.loc['Receivables']
#    tlia = balance.loc['Total Liabilities']
    std = balance.loc['Total Current Liabilities']
    ltd = balance.loc['Total Long Term Liabilities'] #Changed from 'Long Term Debt'!!!
    tdeb = ltd
    tequ = balance.loc['Share Holder Equity']
    cass = balance.loc['Total Current Assets']
    #CSO = balance.loc['    Common Shares Outstanding'] We never used this did we?

    #These are cross sheet calculations, mixing data from income with balance
    roa = dni.divide(tass)
    roe = dni.divide(tequ)
    roi = pti.divide(tdeb+tequ)
    #coc = intpay.divide(tdeb)

    crat = cass.divide(std)
    d2e = tdeb.divide(tequ)
    d2a = tdeb.divide(tass)

    #Generate blank series with correct labels to be used later
    ato = pd.Series(np.zeros(len(yrlab)),index=yrlab)
    rto = pd.Series(np.zeros(len(yrlab)),index=yrlab)
    dtc = pd.Series(np.zeros(len(yrlab)),index=yrlab)
    #Sometimes you got different length vectors for income and balance
    if len(ato) > len(tass):
        ato.pop(yrlab[0])
        trev.pop(yrlab[0])

    ##Calculated back to front of array
    i=0
    top = len(ato)-1
    ato[top]=0
    #print(ato,trev,tass)
    while i < top:
        i=i+1
        ato[top-i] = trev[top-i]/((tass[top-i+1]+tass[top-i])/2)

    i=0
    while i < top:
        rto[top]=0
        dtc[top]=0
        i=i+1
        rto[top-i] = trev[top-i]/((rec[top-i+1]+rec[top-i])/2)
        try:
            dtc[top-i] = round(365/rto[top-i])
        except ZeroDivisionError:
            dtc[top-i] = np.nan
        except ValueError:
            dtc[top-i] = np.nan
##################################Cash-Flow#################################
    ocf = cash.loc['Cash Flow From Operating Activities']*1000000
    capex = cash.loc['Net Change In Property, Plant, And Equipment']*1000000
    runkflow = ocf.add(capex)

    row_labels = ['Gross Margin','SGA Margin','RnD Margin','Profit/Loss Margin',
                  'Return on Asset','Return on Equity','Return on Investment',
                  'Current Ratio','Debt to Equity','Debt to Asset','Asset Turn Over',
                  'Receivables Turn Over','Days to Collect','Operating Cash Flow','Free-Cash-Flow']
    report = pd.DataFrame([grm,sgam,rndm,plm,roa,roe,roi,crat,
                           d2e,d2a,ato,rto,dtc,ocf,runkflow],index=row_labels)
    report.name = 'Runkle Financial Analysis Report (RFAR for ' + tick + ')'
    return report


def valeria(tick,yrlab,report,yrs_bak,yrs_len):
    """
    Utilizes the forecast, discount, and yuqi.list_avg functions to place a fair value on a given company.

    The output is another dataframe containing relevant information to the valuation calculation.
    The main metric in the output is a percentage derived from: (realPrice-fairPrice)/(fairPrice).
    If positive: overvalued by the given percent. If negative: undervalued by the given percent.
    """
    excel_file = "../docs/caps.xlsx"
    #caps = minnie.macro_caps(tick)
    caps = pd.read_excel(excel_file,sheet_name='CAPS',nrows=21,index_col=0)
    disc = 0.07
    infl = 0.02
    grow = 0.00

#    print('Discount: ',disc,'%','\nInflation: ',infl,'%','\nGrowth: ',grow,'%')

    assum = pd.DataFrame([disc,infl,grow],index=['Discount Rate: ','Inflation: ','Growth: '],
                         columns=['Fair Value Discount Assumptions'])


    #Time Dynamic Selection of Historic FCF
    yrs_max = len(yrlab)
    if yrs_len > (yrs_max-(yrs_bak-1)):
        yrs_len = (yrs_max-(yrs_bak-1))
    if yrs_bak == 0:
        fcf = report.loc['Free-Cash-Flow'][:yrs_len]
    else:
        fcf = report.loc['Free-Cash-Flow'][(yrs_bak-1):(yrs_len+yrs_bak-1)]
    #(if statement handles overselection as in going back 10 years of 12 year data and looking for 5 year history)
    #Macrotrends starts providing data at 2020, its 2021 right now, thus the extra -1.
    #ALWAYS COUNT YRS BACK FROM CURRENT YEAR YOU ARE LIVING IN, NOT VIA STUPID MACROTRENDS RECORDS

    fcf_avg = yuqi.list_avg(fcf)

###########################Actual Calculation##################################

    #Calculate forecasted and discounted CF vectors
    f_fcf = yuqi.forcast(fcf_avg,yrs_len,grow)
    d_fcf = yuqi.discount(f_fcf,yrs_len,disc)
    #Calc terminal and fair value
    t_val = f_fcf[yrs_len-1]*(1+infl)/(disc-infl)
    f_val = d_fcf.sum()+t_val #Old Discounted Cash Flow Calculation
    #f_val = fcf_avg/disc

    #Find the 'Current' actual price, either live or dated.
    if yrs_bak == 0:
        mcap = pdr.data.get_quote_yahoo(tick)['marketCap'][0]
        shares = pdr.data.get_quote_yahoo(tick)['sharesOutstanding'][tick]
        price = pdr.data.get_quote_yahoo(tick)['regularMarketPreviousClose'][0]
        #Live error is the percentage difference between Market Cap derived stock price
        # and the previous close stock price.
        error = round(np.abs(((mcap/shares)-price)/price),3)
#        print('Live error: ',error,'\n')
    else:
#        print(caps.loc[(int(datetime.date.today().year)-yrs_bak)],'\n^^^ MarketCap, Time @ end of Year Shown ^^^')
        mcap = caps[tick][(int(datetime.date.today().year)-yrs_bak)]
        stupid_param = str(int(datetime.date.today().year) - (yrs_bak-1)) #This is insane.
        #I really need to figure this out someday...
        #You see, two different data sources have different levels of current... It messes up indexing.
        if '.' in tick:
            tick=tick.replace('.','-')
        link = 'https://query1.finance.yahoo.com/v8/finance/chart/'+tick+'?interval=1mo&range='+str(yrs_bak+1)+'y'

        r = requests.get(link)
        time = r.json()['chart']['result'][0]['timestamp']
        high = r.json()['chart']['result'][0]['indicators']['quote'][0]['high']
        low = r.json()['chart']['result'][0]['indicators']['quote'][0]['high']

        i=0
        for t in time:
            timestamp = datetime.datetime.fromtimestamp(int(t))
            if stupid_param+'-01' in timestamp.strftime('%Y-%m-%d %H:%M:%S'):
#                print('Time of price: ',timestamp.strftime('%Y-%m-%d %H:%M:%S'))
                price = (high[i]+low[i])/2
            i+=1
        shares = round(mcap/price)
        error = 0
#        print('Stupid error, code later: ',error,'\n')

    f_price = f_val/shares
    f_price = round(f_price,2)

######################################################################

    if len(fcf) >= 5:
        qk_sc = yuqi.list_avg(fcf[:5])/0.07
    else:
        qk_sc = yuqi.list_avg(fcf)/0.07
        print(f"Limited data. Calculating Quick Screen from {len(fcf)} yrs of data")
        #Quick Screen Value, present cash over expected return

    if f_val > 0:
#        print('Fair Value: ',f_val,'\nFair Price: ',f_price,
#              '\n\nMarket Cap: ',mcap,'\nStock Price: ',price,'\n')
        valuation = (mcap-f_val)/(f_val)
        if valuation < 0:
#            print('Stock Under-Priced By: ',round(valuation*100),'%')
            col = ['Fair Valuation, Cash Discounted Method']
            ind = ['Fair Value','Fair Price','Market Cap','Stock Price',
                   'Stock Under-Priced By','Years of Data Used','Quick Screen Value (5 year avg)']
            val_report = pd.DataFrame([yuqi.num_form(f_val,'big'),yuqi.num_form(f_price,'doll'),yuqi.num_form(mcap,'big'),
                                       yuqi.num_form(price,'doll'),yuqi.num_form(valuation,'perc'),len(fcf),
                                       yuqi.num_form(qk_sc,'big')],columns=col, index=ind)
        else:
#            print('Stock Over-Priced By: ',round(valuation*100),'%')
            col = ['Fair Valuation, Cash Discounted Method']
            ind = ['Fair Value','Fair Price','Market Cap','Stock Price',
                   'Stock Over-Priced By','Years of Data Used','Quick Screen Value (5 year avg)']
            val_report = pd.DataFrame([yuqi.num_form(f_val,'big'),yuqi.num_form(f_price,'doll'),yuqi.num_form(mcap,'big'),
                                       yuqi.num_form(price,'doll'),yuqi.num_form(valuation,'perc'),len(fcf),
                                       yuqi.num_form(qk_sc,'big')],columns=col, index=ind)
    else:
#        print('Average Free Cash Flow is NEGATIVE. Valuation Statement is Meaningless')
#        print('\n\nMarket Cap: ',mcap,'\nStock Price: ',stock,'\n')
        col = ['Fair Valuation, Cash Discounted Method']
        ind = ['Average Free Cash Flow is NEGATIVE. Valuation Statement is Meaningless',
               'Market Cap: ','Stock Price: ']
        val_report = pd.DataFrame([np.nan,yuqi.num_form(mcap,'big'),price],columns=col, index=ind)
    return(val_report,assum)

def condense(val_report,hist_len,yrs_bak,report):
    """Condenses the very long financial analysis report into four key metrics.

    Needs the value report from the valuation function and report from calc.
    Also need to pass it how many years back you are simulating and the length
    of historical data you wish to use.

    Common parameters for hist_len and yrs_bak are 10 and 0 OR 5 and 5."""
    try:
        val = val_report.loc['Stock Under-Priced By'][0]
    except KeyError:
        try:
            val = val_report.loc['Stock Over-Priced By'][0]
        except KeyError:
            val = 0.0

    #print('Calculating prof,cap,eff')
    if hist_len+yrs_bak >= len(report.columns):
        if yrs_bak >= len(report.columns):
            print('Cannot go that far back, not enough data on record')
        else:
            hist_len = len(report.columns)-yrs_bak

    yrs=[]
    for i in range(hist_len):
        yrs.append(report.columns[yrs_bak+(i-1)])

    prof = (report.loc['Return on Asset'][yrs].mean()+
              report.loc['Return on Equity'][yrs].mean()+
              report.loc['Return on Investment'][yrs].mean())/3

    cap = (report.loc['Debt to Equity'][yrs].mean()+
                report.loc['Debt to Asset'][yrs].mean())/2

    eff = report.loc['Asset Turn Over'][yrs].mean()

    return (val,prof,cap,eff)
