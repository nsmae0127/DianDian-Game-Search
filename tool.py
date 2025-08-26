import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import pickle
import time
import urllib.parse
import datetime
import os
import sys


# 콘솔 로그 출력
def log(message):
    print(message)
    sys.stdout.flush()  # 실시간 로그 출력


# 쿠키 생성 함수
def create_cookies():
    log("로그인 창을 띄웁니다. 로그인 후 Enter 키를 누르세요.")
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = None
    try:
        driver = uc.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        driver.get("https://app.diandian.com/login")
        input("로그인 후 Enter 키를 눌러 쿠키를 저장하세요: ")
        with open("cookies.pkl", "wb") as f:
            pickle.dump(driver.get_cookies(), f)
        log("쿠키가 'cookies.pkl'에 저장되었습니다.")
        return True
    except Exception as e:
        log(f"쿠키 생성 실패: {str(e)}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
                log("쿠키 생성 드라이버 정상 종료")
            except Exception as e:
                log(f"쿠키 생성 드라이버 종료 실패: {str(e)}")
                os.system("taskkill /F /IM chromedriver.exe > nul 2>&1")


# 쿠키 로드 함수
def load_cookies(driver):
    max_attempts = 3
    attempt = 1
    if not os.path.exists("cookies.pkl"):
        log("Error: cookies.pkl 파일이 없습니다. 쿠키를 먼저 생성하세요.")
        return False

    with open("cookies.pkl", "rb") as f:
        cookies = pickle.load(f)

    while attempt <= max_attempts:
        try:
            log(f"쿠키 로드 시도 {attempt}/{max_attempts}...")
            driver.get("https://app.diandian.com")
            time.sleep(2)
            for cookie in cookies:
                if "diandian.com" not in cookie["domain"]:
                    log(f"쿠키 스킵: {cookie['name']} (도메인: {cookie['domain']})")
                    continue
                cookie_copy = cookie.copy()
                if (
                    "expires" in cookie_copy
                    and cookie_copy["expires"]
                    and cookie_copy["expires"] != "Session"
                    and isinstance(cookie_copy["expires"], str)
                ):
                    try:
                        expires_dt = datetime.datetime.strptime(
                            cookie_copy["expires"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        )
                        cookie_copy["expires"] = int(expires_dt.timestamp())
                    except ValueError:
                        log(f"Expires 파싱 실패: {cookie['name']}, Session으로 처리")
                        cookie_copy["expires"] = -1
                try:
                    driver.add_cookie(cookie_copy)
                    log(f"쿠키 추가 성공: {cookie['name']}")
                except Exception as e:
                    log(f"쿠키 추가 실패: {cookie['name']} - {str(e)}")
            driver.refresh()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            page_text = driver.find_element(By.TAG_NAME, "body").text
            if "Login & Sign up" in page_text or "ERR_TOO_MANY_REDIRECTS" in page_text:
                log(
                    f"로그인 세션 실패: 'Login & Sign up' 또는 'ERR_TOO_MANY_REDIRECTS' 발견"
                )
                if attempt == max_attempts:
                    return False
                attempt += 1
                time.sleep(2)
                continue
            log("쿠키 로드 성공")
            return True
        except Exception as e:
            log(f"쿠키 로드 실패: {str(e)}")
            if attempt == max_attempts:
                return False
            attempt += 1
            time.sleep(2)
    return False


# 게임 리스트 불러오기
try:
    df = pd.read_csv("games.csv")
    game_list = df["game_name"].tolist()
except FileNotFoundError:
    log("Error: games.csv 파일을 찾을 수 없습니다.")
    input("Press Enter to exit...")
    exit()

# 쿠키 생성 (cookies.pkl이 없으면 실행)
if not os.path.exists("cookies.pkl"):
    if not create_cookies():
        log("쿠키 생성 실패로 종료합니다.")
        input("Press Enter to exit...")
        exit()

# Selenium 설정
options = uc.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
)

# undetected-chromedriver 초기화
driver = None
try:
    driver = uc.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # WebDriver 탐지 방지
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
        },
    )

    # 쿠키 로드
    if not load_cookies(driver):
        log("쿠키 로드 실패로 종료합니다. 새 쿠키를 생성하세요.")
        input("Press Enter to exit...")
        exit()

    results = []

    for game in game_list:
        max_attempts = 3
        attempt = 1
        while attempt <= max_attempts:
            try:
                # 검색 URL 생성
                encoded_game = urllib.parse.quote(game.strip())
                search_url = f"https://app.diandian.com/search/taptap-75-{encoded_game}"
                log(f"{game}: 검색 URL: {search_url}, 시도 {attempt}/{max_attempts}")

                driver.get(search_url)
                log(f"{game}: 페이지 로드 중...")

                # 명시적 대기: <body> 로드
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                log(f"{game}: <body> 로드 성공")

                page_text = driver.find_element(By.TAG_NAME, "body").text
                if "ERR_TOO_MANY_REDIRECTS" in page_text:
                    log(f"{game}: ERR_TOO_MANY_REDIRECTS 발생")
                    if attempt == max_attempts:
                        results.append(
                            {"game": game, "status": "Error: ERR_TOO_MANY_REDIRECTS"}
                        )
                        log(f"{game}: Error - ERR_TOO_MANY_REDIRECTS")
                        break
                    attempt += 1
                    time.sleep(2)
                    continue

                # 명시적 대기: <div class="dd-app-info"> 로드
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located(
                            (By.CLASS_NAME, "dd-app-info")
                        )
                    )
                    log(f"{game}: <dd-app-info> 로드 성공")
                except TimeoutException:
                    log(f"{game}: <dd-app-info> 로드 실패, 대체 클래스 검색")

                # 검색 결과 목록
                result_items = driver.find_elements(By.CLASS_NAME, "dd-app-info")
                if not result_items:
                    log(f"{game}: <dd-app-info> 없음, 대체 클래스 검색")
                    result_items = driver.find_elements(
                        By.CSS_SELECTOR,
                        'div[class*="search-result"], div[class*="app-item"], div[class*="result-item"], div[class*="game-item"]',
                    )

                # 결과 구분
                found = False
                for item in result_items:
                    try:
                        name_elements = item.find_elements(
                            By.CSS_SELECTOR,
                            "div.show-text.dd-max-ellipsis, h3, span, a",
                        )
                        for name_element in name_elements:
                            name_text = name_element.text.strip()
                            if game == name_text or game in name_text:
                                found = True
                                log(f"{game}: 이름 발견 - {name_text}")
                                break
                        if found:
                            break
                    except NoSuchElementException:
                        log(f"{game}: 요소 검색 중 NoSuchElementException")
                        continue

                if found:
                    status = "Found"
                else:
                    if "无结果" in page_text or "未找到" in page_text:
                        status = "Not Found (no results)"
                    elif game in page_text:
                        status = "Not Found (keyword in page text)"
                    else:
                        status = "Not Found"

                results.append({"game": game, "status": status})
                log(f"{game}: {status}")
                break  # 성공 시 루프 종료

            except Exception as e:
                log(f"{game}: Error - {str(e)}, 시도 {attempt}/{max_attempts}")
                if attempt == max_attempts:
                    results.append({"game": game, "status": f"Error: {str(e)}"})
                    break
                attempt += 1
                time.sleep(2)

        # 서버 부하 방지
        time.sleep(1)

finally:
    # 드라이버 안전 종료
    if driver:
        try:
            driver.quit()
            log("드라이버 정상 종료")
        except Exception as e:
            log(f"드라이버 종료 실패: {str(e)}")
            os.system("taskkill /F /IM chromedriver.exe > nul 2>&1")

# 결과 저장
pd.DataFrame(results).to_csv("search_results.csv", index=False, encoding="utf-8-sig")
log("Results saved to search_results.csv")
input("Press Enter to exit...")
