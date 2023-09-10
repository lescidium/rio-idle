"""File I/O and Scraping."""
import re
import urllib.request as ur
from urllib.error import HTTPError
import pandas as pd
from bs4 import BeautifulSoup
import soojin
import yuqi
import numpy as np
from socket import timeout

def yahoo_fcf(tick):
    soup = scrape(f"https://finance.yahoo.com/quote/{tick}/cash-flow?p={tick}")
    data = scout(soup,'div',output=False)

    table = data[0]

    groups = scout(table,'span',output=False)

    ind=0
    for g in groups:
        if g.text == 'Free Cash Flow':
            break
        ind +=1

    ind +=2 #Skip the title and TTM
    fcf=[]
    while ind < 10000: #Iterating Loop with some arbitrary condition
        if groups[ind].text == 'Learn more':
            break
        else:
            fcf.append(int(groups[ind].text.replace(',',''))*1000)
        ind +=1

        avg = yuqi.list_avg(fcf)
        trend = yuqi.num2perc(soojin.linfit(fcf)[0]/np.abs(avg))

    return (avg,trend,len(fcf))

def macro_fcf(tick):
    soup = scrape(f"https://www.macrotrends.net/stocks/charts/{tick}/CHINGUS/free-cash-flow")
    data = scout(soup,'div',output=False)

    ind = 0
    for d in data:
        if len(d.text) > 1000:
            div = d
            break
        ind +=1

    tables = scout(div,'tbody',output=False)
    ann = tables[0]
    qtr = tables[1]

    ann1 = scout(ann,'td',output=False)

    fcf=[]
    i=1
    while i < len(ann1):
        fcf.append(ann1[i].text)
        i+=2
        if len(fcf) > 4:
            break


    qtr1 = scout(qtr,'td',output=False)

    ind=0
    for q in qtr1:
        if q.text == fcf[0]:
            break
        ind+=1

    fcfQ=[]
    if ind > 2: #check to make sure there are new quarters
        ind-=2 #jump back to the quarter nearest the most recent annual statement
        while ind > 0:
            fcfQ.append(qtr1[ind].text)
            ind-=2
        extrp = (float(fcfQ[len(fcfQ)-1].replace(',',''))*1000000/len(fcfQ))*4 #extrapolated quarters
        fcf.pop(len(fcf)-1)
        temp=[]
        for f in fcf:
            temp.append(float(f.replace(',',''))*1000000)
        fcf = temp
        fcf.insert(0,extrp)
    else:
        temp=[]
        for f in fcf:
            temp.append(float(f.replace(',',''))*1000000)
        fcf = temp

    avg = yuqi.list_avg(fcf)
    trend = yuqi.num2perc(soojin.linfit(fcf)[0]/np.abs(avg))

    return (avg,trend,len(fcf))

def macro_scrape(tick,sheet):
    """
    Scrapes data from the Macrotrend website according to the company and financial statement.

    The financial statements data on Macrotrends is written within a javascript.
    Therefore you cannot isolate the desired data with the simple BS4 find_all function.
    We crack the fruit open with regex.
    The output is a pandas dataframe, a table with all the data in a given financial statement.
    """
    #print(os.getcwd())
    file = pd.read_table('../docs/ticker.txt',header=None)   #SEC official tik-2-cik map
    tick_list=[]
    if isinstance(tick,str) is False:
        raise TypeError('The ticker input is the wrong data type.')
    if isinstance(sheet,str) is False:
        raise TypeError('The sheet input is the wrong data type.')

    for fil in file[0]:
        tick_list.append(str(fil).upper())

    if tick not in tick_list:
        raise ValueError("{0} company does not exist".format(tick))



    url = 'https://www.macrotrends.net/stocks/charts/'+ tick + '/hyung/' + sheet
#     print(url)
    try:
        read = ur.urlopen(url).read()
    except HTTPError:
        print('HTTPError (Probably 403 Access Denied). Trying again with User-Agent set to Mozilla')
        req = ur.Request(url=url,headers={'User-Agent': 'Mozilla/5.0'})
        read = ur.urlopen(req).read()
    soup = BeautifulSoup(read,'lxml')

    mydat = soup.find_all('script')
    listy=[]
    for d in mydat:
        listy.append(len(str(d)))
    ind = listy.index(max(listy))
    takara = mydat[ind] #This is the element with the table data
    gomi = str(takara.string)

    num = re.compile('"?,"?([0-9-]+)"?:"?([0-9.-]*)')
    lbl = re.compile(r'>(\w.*?)<')

    numz = num.findall(gomi)
    labs = lbl.findall(gomi)
    numz = np.array(numz)

    #################################
    # if len(labs) == 0:
    #     return(1,0)
    # #This is a special check to see if financial statements available for the given ticker
    #################################

    yrs = int(numz.shape[0]/len(labs))
    #print('Years on Record: ',yrs,'\nNumber of Financial Elements: ',
    #      len(labs),'\nTotal Data Points: ',numz.shape[0])

    i=0
    yrlab = []
    while i < yrs:
        yrlab.append(numz[i][0])
        i=i+1
    dat = np.zeros((len(labs),yrs))

    numbers = pd.DataFrame(numz)
    numbers = numbers.replace('',np.nan)

    k=0
    i=0
    while i < len(labs):
        j=0
        while j < yrs:
            dat[i][j] = numbers[1][j+k]
            j=j+1
        k=j+k
        i=i+1

    dat = pd.DataFrame(dat,index=labs,columns=yrlab)
    return dat

