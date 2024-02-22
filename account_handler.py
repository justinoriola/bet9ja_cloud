from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException, UnexpectedAlertPresentException
import time
from datetime import datetime, timedelta
from selenium.webdriver.firefox.options import Options as FirefoxOptions

class AccountHandler:

    # Constants
    TIME_NOW = datetime.now().strftime("%H:%M")
    TODAYS_DATE = datetime.now().strftime("%Y-%m-%d")

    def __init__(self, admin_username: str, admin_password: str, amount_to_credit: int, total_number_of_cashiers: int):
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.amount_to_be_credited = amount_to_credit
        self.cashier_to_be_credited = None
        self.total_number_of_cashiers = total_number_of_cashiers

        # Set up Firefox webdriver for Openshift deployment path
        self.options = FirefoxOptions()
        self.options.binary_location = "/usr/lib/firefox-esr/firefox-esr"  # firefox path
        self.options.add_argument("--headless")  # headless mode option
        self.options.add_argument('--disable-gpu')  # Required for headless mode on certain systems
        self.options.add_argument('--private-window')  # incognito mode option
        self.driver_path = "/usr/local/bin/geckodriver"  # geckodriver path (requirement 4 Firefox browser)
        self.options.log.level = "trace"  # Set the log level to trace
        self.options.log.file = "./geckodriver.log"  # Provide the full path to geckodriver.log

    def login(self):
        # Initialize Firefox driver
        print(f'\nlogging into account {self.admin_username}...')

        # Initialize alternative Firefox driver
        self.driver = webdriver.Firefox(options=self.options, executable_path=self.driver_path)
        self.driver.get('https://shop.bet9ja.com/')


        sign_in = self.driver.find_element(By.XPATH, '//*[@id="h_w_PC_cLogin_ctrlLogin_Username"]')
        sign_in.send_keys(self.admin_username)
        password = self.driver.find_element(By.XPATH, '//*[@id="h_w_PC_cLogin_ctrlLogin_Password"]')
        password.send_keys(self.admin_password)
        time.sleep(2)
        login = self.driver.find_element(By.ID, "h_w_PC_cLogin_ctrlLogin_lnkBtnLogin")
        login.click()
        time.sleep(2)

    def select_interaccount(self):
        inter_account = self.driver.find_element(By.LINK_TEXT, 'Interaccount')
        inter_account.click()

    def iframe_func(self):
        iframe = self.driver.find_element(By.XPATH, '//*[@id="s_w_PC_PC_cCoupon_frameCassa"]')
        self.driver.switch_to.frame(iframe)

    def get_admin_balance(self):
        try:
            self.login()
            print(f'Retrieving admin balance for {self.admin_username}')
            select_balance = self.driver.find_element(By.ID, 'hl_w_cLogin_lblDisponibilita')
            admin_balance = select_balance.text[:-2].strip().replace(',', '')
            print('admin balance successfully retrieved\n')
            time.sleep(1)
            return round(float(admin_balance))
        except Exception as e:
            print(f'Error retrieving admin balance for {self.admin_username}: {e}')
        finally:
            self.driver.quit()
            # Get balance on admin

    def deposit_options(self, i):
        select_drop_down = Select(
            self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_ctrlUser_ddlUtente"]'))
        options = [option for option in select_drop_down.options if option.text[10:].startswith('cashier')]
        options[i].click()
        time.sleep(3)
        deposit_amount = self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_txtImporto"]')
        deposit_amount.send_keys(self.amount_to_be_credited)
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

    def credit_cashier(self, admin_balance):

        try:
            # Locate sign-in and password button, input credentials and confirm login.
            self.login()
            print(f"Initiating cashier crediting for account {self.admin_username}...")

            # Get into interaccount and credit cashier accounts
            self.select_interaccount()
            self.iframe_func()

            # Select dropdown option and credit corresponding cashier
            if int(admin_balance) >= self.amount_to_be_credited:
                if self.cashier_to_be_credited is not None:
                    i = self.cashier_to_be_credited - 1
                    self.deposit_options(i)
                    print(
                        f'cashier {self.cashier_to_be_credited} credited successfully for account {self.admin_username}'
                        f'\nDate: {self.TODAYS_DATE}, Time: {self.TIME_NOW}')
                else:
                    for i in range(self.total_number_of_cashiers):
                        self.deposit_options(i)
                    print(
                        f'{self.total_number_of_cashiers} cashiers credited successfully for account {self.admin_username}'
                        f'\nDate: {self.TODAYS_DATE}, Time: {self.TIME_NOW}')
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
            for i in range(self.total_number_of_cashiers):
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
            # self.driver.quit()
            return result

    def winning_balance(self):
        try:
            # self.login()
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
            print(f'admin winning balance successfully retrieved.')
            return winning
        except ValueError as e:
            return 0
        except NoSuchElementException:
            self.driver.find_element(By.LINK_TEXT, 'Bet List').click()
        self.driver.quit()








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