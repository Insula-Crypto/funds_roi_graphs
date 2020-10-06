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
    Malta('Malta.csv')

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    f = open("run_log.txt","a")
    f.write("Ran at " + dt_string + "\n")
    f.close() 


def Malta(file_name):

    # Get the NAV, and sharePrice of the fund on each priceUpdate
    jsonData = '{"query": "{fundCalculationsHistories(where: {fund: \\"0x26491fc7da30b35d818de45982fb1de4f65ed8f5\\"}) { nav, timestamp, totalSupply, source}}"}'
    data = requests.post('https://api.thegraph.com/subgraphs/name/melonproject/melon', data = jsonData).json()['data']

    roi = []
    nav = []
    timestamp = []

    for i in range(len(data['fundCalculationsHistories'])):
        if (data['fundCalculationsHistories'][i]['source'] == 'priceUpdate'):
            roi.append(int(data['fundCalculationsHistories'][i]['nav']) / int(data['fundCalculationsHistories'][i]['totalSupply']))
            nav.append(int(data['fundCalculationsHistories'][i]['nav']) / 1e18)
            timestamp.append((int(data['fundCalculationsHistories'][i]['timestamp'])))

    while (len(data['fundCalculationsHistories']) == 100):
        jsonData = '{"query": "{fundCalculationsHistories(where: {fund: \\"0x26491fc7da30b35d818de45982fb1de4f65ed8f5\\", timestamp_gt:\\"' + str(timestamp[-1]+1) + '\\"}) { nav, timestamp, totalSupply, source}}"}'
        data = requests.post('https://api.thegraph.com/subgraphs/name/melonproject/melon', data = jsonData).json()['data']

        for i in range(len(data['fundCalculationsHistories'])):
            if (data['fundCalculationsHistories'][i]['source'] == 'priceUpdate'):
                roi.append(int(data['fundCalculationsHistories'][i]['nav']) / int(data['fundCalculationsHistories'][i]['totalSupply']))
                nav.append(int(data['fundCalculationsHistories'][i]['nav']) / 1e18)
                timestamp.append((int(data['fundCalculationsHistories'][i]['timestamp'])))


    df1 = pd.DataFrame({'NAV': nav, 'ROI-ETH': roi}, index=timestamp)


    # Get the price of USDC on each price update
    jsonData = '{"query": "{assetPriceHistories(where: {asset: \\"0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48\\", , timestamp_gt: \\"' + str(timestamp[0] - 1) + '\\"}) {price, timestamp}}"}'
    data = requests.post('https://api.thegraph.com/subgraphs/name/melonproject/melon', data = jsonData).json()['data']

    price = []
    timestamp = []

    for i in range(len(data['assetPriceHistories'])):
        price.append(int(data['assetPriceHistories'][i]['price']) / 1e18)
        timestamp.append((int(data['assetPriceHistories'][i]['timestamp'])))

    df2 = pd.DataFrame(price, index=timestamp, columns=['USD-ETH'])

    df = pd.concat([df1, df2], axis=1, sort=False)

    df['ROI-USD'] = ((df['ROI-ETH'] / df['USD-ETH']) / (1 / df.iloc[0]['USD-ETH']) - 1) * 100
    df['ROI-ETH'] = (df['ROI-ETH'] - 1) * 100
    df.index = pd.to_datetime(df.index, unit='s').strftime('%Y-%m-%d')
    df = df[~df.index.duplicated(keep='first')]
    df.index.name = 'Date'

    df.to_csv(file_name[:-4] + '_raw.csv', index=True)
        
    cmc = yf.Ticker("^CMC200")

    hist = cmc.history(period="max")[['Open']]
    hist['Open'] = (np.where(hist['Open'] < 100, hist['Open'] * 10, hist['Open']))
    hist.index = pd.to_datetime(hist.index).strftime('%Y-%m-%d')

    df = pd.concat([df, hist], axis=1, sort=True)
    df = df.interpolate(axis=0).dropna(subset=['ROI-USD'])

    df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')
    
    start_cmc200 = df.head(1)['Open'][0]
    df['CMC200-USD'] = (((df['Open'] - start_cmc200) / start_cmc200)*100)
    df = df[['ROI-USD', 'ROI-ETH', 'CMC200-USD']]
    
    cg = CoinGeckoAPI()
    
    data = cg.get_coin_market_chart_by_id('bitcoin', 'eth', 500)

    dates = [datetime.fromtimestamp(data['prices'][i][0] / 1000).strftime('%Y-%m-%d') for i in range(len(data['prices']))]
    price  = [data['prices'][i][1] for i in range(len(data['prices']))]

    df_btc = pd.DataFrame({'BTC-ETH': price}, index=dates)
    df_btc.index = pd.to_datetime(df_btc.index).strftime('%Y-%m-%d')

    df_btc.drop(df_btc.tail(1).index,inplace=True)
    
    df = pd.concat([df, df_btc], axis=1, sort=True)
    df = df.dropna(subset=['ROI-USD'])
    
    start_btc = df.head(1)['BTC-ETH'][0]
    df['BTC-ETH'] = (((df['BTC-ETH'] - start_btc) / start_btc)*100)
    
    df.drop(df.tail(1).index,inplace=True)
    
    df.to_csv(file_name, index=True)

if __name__ == '__main__':
    main()