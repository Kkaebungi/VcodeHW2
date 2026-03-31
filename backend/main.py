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

@app.post("/filter")
async def apply_filter(
    type: str = Query(..., description="지원 필터: blur, gaussian_blur, grayscale, invert, sepia, blue_future"),
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
