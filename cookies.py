from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pickle

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)
driver.get("https://app.diandian.com/login")
input("로그인 후 Enter: ")
with open("cookies.pkl", "wb") as f:
    pickle.dump(driver.get_cookies(), f)
driver.quit()
