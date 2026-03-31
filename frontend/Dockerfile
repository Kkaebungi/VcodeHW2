# Nginx 경량 이미지 사용
FROM nginx:alpine

# 기본 컴포넌트 HTML/CSS/JS 만 복사하여 서빙
COPY index.html style.css script.js /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
