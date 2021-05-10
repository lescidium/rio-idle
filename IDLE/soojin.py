import numpy as np
import yuqi
import pandas as pd
from sklearn.linear_model import LinearRegression

def make_y(prices,income,cash,ratios):
    """Formats a dataframe for several choice labels."""
    Yrray = prices.drop(columns=['Shares Outstanding'])
    #Use both price and cap b/c both have a possibility of being off

    pti = income.loc['Pre-Tax Income']*1000000
    
    ocf = cash.loc['Cash Flow From Operating Activities']*1000000
    capex = cash.loc['Net Change In Property, Plant, And Equipment']*1000000
    fcf = ocf.add(capex)
    
    roi = ratios.loc['ROI - Return On Investment']

    Yrray.insert(2,'Pre-Tax Income',pti)
    Yrray.insert(3,'Free Cash Flow',fcf)
    Yrray.insert(4,'ROI',roi)
    return Yrray

def linfit(series):
    """Fits a pandas series of data.
    
    The reason it is a series and not a list, it that if we have
    a set of data with an empty entry, we should not contract the
    x-distance between these two points artifically when popping of NaNs.
    Honestly this could probably work with a list though...
    BUT the operations we can use with Data frames is really nice, like inserting
    a column of integers to do the fit with..."""
    a = pd.DataFrame(series)
    a.insert(1,'int',np.linspace(len(a),1,len(a)))
    a = a.dropna()
    #print(a)
    if len(a) > 0:
        model = LinearRegression()
        model.fit(np.array(a['int']).reshape(-1,1), a[a.columns[0]])
    else:
        return 0
    return (round(model.coef_[0],3),round(model.intercept_,3))


def runit(model,loo,xrray,yrray):
    """Runs simple machine learning models on data set.

    The model input should be a model object built from the many choices
    available in scikit learn.

    The loo is just the LeaveOneOut init object from scikit learn.

    Xrray and Yrray are your input and output respectively of the
    multivariable function you are attempting to fit. They should be
    simply numpy arrays (m by N and 1 by N).
    """
    results=[]
    for train_index, test_index in loo.split(xrray):
        x_train, x_test = xrray[train_index], xrray[test_index]
        y_train, y_test = yrray[train_index], yrray[test_index]

        model.fit(x_train,y_train)
        y_guess = model.predict(x_test)
        error = np.abs(y_guess-y_test)
        results.append(error)

    return calc.list_avg(results)

def sigmoid(dep,a,b,c):
    """Normalizes inputs via a sigmoid."""
    ans = a*(1-1/(1+np.exp(b*(dep+c))))
    if ans < .001:
        ans = 0
    ans = round(ans,3)
    return ans

def score(val,prof,cap,eff):
    """Normalizes a set of financial metrics with specially set parameters."""
    return (sigmoid(val,1,-25,0.45)+sigmoid(prof,1,30,-0.1)+
            sigmoid(cap,1,-20,-0.5)+sigmoid(eff,1,4,-0.75))/4
    