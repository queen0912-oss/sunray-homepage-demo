const intro = document.getElementById("intro");
const skipIntro = document.getElementById("skipIntro");
const replayIntro = document.getElementById("replayIntro");
const introTitle = document.getElementById("introTitle");
const introText = document.getElementById("introText");
const introKicker = document.getElementById("introKicker");
const introTime = document.getElementById("introTime");
const introProgress = document.getElementById("introProgress");

const scenes = [
  {
    end: 4000,
    kicker: "Combustion",
    title: "火炎を、技術で制御する。",
    text: "燃焼の安定性と安全性を、現場ごとに設計する。"
  },
  {
    end: 9000,
    kicker: "Equipment",
    title: "装置の細部に、技術が宿る。",
    text: "バーナー、配管、制御盤、計器を精密に組み合わせる。"
  },
  {
    end: 15000,
    kicker: "Engineering",
    title: "装置を、現場に合わせて組み上げる。",
    text: "図面、組立、検査。用途に合わせて一台ずつ設計する。"
  },
  {
    end: 20000,
    kicker: "Environment",
    title: "クリーンな生産環境へ。",
    text: "排ガス処理・脱臭・省エネを支える技術。"
  },
  {
    end: 26000,
    kicker: "Support",
    title: "導入後も、現場を止めない。",
    text: "点検、更新、改造、トラブル対応まで支える。"
  },
  {
    end: 30000,
    kicker: "Sunray Reinetsu",
    title: "燃焼技術で、産業と環境の未来を支える。",
    text: "サンレー冷熱株式会社"
  }
];

let timer = null;
let startedAt = 0;
const duration = 30000;

function formatTime(milliseconds) {
  const seconds = Math.max(Math.ceil(milliseconds / 1000), 0);
  return `00:${String(seconds).padStart(2, "0")}`;
}

function renderScene(elapsed) {
  const ratio = Math.min(elapsed / duration, 1);
  const scene = scenes.find((item) => elapsed < item.end) || scenes[scenes.length - 1];
  const remaining = duration - elapsed;

  introKicker.textContent = scene.kicker;
  introTitle.textContent = scene.title;
  introText.textContent = scene.text;
  introTime.textContent = formatTime(remaining);
  introProgress.style.width = `${ratio * 100}%`;
}

function endIntro() {
  window.clearInterval(timer);
  intro.classList.add("is-hidden");
}

function startIntro() {
  intro.classList.remove("is-hidden");
  startedAt = Date.now();
  renderScene(0);
  window.clearInterval(timer);
  timer = window.setInterval(() => {
    const elapsed = Date.now() - startedAt;
    renderScene(elapsed);
    if (elapsed >= duration) {
      endIntro();
    }
  }, 120);
}

skipIntro.addEventListener("click", endIntro);
replayIntro.addEventListener("click", startIntro);
window.addEventListener("load", startIntro);
