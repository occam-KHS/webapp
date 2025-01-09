import streamlit as st
import pandas as pd
import pickle
import datetime
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
import keyring


import requests
import json
import datetime
import time
import keyring
import numpy as np
import os
import pickle
import random
import FinanceDataReader as fdr
# from pymongo import MongoClient

plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)




def get_access_token(APP_KEY, APP_SECRET):
    """토큰 발급"""
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET}
    PATH = "oauth2/tokenP"
    print("%s, %s" % (URL_BASE, PATH))
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN


def get_approval(APP_KEY, APP_SECRET):
    """웹소켓 접속키 발급"""
    url = 'https://openapi.koreainvestment.com:9443'
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials",
            "appkey": APP_KEY,
            "secretkey": APP_SECRET}
    PATH = "oauth2/Approval"
    URL = f"{url}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    approval_key = res.json()["approval_key"]
    return approval_key


def hashkey(datas):
    """암호화"""
    PATH = "uapi/hashkey"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
        'content-Type': 'application/json',
        'appKey': APP_KEY,
        'appSecret': APP_SECRET,
    }
    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    hashkey = res.json()["HASH"]
    return hashkey

def buy(code="005930", qty="1", buy_price="0", buy_type="01"):
    """주식 시장가 매수"""
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": buy_type,  # 00-지정가 01-시장가 11 IOC 지정가: 체결안되거 전량 취소
        "ORD_QTY": qty,
        "ORD_UNPR": buy_price,
    }
    headers = {"Content-Type": "application/json",
               "authorization": f"Bearer {ACCESS_TOKEN}",
               "appKey": APP_KEY,
               "appSecret": APP_SECRET,
               "tr_id": "TTTC0802U",  # 실전 투자 : "TTTC0802U" 모의투자 'VTTC0802U'
               "custtype": "P",
               "hashkey": hashkey(data)
               }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        print(f"[매수 성공]{str(res.json())}")
        return True
    else:
        print(f"[매수 실패]{str(res.json())}")
        return False


def sell(code="005930", qty="1", sell_price="0", sell_type="01"):
    """주식 시장가 매도"""

    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": sell_type,
        "ORD_QTY": qty,
        "ORD_UNPR": sell_price,
    }
    headers = {"Content-Type": "application/json",
               "authorization": f"Bearer {ACCESS_TOKEN}",
               "appKey": APP_KEY,
               "appSecret": APP_SECRET,
               "tr_id": "TTTC0801U",  # 실전 투자 : TTTC0801U "VTTC0801U"
               "custtype": "P",
               "hashkey": hashkey(data)
               }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        print(f"[매도 성공]{str(res.json())}")
        return True
    else:
        print(f"[매도 실패]{str(res.json())}")
        return False


def inquire_volume(rank_type):
    """투자자 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/volume-rank"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type": "application/json",
               "authorization": f"Bearer {ACCESS_TOKEN}",
               "appKey": APP_KEY,
               "appSecret": APP_SECRET,
               "tr_id": "FHPST01710000",
               "custtype": "P",
               "tr_cont": ""}

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_COND_SCR_DIV_CODE": "20171",
        "FID_INPUT_ISCD": "0000",
        "FID_DIV_CLS_CODE": "1",
        "FID_BLNG_CLS_CODE": rank_type,
        "FID_TRGT_CLS_CODE": "111111111",
        "FID_TRGT_EXLS_CLS_CODE": "111111111",
        "FID_INPUT_PRICE_1": "",
        "FID_INPUT_PRICE_2": "",
        "FID_VOL_CNT": "",
        "FID_INPUT_DATE_1": ""

    }
    res = requests.get(URL, headers=headers, params=params)
    return res.json()['output']


def inquire_investors(code="131400"):
    """종목별 투자자 수량 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-investor"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type": "application/json",
               "authorization": f"Bearer {ACCESS_TOKEN}",
               "appKey": APP_KEY,
               "appSecret": APP_SECRET,
               "tr_id": "FHKST01010900",
               "custtype": "P",
               "tr_cont": ""}

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": code,

    }
    res = requests.get(URL, headers=headers, params=params)
    return res.json()['output']


