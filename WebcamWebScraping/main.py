import json
import pickle
import pprint
import time
from datetime import datetime, timedelta

import html_to_json
import requests

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

# CONTANTS
port = 4444
url_docker = 'http://localhost:'+ str(port) +'/wd/hub'
url_accounts = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
md5 = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
now = datetime.now()
headers = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

# WEB DRIVER
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--user-data-dir=/home/seluser/userdata')

driver = webdriver.Remote(command_executor=url_docker, options=options)
#maximize the window size
driver.maximize_window()
time.sleep(10)

class cb_hours:

    # INIT MAIN - CONSTRUCTOR
    def __init__(self):

        print('Main is Ready!')
        print('### Production Mode')
        
        self.now = datetime.now()
        self.start = ''
        self.end = ''
        self.accounts = []
        self.block_chain = []
        self.auto = False
        # MANUAL
        self.date_ini = '2024-07-08'
        self.date_end = '2024-07-14'
        
    # GET ACCOUNTS FROM API
    def get_accounts(self, site):
        # LOCAL VARS
        n = 50
        chain = []

        # HTTP REQUEST (API GET) FOR ACCOUNTS DATA (nickname, email, site_id)
        try:
        # GET REQUEST  
            print('\n')
            print('# Getting Accounts From Server...')
            http_request = requests.get(url_accounts + '/1?key=' + str(md5), headers=headers)
            print(http_request.status_code)

            if http_request:
                print('Response OK')
                # STRING JSON RESPONSE TO JSON FORMAT 
                response = json.loads(http_request.text)
                # print(response)

                # GET ESPECIFIC SITE ACCOUNTS
                for account in response:

                # print(account)
                # CHATURBATE
                    if account['site_id'] == int(site):
                        chain.append(account)

                # SPLIT RESPONSE TO ARRAY OF ARRAYS WITH 50 PARTS   
                # BLOCKS FOR SEARCH TEXTAREA INSERT
                self.accounts = [chain[i:i + n] for i in range(0, len(chain), n)]

            else:
                print('Response Failed')
                
        except Exception as e:
            print(e)


    # FORMATING AND SEND DATA BLOCKS
    def get_data(self, site):

      # FILTER ACCOCUNTS FOR ACTIONS
      submit = 2

      # ACCOUNTS ARE IN BLOCK OF 50 LEN
      for blocks in self.accounts:

        # CLEAN TEXT AREA FOR LOOP
        self.find('//*[@id="studioForm"]/div[1]/textarea').clear()

        for item in blocks:
          
          if item['site_id'] == site:
            print('# nickname: ' + str(item['nickname']))
            self.insert_nickname(item['nickname'], '//*[@id="studioForm"]/div[1]/textarea')

        print('End Block... #' + str(self.accounts.index(blocks) + 1))
        print('\n')

        # SEND DATA FORM TO SEARCH TIME ONLINE
        print('Sending Data Form...')

        self.click('//*[@id="studioForm"]/div[1]/input['+ str(submit) +']')  
        time.sleep(5)

        # CHATURBATE CONDITION
        if site == 1:
          if submit == 2:
            submit += 1
        # STRIPCHAT CONDITION
        if site == 4:
          if submit == 2:
            submit += 1

        activity_logs = self.find('/html/body/div[1]/div[2]/div/div')
        logs = activity_logs.get_attribute('innerHTML')
        # CONVERT HTML DATA TABLE TO JSON
        json_logs = html_to_json.convert(logs)


        for p in json_logs['p']:

          paragraph  = p['_value']

          # SEARCH STRING ON ORIGINAL TO VALIDATE
          if paragraph.find('Not found') == -1:
            # MODEL WITH TIMEONLINE HAVE LINK ELEMENT

            try:
              for a in p['a']:       
                # CREATE AND CLEAN OBJECT
                print('Nickname: ' + a['_value'] + '  /  TimeOnline: ' + p['_value'])
                object_data = {}
                object_data['nickname'] = a['_value']
                object_data['time'] = self.format_time_str(p['_value'])
                object_data['original'] = p['_value']
                object_data['site'] = site

                self.block_chain.append(object_data)
            except:
              pass

        time.sleep(2.5)

      pprint.pprint(self.block_chain)
    
    # EXTRACT MINUTES FROM CBHOURS TIME STRING
    def format_time_str(self, string):

      SECONDS = int(60)
      time_array = []
      # CLEAN ORIGINAL STRING AND CREATE NEW FORMAT
      new_str = string.replace(' Hours ', '-')
      new_time_str = new_str.replace(' Minutes', '')
      # SPLIT FORMAT TO ARRAY
      time_array = new_time_str.split('-')
      # CONVERT HOURS TO MINUTES
      int_h = int(time_array[0]) * SECONDS
      # GET MINUTES
      int_m = time_array[1] 
      # RETURN TIME IN MINUTES
      return int(int_h) + int(int_m)

    # OPEN URL FROM CHROME DRIVER
    def open_url(self, url):
      try:
        print('Opening URL => ' + url)
        driver.get(url)
        time.sleep(5)
      except Exception as e:
        print('Error abriendo la url => ', e)

    # GET JSON FROM HTML
    def get_json(self, xpath):

      # VIEW CURRENT REPORT 
      element = self.find(xpath) 
      html = element.get_attribute('innerHTML')

      # CONVERT TO JSON
      try:
        return html_to_json.convert(html)
      except:
        print('Ha ocurrido un error convirtiendo el html a json')

    # ELEMENT CLICK
    def click(self, xpath):
      try:
        # FIND ELEMENT BY XPATH
        element = self.find(xpath)
        # WAIT FOR ELEMENT GET READY TO CLICK
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element.click()
      
      except Exception as e:
        print('Error en click element ', e)

    # ELEMENT FIND BY XPATH
    def find(self, xpath):
      try:
        return driver.find_element('xpath', xpath)
      except NoSuchElementException as e:
        print('Elemento no encontrado => ' + str(xpath))

    # INSERT NICKNAME TO TEXTAREA
    def insert_nickname(self, nickname, xpath):
      try:
        # SEARCH ELEMENT FOR NICKNAME INSERT AND SEND KEYS
        element = self.find(xpath)
        element.send_keys(nickname.lower())
        element.send_keys('\n')
      except Exception as e:
        print('Error insertando nickname ', e)

    # SET START AND END
    def get_dates(self):

      time.sleep(5)
      # GET CURRENT WEEK FROM INIT UNTIL THE END (MONDAY TO SUNDAY)
      week_array = [
        self.now + timedelta(days=i) for i in range(0 - self.now.weekday(), 7 - self.now.weekday())
      ]
      # SET DATES FORM
      self.start = week_array[0].strftime('%Y-%m-%d')
      self.end = week_array[6].strftime('%Y-%m-%d')
    
    # SELECT DATE RANGE FOR SEARCH
    def set_date_range(self, start_xpath, end_xpath):

      # CLICK CALENDAR DATE FROM    
      self.click(start_xpath)

      # CALENDAR ITERATOR
      calendar = self.get_calendar(self.start)
      print('Click on Calendar...')
      time.sleep(1)
      
      week_array = [
        self.now + timedelta(days=i) for i in range(0 - self.now.weekday(), 7 - self.now.weekday())
      ]

      if self.auto:
        print('Auto Running...')
        week_array = [self.now + timedelta(days=i) for i in range(0 - self.now.weekday(), 7 - self.now.weekday())]
        # CLIK DATE FROM
        self.click_js_calendar(start_xpath, week_array[0], calendar)
        # # CLIK DATE TO
        self.click_js_calendar(end_xpath, datetime.today(), calendar)
      else:
        # MANUAL UPDATE
        print('Running Manual...')
        self.start = self.date_ini
        self.end = self.date_end
        # CLIK DATE FROM
        self.click_js_calendar(start_xpath, datetime.strptime(self.date_ini, '%Y-%m-%d'), calendar)
        # CLIK DATE TO
        self.click_js_calendar(end_xpath, datetime.strptime(self.date_end, '%Y-%m-%d'), calendar)

    def get_calendar(self, date):

        print('From Get Calendar...')
        print(date)

        date = datetime.strptime(date, '%Y-%m-%d')

        matrix_calendar = []
        # GET CALENDAR DATA FOR SEARCH START AND END DATES
        calendar = driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/table')
        source = calendar.get_attribute('innerHTML')
        json = html_to_json.convert(source)

        try:

            for table in json['tbody']:
                # ROLLING UP ROWS
                for week in table['tr']:
                    # GET INDEX FOR TR
                    week_index = table['tr'].index(week)
                    # print('Week', week_index)

                    # ROLLING UP COLUMNS
                    for day in week['td']:
                    # CREATE CLEAN OBJECT 
                        object_calendar = {}
                        # GET INDEX FOR TD
                        day_index = week['td'].index(day)
                        # print('Day', day_index)
                        # SET VALUES FOR MATRIX CALENDAR INDICES
                        object_calendar['week'] = week_index + 1
                        object_calendar['day'] = day_index
                        if 'a' in day:
                            # INDEX FOR MATRIX TABLE WHEN DAY MATCH
                            # print('Real Day', day['a'][0]['_value'])
                            object_calendar['value'] = day['a'][0]['_value']
                            object_calendar['weekday'] = week['td'].index(day)
                            object_calendar['isoweekday'] = date.isoweekday()
                            # ADD OBJECT TO BLOCK CHAIN ARRAY
                            matrix_calendar.append(object_calendar)

        except Exception as e:
            print('Error seleccionando elemento en la matriz del calendario ', e)

        return matrix_calendar

    # CLICK ON SELETED DATE
    def click_js_calendar(self, xpath, date, calendar):

      # CLICK CALENDAR DATE
      print('From click_js_calendar() ', date)
      self.click(xpath)
      time.sleep(3)

      month = driver.find_element(By.CLASS_NAME, 'ui-datepicker-month').text
      month = datetime.strptime(month, '%B')
      month = int(month.strftime('%m'))

      if date.month != month:     
        prev = driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div/a[1]')
        prev.click()
        time.sleep(3)   

        calendar = self.get_calendar(self.start)
     
      for item in calendar:

        if item['value'] == date.day:
          print('Entramos!!');
          time.sleep(100)

        if item['value'] == str(date.day):

          print('Entramos ###################################################')
          print('item["value"] = ' + str(item['value']))
          print('item["day"] = ' + str(item['day']))
          print('item["weekday"] = ' + str(item['weekday']))
          print('item["isoweekday"] = ' + str(item['isoweekday']))
          print('date.day = ' + str(date.day))
          print('date.weekday() = ' + str(date.weekday()))
          print('\n')

        if item['value'] == str(date.day) and item['day'] == item['weekday']:
          # SELECT INPUT TO DATE 
          print('# Selecting Date ' + str(item['value']))
          print('Week ' + str(item['week']))
          print('Weekday ' + str(item['weekday']))
          print('ISO Weekday ' + str(item['isoweekday']))
          print('Day ', date.day , str(item['day']))              

          self.click('//*[@id="ui-datepicker-div"]/table/tbody/tr['+ str(item['week']) +']/td['+ str(item['day'] + 1) +']/a')
          print('Seleted OK')
          print('\n')

      time.sleep(1)

    # SEND BLOCK
    def send_blocks(self):
     
      # CREATE AND CLEAN OBJECT TO SEND
      data_post = {}
      data_post['key'] = md5
      data_post['data'] = json.dumps(self.block_chain)
      data_post['start'] = self.start
      data_post['end'] = self.end
      data_post['now'] = now

      # HTTP REQUEST
      post_response = requests.post(url_accounts, data_post, headers=headers)

      print(post_response.text)
      print(post_response.status_code)
      # LOGGER RESPONSE
      self.logger(post_response.text)

      if post_response:
        print('Response OK')
        try:
          pprint.pprint(post_response.text)
          print('Send Blocks Success!')
          time.sleep(2)

        except:
          print('Error convirtiendo api response to json')
      else:
        print('Response Failed')

    # LOGGER
    def logger(self, data):
      # GET NOW()
      now = datetime.now()
      # CREATE FILE ON WRITE MODE
      log_file = open('log_'+str(now.strftime('%Y-%m-%d %H%M%S'))+'.html', 'wb')
      # WRITE DATE ON FILE
      pickle.dump(data, log_file)
      # CLOSE FILE
      log_file.close()

