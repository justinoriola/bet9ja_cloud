# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchElementException, InvalidSelectorException
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium import webdriver
# from datetime import datetime
# import time
#
# class AccountHandler:
#
#     # Constants
#     TIME_NOW = datetime.now().strftime("%H:%M")
#     TODAYS_DATE = datetime.now().strftime("%Y-%m-%d")
#
#     def __init__(self, admin_username: str, admin_password: str, amount_to_be_credited: int, total_number_of_cashiers: int, cashier_to_be_credited=None):
#         self.admin_username = admin_username
#         self.admin_password = admin_password
#         self.amount_to_be_credited = amount_to_be_credited
#         self.cashier_to_be_credited = cashier_to_be_credited
#         self.total_number_of_cashiers = total_number_of_cashiers
#         self.chrome_driver_path = '/Users/joriola/Downloads/chromedriver'
#         self.chrome_service = ChromeService(executable_path=self.chrome_driver_path)
#         self.driver = webdriver.Chrome(service=self.chrome_service)
#         self.driver.get("https://shop.bet9ja.com")
#
#     def wait_for_element(self, by, value, timeout=5):
#         return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
#
#     def click_element(self, by, value):
#         element = self.wait_for_element(by, value)
#         element.click()
#
#     def deposit_dropdown_options(self, i):
#         select_drop_down = Select(self.wait_for_element(By.XPATH, '//*[@id="ctl00_PC_ctrlUser_ddlUtente"]'))
#         options = [option for option in select_drop_down.options if option.text[10:].startswith('cashier')]
#         options[i].click()
#         time.sleep(2)
#
#         self.driver.find_element(By.XPATH, '//*[@id="ctl00_PC_txtImporto"]').send_keys(self.amount_to_be_credited)
#         self.click_element(By.XPATH, '//*[@id="ctl00_PC_btnAvanti"]')
#         time.sleep(2)
#         self.click_element(By.XPATH, '//*[@id="ctl00_PC_btnConferma"]')
#         time.sleep(2)
#         self.click_element(By.XPATH, '//*[@id="ctl00_PC_ctrlMessage_BottoneChiusura"]')
#         time.sleep(2)
#
#     def login(self):
#         sign_in = self.wait_for_element(By.XPATH, '//*[@id="h_w_PC_cLogin_ctrlLogin_Username"]')
#         sign_in.send_keys(self.admin_username)
#
#         password = self.wait_for_element(By.XPATH, '//*[@id="h_w_PC_cLogin_ctrlLogin_Password"]')
#         password.send_keys(self.admin_password)
#
#         time.sleep(2)
#         login = self.wait_for_element(By.ID, "h_w_PC_cLogin_ctrlLogin_lnkBtnLogin")
#         login.click()
#         time.sleep(5)
#
#     def get_admin_balance(self):
#         select_balance = self.wait_for_element(By.ID, 'hl_w_cLogin_lblDisponibilita')
#         admin_balance = select_balance.text[:-2].strip().replace(',', '').replace('.', '')
#         time.sleep(1)
#         return int(admin_balance)
#
#     def switch_to_interaccount_frame(self):
#         inter_account = self.wait_for_element(By.LINK_TEXT, 'Interaccount')
#         inter_account.click()
#         iframe = self.wait_for_element(By.XPATH, '//*[@id="s_w_PC_PC_cCoupon_frameCassa"]')
#         self.driver.switch_to.frame(iframe)
#
#     def credit_cashier(self):
#         try:
#             self.login()
#             admin_balance = self.get_admin_balance()
#
#             self.switch_to_interaccount_frame()
#
#             if admin_balance >= self.amount_to_be_credited:
#                 if self.cashier_to_be_credited is not None:
#                     i = self.cashier_to_be_credited - 1
#                     self.deposit_dropdown_options(i)
#                 else:
#                     for i in range(self.total_number_of_cashiers):
#                         self.deposit_dropdown_options(i)
#             else:
#                 print("Balance on admin is low. Kindly fund account to avoid service disruption")
#
#         except UnexpectedAlertPresentException as error:
#             print(f"Unable to log in. Check for possible account disable \n{error}")
#         except (NoSuchElementException, InvalidSelectorException) as e:
#             print(f"Element not found: {e}")
#         finally:
#             print(f'{self.total_number_of_cashiers} cashiers credited successfully for account {self.admin_username}'
#                   f'\nDate: {self.TODAYS_DATE}, Time: {self.TIME_NOW}')
#             self.driver.quit()
#
#     def withdraw_from_cashier(self):
#         try:
#             self.login()
#             self.switch_to_interaccount_frame()
#
#             for i in range(self.total_number_of_cashiers):
#                 select_drop_down = Select(self.wait_for_element(By.XPATH, '//*[@id="ctl00_PC_ctrlUser_ddlUtente"]'))
#         except NoSuchElementException as error:
#             print(f"Element not found: {error}")
