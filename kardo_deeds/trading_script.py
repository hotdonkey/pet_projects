# %%
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date
#import gspread
#from df2gspread import df2gspread as d2g
#from oauth2client.service_account import ServiceAccountCredentials

# %%
def get_info():
    # Upload function
    def google_upload(df, sheet_name):
        # Params used to connect to google api
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

        api_json = ''

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            api_json, scope)  # security token
        gc = gspread.authorize(credentials)

        # Key params for connection to particular document
        spreadsheet_key = ''  # document id
        wks_name = sheet_name  # sheet name that we use
        d2g.upload(df, spreadsheet_key, wks_name, credentials=credentials)
        print(f'Uploading to {sheet_name} completed')

    # Main action block
    # Creating req and bs objects
    url = 'https://tradingeconomics.com/bonds'
    response = requests.get(url=url, headers={'User-Agent': 'Mozilla/5.0'})
    page = BeautifulSoup(response.text, 'html.parser')

    # Specify finding params and clearing data
    us_data_raw = page.find('tr', attrs={'data-symbol': 'USGG10YR:IND'}).text
    us_data = us_data_raw.replace(' ', '').replace('\r', '').split('\n')
    us_data = [i for i in us_data if i != '']

    ru_data_raw = page.find('tr', attrs={'data-symbol': 'RUGE10Y:GOV'}).text
    ru_data = ru_data_raw.replace(' ', '').replace('\r', '').split('\n')
    ru_data = [i for i in ru_data if i != '']

    # Creating dataframe row for concatination
    us_data_row = pd.DataFrame({
        'Major10Y': us_data[0],
        'Yield': float(us_data[1]),
        'Date': us_data[-1] + f'/{date.today().year}'
    }, index=[0])
    us_data_row['Date'] = pd.to_datetime(us_data_row['Date'])

    ru_data_row = pd.DataFrame({
        'Major10Y': ru_data[0],
        'Yield': float(ru_data[1]),
        'Date': ru_data[-1] + f'/{date.today().year}'
    }, index=[0])
    ru_data_row['Date'] = pd.to_datetime(ru_data_row['Date'])

    # Concat our rows
    final_row = pd.concat(
        [us_data_row, ru_data_row],
        axis=0,
        ignore_index=True
    )

    print(f'Parsing is done.')

    # Concat our rows with main dataframe
    try:
        main_df = pd.read_excel('./TE_index.xlsx', index_col=0)
        main_df = pd.concat([main_df, final_row], axis=0, ignore_index=True)
        main_df.drop_duplicates(inplace=True)

        with pd.ExcelWriter('./TE_index.xlsx') as writer:
            main_df.to_excel(writer, sheet_name='TE_usa_ru')

        # google_upload(main_df, 'TE_usa_ru')

    except FileNotFoundError:
        with pd.ExcelWriter('./TE_index.xlsx') as writer:
            final_row.to_excel(writer, sheet_name='TE_usa_ru')

        # google_upload(final_row, 'TE_usa_ru')

    return final_row


if __name__ == '__main__':
    get_info()


# %%



