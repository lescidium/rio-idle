"""Maths package, because Yuqi is a genius."""
import numpy as np
import time
import soojin
from IPython.display import clear_output

LABELS = ['ROI - Return On Investment','ROA - Return On Assets','ROE - Return On Equity',
       'Asset Turnover','Inventory Turnover Ratio','Receiveable Turnover',
       'Long-term Debt \/ Capital','Debt\/Equity Ratio']

def calc_ratios(tick,ratios,yrs_bak,yrs_len,lbls=LABELS):
    """Calculates averages and trends on key financial ratios for a given time range.
    
    Don't forget to give the function the ratios you scraped with macro_scrape"""
    try:
        if ratios.shape[1] >= (yrs_bak+yrs_len):
            record=[]
            record.append(tick)
            for l in lbls:
                dat = ratios.loc[l][(yrs_bak):(yrs_bak+yrs_len)]
                avg = round(list_avg(list(dat.dropna())),3)
                record.append(avg)
                try:
                    trend = soojin.linfit(dat)[0]
                except TypeError:
                    print(f"I believe {l} in {tick} is completely blank for this date range")
                    trend = 0
                record.append(trend)        
    #         roa = yuqi.list_avg(list(ratios.loc['ROA - Return On Assets'][:5].dropna()))
    #         roa = yuqi.list_avg(list(ratios.loc['ROA - Return On Assets'][:5].dropna()))
    #         roe = yuqi.list_avg(list(ratios.loc['ROE - Return On Equity'][:5].dropna()))
    #         ato = yuqi.list_avg(list(ratios.loc['Asset Turnover'][:5].dropna()))
    #         ito = yuqi.list_avg(list(ratios.loc['Inventory Turnover Ratio'][:5].dropna()))
    #         rto = yuqi.list_avg(list(ratios.loc['Receiveable Turnover'][:5].dropna()))
    #         d2a = yuqi.list_avg(list(ratios.loc['Long-term Debt \/ Capital'][:5].dropna()))
    #         d2e = yuqi.list_avg(list(ratios.loc['Debt\/Equity Ratio'][:5].dropna()))
        else:
            print(f"{tick} is smol. Only {ratios.shape[1]} years on record.")
            return 0
    except AttributeError:
        print(f"{tick} has attribute error. Probably HTML404ERROR")

    return record

def simple_grow(dat):
    return (dat[0]/dat[len(dat)-1]-1)/len(dat)

def fit_grow(dat):
    slope,intercept = soojin.linfit(dat)
    avg = list_avg(dat)
    return slope/avg

def runk_grow(dat):
    ann_perc=[]
    for i in range(len(dat)):
        ann_perc.append(dat[i]/dat[i-1]-1)
    return list_avg(ann_perc)

def grow4(dat):
    return (dat[0]/dat[len(dat)-1])**(1/len(dat))-1

def timer(i,total,start,steps):
    """Work in progress.
    
    Meant to run within a loop, tell you how close the loop is to finishing.
    Put this code at the top of your loop:
    import time
    start = time.time()
    steps = []
    i=0
    """    
    if i == 0:
        print('Setting Timer!!!')
        if total > 100:
            step = np.floor(round(total/100))
            top = 100
        else:
            step = 1
            top = total
        steps=[]
        for n in np.linspace(1,top,top):
            steps.append(int(step*n))
    else:
        if i in steps:
            
            perc = i/total
            raw = time.time()-start
            time_elps = time_form(raw)
            eta = time_form(raw/perc-raw)
            per = round(raw/i,3)
            clear_output()
            print(f"Seconds per loop: {per}\nTime Elapsed: {time_elps[0]} min, {time_elps[1]} sec\n")
            print(f"Percent complete: {perc}\nEstimated Time Left: {eta[0]} min, {eta[1]} sec")
    return(steps)

def list_avg(listy):
    """Take an average of a given list."""
    try:
        ans = sum(listy) / len(listy)
    except ZeroDivisionError:
        ans = np.nan
    return ans

def time_form(raw):
    mins = np.floor(raw/60)
    return [mins,(raw-mins*60)]

########################################Single fcts better for DataFrames...##########################################

def num2MBT(num):
    if num >= 1000000 and num <= 999999999:
        fnum = str(round(num/1000000,3))+' M'
    if num >= 1000000000 and num <= 999999999999:
        fnum = str(round(num/1000000000,3))+' B'
    if num >= 1000000000000:
        fnum = str(round(num/1000000000000,3))+' T'
    return fnum

def num2perc(num):
    return str(round(num*100,3))+'%'

def num2doll(num):
    return '$'+str(round(num,2))

