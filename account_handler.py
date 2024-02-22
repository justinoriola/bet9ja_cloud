from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException, UnexpectedAlertPresentException, ElementClickInterceptedException
import time
from datetime import datetime, timedelta
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import os

ACCOUNT_CREDENTIALS = {
    'ogba':{
        'username': os.getenv('USERNAME_OGBA'),
        'password': os.getenv('PASSWORD'),
        'cashier_password': os.getenv('CASHIER_PASSWORD_OGBA'),
        'amount_to_credit': 40000,
        'number_of_cashier': 4,
        'base_balance':1000000,
        'worksheet_name': "ogba_daily_spreadsheet",
        'worksheet_id': os.getenv('SPREADSHEET_OGBA')
    },
    'idiaraba':{
        'username': os.getenv('USERNAME_IDIARABA'),
        'password': os.getenv('PASSWORD'),
        'cashier_password': os.getenv('CASHIER_PASSWORD_IDIARABA'),
        'amount_to_credit': 40000,
        'number_of_cashier': 4,
        'base_balance':1000000,
        'worksheet_name': "idiaraba_daily_spreadsheet",
        'worksheet_id': os.getenv('SPREADSHEET_IDIARABA')
    },
    'awori': {
        'username': os.getenv('USERNAME_AWORI'),
        'password': os.getenv('PASSWORD'),
        'cashier_password': os.getenv('CASHIER_PASSWORD_AWORI'),
        'amount_to_credit': 30000,
        'number_of_cashier': 3,
        'base_balance':700000,
        'worksheet_name': "awori_daily_spreadsheet",
        'worksheet_id': os.getenv('SPREADSHEET_AWORI')
    },
    'moshalashi': {
        'username': os.getenv('USERNAME_MOSH'),
        'password': os.getenv('PASSWORD'),
        'cashier_password': os.getenv('CASHIER_PASSWORD_MOSH'),
        'amount_to_credit': 30000,
        'number_of_cashier': 3,
        'base_balance': 500000,
        'worksheet_name': "moshalashi_daily_spreadsheet",
        'worksheet_id': os.getenv('SPREADSHEET_MOSH'),
    },

}

# create a login decorator
def login_decorator(func):
    def wrapper(self, *args, **kwargs):
        self.login(*args, **kwargs)
        func(self, *args, **kwargs)
    return wrapper


