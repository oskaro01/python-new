const QUESTION_COUNT = 10;
const HISTORY_KEY = "additionPracticeHistory";

const RANGES = {
  Easy: [[10, 99], [10, 99]],
  Medium: [[100, 999], [100, 999]],
  Hard: [[1000, 99999], [1000, 99999]],
};

const difficultySelect = document.querySelector("#difficulty");
const refreshButton = document.querySelector("#refresh-button");
const checkButton = document.querySelector("#check-button");
const questionsElement = document.querySelector("#questions");
const timerElement = document.querySelector("#timer");
const statusElement = document.querySelector("#status");
const resultsElement = document.querySelector("#results");

let questions = [];
let answerInputs = [];
let startedAt = 0;
let timerId = null;
let submitted = false;

function formatDuration(seconds) {
  const totalSeconds = Math.max(0, Math.round(seconds));
  const minutes = Math.floor(totalSeconds / 60);
  const remainingSeconds = totalSeconds % 60;
  const minuteWord = minutes === 1 ? "minute" : "minutes";
  const secondWord = remainingSeconds === 1 ? "second" : "seconds";
  if (minutes && remainingSeconds) return `${minutes} ${minuteWord} ${remainingSeconds} ${secondWord}`;
  if (minutes) return `${minutes} ${minuteWord}`;
  return `${remainingSeconds} ${secondWord}`;
}

function randomInteger(minimum, maximum) {
  return Math.floor(Math.random() * (maximum - minimum + 1)) + minimum;
}

function generateQuestions(difficulty) {
  const modes = Object.keys(RANGES);
  return Array.from({ length: QUESTION_COUNT }, () => {
    const selectedMode = difficulty === "Mixed"
      ? modes[randomInteger(0, modes.length - 1)]
      : difficulty;
    const [[leftMin, leftMax], [rightMin, rightMax]] = RANGES[selectedMode];
    const left = randomInteger(leftMin, leftMax);
    const right = randomInteger(rightMin, rightMax);
    return { left, right, answer: left + right };
  });
}

function loadHistory() {
  try {
    const data = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    return Array.isArray(data) ? data : [];
  } catch (_error) {
    return [];
  }
}

function saveHistory(history) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(-100)));
  } catch (_error) {
    // The practice page still works if browser storage is unavailable.
  }
}

function focusInput(index) {
  if (!answerInputs[index]) return;
  answerInputs[index].focus();
  answerInputs[index].select();
}

function handleKey(event, index) {
  if (submitted) return;
  if (event.key === "Enter") {
    event.preventDefault();
    if (index === answerInputs.length - 1) checkAnswers();
    else focusInput(index + 1);
  } else if (event.key === "ArrowUp") {
    event.preventDefault();
    if (index > 0) focusInput(index - 1);
  } else if (event.key === "ArrowDown") {
    event.preventDefault();
    if (index < answerInputs.length - 1) focusInput(index + 1);
  }
}

function renderQuestions() {
  questionsElement.replaceChildren();
  answerInputs = [];
  questions.forEach((question, index) => {
    const line = document.createElement("div");
    line.className = "question-line";
    const prompt = document.createElement("span");
    prompt.textContent = `${question.left.toLocaleString()} + ${question.right.toLocaleString()} =`;
    const input = document.createElement("input");
    input.type = "text";
    input.inputMode = "numeric";
    input.autocomplete = "off";
    input.setAttribute("aria-label", `Answer ${index + 1}`);
    input.addEventListener("keydown", (event) => handleKey(event, index));
    line.append(prompt, input);
    questionsElement.append(line);
    answerInputs.push(input);
  });
}

function updateTimer() {
  if (submitted) return;
  timerElement.textContent = `Time: ${formatDuration((performance.now() - startedAt) / 1000)}`;
  timerId = window.setTimeout(updateTimer, 250);
}

function writeResults(text) { resultsElement.textContent = text; }

function progressSummary(history) {
  if (!history.length) return "Progress: no completed pages yet.";
  const recent = history.slice(-5);
  const averageAccuracy = recent.reduce((sum, item) => sum + item.accuracy, 0) / recent.length;
  const averageSeconds = recent.reduce((sum, item) => sum + item.seconds, 0) / recent.length;
  const bestAccuracy = Math.max(...history.map((item) => item.accuracy));
  return `Progress (last ${recent.length} pages): average accuracy ${Math.round(averageAccuracy)}%, `
    + `average time ${formatDuration(averageSeconds)}; best accuracy ${Math.round(bestAccuracy)}%.`;
}

function checkAnswers() {
  if (submitted) return;
  const elapsed = (performance.now() - startedAt) / 1000;
  let correct = 0;
  const wrong = [];
  questions.forEach((question, index) => {
    const rawAnswer = answerInputs[index].value.trim();
    const validAnswer = rawAnswer !== "" && /^\d+$/.test(rawAnswer);
    const isCorrect = validAnswer && Number(rawAnswer) === question.answer;
    if (isCorrect) correct += 1;
    else wrong.push({ index: index + 1, question, userAnswer: rawAnswer || "blank" });
  });

  submitted = true;
  if (timerId !== null) window.clearTimeout(timerId);
  timerElement.textContent = `Time: ${formatDuration(elapsed)}`;
  statusElement.textContent = "Page complete. Choose Refresh page to practise again.";
  checkButton.disabled = true;
  answerInputs.forEach((input) => { input.disabled = true; });

  const accuracy = correct / QUESTION_COUNT * 100;
  const history = loadHistory();
  history.push({ timestamp: new Date().toISOString(), difficulty: difficultySelect.value, correct, accuracy, seconds: elapsed });
  saveHistory(history);

  const lines = [`Score: ${correct}/${QUESTION_COUNT}`, `Accuracy: ${Math.round(accuracy)}%`, `Time: ${formatDuration(elapsed)}`, ""];
  if (wrong.length) {
    lines.push("Review these answers:");
    wrong.forEach(({ index, question, userAnswer }) => {
      lines.push(`${String(index).padStart(2, " ")}. ${question.left.toLocaleString()} + `
        + `${question.right.toLocaleString()} | You: ${userAnswer} | Correct: ${question.answer.toLocaleString()}`);
    });
  } else {
    lines.push("Perfect page! Every answer was correct.");
  }
  lines.push("", progressSummary(history));
  writeResults(lines.join("\n"));
}

function startPage() {
  if (timerId !== null) window.clearTimeout(timerId);
  questions = generateQuestions(difficultySelect.value);
  submitted = false;
  startedAt = performance.now();
  timerElement.textContent = "Time: 0 seconds";
  statusElement.textContent = "Type an answer for each question.";
  checkButton.disabled = false;
  writeResults("Your score and answer review will appear here after submission.");
  renderQuestions();
  focusInput(0);
  updateTimer();
}

refreshButton.addEventListener("click", startPage);
difficultySelect.addEventListener("change", startPage);
checkButton.addEventListener("click", checkAnswers);
startPage();
