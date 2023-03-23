from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.firefox import GeckoDriverManager
from finances_login_selenium import FinancesLoginSelenium
from extension_methods import IReadOnlyIWebElementCollectionExtension
from datetime import date
import json

class FinancesSelenium:    
    FinancesHomeUrl = "https://sitfiscal.portaldasfinancas.gov.pt/geral/dashboard"
    FinancesInvoicesUrl = "https://irs.portaldasfinancas.gov.pt/recibos/portal/emitir/emitirDocumentos"
    HasRNH = False
    BaseValue = 0
    Password = ""
    VAT = ""
    ContractorVat = "",
    InvoiceDescription = ""

    def __init__(self):
        self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        self.get_config()
        self.driver.get(self.FinancesHomeUrl)

    def start(self):
        finances_login_selenium = FinancesLoginSelenium(self.driver, self.VAT, self.Password)
        if finances_login_selenium.is_login_available():
            finances_login_selenium.login()

        self.driver.get(self.FinancesInvoicesUrl)
        start_invoice_creation_result = self.start_invoice_creation()

        if not start_invoice_creation_result:
            raise Exception("Something went wrong starting a new invoice")

        self.fill_invoice()

    def start_invoice_creation(self):
        self.fill_service_date()
        self.fill_service_type()
        return True

    def fill_invoice(self):
        try:
            
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            IReadOnlyIWebElementCollectionExtension.filter_by_content(buttons, "Emitir")[0].click()
            self.fill_contractor_information()
            self.fill_invoice_reason()
            self.fill_tax_data()
            self.fill_invoice_values()
        except Exception as ex:
            print(ex)
            raise

        # is_invoice_valid_to_submit = self.is_invoice_valid_to_submit()

        # if not is_invoice_valid_to_submit:
            return

        # self.submit_invoice()

        return

    def is_invoice_valid_to_submit(self):
        raise NotImplementedError

    def submit_invoice(self):
        btn_submit_invoice_class = "btn.btn-primary.btn-sm"
        btn_submit_invoice_elements = self.driver.find_elements(By.CLASS_NAME, btn_submit_invoice_class)
        btn_submit_invoice = btn_submit_invoice_elements[-1] if len(btn_submit_invoice_elements) > 1 else btn_submit_invoice_elements[0]

        btn_submit_invoice.click()

    def fill_invoice_values(self):
        txtn_invoice_base_value_name = "valorBase"
        txtn_invoice_base_value_elements = self.driver.find_elements(By.NAME, txtn_invoice_base_value_name)
        txtn_invoice_base_value = txtn_invoice_base_value_elements[-1] if len(txtn_invoice_base_value_elements) > 1 else txtn_invoice_base_value_elements[0]

        txtn_invoice_base_value.send_keys(str(self.BaseValue))

    def fill_tax_data(self):
        self.fill_vat()
        self.fill_income_tax()

    def fill_income_tax(self):
        self.fill_income_base()
        if self.invoice_initial_configuration.has_rnh:
            self.fill_income_source_rnh()
        else:
            self.fill_income_source()

    def fill_income_source(self):
        # Validar
        # À taxa de 25 % -art. 101.º, n.º1, do CIRS
        sel_income_base_name = "regimeRetencaoIrs"
        sel_income_base_elements = self.driver.find_elements(By.NAME, sel_income_base_name)
        sel_income_base = sel_income_base_elements[-1] if len(sel_income_base_elements) > 1 else sel_income_base_elements[0]

        select_element = Select(sel_income_base)
        select_element.select_by

    def fill_service_date(self):
        txt_service_date_elements = self.driver.find_elements(By.NAME, "dataPrestacao")
        txt_service_date_elements = IReadOnlyIWebElementCollectionExtension.filter_by_type(txt_service_date_elements, "input")
        txt_service_date = txt_service_date_elements[0] if len(txt_service_date_elements) > 1 else txt_service_date_elements[-1]

        service_date = date(date.today().year, date.today().month, date.today().day)

        txt_service_date.send_keys(service_date.strftime("%Y-%m-%d"))
        txt_service_date.send_keys(Keys.ESCAPE)
        txt_service_date.click()

    def fill_service_type(self):
        sel_service_type_elements = self.driver.find_elements(By.NAME, "tipoRecibo")
        sel_service_type_elements = IReadOnlyIWebElementCollectionExtension.filter_by_type(sel_service_type_elements, "select")
        sel_service_type = sel_service_type_elements[-1] if len(sel_service_type_elements) > 1 else sel_service_type_elements[0]

        select_element = Select(sel_service_type)
        select_element.select_by_visible_text("Fatura-Recibo")

    def fill_contractor_information(self):

        selCountryElements = self.driver.find_elements( By.NAME,"pais")
        selCountryElements = IReadOnlyIWebElementCollectionExtension.filter_by_type(selCountryElements,"select")
        selCountry = selCountryElements[-1] if len(selCountryElements) > 1 else selCountryElements[0]
        countrySelectElement = Select(selCountry)
        country = countrySelectElement.first_selected_option.text

        if "portugal" != country.lower():
            countrySelectElement.select_by_visible_text("portugal")

        txtCompanyIdentificationElements = self.driver.find_elements(By.NAME,"nifAdquirente")
        txtCompanyIdentificationElements = IReadOnlyIWebElementCollectionExtension.filter_by_type(txtCompanyIdentificationElements,"input")
        txtCompanyIdentification = txtCompanyIdentificationElements[-1] if len(txtCompanyIdentificationElements) > 1 else txtCompanyIdentificationElements[0]
        txtCompanyIdentification.send_keys(self.ContractorVAT)
        
    def fill_invoice_reason(self):
        self.fill_invoice_reason_title()
        self.fill_invoice_reason_description()

    def fill_invoice_reason_title(self):
        serviceRadioValue = "1"        
        radionInvoiceReasonElements = self.driver.find_elements(By.NAME,"titulo")
        radionInvoiceReasonElements = IReadOnlyIWebElementCollectionExtension.filter_by_type(radionInvoiceReasonElements, "input")
        radionInvoiceReason = next((x for x in radionInvoiceReasonElements if x.get_attribute("value") == serviceRadioValue), None)

        if radionInvoiceReason is None:
            raise Exception("Radio button not found.")

        radionInvoiceReason.click()
        radionInvoiceReason.send_keys(Keys.TAB)

    def fill_invoice_reason_description(self):    

        txtnInvoiceReasonDescriptionElements = self.driver.find_elements(By.NAME, "servicoPrestado")
        txtnInvoiceReasonDescriptionElements = IReadOnlyIWebElementCollectionExtension.filter_by_type(txtnInvoiceReasonDescriptionElements,"textarea")
        if len(txtnInvoiceReasonDescriptionElements) == 0:
            raise Exception("Description field not found.")

        txtnInvoiceReasonDescription = txtnInvoiceReasonDescriptionElements[0]

        actions = ActionChains(self.driver)
        actions.move_to_element(txtnInvoiceReasonDescription).click().perform()
        txtnInvoiceReasonDescription.send_keys(self.InvoiceDescription)

    def fill_vat(self):
        # Validar
        # Continente - 23% [taxa normal atual]        
        selVatElements = self.driver.find_elements(By.NAME, "regimeIva")
        selVatElements = IReadOnlyIWebElementCollectionExtension.filter_by_type(selVatElements, "select")
        selVat = selVatElements[-1] if len(selVatElements) > 1 else selVatElements[0]

        selectElement = Select(selVat)
        selectElement.select_by_value("string:15")
        selVat.click()

    def fill_income_tax(self):
        self.fill_income_base()

        if self.HasRNH:
            self.fill_income_source_RNH()
        else:
            self.fill_income_source()

    def fill_income_source(self):
        # Validar
        # À taxa de 25 % -art. 101.º, n.º1, do CIRS
        selIncomeBaseElements = self.driver.find_elements(By.NAME,"regimeRetencaoIrs")
        selIncomeBaseElements = IReadOnlyIWebElementCollectionExtension.filter_by_type(selIncomeBaseElements, "select")
        selIncomeBase = selIncomeBaseElements[-1] if len(selIncomeBaseElements) > 1 else selIncomeBaseElements[0]

        selectElement = Select(selIncomeBase)
        selectElement.select_by_value("string:11")
        selIncomeBase.click()

    def fill_income_source_RNH(self):
        # Validar
        # À taxa de 20 % -art. 101.º, n.º1, do CIRS
        selIncomeBaseElements = self.driver.find_elements(By.NAME,"regimeRetencaoIrs")
        selIncomeBaseElements = IReadOnlyIWebElementCollectionExtension.filter_by_type(selIncomeBaseElements, "select")
        selIncomeBase = selIncomeBaseElements[-1] if len(selIncomeBaseElements) > 1 else selIncomeBaseElements[0]

        selectElement = Select(selIncomeBase)
        selectElement.select_by_value("string:10")
        selIncomeBase.click()

    def fill_income_base(self):
        # Validar
        # À taxa de 25 % -art. 101.º, n.º1, do CIRS
        selIncomeBaseElements = self.driver.find_elements(By.NAME, "regimeIncidenciaIrs")
        selIncomeBaseElements = IReadOnlyIWebElementCollectionExtension.filter_by_type(selIncomeBaseElements, "select")
        selIncomeBase = selIncomeBaseElements[-1] if len(selIncomeBaseElements) > 1 else selIncomeBaseElements[0]

        selectElement = Select(selIncomeBase)
        selectElement.select_by_value("string:08")
        selIncomeBase.click()

    def get_config(self):
        with open('config.json') as f:
            data = json.load(f)

            self.Password = data['password']
            self.VAT = data['vat']
            self.BaseValue = data['base-value']
            self.HasRNH = bool(data['has-rnh'])
            self.ContractorVAT = data['contractor-vat']
            self.InvoiceDescription = data['invoice-description']