# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

# Data Preprocessing
import html
import re
import ast

# Save to Google Sheets
import gspread
import xlsxwriter 
from google.oauth2.service_account import Credentials
import xlsxwriter.utility


class BubbleAgenciesPipeline:
    def _get_single_entity(self, value):
        return value[0] if isinstance(value, tuple) else value
    
    def _clean_extracted_html(self, value):
        if value is not None:
            return html.unescape(value.replace('\\u200d', '\u200d')).strip()

    def _extract_currency(self, value):
        if value is not None:
            currency_pattern = r'\$[\d\.,\w/]+'
            match = re.search(currency_pattern, value)
            result = match.group()

            # Replace comma with point, as comma is prohibited as decimals in python
            return result.replace(",", ".")

    def _extract_number(self, value):
        if value is not None:
            number_pattern = r'[\d\.,]+'
            match = re.search(number_pattern, value)
            result = match.group()

            # Replace comma with point, as comma is prohibited as decimals in python
            result = result.replace(",", ".")

            # Check whether it is numerical or not
            try:
                converted_result = ast.literal_eval(result)
            
            except SyntaxError:
                converted_result = result

            return converted_result

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()

        # Correct the emoji and unescape HTML entities
        for field_name in field_names:
            value = self._get_single_entity(value=adapter.get(field_name))
            adapter[field_name] = self._clean_extracted_html(value)
                
        # Convert some features to be currency-typed
        curr_fields = ["projects_starting_at", "rates_starting_at"]
        for field_name in curr_fields:
            value = self._get_single_entity(value=adapter.get(field_name))
            adapter[field_name] = self._extract_currency(value)
        
        # Convert some features to be numerical-typed
        num_fields = ["years_active", "quick_stats_team_members", "quick_stats_certified_developers", "quick_stats_apps_built", "quick_stats_templates", "quick_stats_plugins"]
        for field_name in num_fields:
            value = self._get_single_entity(value=adapter.get(field_name))
            adapter[field_name] = self._extract_number(value)
    
        return item
    
class SaveToGoogleSheetsPipeline:
    def __init__(self):
        # Initialize credentials
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.service_account_filename = None # Google Service Account File Path
        self.sheet_id = None # Google Spreadsheet ID
        self.sheet_title = "Agency"

        # Authentication of Google Sheets
        self.creds = Credentials.from_service_account_file(self.service_account_filename, scopes=self.scopes)
        self.client = gspread.authorize(self.creds)
        self.workbook = self.client.open_by_key(self.sheet_id)
        self.sheet = self.workbook.worksheet(self.sheet_title)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()

        # Add headers in first row
        first_row = self.sheet.row_values(1)
        is_contain_headers: bool = len(first_row) == len(field_names)
        if not is_contain_headers:
            headers = [field_name for field_name in field_names]
            range_start, range_end = "A1", f"{xlsxwriter.utility.xl_col_to_name(len(field_names)-1)}1"
            self.sheet.update([headers], range_name=f"{range_start}:{range_end}")
            self.sheet.format(ranges=f"{range_start}:{range_end}", format={"textFormat": {"bold": True}})

        # Add values
        next_row = len(self.sheet.get_all_values()) + 1
        range_start, range_end = f"A{next_row}", f"{xlsxwriter.utility.xl_col_to_name(len(field_names)-1)}{next_row}"

        row_values = [item[field_name] for field_name in field_names]
        self.sheet.update([row_values], range_name=f"{range_start}:{range_end}")
        