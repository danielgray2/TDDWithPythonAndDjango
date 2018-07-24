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

    def wait_for_element_present(self, id_of_element):
        time.sleep(0.5)
        start_time = time.time()
        while True:
            try:
                element = self.browser.find_element_by_id(id_of_element)
                return element
            except (AssertionError, WebDriverException) as e:
                    if time.time() - start_time > MAX_WAIT:
                        raise e
                    time.sleep(0.5)

    def check_for_element_in_table(self, row_text, table_on_webpage):
        rows = table_on_webpage.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def test_can_start_a_list_and_retrieve_it_later(self):
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

        self.fail('Finish the test!')