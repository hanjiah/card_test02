# 국내 신용카드사 비교 대시보드 — Vercel 배포본

Vercel과 GitHub 연동을 위해 독립시킨 정적 웹 프로젝트입니다. 배포 진입점은 `public/index.html`이며, 별도 빌드나 Python 서버가 필요하지 않습니다.

사용자가 입력한 공공데이터포털 인증키로 브라우저가 금융위원회 OpenAPI에 HTTPS/XML 요청을 직접 보냅니다. 키는 파일, GitHub, Vercel 환경 변수, 브라우저 저장소에 보관하지 않습니다.

## GitHub 저장소 만들기

이 `vercel-card-dashboard` 폴더에서 아래 명령을 실행합니다.

```bash
git init
git add .
git commit -m "Initial credit card dashboard"
git branch -M main
git remote add origin https://github.com/본인계정/저장소이름.git
git push -u origin main
```

GitHub에서 먼저 비어 있는 저장소를 만든 뒤, 위의 `본인계정/저장소이름` 부분을 실제 주소로 바꿉니다. 인증키는 절대 커밋하지 않습니다.

## Vercel 연동

1. Vercel Dashboard에서 **Add New → Project**를 선택합니다.
2. 방금 만든 GitHub 저장소를 Import합니다.
3. Framework Preset은 **Other**, Root Directory는 저장소 루트로 둡니다.
4. Build Command는 비워 둡니다. `vercel.json`이 Output Directory를 `public`으로 고정하므로 Dashboard 설정에 값이 남아 있다면 **Override**를 켜고 `public`으로 맞춥니다.
5. **Deploy**를 누릅니다.

`vercel.json`은 보안 헤더를 포함합니다. 대시보드는 Vercel Origin에 대한 공공 API CORS 허용 여부를 확인한 방식으로 동작합니다.

## CLI 배포 선택지

Node.js 20 이상에서 다음을 실행할 수도 있습니다.

```bash
npm run deploy
# 운영 배포
npm run deploy:production
```

첫 실행에서 Vercel 로그인과 프로젝트 연결을 안내합니다.

## 구성

- `public/index.html`: 대시보드 전체 UI와 API 조회 로직
- `vercel.json`: 정적 배포와 보안 헤더
- `package.json`: 선택적 Vercel CLI 명령
