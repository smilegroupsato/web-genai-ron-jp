#!/usr/bin/env node
/**
 * Validate desktop/mobile rendering for one promoted research note.
 *
 * ページ作成日時：2026-08-04 16:34 JST
 * 最終更新日時：2026-08-04 16:36 JST
 */

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const baseUrl = process.env.NOTES_PREVIEW_BASE_URL || "http://127.0.0.1:8765";
const route = process.env.NOTES_PREVIEW_ROUTE || "/notes/tool-discovery-layer/";
const outputDir = process.env.NOTES_VISUAL_QA_OUTPUT || "_notes_visual_qa";

const cases = [
  { name: "desktop", width: 1440, height: 1000 },
  { name: "mobile", width: 390, height: 844 },
];

async function main() {
  fs.mkdirSync(outputDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const report = [];

  try {
    for (const item of cases) {
      const page = await browser.newPage({
        viewport: { width: item.width, height: item.height },
      });
      const consoleErrors = [];
      page.on("console", (message) => {
        if (message.type() === "error") consoleErrors.push(message.text());
      });

      await page.goto(new URL(route, baseUrl).toString(), {
        waitUntil: "networkidle",
      });
      const metrics = await page.evaluate(() => ({
        title: document.title,
        h1: document.querySelector("h1")?.textContent?.trim() || "",
        hasHero: Boolean(document.querySelector(".note-hero")),
        hasSidebar: Boolean(document.querySelector(".note-sidebar")),
        hasArticle: Boolean(document.querySelector(".note-content")),
        hasFooter: Boolean(document.querySelector(".note-footer")),
        sections: document.querySelectorAll(".note-section").length,
        sidebarLinks: document.querySelectorAll(".note-sidebar a").length,
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));

      const errors = [];
      if (!metrics.title || !metrics.h1) errors.push("title or h1 is missing");
      for (const key of ["hasHero", "hasSidebar", "hasArticle", "hasFooter"]) {
        if (!metrics[key]) errors.push(`required region is missing: ${key}`);
      }
      if (metrics.sections < 1) errors.push("no note sections found");
      if (metrics.sidebarLinks < 1) errors.push("no sidebar links found");
      if (metrics.scrollWidth > metrics.clientWidth) {
        errors.push(
          `horizontal overflow: ${metrics.scrollWidth} > ${metrics.clientWidth}`
        );
      }
      errors.push(...consoleErrors.map((value) => `console: ${value}`));

      const screenshot = path.join(outputDir, `${item.name}.png`);
      await page.screenshot({ path: screenshot, fullPage: true });
      report.push({ case: item.name, route, metrics, errors, screenshot });
      await page.close();

      if (errors.length) {
        throw new Error(`${item.name}: ${errors.join("; ")}`);
      }
    }
  } finally {
    await browser.close();
    fs.writeFileSync(
      path.join(outputDir, "report.json"),
      `${JSON.stringify(report, null, 2)}\n`,
      "utf8"
    );
  }

  console.log(`notes visual QA: OK (${cases.length} cases)`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
