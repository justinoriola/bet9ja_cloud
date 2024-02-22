
from datetime import datetime, timedelta, time
from spreadsheet_handler import SpreadSheetHandler
from account_handler import AccountHandler
from logic_handler import LogicHandler
import os
from tabulate import tabulate
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

# Constants
DAYS_OF_THE_WEEK = ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday']
CURRENT_TIME = datetime.now().time()
TODAY = datetime.now().strftime('%A')
TODAYS_DATE = datetime.now().date().strftime("%d/%m/%Y")
PAST_DATE = (datetime.now().date() - timedelta(days=6)).strftime("%d/%m/%Y")

account_credentials = {
    'ogba':{
        'username': os.getenv('USERNAME1'),
        'password': os.getenv('PASSWORD'),
        'amount_to_credit': 40000,
        'number_of_cashier': 4,
        'base_balance':1000000,
        'worksheet_name': "ogba_daily_spreadsheet",
        'worksheet_id': os.getenv('SPREADSHEET_ID1')
    },
    'idiaraba':{
        'username': os.getenv('USERNAME2'),
        'password': os.getenv('PASSWORD'),
        'amount_to_credit': 40000,
        'number_of_cashier': 4,
        'base_balance':1000000,
        'worksheet_name': "idiaraba_daily_spreadsheet",
        'worksheet_id': os.getenv('SPREADSHEET_ID2')
    },
    'awori': {
        'username': os.getenv('USERNAME3'),
        'password': os.getenv('PASSWORD'),
        'amount_to_credit': 30000,
        'number_of_cashier': 3,
        'base_balance':700000,
        'worksheet_name': "awori_daily_spreadsheet",
        'worksheet_id': os.getenv('SPREADSHEET_ID3')
    },
    'moshalashi': {
        'username': os.getenv('USERNAME4'),
        'password': os.getenv('PASSWORD'),
        'amount_to_credit': 10,
        'number_of_cashier': 3,
        'base_balance': 650000,
        'worksheet_name': "moshalashi_daily_spreadsheet",
        'worksheet_id': os.getenv('SPREADSHEET_ID4'),
    },

}

# Main script
if __name__ == '__main__':
    # set a start time
    start_time = datetime.now()

    # Loop through the credential dictionary's key
    for key in account_credentials.keys():

        # Unpacking account credentials
        username = account_credentials[key]['username']
        password = account_credentials[key]['password']
        amount_to_credit = account_credentials[key]['amount_to_credit']
        number_of_cashier = account_credentials[key]['number_of_cashier']
        sheet_name = account_credentials[key]['worksheet_name']
        sheet_id = account_credentials[key]['worksheet_id']
        base_balance = account_credentials[key]['base_balance']

        # Instantiate account handler objects
        account = AccountHandler(username, password, amount_to_credit, number_of_cashier)

        # Withdraw and credit cashier account
        if time(10, 0) <= CURRENT_TIME <= time(23, 0):
            account.withdraw_from_cashier()

        # Instantiate spreadsheet handler objects and get spreadsheet values
        if time(10, 0) <= CURRENT_TIME <= time(23, 0):
            try:
                # Instantiate handler object and get spreadsheet values
                handler = SpreadSheetHandler(sheet_id, sheet_name, username, password, amount_to_credit, number_of_cashier)
                spreadsheet_values = handler.get_spreadsheet_values()

                # Unpack spreadsheet values
                cash_float = int(spreadsheet_values['total_float'][0].replace(',', ''))
                expenses = int(spreadsheet_values['total_expenses'][0].replace(',', ''))
                banking = int(spreadsheet_values['total_banking'][0].replace(',', ''))
                closing_balance = int(spreadsheet_values['closing_balance'][0].replace(',', ''))
                bet_paid = spreadsheet_values['bet_ids']
                already_paid_bet = spreadsheet_values['already_paid_bet']

                # filter bet_paid list
                filtered_betlist = handler.filtered_bet_list(bet_paid, already_paid_bet)

                # Pay out bet slips
                paid_betlist = account.bet_payout(filtered_betlist)
                handler.upload_to_google_sheets(paid_betlist, already_paid_bet)
                if not paid_betlist:
                    account.login()
                winning = account.winning_balance()

                # Instantiate logic
                logic = LogicHandler()
                admin_balance = account.get_admin_balance()

                account_balance = logic.account_balance(base_balance=base_balance, expenses=expenses, banking=banking,
                                                        closing_balance=closing_balance, float=cash_float,
                                                        winning=winning, admin_balance=admin_balance)

                # tabulate the output and make it presentable
                print(tabulate(logic.table(base_balance=base_balance, expenses=expenses, banking=banking,
                                                        closing_balance=closing_balance, float=cash_float,
                                                        winning=winning, admin_balance=admin_balance),
                                                        headers=[username, key]))

                dot_line_length = len(logic.account_status(account_balance))
                print('-' * dot_line_length)
                print(logic.account_status(account_balance))
                print('-' * dot_line_length)

                # Create duplicate spreadsheet and reset existing spreadsheet for re-use.
                if TODAY == "Monday" and time(00, 0) <= CURRENT_TIME <= time(00, 59):
                    new_sheet_name = f'{sheet_name}: {PAST_DATE} - {TODAYS_DATE}'
                    handler.create_spreadsheet_duplicate(new_sheet_name)
                    for days_to_clear in DAYS_OF_THE_WEEK:
                        handler.clear_spreadsheet(days_to_clear)
                else:
                    print(f'\nspreadsheet duplicate/clear function not schedule to run by this time')
            except Exception as e:
                print(f'An error occurred: {e}')
            # finally:
            #     account.driver.quit()

        elif time(5, 0) <= CURRENT_TIME <= time(13, 59):
            admin_balance = account.get_admin_balance()
            account.credit_cashier(admin_balance)
        else:
            print('This other section(s) of the script is not scheduled to run by this time')
            print(f'CURRENT_TIME: {CURRENT_TIME}')

    # calculate and print the total time taken to process the entire script
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time.seconds, 60)
    print(f'\nTotal time: {minutes} minutes and {seconds} seconds')
