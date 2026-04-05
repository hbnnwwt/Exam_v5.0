// docs/scripts/screenshot-exam-steps.js
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const http = require('http');

const OUTPUT_DIR = path.join(__dirname, '..', 'images', 'exam-system');

function postJSON(url) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const req = http.request({
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname,
      method: 'POST'
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    });
    req.on('error', reject);
    req.end();
  });
}

async function closeModalByX(page) {
  const closeBtn = page.locator('.modal-overlay button').filter({ hasText: '×' }).first();
  if (await closeBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
    await closeBtn.click();
    await page.waitForTimeout(500);
    return true;
  }
  return false;
}

async function main() {
  // 创建输出目录
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // 先重置后端状态，确保干净的开始
  try {
    await postJSON('http://localhost:5000/exam-api/reset');
    console.log('后端已重置');
  } catch (e) {
    console.warn('后端重置失败，继续执行:', e.message);
  }

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();
  page.setViewportSize({ width: 1440, height: 900 });

  try {
    // 1. 访问首页
    console.log('访问 http://localhost:5000/');
    await page.goto('http://localhost:5000/', { waitUntil: 'networkidle' });

    // 2. 点击"开始考试"按钮
    const startBtn = page.locator('button').filter({ hasText: '开始考试' }).first();
    await startBtn.waitFor({ timeout: 5000 });
    await startBtn.click();
    console.log('已点击"开始考试"');
    await page.waitForTimeout(1000);

    // 3. 截图 step1 - 中文自我介绍
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step1-intro-zh.png'), fullPage: false });
    console.log('截图: step1-intro-zh.png');

    // 4. 点击"下一步"进入步骤2
    const nextBtn = page.locator('button').filter({ hasText: '下一步' }).first();
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

    // 6. 点击"抽取翻译题目"按钮
    const drawBtn = page.locator('button').filter({ hasText: '抽取翻译题目' }).first();
    await drawBtn.waitFor({ timeout: 5000 });
    await drawBtn.click();
    await page.waitForTimeout(1500);

    // 7. 在弹出的模态框中点击"开始抽取"
    const startDrawBtn = page.locator('button').filter({ hasText: '开始抽取' }).first();
    await startDrawBtn.waitFor({ state: 'visible', timeout: 5000 });
    await startDrawBtn.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step3-translation-done.png'), fullPage: false });
    console.log('截图: step3-translation-done.png');

    // 8. 关闭模态框
    await closeModalByX(page);

    // 9. 点击"下一步"进入步骤4（专业问题）
    await nextBtn.click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step4-professional-start.png'), fullPage: false });
    console.log('截图: step4-professional-start.png');

    // 10. 点击"抽取专业题目"按钮
    const drawProfBtn = page.locator('button').filter({ hasText: '抽取专业题目' }).first();
    await drawProfBtn.waitFor({ timeout: 5000 });
    await drawProfBtn.click();
    await page.waitForTimeout(1000);

    // 11. 在科目选择模态框中选择第一个科目并确定
    // 模态框中有科目按钮如"C语言"，点击后再点确定
    const subjectBtn = page.locator('.modal-overlay button').filter({ hasText: 'C语言' }).first();
    if (await subjectBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await subjectBtn.click();
      await page.waitForTimeout(300);
    }
    const confirmBtn = page.locator('.modal-overlay button').filter({ hasText: '确定' }).first();
    if (await confirmBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await confirmBtn.click();
      await page.waitForTimeout(2000);
    }
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step4-professional-done.png'), fullPage: false });
    console.log('截图: step4-professional-done.png');

    // 12. 关闭可能残留的模态框
    await closeModalByX(page);

    // 13. 点击"下一步"进入步骤5（综合问答）
    await nextBtn.click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step5-qa.png'), fullPage: false });
    console.log('截图: step5-qa.png');

    // 14. 点击"下一步"进入步骤6（考试结束）
    await nextBtn.click();
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step6-end.png'), fullPage: false });
    console.log('截图: step6-end.png');

    // 15. 尝试打开快捷键面板
    const shortcutsBtn = page.locator('button').filter({ hasText: '快捷键' }).first();
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
