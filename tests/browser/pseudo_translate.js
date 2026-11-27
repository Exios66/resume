// Simulated in-place page translation for layout tests; not a real translator.
//
// Chrome, Edge and Safari translate a page by replacing its text nodes in place and
// skipping anything inside translate="no". This does the same with deterministic
// pseudo-text that keeps each language's shape: German runs about 35% longer and
// joins words into long compounds, French and Spanish run about 20-25% longer,
// Chinese is about half as long with no spaces, and Arabic is right to left.
// Interface labels use real translations. Numbers stay as they are, as translators
// keep them. Chrome also tags the root element: lang and translated-ltr/-rtl.
//
// Usage: pass the file to page.add_init_script or page.evaluate, then call
// window.pseudoTranslate("de") and read the returned summary.
(() => {
  const LABELS = {
    de: { Home: "Startseite", About: "Über mich", Projects: "Projekte", Research: "Forschung", Writing: "Veröffentlichungen", "Résumé": "Lebenslauf", Search: "Suchen", Copy: "Kopieren", Copied: "Kopiert" },
    fr: { Home: "Accueil", About: "À propos", Projects: "Projets", Research: "Recherche", Writing: "Écrits", "Résumé": "Curriculum vitæ", Search: "Rechercher", Copy: "Copier", Copied: "Copié" },
    es: { Home: "Inicio", About: "Acerca de mí", Projects: "Proyectos", Research: "Investigación", Writing: "Escritos", "Résumé": "Currículum", Search: "Buscar", Copy: "Copiar", Copied: "Copiado" },
    zh: { Home: "首页", About: "关于", Projects: "项目", Research: "研究", Writing: "写作", "Résumé": "简历", Search: "搜索", Copy: "复制", Copied: "已复制" },
    ar: { Home: "الرئيسية", About: "نبذة عني", Projects: "المشاريع", Research: "البحث", Writing: "الكتابات", "Résumé": "السيرة الذاتية", Search: "بحث", Copy: "نسخ", Copied: "تم النسخ" },
  };
  const ALPHABET = {
    de: "abcdeefghiklmnnorssttuäöüß",
    fr: "aabcdeeéèfgilmnoorsstuùàç",
    es: "aabcdeefgilmnñoorsstuáéíó",
    zh: "的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处理府研",
    ar: "ابتثجحخدذرزسشصضطظعغفقكلمنهوي",
  };
  const EXPAND = { de: 1.35, fr: 1.2, es: 1.25, zh: 0.5, ar: 1.1 };
  const SKIP = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE", "TEXTAREA"]);

  function hash(text) {
    let h = 2166136261;
    for (let i = 0; i < text.length; i++) { h ^= text.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  }
  function pseudoWord(word, lang, seed) {
    const letters = ALPHABET[lang];
    const n = Math.max(1, Math.round(word.length * EXPAND[lang]));
    let out = "";
    for (let i = 0; i < n; i++) out += letters[(seed + i * 7 + word.charCodeAt(i % word.length)) % letters.length];
    return word[0] === word[0].toUpperCase() && lang !== "zh" && lang !== "ar" ? out[0].toUpperCase() + out.slice(1) : out;
  }
  function translateText(text, lang) {
    const trimmed = text.trim();
    if (LABELS[lang][trimmed]) return text.replace(trimmed, LABELS[lang][trimmed]);
    let joined = 0;
    const words = text.split(/(\s+)/);
    return words.map((part, i) => {
      if (!/\p{L}/u.test(part)) return part;
      return part.replace(/\p{L}+/gu, (word) => {
        const seed = hash(word);
        const out = pseudoWord(word, lang, seed);
        // German compounds: about one long word in six absorbs the next one.
        if (lang === "de" && seed % 6 === 0 && words[i + 1] && /^\s+$/.test(words[i + 1]) && words[i + 2] && /^\p{L}/u.test(words[i + 2])) {
          words[i + 1] = ""; joined++;
        }
        return out;
      });
    }).join("").replace(/\s+/g, (space) => (lang === "zh" && !/\n/.test(space) ? "" : space));
  }
  window.pseudoTranslate = function (lang) {
    if (!LABELS[lang]) throw new Error("unknown language " + lang);
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent || SKIP.has(parent.tagName) || parent.closest('[translate="no"]')) return NodeFilter.FILTER_REJECT;
        return /\p{L}/u.test(node.data) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      },
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => { node.data = translateText(node.data, lang); });
    // Translators also translate placeholder text, which sets a field's width.
    document.querySelectorAll("[placeholder]").forEach((field) => {
      if (!field.closest('[translate="no"]')) field.placeholder = translateText(field.placeholder, lang);
    });
    const root = document.documentElement;
    root.lang = lang;
    root.classList.add(lang === "ar" ? "translated-rtl" : "translated-ltr");
    return { lang, translated: nodes.length, kept: document.querySelectorAll('[translate="no"]').length };
  };
})();
