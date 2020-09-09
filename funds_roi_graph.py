import requests
import pandas as pd
from datetime import datetime
import yfinance as yf
import numpy as np
from pycoingecko import CoinGeckoAPI

def get_fund_ROI(address, file_name):
    sent = requests.get('https://api.bloxy.info/widget/address_value_daily?address=' + address + '&currency=ETH&key=ACCunOMWYpmCp&format=table&price_currency=USD').json()
    df1 = pd.DataFrame(sent)
    df1.rename(columns={0:'Date-USD', 11: 'ROI'}, inplace=True)
    df1['ROI-USD'] = df1.ROI.cumsum()

    sent = requests.get('https://api.bloxy.info/widget/address_value_daily?address=' + address + '&currency=ETH&key=ACCunOMWYpmCp&format=table&price_currency=ETH').json()
    df2 = pd.DataFrame(sent)
    df2.rename(columns={0:'Date', 11: 'ROI'}, inplace=True)
    df2['ROI-ETH'] = df2.ROI.cumsum()

    df = pd.concat([df1, df2], axis=1, sort=False)[['Date', 'ROI-USD', 'ROI-ETH']]
    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    
    cmc = yf.Ticker("^CMC200")

    hist = cmc.history(period="max")[['Open']]
    hist['Open'] = (np.where(hist['Open'] < 100, hist['Open'] * 10, hist['Open']))

    df = pd.concat([df, hist], axis=1, sort=False)
    df = df.interpolate(axis=0).dropna(subset=['ROI-USD'])
    
    start_cmc200 = df.head(1)['Open'][0]
    df['CMC200-USD'] = (((df['Open'] - start_cmc200) / start_cmc200)*100)
    df = df[['ROI-USD', 'ROI-ETH', 'CMC200-USD']]
    
    cg = CoinGeckoAPI()

    data = cg.get_coin_market_chart_by_id('bitcoin', 'eth', 500)

    dates = [datetime.fromtimestamp(data['prices'][i][0] / 1000).strftime('%Y-%m-%d') for i in range(len(data['prices']))]
    price  = [data['prices'][i][1] for i in range(len(data['prices']))]

    df_data = {'BTC-ETH': price, 'Date' : dates} 
    df_btc = pd.DataFrame(df_data)
    df_btc = df_btc.set_index('Date')
    df_btc.index = pd.to_datetime(df_btc.index)
    
    df = pd.concat([df, df_btc], axis=1, sort=False)
    df = df.dropna(subset=['ROI-USD'])
    
    start_btc = df.head(1)['BTC-ETH'][0]
    df['BTC-ETH'] = (((df['BTC-ETH'] - start_btc) / start_btc)*100)
    
    df.drop(df.tail(1).index,inplace=True)
    
    df.to_csv(file_name, index=True)
    
def main():
    get_fund_ROI('0xCB60D600160D005845Ec999f64266D5608fd8943', 'Fnd.csv')
    get_fund_ROI('0x9C49c053a8b9106024793516EE3c5562875A5C9a', 'Anastasia.csv')
    get_fund_ROI('0x0d9596Afc608B3322A17118A573750045F52C0B8', 'Malta.csv')

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    f = open("run_log.txt","a")
    f.write("Ran at " + dt_string + "\n")
    f.close() 


def test():
    fundToken = '0x36c4abec6166b5009b0abf493ef4500d76eb02d4'

    sent = requests.get('https://api.bloxy.info/money_flow/transfers?address=0x0a27a978dfe58659d724ae96d9f25b7ed6b4fd97&chain=eth&token=0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2&direction=all&key=ACCunOMWYpmCp&format=table').json()
    tokenDist = pd.DataFrame(sent)
    investmentTx = tokenDist[tokenDist[3] == '0x0d9596afc608b3322a17118a573750045f52c0b8'][[1, 4, 6]]

    # sent = requests.get('https://api.bloxy.info/widget/address_value_daily?address=' + '0x0d9596Afc608B3322A17118A573750045F52C0B8' + '&currency=ETH&key=ACCunOMWYpmCp&format=table&price_currency=USD').json()
    # df1 = pd.DataFrame(sent)
    # df1.rename(columns={0:'Date-USD', 11: 'ROI'}, inplace=True)
    # df1['ROI-USD'] = df1.ROI.cumsum()
    # print(df1)

    investmentTx[1] = pd.to_datetime(investmentTx[1]).dt.strftime('%y-%m-%d')
    # investmentTx[1] = investmentTx[1].dt.strftime('%y-%m-%d')
    print(investmentTx)



if __name__ == '__main__':
    test()
