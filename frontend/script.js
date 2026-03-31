const imageInput = document.getElementById('imageInput');
const fileName = document.getElementById('fileName');
const applyBtn = document.getElementById('applyBtn');
const filterType = document.getElementById('filterType');
const previewSection = document.getElementById('previewSection');
const resultImage = document.getElementById('resultImage');
const downloadBtn = document.getElementById('downloadBtn');
const loading = document.getElementById('loading');

let selectedFile = null;
let blobUrl = null;

// 백엔드 API 주소 (동일한 docker-compose 실행 기준 로컬호스트 매핑)
const API_URL = 'http://localhost:8124';

// 말풍선 제어 함수
function showBubble(text) {
    const catBubble = document.getElementById('catBubble');
    if (catBubble) {
        if (text) catBubble.textContent = text;
        catBubble.classList.add('show');
        setTimeout(() => catBubble.classList.remove('show'), 3000);
    }
}

// 고양이 아이콘 클릭 시 인터랙션 (추가 재미 요소)
const catMascot = document.getElementById('catMascot');
if (catMascot) {
    catMascot.addEventListener('click', () => showBubble("야옹! 예쁜 필터를 골라봐!"));
}

// 페이지 로드 시 서버에서 버전과 필터 목록을 동기화
document.addEventListener('DOMContentLoaded', async () => {
    // 요구사항: 페이지 최초 로드 시 말풍선 표시
    showBubble("안녕하세요, 이미지를 수정해드려요!");
    try {
        const versionRes = await fetch(`${API_URL}/version`);
        const versionData = await versionRes.json();
        document.getElementById('appVersion').textContent = `(${versionData.version})`;

        const filtersRes = await fetch(`${API_URL}/filters`);
        const filters = await filtersRes.json();
        
        filterType.innerHTML = '';
        filters.forEach(f => {
            const option = document.createElement('option');
            option.value = f.id;
            option.textContent = f.name;
            filterType.appendChild(option);
        });
    } catch (e) {
        console.error("Failed to load initial dynamic data", e);
    }
});

imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        fileName.textContent = selectedFile.name;
        applyBtn.disabled = false;
        previewSection.style.display = 'none';
        if (blobUrl) URL.revokeObjectURL(blobUrl);
        // 요구사항: 이미지 업로드 시 나타남
        showBubble("멋진 사진이에요! 이제 필터를 적용해 보세요.");
    }
});

applyBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('image', selectedFile);
    const type = filterType.value;
    
    loading.style.display = 'block';
    applyBtn.disabled = true;
    previewSection.style.display = 'none';

    try {
        const response = await fetch(`${API_URL}/filter?type=${type}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Filter application failed');

        const blob = await response.blob();
        blobUrl = URL.createObjectURL(blob); // 응답받은 메모리 이미지 바이너리를 URL로 변환
        
        resultImage.src = blobUrl;
        previewSection.style.display = 'block';
    } catch (error) {
        alert(error.message);
    } finally {
        loading.style.display = 'none';
        applyBtn.disabled = false;
    }
});

// 이미지 다운로드 로직
downloadBtn.addEventListener('click', () => {
    if (!blobUrl) return;
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = `filtered_${selectedFile.name}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});
