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
    print(res.status_code)  # Print the HTTP status code
    print(res.json())
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
global ACCESS_TOKEN
ACCESS_TOKEN = get_access_token(APP_KEY, APP_SECRET)
print(ACCESS_TOKEN)

with open("access_token.pkl", "wb") as file:
    pickle.dump(ACCESS_TOKEN, file)