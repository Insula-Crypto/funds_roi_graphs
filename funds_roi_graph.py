import requests
import pandas as pd
from datetime import datetime 

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
    df.to_csv(file_name, index=False)

def get_fund_gain_loss(address, file_name):
    sent = requests.get('https://api.bloxy.info/widget/address_value_daily?address=' + address + '&key=ACCunOMWYpmCp&format=table').json()
    df = pd.DataFrame(sent)
    df.rename(columns={0:'Date', 7:'Total Gain/Loss', 8:'Unrealized Gain/Loss', 9:'Realized Gain/Loss'}, inplace=True)
    df = df[['Date', 'Total Gain/Loss', 'Unrealized Gain/Loss', 'Realized Gain/Loss']]
    df.to_csv(file_name, index=False)

def main():
    get_fund_ROI('0xCB60D600160D005845Ec999f64266D5608fd8943', 'Fnd.csv')
    ## get_fund_ROI('0x9f73d7874aa731a6e3185e2fdc201a07c736f45b', 'Elba.csv')
    ## get_fund_ROI('0x10603633e9a021b8dbc1f0ccb172178b07dfb1f4', 'Sark.csv')
    get_fund_ROI('0x392e693e0222e07e88fbf2cf7107e2dfac8af678', 'Madeira.csv')

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    f = open("run_log.txt","a")
    f.write("Ran at " + dt_string + "\n")
    f.close() 

if __name__ == '__main__':
    main()
