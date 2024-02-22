from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from time import sleep
from googleapiclient.errors import HttpError
import random
load_dotenv(dotenv_path='.env')
from datetime import datetime, timedelta, time
from account_handler import AccountHandler


# Constants
MY_EMAIL = os.environ.get('MY_EMAIL')
GOOGLE_API_SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'old-credentials.json'
MAX_RETRIES = 5
CURRENT_TIME = datetime.now().time()




class SpreadSheetHandler(AccountHandler):

    def __init__(self, spreadsheet_id, spreadsheet_name, admin_username: str, admin_password: str, amount_to_credit: int,
                 total_number_of_cashiers: int):
        super().__init__(admin_username, admin_password, amount_to_credit, total_number_of_cashiers)

        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet_name = spreadsheet_name
        self.scope = GOOGLE_API_SCOPES
        self.service_account_file = SERVICE_ACCOUNT_FILE
        self.spreadsheet_data = {}
        self.credentials = self.get_credentials()
        self.service_sheet = build('sheets', 'v4', credentials=self.credentials)
        self.service_drive = build('drive', 'v3',credentials=self.credentials)
        self.today = datetime.now().strftime('%A')
        self.retry_counter = 0

    def get_credentials(self):
        return service_account.Credentials.from_service_account_file(self.service_account_file, scopes=self.scope)

    # Select spreadsheet day based on script run time
    def closing_balance(self):
        if time(00, 0) <= CURRENT_TIME <= time(20, 29):
            closing_balance_day = datetime.now() - timedelta(days=1)
            return closing_balance_day.strftime('%A')
        else:
            return self.today

    def bet_day(self, day_of_the_week):
        day_ranges = {
            'Tuesday': '!N6:N56',
            'Wednesday': '!O6:O56',
            'Thursday': '!P6:P56',
            'Friday': '!R6:R56',
            'Saturday': '!O6:O56',
            'Sunday': '!S6:S56',
            'Monday': '!T6:T56'
        }
        return 'Weekly Report' + day_ranges.get(day_of_the_week, '')

    def get_spreadsheet_values(self):
        print(f'\nRetrieving spreadsheet value(s) for account {self.admin_username}...')

        # Data
        WEEKLY_REPORT_RANGE = {
            'total_float': 'Weekly Report' + '!G15',
            'total_expenses': 'Weekly Report' + '!I15',
            'total_banking': 'Weekly Report' + '!k15',
            'bet_ids': 'Weekly Report' + '!N6:T56',
            'closing_balance': f'{self.closing_balance()}' + '!G19',
            'already_paid_bet': 'Weekly Report' + '!W6:W100',
        }
        # Calculate the delay between each request to avoid exceeding rate limit (60 requests per minute)
        delay = 100.0 / 60

        # Loop over the weekly report range
        for key, value in WEEKLY_REPORT_RANGE.items():
            for i in range(MAX_RETRIES):
                sleep(delay)
                try:
                    response = self.service_sheet.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id,
                                                                              range=value).execute()
                    values = response.get('values', [])
                    result = [item[0].strip() for item in values]
                    if key == 'bet_ids':
                        result = [value.strip() for sublist in values for value in sublist if isinstance(value, str)
                              and value.lower().startswith('b')]
                    self.spreadsheet_data[key] = result
                    break
                except HttpError as error:
                    if error.resp.status == 429:
                        print(f'API rate limit exceeded. Retrying in {i ** 2} seconds.')
                        sleep((i ** 2) + random.random())
                    else:
                        if self.retry_counter == 0:
                            print(f'Something went wrong. Retrying in {120} seconds.')
                            sleep(120)
                            self.get_spreadsheet_values()
                            self.retry_counter += 1
                        else:
                            print(f'Unable to retrieve spreadsheet value for {key}: {value}')
                            print(f'HTTP error occurred: {error}')
                            break
        print(f'All spreadsheet values retrieved successfully')

        return self.spreadsheet_data


    def create_spreadsheet_duplicate(self, duplicate_spreadsheet_name):

        try:
            # Create a request for duplicating the Spreadsheet
            request = self.service_drive.files().copy(
                fileId=self.spreadsheet_id,
                body={"name": duplicate_spreadsheet_name}
            ).execute()
            copied_file_id = request.get('id')

            # Share the copied spreadsheet with your account
            def_permission = self.service_drive.permissions().create(
                fileId=copied_file_id,
                body={
                    'type': 'user',
                    'role': 'writer',
                    'emailAddress': MY_EMAIL
                },
                fields='id'
            ).execute()
            sleep(3)
            print(f"duplicate spreadsheet '{duplicate_spreadsheet_name}' was successfully created.")
        except Exception as error:
            print(f'An error occurred: {error}')



    def clear_spreadsheet(self, days_to_clear):

        """Clears specific cells of a spreadsheet for a given day."""
        # Data - cells in spreadsheet to be cleared
        cells_to_clear = {
            f'{days_to_clear}!C10:E19': [['0', '0', '0']] * 10,
            f'{days_to_clear}!G10:G19': [['0']] * 10,
            f'{days_to_clear}!K6:K22': [['x']] * 17,
            f'{days_to_clear}!L6:L22': [['0']] * 17,
            f'{days_to_clear}!M6:M22': [['x']] * 17,
            f'{days_to_clear}!N6:N22': [['0']] * 17,
            f'{days_to_clear}!O6:O22': [['x']] * 17,
            f'{days_to_clear}!P6:P22': [['0']] * 17,
            f'{days_to_clear}!C32:C56': [['0']] * 25,
            f'{days_to_clear}!D33:D56': [['x']] * 24,
            f'{days_to_clear}!E32:E56': [['0']] * 25,
            f'{days_to_clear}!F33:F56': [['x']] * 24,
            f'{days_to_clear}!G32:G56': [['0']] * 25,
            f'{days_to_clear}!L33:L57': [['0']] * 25,
            f'{days_to_clear}!N33:N57': [['0']] * 25,
            f'{days_to_clear}!P33:P57': [['0']] * 25,
            f'{days_to_clear}!M34:M57': [['x']] * 24,
            f'{days_to_clear}!O34:O57': [['x']] * 24,
        }

        # Loop over the cells to be cleared
        for cell_range, new_values in cells_to_clear.items():
            for i in range(MAX_RETRIES):
                try:

                    # Prepare the request body with the new values
                    body = {
                        'values': new_values
                    }

                    # Send the update request
                    result = self.service_sheet.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=cell_range,
                        valueInputOption='USER_ENTERED',
                        body=body).execute()

                    print(f'Successfully cleared cells "{cell_range}"')
                    sleep(3)
                    break
                except HttpError as error:
                    if error.resp.status == 429:
                        print(f'API rate limit exceeded. Retrying in {i ** 2} seconds.')
                        sleep((i ** 2) + random.random())
                    else:
                        print(f'HTTP error occurred: {error}')
                        break

    def upload_to_google_sheets(self, value_list1, value_list2):
        if value_list1 is not None:
            for i in range(MAX_RETRIES):
                try:
                    """
                    Upload a list of values to a Google Spreadsheet using Google Sheets API.
            
                    Args:
                    - values_list (list): The list of values to upload.
                    - spreadsheet_id (str): The ID of the Google Spreadsheet.
                    - sheet_name (str): The name of the sheet in the spreadsheet (default is 'Sheet1').
                    """
                    range_ = f'Weekly Report!W{len(value_list2) + 6}'

                    # Resize the sheet based on the length of the values_list
                    result = self.service_sheet.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=range_,
                        body={'values': [[value] for value in value_list1]},
                        valueInputOption='RAW'
                    ).execute()
                    print(f'Paid tickets successfully uploaded on the spreadsheet')
                    break
                except HttpError as error:
                    if error.resp.status == 429:
                        print(f'API rate limit exceeded. Retrying in {i ** 2} seconds.')
                        sleep((i ** 2) + random.random())
                    else:
                        print(f'HTTP error occurred: {error}')
                        break

    def filtered_bet_list(self, bet_list1: list, bet_list2: list) -> list:
        print('\nfiltering bet list...')
        try:
            filtered_bet_list = [item for item in bet_list1 if item not in bet_list2]
            if len(filtered_bet_list) == 0:
                print('no new bet ticket(s) found')
            else:
                print(f'{len(filtered_bet_list)} new bet tickets found')
            return filtered_bet_list
        except Exception as error:
            print(f'error occurred: {error}')

