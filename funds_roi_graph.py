import requests
import pandas as pd
from datetime import datetime 

def fnd():
    sent = requests.get('https://api.bloxy.info/widget/address_value_daily?address=0xCB60D600160D005845Ec999f64266D5608fd8943&key=ACCunOMWYpmCp&format=table').json()
    df = pd.DataFrame(sent)
    df.rename(columns={0:'Date', 11: 'ROI'}, inplace=True)
    # df.rename(columns={0:'Date', 7:'Total Gain/Loss', 8:'Unrealized Gain/Loss', 9:'Realized Gain/Loss', 11: 'ROI'}, inplace=True)
    df['ROI'] = df.ROI.cumsum()
    df = df[['Date', 'ROI']]
    # df = df[['Date', 'Total Gain/Loss', 'Unrealized Gain/Loss', 'Realized Gain/Loss', 'ROI']]
    df.to_csv('Fnd.csv', index=False)

def elba():
    sent = requests.get('https://api.bloxy.info/widget/address_value_daily?address=0x9f73d7874aa731a6e3185e2fdc201a07c736f45b&key=ACCunOMWYpmCp&format=table').json()
    df = pd.DataFrame(sent)
    df.rename(columns={0:'Date', 11: 'ROI'}, inplace=True)
    # df.rename(columns={0:'Date', 7:'Total Gain/Loss', 8:'Unrealized Gain/Loss', 9:'Realized Gain/Loss', 11: 'ROI'}, inplace=True)
    df['ROI'] = df.ROI.cumsum()
    df = df[['Date', 'ROI']]
    # df = df[['Date', 'Total Gain/Loss', 'Unrealized Gain/Loss', 'Realized Gain/Loss', 'ROI']]
    df.to_csv('Elba.csv', index=False)

def sark():
    sent = requests.get('https://api.bloxy.info/widget/address_value_daily?address=0x10603633e9a021b8dbc1f0ccb172178b07dfb1f4&key=ACCunOMWYpmCp&format=table').json()
    df = pd.DataFrame(sent)
    df.rename(columns={0:'Date', 11: 'ROI'}, inplace=True)
    # df.rename(columns={0:'Date', 7:'Total Gain/Loss', 8:'Unrealized Gain/Loss', 9:'Realized Gain/Loss', 11: 'ROI'}, inplace=True)
    df['ROI'] = df.ROI.cumsum()
    df = df[['Date', 'ROI']]
    # df = df[['Date', 'Total Gain/Loss', 'Unrealized Gain/Loss', 'Realized Gain/Loss', 'ROI']]
    df.to_csv('Sark.csv', index=False)

def madeira():
    sent = requests.get('https://api.bloxy.info/widget/address_value_daily?address=0x392e693e0222e07e88fbf2cf7107e2dfac8af678&key=ACCunOMWYpmCp&format=table').json()
    df = pd.DataFrame(sent)
    df.rename(columns={0:'Date', 11: 'ROI'}, inplace=True)
    # df.rename(columns={0:'Date', 7:'Total Gain/Loss', 8:'Unrealized Gain/Loss', 9:'Realized Gain/Loss', 11: 'ROI'}, inplace=True)
    df['ROI'] = df.ROI.cumsum()
    df = df[['Date', 'ROI']]
    # df = df[['Date', 'Total Gain/Loss', 'Unrealized Gain/Loss', 'Realized Gain/Loss', 'ROI']]
    df.to_csv('Madeira.csv', index=False)

def main():
    fnd()
    elba()
    sark()
    madeira()

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    f = open("run_log.txt","a")
    f.write("Ran at " + dt_string + "\n")
    f.close() 

if __name__ == '__main__':
    main()
