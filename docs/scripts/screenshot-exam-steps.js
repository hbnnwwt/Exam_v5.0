// docs/scripts/screenshot-exam-steps.js
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUTPUT_DIR = path.join(__dirname, '..', 'images', 'exam-system');

async function main() {
  // 创建输出目录
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  page.setViewportSize({ width: 1440, height: 900 });

  try {
    // 1. 访问首页
    console.log('访问 http://localhost:5000/');
    await page.goto('http://localhost:5000/', { waitUntil: 'networkidle' });

    // 2. 点击"开始考试"按钮
    const startBtn = page.locator('button.load-btn, text=开始考试').first();
    await startBtn.waitFor({ timeout: 5000 });
    await startBtn.click();
    console.log('已点击"开始考试"');
    await page.waitForTimeout(1000);

    // 3. 截图 step1 - 中文自我介绍
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step1-intro-zh.png'), fullPage: false });
    console.log('截图: step1-intro-zh.png');

    // 4. 点击"下一步"进入步骤2
    const nextBtn = page.locator('text=下一步').first();
    await nextBtn.waitFor({ timeout: 5000 });
    await nextBtn.click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step2-intro-en.png'), fullPage: false });
    console.log('截图: step2-intro-en.png');

    // 5. 点击"下一步"进入步骤3（英文翻译）
    await nextBtn.click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step3-translation-start.png'), fullPage: false });
    console.log('截图: step3-translation-start.png');

    // 6. 点击"抽题"按钮
    const drawBtn = page.locator('button:has-text("抽题")').first();
    await drawBtn.waitFor({ timeout: 5000 });
    await drawBtn.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step3-translation-done.png'), fullPage: false });
    console.log('截图: step3-translation-done.png');

    // 7. 点击"下一步"进入步骤4（专业问题）
    await nextBtn.click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step4-professional-start.png'), fullPage: false });
    console.log('截图: step4-professional-start.png');

    // 8. 点击"抽题"按钮
    await drawBtn.click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step4-professional-done.png'), fullPage: false });
    console.log('截图: step4-professional-done.png');

    // 9. 点击"下一步"进入步骤5（综合问答）
    await nextBtn.click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step5-qa.png'), fullPage: false });
    console.log('截图: step5-qa.png');

    // 10. 点击"下一步"进入步骤6（考试结束）
    await nextBtn.click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step6-end.png'), fullPage: false });
    console.log('截图: step6-end.png');

    // 11. 尝试打开快捷键面板
    const shortcutsBtn = page.locator('text=快捷键').first();
    if (await shortcutsBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await shortcutsBtn.click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(OUTPUT_DIR, 'shortcuts-panel.png'), fullPage: false });
      console.log('截图: shortcuts-panel.png');
    } else {
      console.log('快捷键按钮未找到，跳过');
    }

    console.log('\n所有截图完成！输出目录:', OUTPUT_DIR);
  } catch (err) {
    console.error('脚本执行出错:', err.message);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'error-screenshot.png'), fullPage: false });
  } finally {
    await browser.close();
  }
}

main();