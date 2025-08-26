# DianDian-Game-Search

## 개요

이 Python 스크립트는 [DianDian 웹사이트](https://app.diandian.com)에서 게임 이름을 자동으로 검색하는 데 사용됩니다. `undetected-chromedriver`를 활용해 헤드리스 Chrome 브라우저에서 검색을 수행하며, 봇 탐지 메커니즘을 우회합니다. 스크립트는 `cookies.pkl` 파일에서 인증 쿠키를 로드하여 로그인 세션을 유지하고, 지정된 게임 이름을 검색한 뒤 결과를 `search_results.csv` 파일에 저장합니다.

## 기능

- **웹 스크래핑**: DianDian의 검색 페이지(`https://app.diandian.com/search/taptap-75-<game_name>`)에서 게임 이름을 검색합니다.
- **인증 처리**: `cookies.pkl` 파일에서 쿠키(예: `token`, `deviceid`)를 로드하여 로그인 세션을 유지합니다.
- **에러 처리**: `ERR_TOO_MANY_REDIRECTS`, 로그인 세션 실패, 타임아웃 등의 문제를 최대 3회 재시도로 처리합니다.
- **유연한 검색**: `<div class="dd-app-info">`, `<div class="show-text dd-max-ellipsis">`를 포함한 여러 HTML 요소와 대체 클래스(`search-result`, `app-item`, `game-item`)를 검색합니다.
- **결과 저장**: 검색 결과를 `search_results.csv` 파일에 저장하며, 각 게임 이름과 상태(`Found`, `Not Found`, `Error`)를 기록합니다.
- **봇 탐지 우회**: `undetected-chromedriver`와 `navigator.webdriver` 비활성화, 사용자 정의 User-Agent를 사용해 서버 차단을 최소화합니다.

## 의존성

- **Python**: 3.12 이상
- **라이브러리**:
  - `undetected-chromedriver`: 헤드리스 브라우저 자동화 및 봇 탐지 우회
  - `selenium`: 웹 스크래핑 및 브라우저 상호작용
  - `webdriver-manager`: ChromeDriver 자동 관리
  - `pandas`: 게임 목록 CSV 읽기 및 결과 저장
  - `setuptools`: Python 3.12+에서 `undetected-chromedriver` 호환성 지원

## 입력

- **games.csv**: 검색할 게임 이름이 포함된 CSV 파일 (`game_name` 열 필요, 예: `向僵尸开炮`, `三国：冰河时代`, `无尽冬日`).
- **cookies.pkl**: DianDian 로그인 세션을 유지하기 위한 인증 쿠키(예: `token`, `deviceid`)가 포함된 pickle 파일.

## 출력

- **search_results.csv**: 다음 두 열을 포함한 CSV 파일:
  - `game`: 검색한 게임 이름
  - `status`: 검색 결과 (`Found`, `Not Found (no results)`, `Not Found (keyword in page text)`, `Error: <error_message>`)

## 참고

- 이 스크립트는 2025년 8월 기준 DianDian 웹사이트의 HTML 구조에 최적화되어 있습니다. 웹사이트 구조 변경 시 CSS 선택자 업데이트가 필요할 수 있습니다.
- 엄격한 봇 탐지나 IP 기반 제한(예: 한국 IP 차단)이 적용될 경우, 중국 서버 VPN 사용이 필요할 수 있습니다.
- 안정적인 실행을 위해 리디렉션 및 타임아웃 문제를 처리하는 재시도 로직이 포함되어 있습니다.
