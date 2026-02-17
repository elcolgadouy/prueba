const form = document.getElementById('upload-form');
const output = document.getElementById('output');
const useAi = document.getElementById('use-ai');
const speakBtn = document.getElementById('speak');
const stopBtn = document.getElementById('stop');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const fileInput = document.getElementById('pdf');
  const file = fileInput.files[0];

  if (!file) {
    alert('Selecciona un PDF.');
    return;
  }

  const data = new FormData();
  data.append('file', file);

  output.value = 'Procesando PDF...';

  const params = new URLSearchParams({ use_ai: useAi.checked ? 'true' : 'false' });

  const response = await fetch(`/api/clean?${params.toString()}`, {
    method: 'POST',
    body: data,
  });

  const payload = await response.json();

  if (!response.ok) {
    output.value = payload.error || 'Error al procesar el PDF';
    return;
  }

  output.value = payload.cleaned_text;
});

speakBtn.addEventListener('click', () => {
  const text = output.value.trim();
  if (!text) return;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'es-ES';
  utterance.rate = 1;
  window.speechSynthesis.speak(utterance);
});

stopBtn.addEventListener('click', () => {
  window.speechSynthesis.cancel();
});
