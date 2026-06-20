# 전체 API 라우트 구조 (API 명세서)

본 문서는 `app.py`에서 기능별로 분리된 백엔드 라우트(API) 구조를 파악하기 쉽게 요약한 명세서입니다.

---

## 1. 코어 API (core.py)
서버 기본 상태, 방문자 통계, 메인 화면 서빙을 담당합니다.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | 프론트엔드 React 빌드 파일(`index.html`)을 서빙합니다. |
| `GET` | `/api/hello` | 서버 동작 확인용 기본 API |
| `POST` | `/api/visit` | 오늘 날짜의 일일 방문자 카운트를 1 증가시킵니다. |
| `GET` | `/api/stats` | 전체/오늘 방문자 수와 재생 수(play_count) 기반 Top 20 곡을 반환합니다. |

---

## 2. Spotify 연동 API (spotify.py)
Spotify 토큰을 발급받아 곡 정보와 플레이리스트를 검색 및 조회합니다.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/spotify/search` | `?q=검색어` 로컬 DB 및 Spotify에서 트랙을 검색합니다. |
| `GET` | `/api/spotify/artist/<artist_id>/top-tracks` | 특정 아티스트의 인기곡 목록을 조회합니다. |
| `GET` | `/api/spotify/playlist/<playlist_id>/latest` | 특정 플레이리스트의 가장 최근 등록된 50곡을 조회합니다. |
| `GET` | `/api/spotify/track/<track_id>` | 단일 트랙의 상세 정보를 Spotify에서 조회합니다. |

---

## 3. YouTube 연동 API (youtube.py)
Youtube API를 사용하여 뮤직비디오를 검색합니다.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/youtube/search` | `?q=검색어` 또는 `?track_id=ID`를 기반으로 YouTube 비디오를 검색 및 DB에 캐싱합니다. |

---

## 4. 노래 가사 및 처리 API (lyrics.py)
노래 리스트, 가사 처리/조회, 번역, 좋아요, 색상 추출 등 주요 데이터 로직을 담당합니다.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/songlist` | 저장된 곡 목록을 페이징 처리(`?page=1`)하여 반환합니다. |
| `GET` | `/api/lyrics/<track_id>` | 트랙 ID에 해당하는 가사 배열 반환 및 조회수를 1 증가시킵니다. |
| `PUT` | `/api/songlist/<track_id>` | 트랙의 정보(제목, 아티스트, 가사)를 수정합니다. |
| `DELETE` | `/api/songlist/<track_id>` | 해당 트랙을 DB에서 완전히 삭제합니다. |
| `POST` | `/api/translate/info` | 곡 제목과 앨범명의 번역 정보를 가져오거나 생성/저장합니다. |
| `POST` | `/api/lyrics/process` | 원본 가사(`raw_lyrics`)를 전달받아 가공 후 반환하며 DB에 저장합니다. |
| `GET` | `/api/song/<track_id>/likes` | 곡의 좋아요(Likes) 개수를 반환합니다. |
| `POST` | `/api/song/<track_id>/like` | 곡의 좋아요 수를 1 증가시킵니다. |
| `GET` | `/api/color` | `?url=이미지주소` 커버 이미지에서 주요(Dominant) 색상과 팔레트를 추출합니다. |

---

## 5. 십자말풀이 & 단어 찾기 게임 (engcross.py)
영어 게임용 랭킹 처리와 Word Search 카테고리 데이터를 제공합니다.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/engcross/newrank(난이도)` | 초등/중고등/토익/공무원 난이도의 랭킹 목록을 조회합니다. |
| `GET/POST` | `/engcross/new(one~four)` | 비밀번호 확인 후 해당 레벨의 점수를 증가시킵니다. |
| `GET` | `/engcross/wordsearch/categories` | Word Search 게임의 카테고리(주제) 목록을 반환합니다. |
| `GET` | `/engcross/wordsearch/words` | `?category=코드` 특정 카테고리에 속한 영어/한국어 단어 목록을 반환합니다. |

---

## 6. While My Guitar API (guitar.py)
기타 연주 앱을 위한 프리셋 메타데이터와 전체 JSON을 반환합니다.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/presets` | 앱 목록에 표시할 모든 프리셋의 기본 정보(이름, BPM 등)를 반환합니다. |
| `GET` | `/api/presets/<preset_id>` | 특정 프리셋의 다운로드용 전체 JSON 데이터를 반환합니다. |

---

## 7. 라디오 채널 API (radio.py)
로컬 JSON 파일들을 서빙합니다.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/radio/mon` ~ `/radio/sun` | 월~일요일까지 정해진 라디오 플레이리스트 JSON을 반환합니다. |
