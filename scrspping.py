from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from typing import List
import pandas as pd
from datetime import datetime
import os
import locale
# Deixar o mes em portugues
locale.setlocale(locale.LC_ALL,'pt_BR.UTF-8')
def handle_directory() -> str:
    '''
        Cria as pastas para salvar o scraping com o nome determinado pelo trabalho
    '''
    try:
        current_month_name = datetime.now().strftime("%B")
        current_month = datetime.now().strftime("%m")
        current_year = datetime.now().year
        current_day = datetime.now().strftime("%d")
        name_dir = f"coleta_{current_year}/coleta_{current_month_name}/coleta_{current_day}_{current_month}_{current_year}"
        os.makedirs(name_dir)
        return name_dir
    except:
        print("An error has occurred in directory function.")
        
def mount_table():
    '''
        Cria uma tabela vazia para ser posteriormente preenchida com os valores necessarios
        de cada book
    '''
    df = pd.DataFrame({"SKU":[],"Category":[],"Title": [],"Price":[],"Stock":[],"Rating":[],"URL":[]})
    return df
    
URL = 'http://books.toscrape.com/'
dataframe = mount_table()

def init_driver() -> webdriver.Chrome:
    '''
        Inicializa o chrome
    '''
    options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def test():
    '''
        Testar se esta funcionando okay o selenium
    '''
    driver = init_driver()
    driver.get('http://www.google.com')
    search = driver.find_element(by=By.NAME, value="q")
    search.send_keys("Hey, Tecademin")
    search.send_keys(Keys.RETURN)
    time.sleep(5)
    driver.close()

def get_categories_easy() -> List[str]:
    '''
        Uma forma de listar todas categorias presentes no site
    '''
    driver = init_driver()
    driver.get(URL)
    elements = driver.find_elements(by = By.CSS_SELECTOR, value = ".nav-list ul > li")
    categories = []
    for element in elements:
        categories.append(element.text)
    print(categories)
    return categories

def export_to_excel(dataframe: pd.DataFrame):
    '''
        Exportar a tabela depois de preenchida com os valores do books para um excel xlsx
    '''
    try:
        dir = handle_directory()
        dataframe.to_excel(f"{dir}/coleta_bookstoscrape.xlsx")
        print("Exported!!!!")
    except:
        print("An error occurred. Check if the folder already exist!")
    
def scrape_book_page(driver: webdriver.Chrome, link: str) -> pd.DataFrame:
    '''
        Faz a raspagem de dados de uma pagina de um livro dado especifico
    '''
    global dataframe
    driver.get(link)
    search_category_element = driver.find_element(by=By.CSS_SELECTOR, value='.breadcrumb > li:nth-child(3)')
    category = search_category_element.text
    search_title_element = driver.find_element(by=By.CSS_SELECTOR, value=".product_main > h1")
    search_price_element = driver.find_element(by=By.CSS_SELECTOR, value=".product_main .price_color")
    search_stock_element = driver.find_element(by=By.CSS_SELECTOR, value=".product_main .instock")
    search_rating_element = driver.find_elements(by=By.CSS_SELECTOR, value=".product_main .star-rating > i")
    search_sku = driver.find_element(by=By.CSS_SELECTOR, value=".table tbody > tr:first-child")
    # "UPC abd3112321312".split() -> ["UPC","abd3112321312"]
    # [1]
    sku = search_sku.text
    sku = sku.split()
    sku = sku[1]
    title = search_title_element.text
    price = search_price_element.text[1:].replace('.',',')
    stock = search_stock_element.text
    url = link
    rating = 0
    print(category)
    print(title)
    print(price)
    print(stock)
    print(sku)
    print(url)
    for rating_element in search_rating_element:
        # Conta as estrelas que tem a cor amarela
        if rating_element.value_of_css_property("color") == "rgba(230, 206, 49, 1)":
            rating += 1
        else:
            break
    print(rating)
    temp_df = pd.DataFrame({"SKU":[sku],"Category":[category],"Title": [title],"Price":[price],"Stock":[stock],"Rating":[rating],"URL":[url]})
    dataframe = pd.concat([dataframe,temp_df], ignore_index=True)
            
    
#get_categories_easy()
driver = init_driver()
scrape_book_page(driver, "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")
scrape_book_page(driver, "http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html")
scrape_book_page(driver,"http://books.toscrape.com/catalogue/i-am-a-hero-omnibus-volume-1_898/index.html")
scrape_book_page(driver,"http://books.toscrape.com/catalogue/the-requiem-red_995/index.html")
scrape_book_page(driver,"http://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html")
export_to_excel(dataframe)