def macro_prices(TICK,shares):
    soup = scrape(f"https://www.macrotrends.net/stocks/charts/{TICK}/minnie/stock-price-history")
    divs = scout(soup,'div',output=False)
    i=0
    for d in divs:
        if len(d.text) > 1000:
            ind = i
            break
        i+=1

    tds = scout(divs[ind],'td',output=False)
    #ths = scout(divs[ind],'th') Use these to fix index issues if they ever arise

    inds = np.linspace(0,7*(len(shares)-1),len(shares),dtype=int)

    listy=[]
    i=0
    for i in inds:
        listy.append([tds[i].text,tds[i+1].text])

    ray = np.array(listy).astype(float)


    ydat = pd.DataFrame(shares)
    ydat.insert(1,'Avg Annual Price',ray[:,1])
    ydat.insert(2,'Market Cap',ydat['Shares Outstanding']*ydat['Avg Annual Price'])
    return ydat

def scrape(url,fancy=False):
    """Scrapes a messy soup object from any url.

    I recommend using control+F on the output of this function to find the data you are looking for.
    Then you can see what tag it's associated with. (Alternatively, code something up with RegEx)
    Then use the scout function to find the index positioning of that data.

    If you wanna work manually you can use: soup.find_all(tag) and I'm sure it will all come back to you."""

    if fancy == False:
        read = ur.urlopen(url).read()       #Reads a whole big string mess
        soup = BeautifulSoup(read,'lxml')   #Transforms string mess intro workable object: Soup
    else:
        req = ur.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            read = ur.urlopen(req,timeout=3).read()       #Reads a whole big string mess
        except timeout:
            return None
        soup = BeautifulSoup(read,'lxml')   #Transforms string mess intro workable object: Soup
    return soup

def scout(soup,tag,output=True,tagclass=None):
    """Scouts messy soup for your tag of choice and places an index by each one.

    Here a several common tags: div, td, script, tr.
    tr  --> Tables
    div --> Macroscopic resolution
    td  --> Microscopic resolution
    script --> Volatile page elements
    This function returns the results list."""
    if tagclass == None:
        result = soup.find_all(tag)
    else:
        result = soup.find_all(tag,{"class":tagclass})

    if output == True:
        i=0
        for r in result:
            print(i,len(r.text),r.text)
            i+=1
    return result

def ez_read(file):
    with open(file, "r") as f:
        dat = f.read()
    return dat

def ez_write(data,file,opt):
    """Writes any object into a file.

    Currently this only supports simple strings and lists.
    However the idea in the long term is a flexible writer where you can
    pass the function any object and it will write it into any file type
    you wish.
    """

    if type(data) is str:
        with open(f"{file}",opt,encoding='utf8') as file:
            file.write(data)
    elif type(data) is list or type(data) is pd.core.series.Series:
        with open(f"{file}",opt,encoding='utf8') as file:
            for d in data:
                file.write(str(d))
                file.write('\n')
    else:
        data = str(data)
        with open(f"{file}",opt,encoding='utf8') as file:
            file.write(data)

    return ('File closed: ',file.closed)

def write(report, val_report, assum, macurl,tick):
    """
    Write the collection of reports into an excel file.

    The output lets you know the program has finished running successfully.
    """

    title = '../docs/' + tick + '_report.xlsx'
    writer = pd.ExcelWriter(title,engine='xlsxwriter')
    workbook=writer.book
    worksheet=workbook.add_worksheet('Report')
    writer.sheets['Report'] = worksheet

    worksheet.write_string(0, 0, report.name)
    report.to_excel(writer,sheet_name='Report',startrow=1 , startcol=0)

    worksheet.write_string(report.shape[0] + 3, 3, macurl)

    val_report.to_excel(writer,sheet_name='Report',startrow=report.shape[0] + 5, startcol=0)

    assum.to_excel(writer,sheet_name='Report',startrow=report.shape[0] + 5, startcol=5)

    try:
        writer.save()
        result = 'Successfully created, wrote, and saved the report file.'
    except Exception as e:
        result = ("""Error: {0}\nThat path probably doesn\'t exist.\n
        Or its some environment issue because the code is being ran from the wrong directory.""".format(e))
        return result


    return result
