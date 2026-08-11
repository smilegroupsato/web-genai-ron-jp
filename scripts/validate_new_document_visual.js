#!/usr/bin/env node
/**
 * Validate desktop/mobile rendering for a new-document candidate.
 *
 * ページ作成日時：2026-08-11 15:35 JST
 * 最終更新日時：2026-08-11 15:35 JST
 */

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const baseUrl = process.env.NEW_DOCUMENT_PREVIEW_BASE_URL || "http://127.0.0.1:8765";
const route = process.env.NEW_DOCUMENT_PREVIEW_ROUTE || "/_new_document_candidate/fixtures/v2-publication-lane-test/";
const outputDir = process.env.NEW_DOCUMENT_VISUAL_QA_OUTPUT || "_new_document_visual_qa";
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
      const page = await browser.newPage({ viewport: { width: item.width, height: item.height } });
      const consoleErrors = [];
      page.on("console", (message) => {
        if (message.type() === "error") consoleErrors.push(message.text());
      });
      await page.goto(new URL(route, baseUrl).toString(), { waitUntil: "networkidle" });
      const metrics = await page.evaluate(() => ({
        title: document.title,
        h1: document.querySelector("h1")?.textContent?.trim() || "",
        hasHeader: Boolean(document.querySelector(".series-header")),
        hasPreferences: Boolean(document.querySelector(".reading-preferences")),
        hasHero: Boolean(document.querySelector(".series-hero")),
        hasArticle: Boolean(document.querySelector("article.note-box")),
        hasFooter: Boolean(document.querySelector(".series-footer")),
        headings: document.querySelectorAll("article.note-box h2").length,
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));
      const errors = [];
      if (!metrics.title || !metrics.h1) errors.push("title or h1 is missing");
      for (const key of ["hasHeader", "hasPreferences", "hasHero", "hasArticle", "hasFooter"]) {
        if (!metrics[key]) errors.push(`required region is missing: ${key}`);
      }
      if (metrics.headings < 1) errors.push("no article h2 found");
      if (metrics.scrollWidth > metrics.clientWidth) {
        errors.push(`horizontal overflow: ${metrics.scrollWidth} > ${metrics.clientWidth}`);
      }
      errors.push(...consoleErrors.map((value) => `console: ${value}`));
      const screenshot = path.join(outputDir, `${item.name}.png`);
      await page.screenshot({ path: screenshot, fullPage: true });
      report.push({ case: item.name, route, metrics, errors, screenshot });
      await page.close();
      if (errors.length) throw new Error(`${item.name}: ${errors.join("; ")}`);
    }
  } finally {
    await browser.close();
    fs.writeFileSync(path.join(outputDir, "report.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8");
  }
  console.log(`new-document visual QA: OK (${cases.length} cases)`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
