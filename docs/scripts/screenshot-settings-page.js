const { chromium } = require('playwright');
const path = require('path');

async function main() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  page.setViewportSize({ width: 1440, height: 900 });

  try {
    console.log('访问 http://localhost:5000/settings');
    await page.goto('http://localhost:5000/settings', { waitUntil: 'networkidle', timeout: 10000 });
    await page.waitForTimeout(1500);

    const outputPath = path.join(__dirname, '..', 'exam-settings-main.png');
    await page.screenshot({ path: outputPath, fullPage: false });
    console.log('截图已保存:', outputPath);
  } catch (err) {
    console.error('截图失败:', err.message);
    await page.screenshot({ path: path.join(__dirname, '..', 'exam-settings-error.png'), fullPage: false });
  } finally {
    await browser.close();
  }
}

main();