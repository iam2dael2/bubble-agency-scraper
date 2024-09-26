from typing import Iterable, List
from commons.validation import is_containing_email

import scrapy
from scrapy.http import Response
from scrapy.selector import Selector
from bubble_agencies.items import AgencyItem

from scrapy_selenium import SeleniumRequest
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException, TimeoutException

import time
import json


class BubbleSpider(scrapy.Spider):
    name = "bubble"

    def start_requests(self):
        yield SeleniumRequest(
            url="https://bubble.io/agencies",
            wait_time=20,
            wait_until=EC.presence_of_all_elements_located((By.XPATH, "//div[@class='clickable-element bubble-element Group cmsaIo1 bubble-r-container flex column']/div/div[@class='bubble-element Text cmsaIq1']")),
            callback=self.parse
        )
    
    def parse(self, response: Response):
        driver: Chrome = response.meta["driver"]

        agencies: List[WebElement] = driver.find_elements(by=By.XPATH, value="//div[@class='clickable-element bubble-element Group cmsaIo1 bubble-r-container flex column']/div/div[@class='bubble-element Text cmsaIq1']")
        main_url: str = driver.current_url

        agency_num = 0
        while agency_num < len(agencies):
            # Go to main page
            if driver.current_url != main_url:
                driver.back()
                WebDriverWait(driver, timeout=60).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='clickable-element bubble-element Group cmsaIo1 bubble-r-container flex column']/div/div[@class='bubble-element Text cmsaIq1']")))
                time.sleep(2)
                agencies: List[WebElement] = driver.find_elements(by=By.XPATH, value="//div[@class='clickable-element bubble-element Group cmsaIo1 bubble-r-container flex column']/div/div[@class='bubble-element Text cmsaIq1']")
            
            # Go to agency page
            agencies[agency_num].click()
            agency_num += 1

            # Extract each agency data
            WebDriverWait(driver, timeout=60).until(EC.presence_of_element_located((By.XPATH, "//button[@class='clickable-element bubble-element Button cnaaTd']")))
            time.sleep(3)

            response_obj = Selector(text=driver.page_source)
            agency_data: dict = self.parse_agency(response_obj, driver=driver)
            yield agency_data

        # Check whether to have next page
        try:
            driver.back()
            next_page_xpath = "//button/preceding-sibling::a[contains(@href, 'bubble.io/agencies')]"
            WebDriverWait(driver, timeout=60).until(EC.presence_of_element_located((By.XPATH, next_page_xpath)))
            time.sleep(2)

            next_page = response.xpath(next_page_xpath+"/@href")[-1]

        except IndexError:
            raise IndexError("There is no item contained in `next page`")

        else:
            next_page_url = response.urljoin(next_page.get())
            yield SeleniumRequest(
                url=next_page_url,
                wait_time=60,
                wait_until=EC.presence_of_all_elements_located((By.XPATH, "//div[@class='clickable-element bubble-element Group cmsaIo1 bubble-r-container flex column']/div/div[@class='bubble-element Text cmsaIq1']")),
                callback=self.parse
            )

    def parse_agency(self, response, driver):
        agency_data = AgencyItem()
        
        agency_data["name"] = response.xpath("//h1/text()").get()
        agency_data["description"] = response.xpath("//h1/following::div[1]/text()").get()
        agency_data["link"] = self.parse_agency_link(driver=driver)
        agency_data["projects_starting_at"] = response.xpath("//div[contains(text(), 'Projects starting')]/text()").get()
        agency_data["rates_starting_at"] = response.xpath("//div[contains(text(), 'Rates starting')]/text()").get()
        agency_data["tier_level"] = response.xpath("//div[contains(text(), 'Agency Partner')]/text()").get()
        agency_data["years_active"] = response.xpath("//h1/following::div[2]/div[1]/div/text()").get()
        agency_data["country"] = response.xpath("//h1/following::div[2]/div[2]/div/text()").get()
        agency_data["banner_image_link"] = response.xpath("//img[contains(@alt, 'cover image')]/@src").get()
        agency_data["featured_works"] = self.parse_agency_featured_works(driver=driver, response=response)
        agency_data["quick_stats_team_members"] = response.xpath("//h2[text()='QUICK STATS']/following::div[contains(text(), 'Team members')]/preceding-sibling::node()/text()").get(),
        agency_data["quick_stats_certified_developers"] = response.xpath("//h2[text()='QUICK STATS']/following::div[contains(text(), 'Certified developers')]/preceding-sibling::node()/text()").get(),
        agency_data["quick_stats_apps_built"] = response.xpath("//h2[text()='QUICK STATS']/following::div[contains(text(), 'Apps built')]/preceding-sibling::node()/text()").get(),
        agency_data["quick_stats_templates"] = response.xpath("//h2[text()='QUICK STATS']/following::div[contains(text(), 'Template')]/preceding-sibling::node()/text()").get(),
        agency_data["quick_stats_plugins"] = response.xpath("//h2[text()='QUICK STATS']/following::div[contains(text(), 'Plugins')]/preceding-sibling::node()/text()").get(),
        agency_data["working_with_section_text"] = "\n".join(response.xpath("//h2[contains(text(), 'Working with')]/following::div[@class='bubble-element Text cnbaAaE3']//text()").getall()),
        agency_data["working_with_section_image"] = response.xpath("//h2[contains(text(), 'Working with')]/following::div[2]//img/@src").get(),
        agency_data["working_with_section_video"] = response.xpath("//h2[contains(text(), 'Working with')]/following::div[2]//video/source/@src").get(),
        agency_data["primary_services"] = ", ".join(response.xpath("//h2[contains(text(), 'Primary services')]/parent::node()//h3/text()").getall()),
        agency_data["external_profiles"] = self.parse_external_profiles(driver=driver, response=response)
        return agency_data
    
    def parse_agency_link(self, driver):
        agency_website_element = driver.find_element(by=By.XPATH, value="//div[text()='Visit agency website']/parent::div")
        
        # Move to other link
        agency_website_element.click()
        WebDriverWait(driver, timeout=60).until(lambda driver: len(driver.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[-1]) # move to other tab
        current_url = driver.current_url

        # Back to previous link
        driver.close() # close the recent tab
        driver.switch_to.window(driver.window_handles[-1])

        return current_url
    
    def parse_agency_featured_works(self, driver, response: Response):
        featured_work_element = response.xpath("//div[contains(text(), 'FEATURED WORK')]").get()
        if featured_work_element:
            # Determine total works attached in bubble.io
            raw_total_works: str = response.xpath("//div[text()='FEATURED WORK']/ancestor::div[@class='bubble-r-container flex column']//div[contains(text(), ' of ')]/text()").getall()[-1] # Format: 'x of y'
            total_works: int = int(raw_total_works.split(" ")[-1].strip()) # Take 'y' from 'x of y'
            
            # Extract all featured works
            featured_works: List[str] = []
            while True:
                featured_work = driver.find_element(by=By.XPATH, value="//div[text()='FEATURED WORK']/following-sibling::h4").text
                featured_works.append(featured_work)

                if len(featured_works) == total_works:
                    break

                # Move to next featured work
                next_button = driver.find_element(by=By.XPATH, value="//div[text()='FEATURED WORK']/ancestor::div[@class='bubble-r-container flex column']//*[local-name()='use'][contains(@href, 'arrow-right')]/ancestor::button")
                driver.execute_script("arguments[0].click();", next_button) # next_button.click()
                WebDriverWait(driver, timeout=60).until(lambda driver: driver.find_element(by=By.XPATH, value="//div[text()='FEATURED WORK']/following-sibling::h4").text != featured_work)

            return ", ".join(featured_works)
        
    def parse_external_profiles(self, driver, response: Response):
        result: dict = dict()
        
        counter: int = 0
        if response.xpath("//h4[contains(text(), 'External profiles')]").get():
            
            while True:
                WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//h4[contains(text(), 'External profiles')]/following::div[2]/div/div/div")))
                time.sleep(1)
                external_profiles = driver.find_elements(by=By.XPATH, value="//h4[contains(text(), 'External profiles')]/following::div[2]/div/div/div")
                if counter >= len(external_profiles):
                    break

                external_profile_element = external_profiles[counter]

                # Get name of external profile
                external_profile_name: str = response.xpath(f"//h4[contains(text(), 'External profiles')]/following::div[2]/div[{counter+1}]//text()").get()

                # Get link of external 
                try:
                    driver.execute_script("arguments[0].click();", external_profile_element)
                    WebDriverWait(driver, timeout=30).until(lambda driver: len(driver.window_handles) > 1)

                except TimeoutException:
                    external_profile_link = None

                else:
                    external_profile_link = None
                    while len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1]) # move to other tab
                        external_profile_link_temp: str = driver.current_url

                        # Get real external profile link
                        if (external_profile_link is None) or (external_profile_link_temp is not None):
                            external_profile_link = external_profile_link_temp
                        
                        # Close window until remain first page
                        if external_profile_link_temp is not None:
                            try:
                                driver.close()

                            except NoSuchWindowException:
                                pass

                finally:
                    driver.switch_to.window(driver.window_handles[-1]) # back to original page

                # Append data to result
                result[external_profile_name] = external_profile_link
                counter += 1

            return str(result)