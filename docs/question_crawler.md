# Agent: EV User Question Crawler

## 프로젝트 목적

전기차 사용자들이 실제로 궁금해하는 질문 데이터를 수집하여 FAQ 데이터셋을 구축한다.

공식 FAQ가 아닌 실제 사용자 질문을 수집하여 향후 다음 기능에 활용한다.

* 전기차 FAQ 제공
* FAQ 검색
* FAQ 통계 분석
* FAQ 챗봇(RAG) 구축
* Streamlit 대시보드 연동

---

# 실행 환경

현재 프로젝트는 Streamlit 기반 프로젝트이며 실행 파일은 아래와 같다.

```bash
streamlit run app.py
```

모든 크롤링 결과는 app.py 에서 실행 및 조회 가능하도록 구현한다.

---

# 수집 대상 사이트

## 1. EVDang

메인

```text
https://evdang.com
```

검색 URL 예시

```text
https://evdang.com/articles?board=all&category=&board_category=1&q%5Btitle_or_body_or_comments_body_or_user_nick_name_cont%5D=테슬라
```

URL 패턴

```python
f"https://evdang.com/articles?board=all&category=&board_category=1&q%5Btitle_or_body_or_comments_body_or_user_nick_name_cont%5D={keyword}"
```

검색 범위

* 제목
* 본문
* 댓글
* 작성자

---

## 2. EV 라운지

메인

```text
https://www.evpost.co.kr
```

검색 URL 예시

```text
https://www.evpost.co.kr/wp/?s=테슬라
```

URL 패턴

```python
f"https://www.evpost.co.kr/wp/?s={keyword}"
```

검색 범위

* 게시글 제목
* 게시글 본문

---

## 3. 클리앙 굴러간당

메인

```text
https://www.clien.net/service/board/cm_car
```

검색 URL 예시

```text
https://www.clien.net/service/board/cm_car/19210375?combine=true&q=테슬라&p=0&sort=recency&boardCd=&isBoard=false
```

검색 패턴

```python
keyword = "테슬라"
```

검색 결과 URL에서

```python
q=keyword
```

값을 변경하여 사용한다.

검색 범위

* 게시글 제목
* 게시글 본문

---

# 검색 키워드

초기 수집 키워드

```python
SEARCH_KEYWORDS = [
    "전기차",
    "충전",
    "배터리",
    "테슬라",
    "아이오닉5",
    "아이오닉6",
    "EV6",
    "EV9",
    "모델3",
    "모델Y",
]
```

---

# 수집 데이터

각 게시글에서 아래 정보를 수집한다.

| 컬럼명           | 설명      |
| ------------- | ------- |
| source_name   | 수집 사이트명 |
| category      | 게시판명    |
| title         | 게시글 제목  |
| content       | 게시글 본문  |
| url           | 게시글 URL |
| published_at  | 작성일     |
| view_count    | 조회수     |
| comment_count | 댓글 수    |
| collected_at  | 수집 시각   |

---

# DB 테이블

```sql
CREATE TABLE ev_user_questions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '질문 고유 ID',

    source_name VARCHAR(100) NOT NULL COMMENT '수집 사이트',

    category VARCHAR(100) NULL COMMENT '게시판',

    title VARCHAR(500) NOT NULL COMMENT '게시글 제목',

    content TEXT NULL COMMENT '게시글 본문',

    url VARCHAR(1000) NOT NULL COMMENT '원본 URL',

    published_at VARCHAR(50) NULL COMMENT '작성일',

    view_count INT NULL COMMENT '조회수',

    comment_count INT NULL COMMENT '댓글 수',

    collected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '수집일',

    UNIQUE KEY uq_ev_user_questions_url (
        url
    )
);
```

---

# 프로젝트 구조

```text
project/

├── app.py
│
├── crawlers/
│   ├── base_crawler.py
│   ├── evdang_crawler.py
│   ├── evlounge_crawler.py
│   └── clien_crawler.py
│
├── db/
│   ├── connection.py
│   └── question_repository.py
│
├── utils/
│   ├── text_cleaner.py
│   ├── keyword_filter.py
│   └── dataframe_helper.py
│
├── data/
│   └── ev_user_questions.csv
│
└── requirements.txt
```

