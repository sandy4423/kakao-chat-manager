# 🗨️ 카카오톡 대화 분석기

하이브리드 저장소(Cloudinary + Supabase)를 사용한 카카오톡 대화내용 분석 웹 애플리케이션입니다.

## ✨ 주요 기능

- 📤 **파일 업로드**: 카카오톡 대화내용 .txt 파일 업로드
- 🔍 **실시간 검색**: 키워드, 사용자별 메시지 검색
- 📊 **통계 분석**: 사용자별 활동, 키워드 빈도 분석
- ☁️ **하이브리드 저장**: Cloudinary(백업) + Supabase(분석)
- 📱 **모바일 최적화**: 반응형 웹 디자인
- 🚀 **Vercel 배포**: 무료 클라우드 호스팅

## 🏗️ 기술 스택

### Backend
- **Flask**: 웹 프레임워크
- **Supabase**: PostgreSQL 데이터베이스
- **Cloudinary**: 파일 스토리지
- **Python**: 메인 프로그래밍 언어

### Frontend
- **Bootstrap 5**: UI 프레임워크
- **jQuery**: JavaScript 라이브러리
- **Bootstrap Icons**: 아이콘

### Deployment
- **Vercel**: 서버리스 호스팅
- **GitHub**: 코드 저장소

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/kakao-chat-analyzer.git
cd kakao-chat-analyzer
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정
`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# Cloudinary 설정
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key

# Flask 설정
SECRET_KEY=your-secret-key-here
```

### 4. 로컬 실행
```bash
python app.py
```

브라우저에서 `http://localhost:5000`으로 접속하세요.

## 📱 사용법

### 1. 파일 업로드
1. 카카오톡에서 대화내용 내보내기 (.txt 파일)
2. 웹앱의 "파일 업로드" 페이지로 이동
3. 파일을 드래그하거나 클릭하여 선택
4. 자동으로 파싱되어 저장됩니다

### 2. 메시지 검색
- **키워드 검색**: 메시지 내용에서 특정 단어 검색
- **사용자별 검색**: 특정 사용자의 메시지만 검색
- **실시간 검색**: 타이핑하면 자동으로 검색 결과 업데이트

### 3. 통계 보기
- **사용자별 통계**: 메시지 수, 입장/퇴장 횟수
- **키워드 빈도**: 가장 많이 언급된 단어들
- **전체 통계**: 총 메시지 수, 고유 사용자 수

## 🗄️ 데이터베이스 구조

### Supabase 테이블

#### messages
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    message_type VARCHAR(20),
    nickname VARCHAR(255),
    time_str VARCHAR(50),
    message_text TEXT,
    raw_line TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### users
```sql
CREATE TABLE users (
    nickname VARCHAR(255) PRIMARY KEY,
    total_messages INTEGER DEFAULT 0,
    join_count INTEGER DEFAULT 0,
    leave_count INTEGER DEFAULT 0,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP
);
```

## 🌐 배포 (Vercel)

### 1. GitHub에 푸시
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Vercel 연결
1. [Vercel](https://vercel.com)에 가입
2. GitHub 저장소 연결
3. 환경변수 설정 (Cloudinary, Supabase)
4. 자동 배포 완료!

## 🔧 개발

### 프로젝트 구조
```
kakao-chat-analyzer/
├── app.py                 # Flask 메인 앱
├── kakao_parser.py        # 카카오톡 파싱 엔진
├── hybrid_storage.py      # 하이브리드 저장소
├── requirements.txt       # Python 의존성
├── vercel.json           # Vercel 설정
├── templates/            # HTML 템플릿
│   ├── base.html
│   ├── dashboard.html
│   └── upload.html
└── static/              # 정적 파일
    ├── css/style.css
    └── js/main.js
```

### API 엔드포인트

#### 파일 업로드
```
POST /upload
Content-Type: multipart/form-data
```

#### 검색
```
GET /api/search?keyword=검색어&nickname=사용자&limit=100
```

#### 통계
```
GET /api/statistics
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🙏 감사의 말

- [Flask](https://flask.palletsprojects.com/) - 웹 프레임워크
- [Supabase](https://supabase.com/) - 데이터베이스
- [Cloudinary](https://cloudinary.com/) - 파일 스토리지
- [Bootstrap](https://getbootstrap.com/) - UI 프레임워크
- [Vercel](https://vercel.com/) - 호스팅 플랫폼

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.

---

⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요! 