class AccountHandler:

    # Constants
    TIME_NOW = datetime.now().strftime("%H:%M")
    TODAYS_DATE = datetime.now().strftime("%Y-%m-%d")

    def __init__(self, account_key):
        self.key = account_key
        self.admin_username = ACCOUNT_CREDENTIALS[self.key]['username']
        self.admin_password = ACCOUNT_CREDENTIALS[self.key]['password']
        self.cashier_password = ACCOUNT_CREDENTIALS[self.key]['cashier_password']
        self.credited_amount = ACCOUNT_CREDENTIALS[self.key]['amount_to_credit']
        self.cashier_numbers = ACCOUNT_CREDENTIALS[self.key]['number_of_cashier']
        self.sheet_name = ACCOUNT_CREDENTIALS[self.key]['worksheet_name']
        self.sheet_id = ACCOUNT_CREDENTIALS[self.key]['worksheet_id']
        self.base_balance = ACCOUNT_CREDENTIALS[self.key]['base_balance']
        self.cashier_to_be_credited = None
        self.password_checker = False
        self.cashier_reset_list = []

        # Set up Firefox webdriver for Openshift deployment path
        self.options = FirefoxOptions()
        self.options.binary_location = "/usr/lib/firefox-esr/firefox-esr"  # firefox path
        self.options.add_argument("--headless")  # headless mode option
        self.options.add_argument('--disable-gpu')  # Required for headless mode on certain systems
        self.options.add_argument('--private-window')  # incognito mode option
        self.driver_path = "/usr/local/bin/geckodriver"  # geckodriver path (requirement 4 Firefox browser)
        self.options.log.level = "trace"  # Set the log level to trace
        self.options.log.file = "./geckodriver.log"  # Provide the full path to geckodriver.log

    def login(self, **kwargs):
        try:
            # Initialize Firefox driver
            print(f"\nlogging into {self.admin_username}...")

            # Initialize alternative Firefox driver
            self.driver = webdriver.Firefox(options=self.options, executable_path=self.driver_path)

            # Navigate to the website and wait up to 60 seconds for the page to load
            self.driver.get('https://shop.bet9ja.com/')
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="h_w_PC_cLogin_ctrlLogin_Username"]'))
            )

            # check for admin or cashier password
            if self.password_checker:
                self.admin_password = self.cashier_password

            # log into admin or cashier account
            sign_in = self.driver.find_element(By.XPATH, '//*[@id="h_w_PC_cLogin_ctrlLogin_Username"]')
            sign_in.send_keys(self.admin_username)

            # Wait for the password field to be interactable
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="h_w_PC_cLogin_ctrlLogin_Password"]'))
            )
            password = self.driver.find_element(By.XPATH, '//*[@id="h_w_PC_cLogin_ctrlLogin_Password"]')
            password.send_keys(self.admin_password)

            # Wait for the login button to be interactable and click it
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.ID, "h_w_PC_cLogin_ctrlLogin_lnkBtnLogin"))
            )
            login = self.driver.find_element(By.ID, "h_w_PC_cLogin_ctrlLogin_lnkBtnLogin")
            login.click()

            # You can add another WebDriverWait here to wait for a successful login indication
            # For example, wait for a logout button to appear or a user profile section

            print("Logged in successfully")
        except Exception as e:
            print(f'login error occurred', e)

    def select_interaccount(self):
        # select interaccount option from portal
        inter_account = self.driver.find_element(By.LINK_TEXT, 'Interaccount')
        inter_account.click()

    def iframe_func(self):
        # select to iframe option
        iframe = self.driver.find_element(By.XPATH, '//*[@id="s_w_PC_PC_cCoupon_frameCassa"]')
        self.driver.switch_to.frame(iframe)

    def cashier_iframe_func(self):
        # switch to iframe option
        iframe_cashier = self.driver.find_element(By.ID, "iframe-content")
        self.driver.switch_to.frame(iframe_cashier)

    # @login_decorator
    def get_admin_balance(self):
        try:
            # instantiate account login
            self.login()
            print(f'Retrieving admin balance for {self.admin_username}')
            select_balance = self.driver.find_element(By.ID, 'hl_w_cLogin_lblDisponibilita')
            admin_balance = select_balance.text[:-2].strip().replace(',', '')
            print('admin balance retrieved successfully.\n')
            time.sleep(1)
            return round(float(admin_balance))
        except Exception as e:
            print(f'Error retrieving admin balance for {self.admin_username}: {e}')
        finally:
            self.driver.close()
        #     time.sleep(5)

    def deposit_options(self, i):
        try:
            select_drop_down = Select(
                self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_ctrlUser_ddlUtente"]'))
            options = [option for option in select_drop_down.options if option.text[10:].startswith('cashier')]
            options[i].click()
            time.sleep(3)
            deposit_amount = self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_txtImporto"]')
            deposit_amount.send_keys(self.credited_amount)
            time.sleep(3)
            submit_deposit = self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_btnAvanti"]')
            submit_deposit.click()
            time.sleep(3)
            confirm_submit = self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_btnConferma"]')
            confirm_submit.click()
            time.sleep(2)
            close_btn = self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_ctrlMessage_BottoneChiusura"]')
            close_btn.click()
            time.sleep(2)
        except Exception as e:
            print('An error occurred:', e)

    def credit_cashier(self, admin_balance: int):

        try:
            # Locate sign-in and password button, input credentials and confirm login.
            self.login()
            print(f"\nInitiating cashier crediting for account {self.admin_username}...")

            # Get into interaccount and credit cashier accounts
            self.select_interaccount()
            self.iframe_func()

            # Select dropdown option and credit corresponding cashier
            if int(admin_balance) >= self.credited_amount:
                if self.cashier_to_be_credited is not None:
                    i = self.cashier_to_be_credited - 1
                    self.deposit_options(i)
                    print(f'cashier {self.cashier_to_be_credited} credited successfully for account {self.admin_username}')
                else:
                    for i in range(self.cashier_numbers):
                        self.deposit_options(i)
                    print(f'{self.cashier_numbers} cashiers credited successfully for account {self.admin_username}')
            else:
                print("Balance on admin is low. Kindly fund account to avoid service disruption")

        except UnexpectedAlertPresentException as error:
            print("Unable to log in. Check for possible account disable \n{error}")
        except NoSuchElementException as e:
            print(f"Element not found: {e}")
        except InvalidSelectorException as error:
            print(f"Invalid selector found: {error}")
        finally:
            self.driver.quit()

    def withdraw_from_cashier(self):
        # Locate sign-in and password button, input credentials and confirm login.
        self.login()
        print(f"Initiating cashier Withdrawal for account {self.admin_username}...")
        try:
            # Select inter-account and get into iframe
            self.select_interaccount()
            self.iframe_func()

            # Loop through the cashier options
            for i in range(self.cashier_numbers):
                select_drop_down = Select(
                    self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_ctrlUser_ddlUtente"]'))
                select_drop_down = [option for option in select_drop_down.options if
                                    option.text[10:].startswith('cashier')]
                select_drop_down[i].click()
                time.sleep(2)

                # Get the amount to withdraw
                amount_to_withdraw = self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_lblSaldoUtente"]').text
                amount_to_withdraw = amount_to_withdraw[:-5].replace(",", "")
                if int(amount_to_withdraw) <= 0:
                    continue

                # Process withdrawal using amount_to_withdraw
                withdraw_button = self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_aPrelievo"]')
                withdraw_button.click()
                time.sleep(2)
                withdrawal_input = self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_txtImporto"]')
                withdrawal_input.send_keys(amount_to_withdraw)
                submit_withdrawal = self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_btnAvanti"]')
                submit_withdrawal.click()
                time.sleep(2)
                confirm_submit = self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_btnConferma"]')
                confirm_submit.click()
                time.sleep(2)
                close_btn = self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_ctrlMessage_BottoneChiusura"]')
                close_btn.click()
                time.sleep(2)

        except UnexpectedAlertPresentException as error:
            print("Unable to log in. Check for possible account disable \n{error}")
        except NoSuchElementException as e:
            print(f"Element not found: {e}")
        except InvalidSelectorException as error:
            print(f"Invalid selector found: {error}")
        else:
            print(f'All cashier withdrawal was successful for account {self.admin_username}')
        finally:
            self.driver.quit()

    def bet_payout(self, bet_ids: list) -> list:
        # Check the length of bet_id list, instantiate login, and then loop through.
        if len(bet_ids) > 0:
            self.login()
            print(f'Paying out bets for account {self.admin_username}...')
            result = []
            for bet in bet_ids:
                if bet.lower().startswith('b'):
                    try:
                        # Select inter-account and get into iframe
                        self.driver.find_element(By.LINK_TEXT, 'Bet List').click()
                        time.sleep(2)
                        input_id = self.driver.find_element(By.XPATH, '//*[@id="ac_w_PC_PC_BetList_txtCodiceCoupon"]')
                        input_id.send_keys(bet.strip())
                        time.sleep(2)
                        continue_btn = self.driver.find_element(By.XPATH, '//*[@id="ac_w_PC_PC_BetList_btnAvanti"]')
                        continue_btn.click()
                        time.sleep(2)
                        self.driver.find_element(By.XPATH, '//*[@id="ac_w_PC_PC_BetList_grid_ctl02_lnkCoupon"]').click()
                        time.sleep(2)
                        bet_id_radio_button = self.driver.find_element(By.XPATH, '//*[@id="ac_w_PC_PC_chkPagata"]')
                        if bet_id_radio_button.is_selected():
                            print(f'Bet ID {bet} previously paid')
                            continue

                        bet_id_radio_button.click()
                        time.sleep(1)
                        self.driver.find_element(By.XPATH, '// *[ @ id = "ac_w_PC_PC_btnSalvaPag"]').click()
                        self.driver.find_element(By.LINK_TEXT, 'Bet List').click()
                        result.append(bet)
                        print(f"Bet ID: {bet} paid successfully!")
                    except NoSuchElementException as e:
                        print(f"Bet ID: {bet} not found!")
                        time.sleep(2)
            self.driver.quit()
            return result

    def winning_balance(self):
        try:
            self.login()
            print("Retrieving winning_balance...")
            self.driver.find_element(By.LINK_TEXT, 'Bet List').click()
            time.sleep(2)
            input_element = self.driver.find_element(By.XPATH, '//*[@id="ac_w_PC_PC_BetList_cpopDal_CalendarBase_txtDate"]')

            # Retrieve the value attribute
            date_value = input_element.get_attribute('value')

            # Subtract 14 days and format the result back to a string
            date_value = (datetime.strptime(date_value, '%d/%m/%Y') - timedelta(days=30)).strftime('%d/%m/%Y')
            input_element.clear()
            time.sleep(1)
            input_element.send_keys(date_value)
            self.driver.find_element(By.XPATH, '//*[@id="ac_w_PC_PC_BetList_rblStatoPagamento_1"]').click()
            self.driver.find_element(By.XPATH, '//*[@id="ac_w_PC_PC_BetList_ddlPageSize"]/option[3]').click()

            select_drop_down = self.driver.find_element(By.XPATH, '//*[@id="ac_w_PC_PC_BetList_ddlEsito"]/option[4]')
            select_drop_down.click()
            time.sleep(3)
            continue_btn = self.driver.find_element(By.XPATH, '//*[@id="ac_w_PC_PC_BetList_btnAvanti"]')
            continue_btn.click()
            time.sleep(2)
            winning_value = self.driver.find_element(By.XPATH, '//*[@id="ac_w_PC_PC_BetList_VincitaTotPagina"]')
            winning = int(winning_value.get_attribute('value')[:-3].replace(',', ''))
            print(f'winning balance retrieved successfully.')
            return winning
        except ValueError as e:
            return 0
        except NoSuchElementException:
            self.driver.find_element(By.LINK_TEXT, 'Bet List').click()
        finally:
            self.driver.quit()
            time.sleep(3)

    def cashier_check(self, number_of_cashiers):
        """"This function is used to check the cashier account for any stranded fund.
        If found, withdraw the fund into admin"""

        # output to console when logging process is initiated/set password_checker variable.
        print(f'\nprocessing cashier league/racing reset for {self.admin_username}...')
        self.password_checker = True
        username = self.admin_username
        password = self.admin_password

        # loop through the number of cashiers to process stranded funds.
        for i in range(1, (number_of_cashiers + 1)):
            try:
                time.sleep(2)
                username_split_value = username.split('-')[2]
                self.admin_username = f"cashier{username_split_value}-0{i}"
                self.login()
                time.sleep(1)

                # Get the initial window handles
                initial_window_handles = self.driver.window_handles
                # interact with element within initial window_handle
                cashier_button = self.driver.find_element(By.XPATH, '//*[@id="divContent"]/div[1]/ul/li[1]/ul/li[5]/a')
                cashier_button.click()
                time.sleep(3)

                # Get the updated window handles
                updated_window_handles = self.driver.window_handles
                # Find the new tab handle by comparing the initial and updated handles
                new_tab_handle = [handle for handle in updated_window_handles if handle not in initial_window_handles][0]
                # Switch to the new tab
                self.driver.switch_to.window(new_tab_handle)
                time.sleep(5)

                # switch to iframe element
                self.cashier_iframe_func()
                # interact with iframe content in new tab
                reset_league = self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div/table/tbody/tr[1]/td[1]/div/div[2]/a')
                reset_league.click()
                time.sleep(2)
                # reset_race = self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div/table/tbody/tr[2]/td[1]/div/div[2]/a')
                # reset_race.click()
                self.cashier_reset_list.append(self.admin_username)
                print(f'stranded funds found in {self.admin_username}')

                # Close the both windows
                self.driver.close()
                self.driver.switch_to.window(initial_window_handles[0])  # Switch back to the main tab
                self.driver.close()  # Close the initial window

                # Quit the WevDriver
                self.driver.quit()

            except (ElementClickInterceptedException, NoSuchElementException) as e:
                print(f'no stranded fund in {self.admin_username}, tab closed!')
                self.driver.close()
                self.driver.quit()
                time.sleep(5)
            except Exception as e:
                login_error = f'unable to login to {self.admin_username}'
                self.cashier_reset_list.append(login_error)
        self.password_checker = False
        self.admin_username = username
        self.admin_password = password
        print('cashier reset processed successfully!')
        if len(self.cashier_reset_list) > 0:
            cashiers_with_stranded_funds = ', '.join(self.cashier_reset_list)
            return f'stranded funds found in {cashiers_with_stranded_funds}'
        else:
            return f'no stranded funds found in cashiers'







    # Reserve
    # options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # options.add_argument('--no-sandbox')
    # options.add_argument('disable-dev-shm-usage')
    # options.add_argument("--user-data-dir=/tmp")
    # self.driver = webdriver.Chrome(options=options)
    # self.driver.get("https://shop.bet9ja.com")

    # self.chrome_driver_path = '/usr/local/bin/chromedriver'
    # self.options = webdriver.ChromeOptions()
    # self.options.add_argument('--ignore-ssl-errors=yes')
    # self.options.add_argument('--ignore-certificate-errors')
    # self.driver = webdriver.Remote(
    #     command_executor='http://selenium-hub:4444/wd/hub', desired_capabilities={'browserName': 'chrome'}
    # )
    # self.driver = webdriver.Remote(
    #     command_executor='http://localhost:4444/wd/hub',
    #     options=self.options
    # )