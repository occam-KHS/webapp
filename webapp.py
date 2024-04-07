import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


# Title of the web application
st.title('수급분석')

# File uploader widget
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])

if uploaded_file is not None:
    data = pd.read_excel(uploaded_file, header=1)

    # Use Pandas to read the Excel file
    def cal_prop(segment):
        data['s_cumsum'] = data[segment].cumsum()
        data['s_bal'] = data['s_cumsum'] - data['s_cumsum'].min()
        return data['s_bal'] / data['s_bal'].max()


    def avg_price(segment):
        data['s_cumsum'] = data[segment].cumsum()
        data['s_bal'] = data['s_cumsum'] - data['s_cumsum'].min()
        return data[['종가', 's_bal']].prod(axis=1).cumsum() / data['s_bal'].cumsum()


    data.columns = ['일자', '종가', '전일대비', '등락율', '거래량', '외국인', '개인', '기관종합', '금융투자', '투신(일반)', '투신(사모)', '은행', '보험', '기타금융', '연기금등', '국가지방', '기타']
    data.set_index('일자', inplace=True)
    data.sort_index(inplace=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    plt.title('Price vs. Investor Share')
    ax = cal_prop('외국인').plot(figsize=(15,6), color='green', label='foreigner')
    ax = cal_prop('개인').plot(figsize=(15,6), color='orangered', label='individuals')
    ax = cal_prop('기관종합').plot(figsize=(15,6), color='blue', label='institutions')
    ax2 = ax.twinx()
    ax2 = data['종가'].plot(figsize=(15,6), color='black', label='price')
#
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')

    st.pyplot(fig)