class strip_hours(cb_hours):

    def __init__(self):
        super().__init__()
        print('StripHours is Ready!')

class soda_hours(cb_hours):

    def __init__(self):
        super().__init__()
        print('SodaHours is Ready!')

# ROUTINES
def chaturbate():

  # CREATING MAIN OBJECT
  cbhours = cb_hours()

  # CREATING INSTANCE FORM SELENIUM CHROME DRIVER
  # cbhours.get_chrome_driver()

  # API REQUEST FOR CHATURBATE ACCOUNTS => 1 
  cbhours.get_accounts(1)

  # OPEN CB HOURS FOR EXTRACT DATA
  cbhours.open_url('https://www.cbhours.com/studio.php')

  # GET DATES
  cbhours.get_dates()

  # EXECUTING RANGE DATE TO EXTRACT DATA FROM TIMEONLINE TABLE
  cbhours.set_date_range('//*[@id="datepicker-from"]', '//*[@id="datepicker-to"]')      

  # 1. CHATURBATE
  cbhours.get_data(1)

  # SEND BLOCKS TO API 
  cbhours.send_blocks()

  # CLOSE TAB
  # driver.close()
  print('End chaturbate()')
  print('[Control + C] para salir...')
  time.sleep(1)

def stripchat():

  # CREATING MAIN OBJECT
  striphours = strip_hours()

  # API REQUEST FOR STRIPCHAT ACCOUNTS => 4 
  striphours.get_accounts(4)

  # OPEN CB HOURS FOR EXTRACT DATA
  striphours.open_url('https://www.striphours.com/studio.php')

  # GET DATES
  striphours.get_dates()

  # EXECUTING RANGE DATE TO EXTRACT DATA FROM TIMEONLINE TABLE
  striphours.set_date_range('//*[@id="datepicker-from"]', '//*[@id="datepicker-to"]')      

  # 4. STRIPCHAT
  striphours.get_data(4)

  # SEND BLOCKS TO API 
  striphours.send_blocks()

  # CLOSE BROWSER
  # driver.close()

  print('End stripchat()')
  print('[Control + C] para salir...')
  time.sleep(1)

