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
    if np.abs(num) >= 1000000 and num <= 999999999:
        fnum = str(round(num/1000000,3))+' M'
    if np.abs(num) >= 1000000000 and num <= 999999999999:
        fnum = str(round(num/1000000000,3))+' B'
    if np.abs(num) >= 1000000000000:
        fnum = str(round(num/1000000000000,3))+' T'
    return fnum

def num2perc(num):
    return str(round(num*100,3))+'%'

def num2doll(num):
    return '$'+str(round(num,2))

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
        rnum = float(num.replace('%','')) /100   
    elif style == 'doll':
        rnum = float(num.replace('$',''))
    else:
        rnum = f"Style {style} not recognize"
    return rnum

########################################Single fcts better for DataFrames...##########################################

def exp_for(fcf,yrs_len,grow):
    """Forecast the growth of cash flow with a set power growth rate."""
    
    fcf_avg = list_avg(fcf)
    i=0
    f_fcf = np.zeros(yrs_len)
    f_fcf[0] = fcf_avg
    while i < (yrs_len-1):
        f_fcf[i+1] = f_fcf[i]*(1+grow)
        i=i+1
    return f_fcf

def lin_for(fcf,yrs_len):
    """Forecast future cash flow with linear extrapolation."""
    
    slope,intercept = soojin.linfit(fcf)
    
    i=0
    f_fcf = np.zeros(yrs_len)
    f_fcf[0] = fcf[(len(fcf)-1)]+slope
    while i < (yrs_len-1):
        f_fcf[i+1] = f_fcf[i]+slope
        i+=1
    return f_fcf

def discount(f_fcf,yrs_len,disc):
    """
    Discount each year in the forecasted cash flow by a power law.

    The discount percent is related to the time value of money.
    What could you be doing with money you had right now?
    """
    i=0
    d_fcf = np.zeros(yrs_len)
    for y in range(yrs_len):
        d_fcf[i] = f_fcf[i]/(1+disc)**(y+1)
        i=i+1
    return d_fcf

def valeria(fcf,mcap,params,style):
    """
    Utilizes the forecast, discount, and list_avg functions to place a fair value on a given company.

    Params is a 4 element tuple containing params in the following order:
    disc, infl, grow, yrs_len
    Style is 1 or 0. Choose 0 for power forecast of FCF, 1 for linear extrapolation forecast.
    
    The output is another dataframe containing relevant information to the valuation calculation.
    The main metric in the output is a percentage derived from: (realPrice-fairPrice)/(fairPrice).
    If positive: overvalued by the given percent. If negative: undervalued by the given percent.
    """
    
    if len(params) == 4:
        disc = params[0]
        infl = params[1]
        grow = params[2]
        yrs_len = params[3]
    else:
        print('Need 4 params to run: Disc, Infl, Grow, Yrs_len (future forecast)')
        return

###########################Actual Calculation##################################

    #Guessing the future
    if style == 0:
        f_fcf = exp_for(fcf,yrs_len,grow)
    elif style == 1:
        f_fcf = lin_for(fcf,yrs_len)
    #Accounting for time value of money in discounting
    dcf = discount(f_fcf,yrs_len,disc)
    #Calculating terminal value with Perpetuity method
    tval = (f_fcf[yrs_len-1]*(1+infl))/(disc-infl)
    #Summing values
    fval = dcf.sum()+tval

######################################################################

    qk_sc = list_avg(fcf[:5])/0.07
    print(f"Quick screen: {qk_sc}")

    if fval > 0:
        valuation = (mcap-fval)/(fval)
        if valuation < 0:
            print(f"Stock Under-Priced By: {num2perc(valuation)}")
        else:
            print(f"Stock Over-Priced By: {num2perc(valuation)}")
    else:
        print('Average Free Cash Flow is NEGATIVE. Valuation Statement is Meaningless')
        print(f"tval: {tval}, fval: {fval}, f_fcf: {f_fcf}, dcf: {dcf}")
        valuation = 0
    return valuation