def estimate_program(code="131400"):
    """당일 프로그램 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/program-trade-by-stock"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type": "application/json",
               "authorization": f"Bearer {ACCESS_TOKEN}",
               "appKey": APP_KEY,
               "appSecret": APP_SECRET,
               "tr_id": "FHPPG04650100",
               "custtype": "P",
               "tr_cont": ""}

    params = {
        "FID_INPUT_ISCD": code,

    }
    res = requests.get(URL, headers=headers, params=params)
    return res.json()['output']


def estimate_investors(code="131400"):
    """당일 투자자 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/investor-trend-estimate"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type": "application/json",
               "authorization": f"Bearer {ACCESS_TOKEN}",
               "appKey": APP_KEY,
               "appSecret": APP_SECRET,
               "tr_id": "HHPTJ04160200",
               "custtype": "P",
               "tr_cont": ""}

    params = {
        "MKSC_SHRN_ISCD": code,

    }
    res = requests.get(URL, headers=headers, params=params)
    return res.json()['output2']


def get_current_price(code="005930"):  # 주식 현재가 시세
    """현재가 조회"""
    PATH = "/uapi/etfetn/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type": "application/json",
               "authorization": f"Bearer {ACCESS_TOKEN}",
               "appKey": APP_KEY,
               "appSecret": APP_SECRET,
               "tr_id": "FHPST02400000"}
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": code,
    }
    res = requests.get(URL, headers=headers, params=params)
    return int(res.json()['output']['stck_prpr']), float(res.json()['output']['prdy_ctrt'])

def get_stock_balance():
    """주식 잔고조회"""
    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type": "application/json",
               "authorization": f"Bearer {ACCESS_TOKEN}",
               "appKey": APP_KEY,
               "appSecret": APP_SECRET,
               "tr_id": "TTTC8434R",  # 실전 투자 "TTTC8434R" 모의투자 "VTTC8434R"
               "custtype": "P",
               }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    res = requests.get(URL, headers=headers, params=params)
    stock_list = res.json()['output1']
    evaluation = res.json()['output2']
    stock_dict = {}
    # print(f"====주식 보유잔고====")
    for stock in stock_list:
        if int(stock['hldg_qty']) > 0:
            stock_dict[stock['pdno']] = [stock['hldg_qty'], stock['ord_psbl_qty'], stock['evlu_pfls_rt']]  # 0: 보유 수량, 1: 주문가능수량 2: 평가수익율
    return stock_dict


APP_KEY = keyring.get_password("real_app_key", "occam123")
APP_SECRET = keyring.get_password("real_app_secret", "occam123")
URL_BASE = "https://openapi.koreainvestment.com:9443"  # 실전 투자
CANO = keyring.get_password("CANO", "occam123")
ACNT_PRDT_CD = "01"
print(CANO)
print(APP_KEY)
print(APP_SECRET)


# URL_BASE = "https://openapi.koreainvestment.com:9443"  # 실전 투자
# APP_KEY = keyring.get_password('real_app_key_2', 'occam123')
# APP_SECRET = keyring.get_password('real_app_secret_2', 'occam123')
# CANO = keyring.get_password('CANO_2', 'occam123')
# ACNT_PRDT_CD = "01"
# print(CANO)
# global ACCESS_TOKEN
# ACCESS_TOKEN = get_access_token(APP_KEY, APP_SECRET)
# # print(ACCESS_TOKEN)

# ACCESS_TOKEN ='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjQ1YTkzNjRlLTNiY2EtNDViNy04ODllLTlmNzViMTdmNmQxMyIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTczNjMzODk3MCwiaWF0IjoxNzM2MjUyNTcwLCJqdGkiOiJQU0ZFdnZ0ZVFFb3pVU0l6TnprRWFNSkxJNXUxVVhpZGJFUXIifQ.2FueqIkFDw5gKmcXwAVEIM0jsWkeZGCgh6nWF7qJ-AyDf3nPRbgjLeC58Q1P8JtlQtDWck1XsR4L_dLRiBdIbA'

def ho(x):
    if x < 2000:
        return 1
    elif x < 5000:
        return 5
    elif x < 20000:
        return 10
    elif x < 50000:
        return 50
    elif x < 200000:
        return 100
    elif x < 500000:
        return 500
    else:
        return 1000


year = datetime.datetime.now().year
month = datetime.datetime.now().month
day = datetime.datetime.now().day

date_format = '%Y%m%d'
today = datetime.datetime.now().strftime(date_format)



st.title("기관/외국인 추종 매수 전략")

import pickle
with open('name_dict.pkl', 'rb') as f:
    name_dict = pickle.load(f)
    
with open('access_token.pkl', 'rb') as f:
    ACCESS_TOKEN = pickle.load(f)
    