---

# 크롤러 구조

```python
class BaseCrawler:

    def crawl_list(self):
        pass

    def crawl_detail(self):
        pass

    def crawl(self):
        pass
```

각 사이트 크롤러는 BaseCrawler를 상속받는다.

---

# 필터링 규칙

아래 키워드가 제목 또는 본문에 포함된 경우만 저장한다.

```python
EV_KEYWORDS = [
    "전기차",
    "EV",
    "충전",
    "급속충전",
    "완속충전",
    "배터리",
    "주행거리",
    "충전소",
    "아이오닉",
    "아이오닉5",
    "아이오닉6",
    "EV6",
    "EV9",
    "테슬라",
    "모델3",
    "모델Y",
    "코나EV",
    "니로EV",
    "화재",
]
```

---

# 구현 방식

우선 사용

```python
requests
BeautifulSoup
pandas
mysql-connector-python
```

---

# Selenium 사용 조건

아래 경우에만 사용

* JavaScript 렌더링
* 무한 스크롤
* requests 결과에 게시글이 없는 경우

그 외에는 requests 사용

---

# 중복 제거 규칙

동일 게시글이 여러 검색어에서 검색될 수 있다.

예시

```text
테슬라 검색
모델Y 검색
전기차 검색
```

동일 게시글이 여러 번 검색될 수 있으므로

```python
url
```

기준으로 중복 제거한다.

---

# Streamlit 출력 규칙

수집 결과는 반드시 pandas DataFrame으로 변환한다.

```python
df = pd.DataFrame(results)
```

---

## 화면 표시 컬럼

Streamlit 화면에는 아래 컬럼만 출력한다.

| 컬럼  | 설명         |
| --- | ---------- |
| 인덱스 | 순번         |
| 제목  | 게시글 제목     |
| 링크  | 원본 게시글 URL |

---

## 출력 예시

```python
display_df = pd.DataFrame({
    "인덱스": range(1, len(df) + 1),
    "제목": df["title"],
    "링크": df["url"]
})
```

---

## 링크 이동 기능

링크 컬럼은 클릭 시 원본 게시글로 이동 가능해야 한다.

```python
st.dataframe(
    display_df,
    hide_index=True,
    use_container_width=True,
    column_config={
        "링크": st.column_config.LinkColumn(
            "링크",
            display_text="링크 이동"
        )
    }
)
```

---

## 화면 예시

| 인덱스 | 제목             | 링크    |
| --- | -------------- | ----- |
| 1   | 테슬라 모델Y 충전 질문  | 링크 이동 |
| 2   | EV6 겨울철 배터리 성능 | 링크 이동 |
| 3   | 아이오닉5 충전요금 문의  | 링크 이동 |

---

# app.py 실행 흐름

```python
검색 키워드 목록 생성
        ↓
사이트별 검색 URL 호출
        ↓
게시글 목록 수집
        ↓
상세 페이지 수집
        ↓
DataFrame 변환
        ↓
URL 중복 제거
        ↓
CSV 저장
        ↓
MySQL 저장
        ↓
Streamlit 출력
```

---

# 저장 방식

## CSV 저장

```python
data/ev_user_questions.csv
```

---

## MySQL 저장

```python
ev_user_questions
```

테이블 저장

---

# 예외 처리

필수 구현

```python
try:
    ...
except requests.exceptions.RequestException:
    ...
except Exception:
    ...
```

사이트 하나 실패 시 전체 프로그램 종료 금지

---

# Codex 작업 지시

현재 프로젝트는 app.py를 진입점으로 사용한다.

다음 기능을 구현해줘.

* EVDang 검색 크롤러
* EV 라운지 검색 크롤러
* 클리앙 굴러간당 검색 크롤러
* BaseCrawler 구현
* requests + BeautifulSoup 우선 사용
* 필요 시 Selenium 사용
* pandas DataFrame 변환
* Streamlit 데이터 출력
* 링크 클릭 시 원본 게시글 이동
* CSV 저장
* MySQL 저장
* URL 기준 중복 제거
* 전기차 키워드 필터링
* 예외 처리
* 초보자가 이해할 수 있도록 상세 주석 작성
* app.py 에서 전체 실행 가능하도록 구현
