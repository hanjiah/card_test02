# 국내 신용카드사 비교 대시보드

금융위원회 `GetCredCardCompInfoService`를 이용해 카드사 현황을 비교하는 정적 웹 대시보드입니다.

## Netlify 배포

1. 이 폴더를 Git 저장소에 올리거나 Netlify의 수동 배포 화면에 폴더를 올립니다.
2. Netlify의 Publish directory는 `.`(프로젝트 루트)로 둡니다. 이미 `netlify.toml`에 설정되어 있습니다.
3. Build command는 비워 둡니다.
4. 배포된 사이트에서 공공데이터포털 인증키를 직접 입력해 조회합니다.

Python이나 별도 서버리스 함수는 Netlify에서 실행하지 않습니다. API 요청은 사용자의 브라우저에서 공공데이터포털 API로 HTTPS/XML 방식으로 직접 전송됩니다. 인증키는 저장하지 않으며, `netlify.toml`의 `Referrer-Policy: no-referrer`로 다른 사이트에 참조 URL이 전달되지 않도록 설정했습니다.

## 로컬 실행

`run_dashboard.bat`을 실행한 후 `http://127.0.0.1:8788`을 엽니다.

## 포함 파일

- `index.html`: 배포 대상 대시보드
- `netlify.toml`: Netlify 정적 배포·보안 헤더 설정
- `app.py`, `run_dashboard.bat`: 로컬 미리보기용 파일
- `카드사정보api.txt`: 원본 API 활용 가이드
