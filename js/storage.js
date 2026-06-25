const STORAGE_KEY = 'aica-l2-quiz-progress';

export function loadProgress() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return createEmptyProgress();
    const data = JSON.parse(raw);
    return { ...createEmptyProgress(), ...data };
  } catch {
    return createEmptyProgress();
  }
}

function createEmptyProgress() {
  return {
    records: {},
    sessions: [],
  };
}

export function saveProgress(progress) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
}

export function getRecord(progress, questionId) {
  return progress.records[questionId] || null;
}

export function recordAnswer(progress, questionId, selectedIndex, isCorrect) {
  const prev = progress.records[questionId] || {
    attempts: 0,
    correctCount: 0,
    wrongCount: 0,
    lastSelected: null,
    lastCorrect: false,
    firstAttemptAt: null,
    lastAttemptAt: null,
  };

  const now = Date.now();
  const updated = {
    ...prev,
    attempts: prev.attempts + 1,
    correctCount: prev.correctCount + (isCorrect ? 1 : 0),
    wrongCount: prev.wrongCount + (isCorrect ? 0 : 1),
    lastSelected: selectedIndex,
    lastCorrect: isCorrect,
    firstAttemptAt: prev.firstAttemptAt || now,
    lastAttemptAt: now,
  };

  progress.records[questionId] = updated;
  saveProgress(progress);
  return updated;
}

export function recordSession(progress, mode, stats) {
  progress.sessions.push({
    at: Date.now(),
    mode,
    ...stats,
  });
  if (progress.sessions.length > 50) {
    progress.sessions = progress.sessions.slice(-50);
  }
  saveProgress(progress);
}

export function getStats(progress, allQuestions) {
  const total = allQuestions.length;
  let attempted = 0;
  let correct = 0;
  let wrong = 0;

  for (const q of allQuestions) {
    const r = progress.records[q.id];
    if (!r) continue;
    attempted += 1;
    if (r.lastCorrect) correct += 1;
    else wrong += 1;
  }

  return { total, attempted, correct, wrong, unattempted: total - attempted };
}

export function getWrongQuestionIds(progress) {
  return Object.entries(progress.records)
    .filter(([, r]) => !r.lastCorrect)
    .map(([id]) => id);
}

export function clearProgress() {
  localStorage.removeItem(STORAGE_KEY);
}
