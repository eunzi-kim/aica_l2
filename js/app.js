import {
  loadProgress,
  saveProgress,
  getRecord,
  recordAnswer,
  recordSession,
  getStats,
  getWrongQuestionIds,
  clearProgress,
} from './storage.js';

const MODES = {
  ALL: 'all',
  CHOICES_4: '4',
  CHOICES_5: '5',
  WRONG: 'wrong',
  UNATTEMPTED: 'unattempted',
};

let examData = null;
let progress = loadProgress();
let quizQueue = [];
let currentIndex = 0;
let selectedOption = null;
let answered = false;
let sessionStats = { correct: 0, wrong: 0 };

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

async function init() {
  try {
    const res = await fetch('./data/questions.json');
    examData = await res.json();
  } catch (e) {
    showError('문항 파일을 불러오지 못했습니다. data/questions.json을 확인해주세요.');
    return;
  }

  $('#exam-title').textContent = examData.examTitle || '퀴즈';
  $('#exam-desc').textContent = examData.description || '';

  bindEvents();
  renderHome();
}

function bindEvents() {
  $$('.mode-btn').forEach((btn) => {
    btn.addEventListener('click', () => startQuiz(btn.dataset.mode));
  });

  $('#btn-home').addEventListener('click', () => {
    showView('home');
    renderHome();
  });

  $('#btn-check').addEventListener('click', checkAnswer);
  $('#btn-next').addEventListener('click', nextQuestion);
  $('#btn-clear').addEventListener('click', () => {
    if (confirm('학습 기록을 모두 삭제할까요?')) {
      clearProgress();
      progress = loadProgress();
      renderHome();
    }
  });

  $('#btn-result-home').addEventListener('click', () => {
    showView('home');
    renderHome();
  });

  $('#btn-result-wrong').addEventListener('click', () => startQuiz(MODES.WRONG));
}

function showView(name) {
  $$('.view').forEach((v) => v.classList.remove('active'));
  $(`#view-${name}`).classList.add('active');
}

function showError(msg) {
  $('#view-home').innerHTML = `<p class="error-msg">${msg}</p>`;
  showView('home');
}

function filterQuestions(mode) {
  const all = examData.questions;
  const wrongIds = new Set(getWrongQuestionIds(progress));

  if (mode.startsWith('cat:')) {
    const cat = mode.slice(4);
    return all.filter((q) => q.category === cat);
  }

  switch (mode) {
    case MODES.CHOICES_4:
      return all.filter((q) => q.choices === 4);
    case MODES.CHOICES_5:
      return all.filter((q) => q.choices === 5);
    case MODES.WRONG:
      return all.filter((q) => wrongIds.has(q.id));
    case MODES.UNATTEMPTED:
      return all.filter((q) => !getRecord(progress, q.id));
    default:
      return [...all];
  }
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function startQuiz(mode) {
  quizQueue = shuffle(filterQuestions(mode));
  if (quizQueue.length === 0) {
    alert(
      mode === MODES.WRONG
        ? '틀린 문제가 없어요! 🎉'
        : '해당 조건에 맞는 문항이 없어요.'
    );
    return;
  }

  currentIndex = 0;
  selectedOption = null;
  answered = false;
  sessionStats = { correct: 0, wrong: 0 };

  showView('quiz');
  renderQuestion();
}

function renderHome() {
  const stats = getStats(progress, examData.questions);
  const wrongCount = getWrongQuestionIds(progress).length;
  const pct = stats.attempted
    ? Math.round((stats.correct / stats.attempted) * 100)
    : 0;

  $('#stat-total').textContent = stats.total;
  $('#stat-attempted').textContent = stats.attempted;
  $('#stat-correct').textContent = stats.correct;
  $('#stat-wrong').textContent = stats.wrong;
  $('#stat-wrong-badge').textContent = wrongCount;
  $('#stat-pct').textContent = `${pct}%`;

  const count4 = examData.questions.filter((q) => q.choices === 4).length;
  const count5 = examData.questions.filter((q) => q.choices === 5).length;
  $('#count-all').textContent = stats.total;
  $('#count-4').textContent = count4;
  $('#count-5').textContent = count5;
  $('#count-wrong').textContent = wrongCount;
  $('#count-unattempted').textContent = stats.unattempted;

  const byCat = (name) => examData.questions.filter((q) => q.category === name).length;
  $('#count-sample').textContent = byCat('공식 샘플문항');
  $('#count-bank').textContent = byCat('연습 문항 뱅크');
  $('#count-template').textContent = byCat('코드 템플릿');
  $('#count-tip').textContent = byCat('시험 팁');
}

function renderQuestion() {
  const q = quizQueue[currentIndex];
  selectedOption = null;
  answered = false;

  const total = quizQueue.length;
  const pct = ((currentIndex + 1) / total) * 100;
  $('#progress-bar').style.width = `${pct}%`;
  $('#progress-text').textContent = `${currentIndex + 1} / ${total}`;

  $('#q-category').textContent = q.category || '';
  $('#q-choices-badge').textContent = `${q.choices}지선다`;
  $('#q-text').textContent = q.question;

  const prev = getRecord(progress, q.id);
  if (prev) {
    $('#q-history').textContent = `이전: ${prev.attempts}회 시도 · ${prev.lastCorrect ? '✅ 맞음' : '❌ 틀림'}`;
    $('#q-history').hidden = false;
  } else {
    $('#q-history').hidden = true;
  }

  const optionsEl = $('#options');
  optionsEl.innerHTML = '';

  q.options.forEach((text, i) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'option-btn';
    btn.dataset.index = i;
    btn.innerHTML = `<span class="option-num">${i + 1}</span><span class="option-text">${escapeHtml(text)}</span>`;
    btn.addEventListener('click', () => selectOption(i, btn));
    optionsEl.appendChild(btn);
  });

  $('#feedback').hidden = true;
  $('#feedback').className = 'feedback';
  $('#btn-check').hidden = false;
  $('#btn-check').disabled = true;
  $('#btn-next').hidden = true;
}

