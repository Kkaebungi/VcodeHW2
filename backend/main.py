from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageFilter, ImageOps
import io

app = FastAPI(title="Image Filtering API")

# CORS Configuration (모든 도메인 허용 - 프론트엔드 분리를 위함)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/version")
def get_version():
    return {"version": "v5.12"} # 빨간 고양이 마스코트가 반영된 v5.12 업데이트

@app.get("/filters")
def get_filters():
    return [
        {"id": "grayscale", "name": "Grayscale"},
        {"id": "blur", "name": "Blur"},
        {"id": "gaussian_blur", "name": "Gaussian Blur"},
        {"id": "invert", "name": "Invert (색상 반전)"},
        {"id": "sepia", "name": "Sepia (세피아)"},
        {"id": "blue_future", "name": "파란미래 (Blue Future)"},
        {"id": "red_hell", "name": "빨간지옥 (Red Hell)"},
        {"id": "green_naver", "name": "네이버 그린 (Green Naver)"},
        {"id": "pink_calc", "name": "미적분홍 (Pink Calc)"}
    ]

@app.post("/filter")
async def apply_filter(
    type: str = Query(..., description="지원 필터: blur, gaussian_blur, grayscale, invert, sepia, blue_future, red_hell, green_naver, pink_calc"),
    image: UploadFile = File(...)
):
    # 1. 지원하는 이미지 포맷 확인
    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        # 2. 이미지를 메모리로 읽기 (파일 저장 안함)
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # 3. 요청된 필터 적용 (invert, sepia 추가)
        if type == "blur":
            filtered_image = pil_image.filter(ImageFilter.BLUR)
        elif type == "gaussian_blur":
            filtered_image = pil_image.filter(ImageFilter.GaussianBlur(radius=5))
        elif type == "grayscale":
            filtered_image = ImageOps.grayscale(pil_image)
        elif type == "invert":
            # 색상 반전 필터
            filtered_image = ImageOps.invert(pil_image)
        elif type == "sepia":
            # 세피아 톤 (RGB 컬러를 변환 매트릭스로 매핑)
            sepia_matrix = (
                0.393, 0.769, 0.189, 0,
                0.349, 0.686, 0.168, 0,
                0.272, 0.534, 0.131, 0
            )
            filtered_image = pil_image.convert("RGB", sepia_matrix)
        elif type == "blue_future":
            # 파란미래 톤 (흑백화 후 파란 계열로 Colorize)
            grayscale = ImageOps.grayscale(pil_image)
            filtered_image = ImageOps.colorize(grayscale, black="#000033", white="#00ffff")
        elif type == "red_hell":
            # 빨간지옥 톤 (흑백화 후 붉은 계열로 Colorize)
            grayscale = ImageOps.grayscale(pil_image)
            filtered_image = ImageOps.colorize(grayscale, black="#330000", white="#ff0000")
        elif type == "green_naver":
            # 네이버 그린 톤 (녹색 채널 강화, 적/청 채널 약화)
            green_matrix = (
                0.3, 0.0, 0.0, 0,
                0.0, 1.3, 0.0, 0,
                0.0, 0.0, 0.3, 0
            )
            filtered_image = pil_image.convert("RGB", green_matrix)
        elif type == "pink_calc":
            # 미적분홍 톤 (Red 채널은 강화하고, Blue는 약간 유지, Green은 억제하여 핑크톤 강조)
            pink_matrix = (
                1.3, 0.0, 0.0, 0,
                0.0, 0.3, 0.0, 0,
                0.0, 0.0, 0.8, 0
            )
            filtered_image = pil_image.convert("RGB", pink_matrix)
        else:
            raise HTTPException(status_code=400, detail="Invalid filter type")

        # 4. 처리된 이미지를 메모리 버퍼에 저장 유지
        output_buffer = io.BytesIO()
        img_format = image.content_type.split("/")[1].upper()
        if img_format == "JPG": img_format = "JPEG"
        
        filtered_image.save(output_buffer, format=img_format)
        output_buffer.seek(0)

        # 5. 스트리밍 응답 (다운로드 및 화면 표시용)
        return StreamingResponse(output_buffer, media_type=image.content_type)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
