/**
 * vak-translate.js
 */

const API_URL  = "http://localhost:8000";
const API_KEY  = "vak-YJoOYmL_biy8KcMVuIw93MZOzEhRIHMG";
const SRC_LANG = "eng_Latn";

const LANGUAGES = [
  { code: "eng_Latn", label: "English", flag: "🇬🇧" },
  { code: "hin_Deva", label: "Hindi", flag: "🇮🇳" },
  { code: "fra_Latn", label: "French", flag: "🇫🇷" },
  { code: "spa_Latn", label: "Spanish", flag: "🇪🇸" },
  { code: "deu_Latn", label: "German", flag: "🇩🇪" },
  { code: "rus_Cyrl", label: "Russian", flag: "🇷🇺" },
  { code: "zho_Hans", label: "Chinese", flag: "🇨🇳" },
  { code: "ara_Arab", label: "Arabic", flag: "🇸🇦" },
  { code: "jpn_Jpan", label: "Japanese", flag: "🇯🇵" },
  { code: "kor_Hang", label: "Korean", flag: "🇰🇷" },
  { code: "pan_Guru", label: "Punjabi", flag: "🇮🇳" },
  { code: "urd_Arab", label: "Urdu", flag: "🇵🇰" },
];

const originals = new WeakMap();
const cache = {};

function saveOriginals() {

  document.querySelectorAll("[data-translate]").forEach((el) => {

    if (!originals.has(el)) {

      originals.set(el, el.innerText.trim());

    }

  });

}

async function translateBatch(batch, tgtLang) {

  try {

    const res = await fetch(`${API_URL}/translate/batch`, {

      method: "POST",

      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
      },

      body: JSON.stringify({
        texts: batch,
        src_lang: SRC_LANG,
        tgt_lang: tgtLang,
      }),

    });

    if (!res.ok) {

      throw new Error(`API error: ${res.status}`);

    }

    const data = await res.json();

    return data.translations;

  }

  catch (err) {

    console.error("[Vak Translate] Error:", err);

    return [];

  }

}

async function translatePage(tgtLang) {

  if (tgtLang === SRC_LANG) {

    document.querySelectorAll("[data-translate]").forEach((el) => {

      const orig = originals.get(el);

      if (orig) {

        el.innerText = orig;

      }

    });

    return;

  }

  const elements = Array.from(
    document.querySelectorAll("[data-translate]")
  );

  const texts = elements.map((el) =>
    originals.get(el) || el.innerText.trim()
  );

  const toFetch = [];

  texts.forEach((text) => {

    const key = `${tgtLang}|${text}`;

    if (!cache[key] && text.length > 0) {

      toFetch.push(text);

    }

  });

  /* -------- SMALL BATCHES -------- */

  for (let i = 0; i < toFetch.length; i += 5) {

    const batch = toFetch.slice(i, i + 5);

    const translations = await translateBatch(batch, tgtLang);

    translations.forEach((translation, idx) => {

      const originalText = batch[idx];

      cache[`${tgtLang}|${originalText}`] = translation;

    });

  }

  /* -------- UPDATE UI -------- */

  elements.forEach((el, i) => {

    const key = `${tgtLang}|${texts[i]}`;

    if (cache[key]) {

      el.innerText = cache[key];

    }

  });

}

function buildSwitcher() {

  const container = document.getElementById(
    "vak-lang-switcher"
  );

  if (!container) return;

  container.style.cssText = `
    display:inline-flex;
    align-items:center;
    gap:6px;
    font-family:sans-serif;
    font-size:14px;
  `;

  const globe = document.createElement("span");

  globe.textContent = "🌐";

  globe.style.fontSize = "18px";

  const select = document.createElement("select");

  select.style.cssText = `
    padding:6px 10px;
    border:1px solid #ccc;
    border-radius:6px;
    background:#fff;
    font-size:14px;
    cursor:pointer;
  `;

  LANGUAGES.forEach(({ code, label, flag }) => {

    const opt = document.createElement("option");

    opt.value = code;

    opt.textContent = `${flag} ${label}`;

    if (code === SRC_LANG) {

      opt.selected = true;

    }

    select.appendChild(opt);

  });

  select.addEventListener("change", async (e) => {

    select.disabled = true;

    select.style.opacity = "0.6";

    await translatePage(e.target.value);

    select.disabled = false;

    select.style.opacity = "1";

    localStorage.setItem(
      "vak_lang",
      e.target.value
    );

  });

  container.appendChild(globe);

  container.appendChild(select);

  const saved = localStorage.getItem("vak_lang");

  if (saved && saved !== SRC_LANG) {

    select.value = saved;

    translatePage(saved);

  }

}

if (document.readyState === "loading") {

  document.addEventListener(
    "DOMContentLoaded",
    () => {

      saveOriginals();

      buildSwitcher();

    }
  );

}

else {

  saveOriginals();

  buildSwitcher();

}