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

imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        fileName.textContent = selectedFile.name;
        applyBtn.disabled = false;
        previewSection.style.display = 'none';
        if (blobUrl) URL.revokeObjectURL(blobUrl);
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