# Define a function to process the data
def process_data(today, money):

    
    data_all = pd.DataFrame()

    for code in list(name_dict.keys()):
        
        try:
            
            data = inquire_investors(code=code)  
            print(code)
            data2 = pd.DataFrame(data).set_index('stck_bsop_date').astype('int').sort_index()
            data2['code'] = code
            data2['name'] = name_dict[code]
            data_all = pd.concat([data_all, data2], axis=0)   
                 
        except Exception as err:
            print(err)
            pass        
        
    data_all.to_csv(folder_path + '\\' + money + 'data_all.txt')   
    org_30 = data_all.loc[today][['code', 'name', 'prsn_ntby_tr_pbmn', 'frgn_ntby_tr_pbmn', 'orgn_ntby_tr_pbmn']].sort_values(by=money, ascending=False).head(30)
    org_30.to_csv(folder_path + '\\' + money + 'org_30.txt')
    return data_all, org_30
    

# Input for date
st.write("프로그램 실행 가는 시간: 16.30 - 23:59")
options = ['기관', '외국인']
select_investor = st.selectbox('기관/외국인 추종 선택', options)

if select_investor == '기관':
    money = 'orgn_ntby_tr_pbmn'
    div = 'institution'
    stats = 'orgn_tval'
else:
    money = 'frgn_ntby_tr_pbmn'
    div = 'foreign'
    stats = 'frgn_tval'
    
    
print(today)
parent_folder = 'D:\investor_following'
day_folder = str(today)
day_path  = os.path.join(parent_folder, day_folder)
os.makedirs(day_path, exist_ok=True)

div_folder = str(div)
folder_path  = os.path.join(day_path, div_folder)
os.makedirs(folder_path, exist_ok=True)

# Load data    
        
# 프로그램 사용 가능 시간
start_time  = (datetime.datetime.now() > datetime.datetime(year=year, month=month, day=day, hour=16, minute=30, second=1))
end_time  = (datetime.datetime.now() < datetime.datetime(year=year, month=month, day=day, hour=23, minute=59, second=1))
        
if st.button("출력 - 실행 시간 1분") and start_time and end_time:    

    date_format = '%Y%m%d'
    today = datetime.datetime.now().strftime(date_format)
   
    print(today)
    data_all, org_30 = process_data(today, money)

    if data_all is not None and not org_30.empty:
        st.write(select_investor + " 순매수 상위 30 종목")
        st.dataframe(org_30)

        # Perform analysis
        code_list = []
        name_list = []
        orgn_tval = []
        frgn_tval = []
        orgn_pval = []
        frgn_pval = []
        adf_pval =  []

        for code in org_30['code']:
            sample = data_all[data_all['code'] == code]
            y = sample['prdy_vrss']
            X = sample[['frgn_ntby_qty', 'orgn_ntby_qty']]
            X = sm.add_constant(X)
            model = sm.OLS(y, X).fit()
            residuals = model.resid
            adf_result = adfuller(residuals)
            code_list.append(code)
            name_list.append(name_dict[code])
            orgn_tval.append(model.tvalues['orgn_ntby_qty'])
            frgn_tval.append(model.tvalues['frgn_ntby_qty'])
            orgn_pval.append(model.pvalues['orgn_ntby_qty'])
            frgn_pval.append(model.pvalues['frgn_ntby_qty'])
            adf_pval.append(adf_result[1])

        outcome = pd.DataFrame({'code':code_list, 'name': name_list, 'orgn_tval': orgn_tval, 'frgn_tval': frgn_tval,\
            'orgn_pval': orgn_pval, 'frgn_pval': frgn_pval, 'adf_pval': adf_pval})
        st.write(select_investor + " 순매수와 주가 변동율과의 관계가 높은 종목")
        selection = outcome[outcome['adf_pval']<0.01].sort_values(by=stats, ascending=False).round(5)
        st.dataframe(selection)
        selection.to_csv(folder_path + '\\' + money + 'selection.txt')
        st.write('누적순매수 차트')
        # Plot results
        for code in selection['code']:
            sample = data_all[data_all['code'] == code]
            sample_cumsum = sample[['prsn_ntby_tr_pbmn', 'frgn_ntby_tr_pbmn', 'orgn_ntby_tr_pbmn']].cumsum()
            sample_cumsum.columns = ['Individuals', 'Foreigners', 'Institutions']
            fig, ax = plt.subplots(figsize=(15, 6))
            sample_cumsum.plot(ax=ax)
            ax.legend(loc=1)
            ax2 = ax.twinx()
            sample['stck_clpr'].plot(ax=ax2, color='black', linestyle='-.', label='Price Change')
            ax2.legend(loc=2)
            plt.title(f"{code} - {name_dict[code]}")
            st.pyplot(fig)
            plt.savefig(folder_path + '\\' + str(code) + money + '.png')
