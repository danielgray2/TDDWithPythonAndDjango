from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import unittest
from django.test import LiveServerTestCase
from selenium.common.exceptions import WebDriverException

MAX_WAIT = 10

class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    #Trying to figure out how to wait for the browser to refresh so that we can remove the time.sleep(0.5)
    #at the top of the wait_for_element_present() and check_for_element_in_table() methods. See
    #http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
    #def waitForBrowserToRefresh(self, elementToCheck):
    #    try:


    def wait_for_element_present(self, id_of_element):
        time.sleep(0.75)
        start_time = time.time()
        while True:
            try:
                element = self.browser.find_element_by_id(id_of_element)
                return element
            except (AssertionError, WebDriverException) as e:
                    if time.time() - start_time > MAX_WAIT:
                        print("We exited the wait_for_element_present method")
                        raise e
                    time.sleep(0.5)

    def check_for_element_in_table(self, row_text, table_on_webpage):
        time.sleep(0.75)
        start_time = time.time()
        while True:
            try:
                rows = table_on_webpage.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                print("We found the element in the check_for_element_in_table method")
                break
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time >  MAX_WAIT:
                    print("We exited the check_for_element_in_table method")
                    raise e
                time.sleep(0.5)

    def test_can_start_a_list_for_one_user(self):
        self.browser.get(self.live_server_url)
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        inputbox = self.wait_for_element_present('id_new_item')
        self.assertEqual(inputbox.get_attribute('placeholder'), 'Enter a to-do item')

        inputbox.send_keys('Buy peacock feathers')
        inputbox.send_keys(Keys.ENTER)

        inputbox = self.wait_for_element_present('id_new_item')
        inputbox.send_keys('Use peacock feathers to make a fly')
        inputbox.send_keys(Keys.ENTER)
        table_on_webpage = self.wait_for_element_present('id_list_table')
        self.check_for_element_in_table('1: Buy peacock feathers', table_on_webpage)
        self.check_for_element_in_table('2: Use peacock feathers to make a fly', table_on_webpage)

    def test_multiple_users_can_start_lists_at_different_urls(self):
        self.browser.get(self.live_server_url)
        inputbox = self.wait_for_element_present('id_new_item')

        inputbox.send_keys("Buy peacock feathers")
        inputbox.send_keys(Keys.ENTER)
        
        table_on_webpage = self.wait_for_element_present('id_list_table')
        self.check_for_element_in_table("1: Buy peacock feathers", table_on_webpage)

        edith_url = self.browser.current_url
        self.assertRegex(edith_url, "/lists/.+")

        self.browser.quit()
        self.browser = webdriver.Firefox()
        self.browser.get(self.live_server_url)

        body_text = self.browser.find_element_by_tag_name('body').text

        self.assertNotIn('1: Buy peacock feathers', body_text)
        self.assertNotIn('2: Use peacock feathers to make a fly', body_text)

        inputbox = self.wait_for_element_present('id_new_item')
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)

        table_on_webpage = self.wait_for_element_present('id_list_table')
        self.check_for_element_in_table('1: Buy milk', table_on_webpage)
        
        dan_url = self.browser.current_url
        self.assertRegex(dan_url, '/lists/.+')
        self.assertNotEqual(dan_url, edith_url)

        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('1: Buy peacock feathers', body_text)
        self.assertIn('1: Buy milk', body_text)

        self.fail('Finish the test!')