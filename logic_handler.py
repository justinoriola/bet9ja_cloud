import tabulate
class LogicHandler:

    def __init__(self):
        self.base = None

    # function calculate if total account is balanced based on certain inputs
    def account_balance(self, **kwargs):
        x = [kwargs.get('base_balance'), kwargs.get('float'), kwargs.get('winning')]
        y = [kwargs.get('banking'), kwargs.get('expenses'), kwargs.get('closing_balance'), kwargs.get('admin_balance')]
        account_bal = round(sum(x) - sum(y))
        return account_bal

    def account_status(self, account_balance):
        try:
            if account_balance == 0:
                return f'Account is balanced.'
            elif account_balance < 0:
                excess_balance = abs(account_balance)
                return f"Account is balanced with an excess of {excess_balance}"
            else:
                return f'Account not balanced, you have {account_balance} outstanding.'
        except Exception as e:
            print(e)

    def table(self, **kwargs):
        try:
            table = [['base_balance', f"{kwargs.get('base_balance')}"], ["cash_float", f"{kwargs.get('float')}"], ["expenses",
                      f"{kwargs.get('expenses')}"], ["banking", f"{kwargs.get('banking')}"], ["winning",
                     f"{kwargs.get('winning')}"], ["cash_in_shop", f"{kwargs.get('closing_balance')}"], ["admin_balance",
                     f"{kwargs.get('admin_balance')}"]]
            return table
        except Exception as e:
            print(e)
















 # # print the calculation flow for visibility
            # print(f"\nbase_balance: {kwargs.get('base_balance')} + cash_float: {kwargs.get('float')} + winning: {kwargs.get('winning')} -  "
            #       f"cash_in_shop: {kwargs.get('closing_balance')} - expenses: {kwargs.get('expenses')} "
            #       f"- banking: {kwargs.get('banking')} - admin_balance: {kwargs.get('admin_balance')}\n")