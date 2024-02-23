from tabulate import tabulate
from datetime import datetime

TODAY = datetime.now().strftime('%A')
TODAYS_DATE = datetime.now().date().strftime("%d/%m/%Y")
class LogicHandler():

    def __init__(self, **kwargs):
        self.base = None

    # function calculate if total account is balanced based on certain inputs
    def account_balance(self, **kwargs):
        try:
            x = [kwargs.get('base_balance'), kwargs.get('float'), kwargs.get('winning')]
            y = [kwargs.get('banking'), kwargs.get('expenses'), kwargs.get('closing_balance'), kwargs.get('admin_balance')]
            account_bal = round(sum(x) - sum(y))
        except Exception as e:
            print(f'Error occurred: {e}')
        finally:
            return account_bal

    def account_reset(self, **kwargs) -> str:
        try:
            x = [kwargs.get('base_balance'), kwargs.get('winning')]
            y = [kwargs.get('closing_balance'), kwargs.get('admin_balance')]
            account_reset = round(sum(x) - sum(y))
        except Exception as e:
            print(f'Error occurred: {e}')
        finally:
            return f'Reset amount:' + f' {str(account_reset)}'

    def account_status(self, account_balance):
        try:
            if account_balance == 0:
                return f'Account is balanced.'
            elif account_balance < 0:
                excess_balance = abs(account_balance)
                return f"Balanced with N{excess_balance} excess."
            else:
                return f'Not Bal: N{account_balance} shortage!'
        except Exception as e:
            print(f'Error occurred: {e}')

    def table(self, **kwargs):
        try:
            table = [['base_balance', f"{kwargs.get('base_balance')}"], ["cash_float", f"{kwargs.get('float')}"], ["expenses",
                      f"{kwargs.get('expenses')}"], ["banking", f"{kwargs.get('banking')}"], ["winning",
                     f"{kwargs.get('winning')}"], ["cash_in_shop", f"{kwargs.get('closing_balance')}"], ["admin_balance",
                     f"{kwargs.get('admin_balance')}"]]
            return table
        except Exception as e:
            print(f'Error occurred: {e}')

    def text(self, username, shop_code, **kwargs):
        message = (
            # f"\n{'-' * 30}\n"
            f"\n{shop_code.title()}: {username}\n"
            f"{TODAY}, {TODAYS_DATE}.\n"
            f"{'-' * 30}\n"
            f"base_balance     {kwargs.get('base_balance'):>n}\n"
            f"float            {kwargs.get('float'):>n}\n"
            f"expenses         {kwargs.get('expenses'):>n}\n"
            f"banking          {kwargs.get('banking'):>n}\n"
            f"winning          {kwargs.get('winning'):>n}\n"
            f"cash_in_shop     {kwargs.get('closing_balance'):>n}\n"
            f"admin_balance    {kwargs.get('admin_balance'):>n}\n"
            f"{'-' * 30}"
        )
        return message.strip()
















 # # print the calculation flow for visibility
            # print(f"\nbase_balance: {kwargs.get('base_balance')} + cash_float: {kwargs.get('float')} + winning: {kwargs.get('winning')} -  "
            #       f"cash_in_shop: {kwargs.get('closing_balance')} - expenses: {kwargs.get('expenses')} "
            #       f"- banking: {kwargs.get('banking')} - admin_balance: {kwargs.get('admin_balance')}\n")