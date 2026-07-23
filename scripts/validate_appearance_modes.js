#!/usr/bin/env node
/**
 * Validate structured publishing appearance modes.
 *
 * ページ作成日時：2026-07-23 12:46 JST
 * 最終更新日時：2026-07-23 12:46 JST
 *
 * This script is validation-only. It opens generated structured previews through
 * a local HTTP server and verifies that Paper / Reading / Archive modes keep
 * basic article surfaces readable without page-wide horizontal overflow.
 */

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const baseUrl = process.env.PREVIEW_BASE_URL || "http://127.0.0.1:8765";
const outputRoot = path.resolve(
  process.env.APPEARANCE_QA_OUTPUT || "_appearance_visual_qa"
);

const cases = [
  {
    id: "04-desktop",
    route:
      "/_structured_build_preview_ci/series/genai-shikumi-deep-dive/04-tool-execution-loop/",
    width: 1440,
    height: 1000,
  },
  {
    id: "07-desktop",
    route:
      "/_structured_build_preview_ci/series/genai-shikumi-deep-dive/07-agentic-loop/",
    width: 1440,
    height: 1000,
  },
  {
    id: "07-mobile",
    route:
      "/_structured_build_preview_ci/series/genai-shikumi-deep-dive/07-agentic-loop/",
    width: 390,
    height: 844,
  },
];

const modes = [
  { label: "Paper", value: "paper" },
  { label: "Reading", value: "reading" },
  { label: "Archive", value: "archive" },
];

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

async function collectAppearanceMetrics(page, mode) {
  return page.evaluate(async ({ mode }) => {
    const parseRgb = (input) => {
      if (!input || input === "transparent") return null;
      const match = input.match(/rgba?\(([^)]+)\)/i);
      if (!match) return null;
      const parts = match[1]
        .split(",")
        .map((part) => part.trim())
        .map((part) => Number.parseFloat(part));
      if (parts.length < 3 || parts.some((part) => Number.isNaN(part))) return null;
      return {
        r: parts[0],
        g: parts[1],
        b: parts[2],
        a: Number.isFinite(parts[3]) ? parts[3] : 1,
        raw: input,
      };
    };

    const composite = (top, bottom) => {
      if (!top) return bottom;
      if (!bottom) return top;
      const alpha = Math.max(0, Math.min(1, top.a));
      return {
        r: top.r * alpha + bottom.r * (1 - alpha),
        g: top.g * alpha + bottom.g * (1 - alpha),
        b: top.b * alpha + bottom.b * (1 - alpha),
        a: 1,
        raw: `${top.raw} over ${bottom.raw || "ancestor"}`,
      };
    };

    const luminance = (rgb) => {
      if (!rgb) return null;
      const convert = (value) => {
        const channel = value / 255;
        return channel <= 0.03928
          ? channel / 12.92
          : Math.pow((channel + 0.055) / 1.055, 2.4);
      };
      return 0.2126 * convert(rgb.r) + 0.7152 * convert(rgb.g) + 0.0722 * convert(rgb.b);
    };

    const contrastRatio = (fg, bg) => {
      const fgLum = luminance(fg);
      const bgLum = luminance(bg);
      if (!Number.isFinite(fgLum) || !Number.isFinite(bgLum)) return null;
      const light = Math.max(fgLum, bgLum);
      const dark = Math.min(fgLum, bgLum);
      return (light + 0.05) / (dark + 0.05);
    };

    const effectiveBackground = (element) => {
      let current = element;
      let result = null;
      while (current) {
        const style = getComputedStyle(current);
        const bg = parseRgb(style.backgroundColor);
        if (bg && bg.a > 0) {
          result = result ? composite(result, bg) : bg;
          if (result.a >= 0.999) return result;
        }
        current = current.parentElement;
      }
      return result || { r: 255, g: 255, b: 255, a: 1, raw: "fallback white" };
    };

    const textColor = (element) => parseRgb(getComputedStyle(element).color);

    const modeButton = [...document.querySelectorAll(".appearance-switcher button")].find(
      (button) => button.textContent.trim().toLowerCase() === mode.label.toLowerCase()
    );
    if (!modeButton) {
      return { mode: mode.value, modeButtonFound: false, samples: [], overflow: [] };
    }

    modeButton.click();
    await new Promise((resolve) => requestAnimationFrame(resolve));
    await new Promise((resolve) => requestAnimationFrame(resolve));

    const sampleSelectors = [
      { kind: "pre", selector: "article.note-box pre", surface: true },
      { kind: "pre-code", selector: "article.note-box pre code", surface: false },
      { kind: "inline-code", selector: "article.note-box :not(pre) > code", surface: true },
      { kind: "table", selector: "article.note-box table", surface: true },
      { kind: "th", selector: "article.note-box th", surface: true },
      { kind: "td", selector: "article.note-box td", surface: true },
      { kind: "blockquote", selector: "article.note-box blockquote", surface: true },
      { kind: "annotation", selector: "article.note-box .annotation-accordion", surface: true },
      { kind: "toggle", selector: "article.note-box .notion-toggle", surface: true },
    ];

    const samples = sampleSelectors.flatMap((entry) =>
      [...document.querySelectorAll(entry.selector)].slice(0, 3).map((element) => {
        const fg = textColor(element);
        const bg = effectiveBackground(element);
        return {
          kind: entry.kind,
          selector: entry.selector,
          text: (element.textContent || "").trim().slice(0, 80),
          color: fg?.raw || null,
          background: bg?.raw || null,
          backgroundLuminance: luminance(bg),
          contrast: contrastRatio(fg, bg),
          surface: entry.surface,
        };
      })
    );

    const root = document.documentElement;
    const overflow = [...document.querySelectorAll("body *")]
      .map((element) => {
        const rect = element.getBoundingClientRect();
        return {
          tag: element.tagName,
          className: typeof element.className === "string" ? element.className : "",
          text: (element.textContent || "").trim().slice(0, 80),
          left: rect.left,
          right: rect.right,
          width: rect.width,
        };
      })
      .filter((entry) => entry.right > root.clientWidth + 1 || entry.left < -1)
      .slice(0, 20);

    return {
      mode: mode.value,
      modeButtonFound: true,
      rootAppearance: root.dataset.appearance || null,
      clientWidth: root.clientWidth,
      scrollWidth: root.scrollWidth,
      samples,
      overflow,
    };
  }, { mode });
}

