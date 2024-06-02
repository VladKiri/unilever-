import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_product_price(url, price_selectors):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)


    wait = WebDriverWait(driver, 10)
    price = None
    for selector in price_selectors:
        try:
            price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            price = price_element.text.strip()
            if price:
                break
        except:
            continue

    driver.quit()

    return price


def read_previous_prices(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                previous_prices = json.load(file)
            except json.decoder.JSONDecodeError:
                previous_prices = {}
    else:
        previous_prices = {}
    return previous_prices


def write_current_prices(file_path, current_prices):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(current_prices, file, ensure_ascii=False, indent=4)


def send_email(subject, body, to_email, from_email, password):

    smtp_server = 'smtp.gmail.ru'
    smtp_port = 587



    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")



product_url = input("Введите ссылку на карточку товара Wildberries или Lamoda: ")
price_selectors = ['.price-block__final-price', '._price_fow3x_11']

current_price = get_product_price(product_url, price_selectors)
price_file = 'prices.json'
previous_prices = read_previous_prices(price_file)

if current_price is not None:
    print(f"Текущая цена: {current_price}")

    if product_url in previous_prices:
        previous_price = previous_prices[product_url]
        if current_price != previous_price:
            print(f"Цена изменилась с {previous_price} на {current_price}")

            send_email(
                subject="Цена изменилась",
                body=f"Цена на товар по ссылке {product_url} изменилась с {previous_price} на {current_price}",
                to_email=input("Введите email получателя "),
                from_email = input("Введите email отправителя "),
                password = input("Введите пароль отправителя "),
            )
        else:
            print("Цена не изменилась.")
    else:
        print("Предыдущая цена не найдена.")

    previous_prices[product_url] = current_price

    write_current_prices(price_file, previous_prices)
else:
    print("Не удалось получить текущую цену.")

    #Код работает только на платформах партнерах Unilever: Wildberies и Lamoda