def camsoda():

  # CREATING MAIN OBJECT
  sodahours = soda_hours()

  # API REQUEST FOR STRIPCHAT ACCOUNTS => 5 
  sodahours.get_accounts(5)

  # OPEN CB HOURS FOR EXTRACT DATA
  sodahours.open_url('https://www.sodahours.com/studio.php')

  # GET DATES
  sodahours.get_dates()

  # EXECUTING RANGE DATE TO EXTRACT DATA FROM TIMEONLINE TABLE
  sodahours.set_date_range('//*[@id="datepicker-from"]', '//*[@id="datepicker-to"]')      

  # 4. CAMSODA
  sodahours.get_data(5)

  # SEND BLOCKS TO API 
  sodahours.send_blocks()

  # CLOSE BROWSER
  # driver.close()

  print('End Camsoda()')
  print('[Control + C] para salir...')
  time.sleep(1)


def main():
    
    ### GET TIME ONLINE ###

    # 1. CHATURBATE RUTINE
    chaturbate()
    # 2. STRIPCHAT RUTINE
    stripchat()
    # 3. CAMSODA RUTINE
    camsoda()

    driver.quit()

    print('### End Main ROUTINE ###')


##################################################################
# 
# START APP
#

if __name__ == '__main__':


  main()

#
# END APP
# 
##################################################################