function validateModeMetrics(caseId, metrics) {
  const errors = [];
  if (!metrics.modeButtonFound) {
    errors.push(`${caseId}/${metrics.mode}: appearance mode button missing`);
    return errors;
  }
  if (metrics.rootAppearance !== metrics.mode) {
    errors.push(
      `${caseId}/${metrics.mode}: root appearance mismatch: ${metrics.rootAppearance}`
    );
  }
  if (metrics.scrollWidth > metrics.clientWidth + 1) {
    errors.push(
      `${caseId}/${metrics.mode}: document horizontal overflow ${metrics.scrollWidth}px > ${metrics.clientWidth}px`
    );
  }

  const contrastFailures = metrics.samples.filter(
    (sample) => Number.isFinite(sample.contrast) && sample.contrast < 3.6
  );
  for (const sample of contrastFailures) {
    errors.push(
      `${caseId}/${metrics.mode}: low contrast on ${sample.kind}: ${sample.contrast.toFixed(2)}`
    );
  }

  if (metrics.mode === "reading") {
    const brightSurfaces = metrics.samples.filter(
      (sample) =>
        sample.surface &&
        ["pre", "inline-code", "table", "th", "td", "blockquote", "annotation", "toggle"].includes(sample.kind) &&
        Number.isFinite(sample.backgroundLuminance) &&
        sample.backgroundLuminance > 0.55
    );
    for (const sample of brightSurfaces) {
      errors.push(
        `${caseId}/reading: bright surface remains on ${sample.kind}: luminance=${sample.backgroundLuminance.toFixed(3)}`
      );
    }
  }

  return errors;
}

async function main() {
  ensureDir(outputRoot);
  const browser = await chromium.launch({ headless: true });
  const report = [];
  let failed = false;

  for (const testCase of cases) {
    const page = await browser.newPage({
      viewport: { width: testCase.width, height: testCase.height },
      deviceScaleFactor: 1,
    });

    const response = await page.goto(`${baseUrl}${testCase.route}`, {
      waitUntil: "networkidle",
      timeout: 30000,
    });
    if (!response || !response.ok()) {
      throw new Error(
        `${testCase.id}: preview request failed (${response ? response.status() : "no response"})`
      );
    }

    const modeReports = [];
    for (const mode of modes) {
      const metrics = await collectAppearanceMetrics(page, mode);
      const screenshot = path.join(outputRoot, `${testCase.id}-${mode.value}.png`);
      await page.screenshot({ path: screenshot, fullPage: true });
      const errors = validateModeMetrics(testCase.id, metrics);
      if (errors.length > 0) failed = true;
      modeReports.push({
        mode: mode.value,
        screenshot: path.relative(process.cwd(), screenshot),
        metrics,
        errors,
      });
    }

    report.push({ case: testCase, modes: modeReports });
    await page.close();
  }

  await browser.close();
  const reportPath = path.join(outputRoot, "report.json");
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n");

  for (const entry of report) {
    for (const mode of entry.modes) {
      const sampleCount = mode.metrics.samples?.length || 0;
      const minContrast = Math.min(
        ...mode.metrics.samples
          .map((sample) => sample.contrast)
          .filter((value) => Number.isFinite(value))
      );
      console.log(
        `${entry.case.id}/${mode.mode}: samples=${sampleCount} minContrast=${Number.isFinite(minContrast) ? minContrast.toFixed(2) : "n/a"} errors=${mode.errors.length}`
      );
      for (const error of mode.errors) console.error(`  ERROR: ${error}`);
    }
  }

  if (failed) process.exit(1);
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