function selectOption(index, btn) {
  if (answered) return;
  selectedOption = index;
  $$('.option-btn').forEach((b) => b.classList.remove('selected'));
  btn.classList.add('selected');
  $('#btn-check').disabled = false;
}

function checkAnswer() {
  if (selectedOption === null || answered) return;

  const q = quizQueue[currentIndex];
  const isCorrect = selectedOption === q.correct;
  answered = true;

  recordAnswer(progress, q.id, selectedOption, isCorrect);
  if (isCorrect) sessionStats.correct += 1;
  else sessionStats.wrong += 1;

  $$('.option-btn').forEach((btn, i) => {
    btn.disabled = true;
    if (i === q.correct) btn.classList.add('correct');
    if (i === selectedOption && !isCorrect) btn.classList.add('wrong');
  });

  const feedback = $('#feedback');
  feedback.hidden = false;
  feedback.className = `feedback ${isCorrect ? 'feedback-ok' : 'feedback-bad'}`;
  feedback.innerHTML = isCorrect
    ? `<strong>정답!</strong>`
    : `<strong>오답</strong> · 정답: ${q.correct + 1}번`;
  if (q.explanation) {
    feedback.innerHTML += `<p class="explanation">${escapeHtml(q.explanation)}</p>`;
  }

  $('#btn-check').hidden = true;
  $('#btn-next').hidden = false;
  $('#btn-next').textContent =
    currentIndex >= quizQueue.length - 1 ? '결과 보기' : '다음 문제';
}

function nextQuestion() {
  if (currentIndex < quizQueue.length - 1) {
    currentIndex += 1;
    renderQuestion();
    return;
  }

  recordSession(progress, 'quiz', {
    total: quizQueue.length,
    correct: sessionStats.correct,
    wrong: sessionStats.wrong,
  });

  showView('result');
  const total = quizQueue.length;
  const pct = Math.round((sessionStats.correct / total) * 100);
  $('#result-score').textContent = `${sessionStats.correct} / ${total}`;
  $('#result-pct').textContent = `${pct}%`;
  $('#result-msg').textContent =
    pct >= 80 ? '합격권! 🎉' : pct >= 60 ? '조금만 더! 💪' : '오답노트로 복습해봐요 📚';
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

init();
