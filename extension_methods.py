from typing import List
from selenium.webdriver.remote.webelement import WebElement

class IReadOnlyIWebElementCollectionExtension:
    @staticmethod
    def filter_by_type(elements: List[WebElement], element_type: str) -> List[WebElement]:
        return list(filter(lambda e: e.tag_name.lower() == element_type.lower(), elements))
    
    @staticmethod
    def filter_by_content(elements: List[WebElement], content: str) -> List[WebElement]:
        return list(filter(lambda e: content.lower() in e.text.lower(), elements))