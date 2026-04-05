// docs/scripts/screenshot-editor.js
// 截取题库编辑器全部 13 张截图
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUT = path.join(__dirname, '..');
const BASE = 'http://localhost:5000';

if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

async function screenshot(page, filename) {
  const p = path.join(OUT, filename);
  await page.screenshot({ path: p, fullPage: false });
  const size = fs.statSync(p).size;
  console.log(`  [OK] ${filename} (${Math.round(size/1024)}KB)`);
}

async function waitModalOpen(page) {
  await page.waitForSelector('.modal', { timeout: 5000 });
  await page.waitForTimeout(400);
}

async function closeModal(page) {
  // 点击取消按钮或关闭按钮
  const closeBtn = page.locator('.modal .btn-cancel, .modal .modal-close').first();
  await closeBtn.click();
  await page.waitForSelector('.modal', { state: 'hidden', timeout: 5000 });
  await page.waitForTimeout(500);
}

async function main() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });

  try {
    // 1. 主界面
    console.log('1. 访问 /editor...');
    await page.goto(BASE + '/editor', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);
    await screenshot(page, 'database-editor-main.png');

    // 2. 搜索
    console.log('2. 搜索框输入"翻译"...');
    await page.locator('input[placeholder="搜索题目..."]').fill('翻译');
    await page.waitForTimeout(500);
    await screenshot(page, 'database-editor-search.png');
    await page.locator('input[placeholder="搜索题目..."]').clear();
    await page.waitForTimeout(300);

    // 3. 分页
    console.log('3. 分页截图...');
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(600);
    await screenshot(page, 'database-editor-pagination.png');

    // 4. 添加翻译题
    console.log('4. 添加翻译题对话框...');
    await page.locator('.add-btn').first().click();
    await waitModalOpen(page);
    await screenshot(page, 'database-editor-add-translation.png');

    // 5. 套题模式
    console.log('5. 套题模式（添加子题）...');
    await page.locator('.btn-add-sub-large').click();
    await page.waitForTimeout(500);
    await screenshot(page, 'database-editor-question-set.png');

    // 6. AI生成按钮
    console.log('6. AI生成按钮...');
    const aiBtn = page.locator('.ai-btn.ai-btn-primary').first();
    if (await aiBtn.isVisible().catch(() => false)) {
      await screenshot(page, 'database-editor-ai-generate.png');
    } else {
      console.log('  [SKIP] AI生成按钮不可见');
    }
    await closeModal(page);

    // 7. 专业题目tab
    console.log('7. 专业题目tab...');
    await page.locator('.tab-btn').filter({ hasText: '专业题目' }).click();
    await page.waitForTimeout(800);
    await screenshot(page, 'database-editor-professional.png');

    // 8. 添加专业题
    console.log('8. 添加专业题对话框...');
    await page.locator('.add-btn').first().click();
    await waitModalOpen(page);
    await screenshot(page, 'database-editor-add-professional.png');
    await closeModal(page);

    // 9. 科目管理tab
    console.log('9. 科目管理tab...');
    await page.locator('.tab-btn').filter({ hasText: '科目管理' }).click();
    await page.waitForTimeout(800);
    await screenshot(page, 'database-editor-subjects.png');

    // 10. 添加科目
    console.log('10. 添加科目对话框...');
    await page.locator('.add-btn').first().click();
    await page.waitForTimeout(500);
    await screenshot(page, 'database-editor-add-subject.png');
    await closeModal(page);

    // 11. 批量勾选
    console.log('11. 批量勾选...');
    await page.locator('.tab-btn').filter({ hasText: '翻译题目' }).click();
    await page.waitForTimeout(800);
    const checkboxes = page.locator('.question-checkbox');
    const cnt = await checkboxes.count();
    if (cnt >= 2) {
      await checkboxes.nth(0).check();
      await checkboxes.nth(1).check();
      await page.waitForTimeout(500);
      await screenshot(page, 'database-editor-batch-select.png');
      await checkboxes.nth(0).uncheck();
      await checkboxes.nth(1).uncheck();
    } else {
      console.log(`  [SKIP] 只有 ${cnt} 个题目`);
      await screenshot(page, 'database-editor-batch-select.png');
    }

    // 12. 批量导入
    console.log('12. 批量导入...');
    await page.locator('button').filter({ hasText: '批量导入' }).click();
    await page.waitForTimeout(600);
    await screenshot(page, 'database-editor-batch-import.png');
    await closeModal(page);

    // 13. AI批量添加
    console.log('13. AI批量添加...');
    await page.locator('button').filter({ hasText: 'AI批量添加' }).first().click();
    await page.waitForTimeout(600);
    await screenshot(page, 'database-editor-ai-batch.png');

    console.log('\n=== 全部截图完成 ===');
  } catch (err) {
    console.error('ERROR:', err.message);
    await page.screenshot({ path: path.join(OUT, 'error-final.png'), fullPage: false });
  } finally {
    await browser.close();
  }
}

main();
