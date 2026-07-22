#!/usr/bin/env node
/**
 * Capture structured preview screenshots and fail on unexpected horizontal overflow.
 *
 * This script is validation-only. It reads generated previews through a local HTTP
 * server and never writes to site/.
 */

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const baseUrl = process.env.PREVIEW_BASE_URL || "http://127.0.0.1:8765";
const outputRoot = path.resolve(
  process.env.VISUAL_QA_OUTPUT || "_structured_visual_qa"
);

const cases = [
  {
    id: "default-desktop",
    route:
      "/_structured_build_preview_ci/series/genai-shikumi-deep-dive/04-tool-execution-loop/",
    width: 1440,
    height: 1000,
    expectedTheme: "default-academic",
  },
  {
    id: "default-mobile",
    route:
      "/_structured_build_preview_ci/series/genai-shikumi-deep-dive/04-tool-execution-loop/",
    width: 390,
    height: 844,
    expectedTheme: "default-academic",
  },
  {
    id: "library-desktop",
    route:
      "/_structured_library_preview_ci/series/genai-shikumi-deep-dive/04-tool-execution-loop/",
    width: 1440,
    height: 1000,
    expectedTheme: "library-university-humanities-summer",
  },
  {
    id: "library-mobile",
    route:
      "/_structured_library_preview_ci/series/genai-shikumi-deep-dive/04-tool-execution-loop/",
    width: 390,
    height: 844,
    expectedTheme: "library-university-humanities-summer",
  },
];

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
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

    const consoleMessages = [];
    page.on("console", (message) => {
      consoleMessages.push(`${message.type()}: ${message.text()}`);
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

    const metrics = await page.evaluate(() => {
      const root = document.documentElement;

      const hasScrollableAncestor = (element) => {
        let parent = element.parentElement;
        while (parent && parent !== document.body) {
          const style = getComputedStyle(parent);
          const overflowX = style.overflowX;
          if (
            (overflowX === "auto" || overflowX === "scroll") &&
            parent.scrollWidth > parent.clientWidth + 1
          ) {
            return true;
          }
          parent = parent.parentElement;
        }
        return false;
      };

      const overflow = [...document.querySelectorAll("body *")]
        .map((element) => {
          const rect = element.getBoundingClientRect();
          return {
            element,
            tag: element.tagName,
            className:
              typeof element.className === "string" ? element.className : "",
            text: (element.textContent || "").trim().slice(0, 100),
            left: rect.left,
            right: rect.right,
            width: rect.width,
          };
        })
        .filter(
          (entry) =>
            (entry.right > root.clientWidth + 1 || entry.left < -1) &&
            !hasScrollableAncestor(entry.element)
        )
        .slice(0, 30)
        .map(({ element, ...entry }) => entry);

      const rect = (selector) => {
        const element = document.querySelector(selector);
        if (!element) return null;
        const box = element.getBoundingClientRect();
        return {
          left: box.left,
          top: box.top,
          width: box.width,
          height: box.height,
        };
      };

      const switcher = document.querySelector(".appearance-switcher");
      const firstSwitcherButton = switcher?.querySelector("button") || null;
      const firstSwitcherButtonStyle = firstSwitcherButton
        ? getComputedStyle(firstSwitcherButton)
        : null;

      return {
        title: document.title,
        themeId: root.dataset.themeId || null,
        collectionId: root.dataset.themeCollection || null,
        baseTheme: root.dataset.themeBase || null,
        season: root.dataset.themeSeason || null,
        assetStatus: root.dataset.heroAssetStatus || null,
        productionEnabled: root.dataset.themeProductionEnabled || null,
        heroVariant:
          document.querySelector(".series-hero")?.dataset.heroVariant || null,
        textContrast:
          document.querySelector(".series-hero")?.dataset.textContrast || null,
        clientWidth: root.clientWidth,
        scrollWidth: root.scrollWidth,
        bodyScrollWidth: document.body.scrollWidth,
        header: rect(".series-header"),
        readingPreferences: rect("[data-reading-preferences]"),
        nav: rect(".series-nav"),
        hero: rect(".series-hero"),
        article: rect("article.note-box"),
        footer: rect(".series-footer"),
        h2Count: document.querySelectorAll("article.note-box h2").length,
        linkCount: document.querySelectorAll("a").length,
        appearanceButtonCount:
          document.querySelectorAll(".appearance-switcher button").length,
        appearanceInDedicatedSlot: Boolean(
          switcher?.closest("[data-reading-preferences-slot]")
        ),
        appearanceIsDirectBodyChild: Boolean(
          document.querySelector("body > .appearance-switcher")
        ),
        appearanceButtonStyle: firstSwitcherButtonStyle
          ? {
              borderRadius: firstSwitcherButtonStyle.borderRadius,
              fontFamily: firstSwitcherButtonStyle.fontFamily,
              minHeight: firstSwitcherButtonStyle.minHeight,
            }
          : null,
        overflow,
      };
    });

    const screenshot = path.join(outputRoot, `${testCase.id}.png`);
    await page.screenshot({ path: screenshot, fullPage: true });

    const errors = [];
    if (metrics.themeId !== testCase.expectedTheme) {
      errors.push(
        `theme mismatch: expected ${testCase.expectedTheme}, got ${metrics.themeId}`
      );
    }
    if (
      !metrics.header ||
      !metrics.readingPreferences ||
      !metrics.hero ||
      !metrics.article ||
      !metrics.footer
    ) {
      errors.push("required page region is missing");
    }
    if (metrics.appearanceButtonCount !== 3) {
      errors.push(
        `appearance control count mismatch: expected 3, got ${metrics.appearanceButtonCount}`
      );
    }
    if (!metrics.appearanceInDedicatedSlot) {
      errors.push("appearance switcher is not mounted in the dedicated slot");
    }
    if (metrics.appearanceIsDirectBodyChild) {
      errors.push("appearance switcher leaked as a direct child of body");
    }
    if (metrics.scrollWidth > metrics.clientWidth + 1) {
      errors.push(
        `document horizontal overflow: ${metrics.scrollWidth}px > ${metrics.clientWidth}px`
      );
    }
    if (metrics.overflow.length > 0) {
      errors.push(`uncontained overflowing elements: ${metrics.overflow.length}`);
    }

    if (errors.length > 0) failed = true;
    report.push({
      case: testCase,
      screenshot: path.relative(process.cwd(), screenshot),
      metrics,
      consoleMessages,
      errors,
    });

    await page.close();
  }

  await browser.close();
  const reportPath = path.join(outputRoot, "report.json");
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n");

  for (const entry of report) {
    console.log(
      `${entry.case.id}: theme=${entry.metrics.themeId} width=${entry.metrics.clientWidth}/${entry.metrics.scrollWidth} controls=${entry.metrics.appearanceButtonCount} errors=${entry.errors.length}`
    );
    for (const error of entry.errors) console.error(`  ERROR: ${error}`);
  }

  if (failed) process.exit(1);
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
