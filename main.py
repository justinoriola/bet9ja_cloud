
from datetime import datetime, timedelta, time

from notification_handler import NotificationHandler
from spreadsheet_handler import SpreadSheetHandler
from account_handler import AccountHandler, ACCOUNT_CREDENTIALS
from logic_handler import LogicHandler
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')
from time import sleep
# from flask import Flask

# Constants
DAYS_OF_THE_WEEK = ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday']
CURRENT_TIME = datetime.now().time()
TODAY = datetime.now().strftime('%A')
TODAYS_DATE = datetime.now().date().strftime("%d/%m/%Y")
PAST_DATE = (datetime.now().date() - timedelta(days=6)).strftime("%d/%m/%Y")
message_bank = ''

if __name__ == '__main__':
    # set a start time
    start_time = datetime.now()

    # instantiate notification object
    notification_handler = NotificationHandler()

    # Loop through the credential dictionary's key
    for account_key in ACCOUNT_CREDENTIALS.keys():

        # Instantiate account handler object
        account_handler = AccountHandler(account_key)
        # Instantiate handler object and get spreadsheet values
        spreadsheet_handler = SpreadSheetHandler(account_key)

        # Withdraw and credit cashier account
        if time(20, 0) <= CURRENT_TIME <= time(23, 59):
            cashier_checks = account_handler.cashier_check(account_handler.cashier_numbers)
            account_handler.withdraw_from_cashier()

        # Instantiate spreadsheet handler objects and get spreadsheet values
        if time(11, 0) <= CURRENT_TIME <= time(23, 55):
            sleep(2)

            # filter bet_paid list
            bet_ticket_checks = spreadsheet_handler.betid_checks(
                spreadsheet_handler.bet_paid, spreadsheet_handler.already_paid_bet
            )

            # Pay out bet slips and upload betIDs to the spreadsheet
            paid_betlist = account_handler.bet_payout(spreadsheet_handler.bet_paid)
            spreadsheet_handler.upload_to_google_sheets(paid_betlist, spreadsheet_handler.already_paid_bet)
            # if not paid_betlist:
            #     account_handler.login()

            # Get admin winning/balance
            winning = account_handler.winning_balance()
            admin_balance = account_handler.get_admin_balance()

            # Instantiate logic handler object
            logic = LogicHandler(
                base_balance=account_handler.base_balance, expenses=spreadsheet_handler.expenses,
                banking=spreadsheet_handler.banking, closing_balance=spreadsheet_handler.today_closing_balance,
                float=spreadsheet_handler.cash_float, winning=winning, admin_balance=admin_balance
            )

            account_balance = logic.account_balance(
                base_balance=account_handler.base_balance, expenses=spreadsheet_handler.expenses, banking=spreadsheet_handler.banking,
                closing_balance=spreadsheet_handler.today_closing_balance, float=spreadsheet_handler.cash_float,
                winning=winning, admin_balance=admin_balance
            )
            account_handler.driver.quit()

            account_reset_message = logic.account_reset(
                base_balance=account_handler.base_balance, winning=winning,
                closing_balance=spreadsheet_handler.today_closing_balance,
                admin_balance=admin_balance
            )

            # print account balance/reset status
            account_status_message = logic.account_status(account_balance)
            # message_account_reset = f'Reset amount:' + f'{str(account_reset)}'

            # perform various checks: BetIDs, Opening/Closing balance and Cashier_withdrawal checks
            message_account_checks = (
                  f'\nChecks performed:'
                  f'\n-{spreadsheet_handler.betid_checks(spreadsheet_handler.bet_paid, spreadsheet_handler.already_paid_bet)}'
                  f'\n-{spreadsheet_handler.opening_balance_check(spreadsheet_handler.today_opening_balance, spreadsheet_handler.yesterday_closing_balance)}'
                  # f'\n-{cashier_checks}'
            )
            # instantiate and get the message to be sent
            message = logic.text(
                account_handler.admin_username, account_key, base_balance=account_handler.base_balance,
                expenses=spreadsheet_handler.expenses, banking=spreadsheet_handler.banking,
                closing_balance=spreadsheet_handler.today_closing_balance, float=spreadsheet_handler.cash_float,
                winning=winning, admin_balance=admin_balance
            )

            # send report to WhatsApp
            message += f'\nAccount Status:' + f"\n{'-' * 15}|" + f'\n{account_status_message}' + f'\n{account_reset_message}' + f"\n{'-' * 30}"
            if account_balance != 0:
                message += message_account_checks

            # bank messages
            message_bank += f'{message}\n\n'

            # send Notification / print to console
            print(message_bank)
            notification_handler.send_sms(message)

            # Create duplicate spreadsheet and reset existing spreadsheet for re-use.
            if TODAY == "Monday" and time(13, 25) <= CURRENT_TIME <= time(23, 50):
                new_sheet_name = f'{account_handler.sheet_name}: {PAST_DATE} - {TODAYS_DATE}'
                spreadsheet_handler.create_spreadsheet_duplicate(new_sheet_name)
                for days_to_clear in DAYS_OF_THE_WEEK:
                    spreadsheet_handler.clear_spreadsheet(days_to_clear)
            else:
                print(f'\nspreadsheet duplicate/clear function not schedule to run by this time')

        # credit cashier account at specified time
        elif time(5, 0) <= CURRENT_TIME <= time(13, 30):
            admin_balance = account_handler.get_admin_balance()
            account_handler.credit_cashier(admin_balance)
        else:
            print('This other section(s) of the script is not scheduled to run by this time')
            print(f'CURRENT_TIME: {CURRENT_TIME}')
        sleep(5)

    # calculate and print the total time taken to process the entire script
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time.seconds, 60)
    print(f'\nTotal time: {minutes} minutes and {seconds} seconds')


    # app.run(debug=True)