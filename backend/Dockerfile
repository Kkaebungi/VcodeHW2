# 파이썬 3.10 슬림 이미지 (경량화 및 보안 패치 적용)
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 파이썬 환경 변수 설정 (바이트코드 생성 방지, 버퍼링 비활성화)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 시스템 의존성 설치 및 캐시 제거 (이미지 용량 최소화)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# 의존성 파일 먼저 복사 (Docker 빌드 레이어 캐싱 활용하여 빌드 속도 향상)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 소스 코드 복사
COPY . .

# 권한이 제한된 비권한 사용자(appuser) 생성 및 적용 (보안 강화)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