def num_form(num,style):
    """Format a variety numbers into readable strings."""
    
    if style == 'big':
        if num >= 1000000 and num <= 999999999:
            fnum = str(round(num/1000000,3))+' M'
        if num >= 1000000000 and num <= 999999999999:
            fnum = str(round(num/1000000000,3))+' B'
        if num >= 1000000000000:
            fnum = str(round(num/1000000000000,3))+' T'
    elif style == 'perc':
        fnum = str(round(num*100,3))+'%'    
    elif style == 'doll':
        fnum = '$'+str(round(num,2))
    else:
        fnum = f"Style {style} not recognize" 
            
    return fnum

def num_raw(num,style):
    """Reverse process of num_form function."""
    
    if style == 'big':
        print(num)
        if 'M' in num:
            rnum = float(num.replace(' M',''))*1000000
        elif 'B' in num:
            rnum = float(num.replace(' B',''))*1000000000
        elif 'T' in num:
            rnum = float(num.replace(' T',''))*1000000000000
    elif style == 'perc':
        rnum = float(num.replace('%',''))    
    elif style == 'doll':
        rnum = float(num.replace('$',''))
    else:
        rnum = f"Style {style} not recognize"
    return rnum

########################################Single fcts better for DataFrames...##########################################

def forcast(fcf_avg,yrs_len,grow):
    """
    Forecast the growth of cash flow by the desired amount of years.

    The length of years is usually anywhere from five to ten.
    Growth is a parameter set outside the function and usually is pessimistically set to zero.
    """
    i=0
    f_fcf = np.zeros(yrs_len)
    f_fcf[0] = fcf_avg
    while i < (yrs_len-1):
        f_fcf[i+1] = f_fcf[i]*(1+grow)
        i=i+1
    return f_fcf

def discount(f_fcf,yrs_len,disc):
    """
    Discount each year in the forecasted cash flow by a power law.

    The discount percent is the return you want to see in your investment, often set to 7%.
    """
    i=0
    d_fcf = np.zeros(yrs_len)
    for yer in range(yrs_len):
        d_fcf[i] = f_fcf[i]/(1+disc)**(yer+1)
        i=i+1
    return d_fcf

def valeria(fcf,caps):
    """
    Utilizes the forecast, discount, and list_avg functions to place a fair value on a given company.

    The output is another dataframe containing relevant information to the valuation calculation.
    The main metric in the output is a percentage derived from: (realPrice-fairPrice)/(fairPrice).
    If positive: overvalued by the given percent. If negative: undervalued by the given percent.
    """
    disc = 0.07
    infl = 0.02
    grow = 0.00
#    print('Discount: ',disc,'%','\nInflation: ',infl,'%','\nGrowth: ',grow,'%')
    assum = pd.DataFrame([disc,infl,grow],index=['Discount Rate: ','Inflation: ','Growth: '],
                         columns=['Fair Value Discount Assumptions'])

    fcf_avg = list_avg(fcf)

###########################Actual Calculation##################################

    #Calculate forecasted and discounted CF vectors
    f_fcf = forcast(fcf_avg,yrs_len,grow)
    d_fcf = discount(f_fcf,yrs_len,disc)
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
        qk_sc = list_avg(fcf[:5])/0.07
    else:
        qk_sc = list_avg(fcf)/0.07
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
            val_report = pd.DataFrame([num_form(f_val,'big'),num_form(f_price,'doll'),num_form(mcap,'big'),
                                       num_form(price,'doll'),num_form(valuation,'perc'),len(fcf),
                                       num_form(qk_sc,'big')],columns=col, index=ind)
        else:
#            print('Stock Over-Priced By: ',round(valuation*100),'%')
            col = ['Fair Valuation, Cash Discounted Method']
            ind = ['Fair Value','Fair Price','Market Cap','Stock Price',
                   'Stock Over-Priced By','Years of Data Used','Quick Screen Value (5 year avg)']
            val_report = pd.DataFrame([num_form(f_val,'big'),num_form(f_price,'doll'),num_form(mcap,'big'),
                                       num_form(price,'doll'),num_form(valuation,'perc'),len(fcf),
                                       num_form(qk_sc,'big')],columns=col, index=ind)
    else:
#        print('Average Free Cash Flow is NEGATIVE. Valuation Statement is Meaningless')
#        print('\n\nMarket Cap: ',mcap,'\nStock Price: ',stock,'\n')
        col = ['Fair Valuation, Cash Discounted Method']
        ind = ['Average Free Cash Flow is NEGATIVE. Valuation Statement is Meaningless',
               'Market Cap: ','Stock Price: ']
        val_report = pd.DataFrame([np.nan,num_form(mcap,'big'),price],columns=col, index=ind)
    return(val_report,assum)