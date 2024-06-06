from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from typing import List
import pandas as pd
from datetime import datetime
import os
import locale
import re
# Deixar o mes em portugues
locale.setlocale(locale.LC_ALL,'pt_BR.UTF-8')
all_links_pages = []
def sanitize(text:str) -> str:
    '''
        Limpar os caracteres especiais do titulo do livro
    '''
    text_sanitize = re.sub(r'[^\w\s]', '', text)
    return text_sanitize

def handle_directory() -> str:
    '''
        Cria as pastas para salvar o scraping com o nome determinado pelo trabalho
    '''
    name_dir = None
    try:
        current_month_name = datetime.now().strftime("%B")
        current_month = datetime.now().strftime("%m")
        current_year = datetime.now().year
        current_day = datetime.now().strftime("%d")
        name_dir = f"coleta_{current_year}/coleta_{current_month_name}/coleta_{current_day}_{current_month}_{current_year}"
        name_dir_fullpath = f"{name_dir}/prints"
        os.makedirs(name_dir_fullpath)
        return name_dir
    except:
        os.remove(name_dir)
        print("An error has occurred in directory function.")
data_directory =  handle_directory()     
def mount_table():
    '''
        Cria uma tabela vazia para ser posteriormente preenchida com os valores necessarios
        de cada book
    '''
    df = pd.DataFrame({
        "SKU":[],
        "Category":[],
        "Title": [],
        "Price":[],
        "Stock":[],
        "Rating":[],
        "URL":[],
        "Image Directory": [],
        "Image Error": []
        })
    return df
    
URL = 'http://books.toscrape.com/'
dataframe = mount_table()

def init_driver() -> webdriver.Chrome:
    '''
        Inicializa o chrome
    '''
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,3200')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# def test():
#     '''
#         Testar se esta funcionando okay o selenium
#     '''
#     driver = init_driver()
#     driver.get('http://www.google.com')
#     search = driver.find_element(by=By.NAME, value="q")
#     search.send_keys("Hey, Tecademin")
#     search.send_keys(Keys.RETURN)
#     time.sleep(5)
#     driver.close()

# def get_categories_easy() -> List[str]:
#     '''
#         Uma forma de listar todas categorias presentes no site
#     '''
#     driver = init_driver()
#     driver.get(URL)
#     elements = driver.find_elements(by = By.CSS_SELECTOR, value = ".nav-list ul > li")
#     categories = []
#     for element in elements:
#         categories.append(element.text)
#     print(categories)
#     return categories

def export_to_excel(dataframe: pd.DataFrame):
    '''
        Exportar a tabela depois de preenchida com os valores do books para um excel xlsx
    '''
    try:
        dataframe.to_excel(f"{data_directory}/coleta_bookstoscrape.xlsx")
        print("Exported!!!!")
    except:
        print("An error occurred. Check if the folder already exist!")
    
def get_all_links_from_current_page(driver: webdriver.Chrome) -> List[str]:
    global all_links_pages
    search_links = driver.find_elements(by=By.CSS_SELECTOR, value=".product_pod h3 a:first-child")
    for link in search_links:
        current_link = link.get_attribute("href")
        all_links_pages.append(current_link)
    # print(all_links_pages)
    
def get_all_links_from_all_pages(driver: webdriver.Chrome):
    driver.get(URL)
    try:
        while True:
            search_by_next = driver.find_element(by=By.LINK_TEXT,value="next")
            # print(driver.current_url)
            get_all_links_from_current_page(driver)
            search_by_next.click()
    except NoSuchElementException:
        get_all_links_from_current_page(driver)
        #print("END OF PAGES")
        # print(len(all_links_pages))
        
def scrape_book_page(driver: webdriver.Chrome, link: str) -> pd.DataFrame:
    '''
        Faz a raspagem de dados de uma pagina de um livro dado especifico
    '''
    global dataframe
    global data_directory
    driver.get(link)
    page_inner = driver.find_element(by=By.CSS_SELECTOR, value=".page .page_inner")
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
    current_image_dir = f'{data_directory}/prints/{sanitize(title)}.png'
    error_image = page_inner.screenshot(current_image_dir)
    # print(category)
    # print(title)
    # print(price)
    # print(stock)
    # print(sku)
    # print(url)
    for rating_element in search_rating_element:
        # Conta as estrelas que tem a cor amarela
        if rating_element.value_of_css_property("color") == "rgba(230, 206, 49, 1)":
            rating += 1
        else:
            break
    # print(rating)
    temp_df = pd.DataFrame({
            "SKU":[sku],
            "Category":[category],
            "Title": [title],
            "Price":[price],
            "Stock":[stock],
            "Rating":[rating],
            "URL":[url], 
            "Image Directory": [current_image_dir],
            "Image Error": [error_image]
        })
    dataframe = pd.concat([dataframe,temp_df], ignore_index=True)

def scrape_all_books():
    '''
        Concilia as funcoes anteriores para poder scrapear todos os livros 
    '''
    global all_links_pages
    global dataframe
    driver = init_driver()
    counter = 0
    print("Pegando todos os links de livros de todas as paginas...")
    get_all_links_from_all_pages(driver)
    print("Concluido!")
    quantity_links = len(all_links_pages)
    print("Inicializando scraping...")
    for link in all_links_pages:
        scrape_book_page(driver,link)
        counter += 1
        print(f"{counter}/{quantity_links}")
    print("Exportando...")
    export_to_excel(dataframe)
    
            
scrape_all_books() 
#get_categories_easy()
#driver = init_driver()
#get_all_links_from_all_pages(driver)
# get_all_links_from_current_page(driver,"http://books.toscrape.com/catalogue/page-1.html")
# scrape_book_page(driver, "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")
# scrape_book_page(driver, "http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html")
# scrape_book_page(driver, "http://books.toscrape.com/catalogue/i-am-a-hero-omnibus-volume-1_898/index.html")
# scrape_book_page(driver, "http://books.toscrape.com/catalogue/the-requiem-red_995/index.html")
# scrape_book_page(driver, "http://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html")
#export_to_excel(dataframe)