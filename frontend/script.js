const form = document.getElementById('upload-form');
const fileInput = document.getElementById('file-input');
const fileName = document.getElementById('file-name');
const submitBtn = document.getElementById('submit-btn');
const status = document.getElementById('status');
const fileWrapper = document.getElementById('file-wrapper');
const successBlock = document.getElementById('success-block');
const downloadBtn = document.getElementById('download-btn');

let selectedFile = null;
let lastBlobUrl = null;

// Клик по обёртке = клик по input
fileWrapper.addEventListener('click', () => {
    fileInput.click();
});

// Выбор файла
fileInput.addEventListener('change', () => {
    if (fileInput.files.length === 0) {
        resetFile();
        return;
    }

    const file = fileInput.files[0];

    if (!file.name.toLowerCase().endsWith('.xlsx')) {
        status.textContent = '❌ Нужен файл .xlsx';
        status.className = 'error';
        resetFile();
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileName.className = 'file-name has-file';
    submitBtn.disabled = false;
    status.textContent = '';
    status.className = '';
    successBlock.style.display = 'none';
    form.style.display = 'block';
});

function resetFile() {
    selectedFile = null;
    fileInput.value = '';
    fileName.textContent = 'Файл не выбран';
    fileName.className = 'file-name';
    submitBtn.disabled = true;
}

// Отправка формы
form.addEventListener('submit', async (event) => {
    event.preventDefault();

    if (!selectedFile) {
        status.textContent = '❌ Выберите файл';
        status.className = 'error';
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Обработка...';
    status.textContent = '⏳ Формируем отчёт...';
    status.className = 'loading';
    successBlock.style.display = 'none';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            let message = 'Ошибка сервера';
            try {
                const data = await response.json();
                if (data.detail) message = data.detail;
            } catch {}
            throw new Error(message);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        lastBlobUrl = url;

        // Скрываем форму
        form.style.display = 'none';
        status.textContent = '';
        status.className = '';

        // Показываем блок успеха
        successBlock.style.display = 'block';

    } catch (error) {
        status.textContent = '❌ ' + error.message;
        status.className = 'error';
        submitBtn.disabled = false;
        submitBtn.textContent = 'Сформировать отчёт';
    }
});

// Скачивание отчёта
downloadBtn.addEventListener('click', () => {
    if (lastBlobUrl) {
        const a = document.createElement('a');
        a.href = lastBlobUrl;
        a.download = 'report.xlsx';
        document.body.appendChild(a);
        a.click();
        a.remove();
    }
});