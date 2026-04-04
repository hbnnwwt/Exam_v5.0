# 考试系统帮助页截图增强实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 exam-system-help.html 升级为图文并茂的步骤卡片式帮助文档，配合 Playwright 自动截图

**Architecture:** Playwright Node.js 脚本驱动浏览器截图；HTML 文档重写为 6 个独立步骤卡片；CSS 新增 step-guide 样式；侧边栏导航更新锚点

**Tech Stack:** Node.js + Playwright, HTML/CSS

---

## 文件结构

```
docs/
  images/exam-system/          # 截图输出目录
    step1-intro-zh.png
    step2-intro-en.png
    step3-translation-start.png
    step3-translation-done.png
    step4-professional-start.png
    step4-professional-done.png
    step5-qa.png
    step6-end.png
    shortcuts-panel.png
  scripts/
    screenshot-exam-steps.js  # Playwright 截图脚本
  css/
    help-docs.css             # 新增 step-guide CSS（追加）
  exam-system-help.html        # 重写流程控制章节
```

---

## Task 1: 创建目录结构和 Playwright 截图脚本

**文件:**
- 创建: `docs/images/exam-system/`（目录）
- 创建: `docs/scripts/screenshot-exam-steps.js`

**ExamView.vue 关键选择器（参考）:**
- 开始考试按钮: `button.load-btn` 或 `text=开始考试`
- 左侧流程列表: `.step-list`
- 当前步骤: `.step-item.active`
- 步骤名称: `.step-item .step-name`（步骤1=中文自我介绍, 步骤2=英文自我介绍, 步骤3=英文翻译, 步骤4=专业问题, 步骤5=综合问答, 步骤6=考试结束）
- 下一步按钮: `.step-controls button` 或 `text=下一步 ▶`
- 抽题按钮: `button:has-text("抽题")`
- 快捷键面板: `.shortcuts-panel` 或 `text=快捷键`

- [ ] **Step 1: 创建截图脚本**

```javascript
// docs/scripts/screenshot-exam-steps.js
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUTPUT_DIR = path.join(__dirname, '..', 'images', 'exam-system');
const BASE_URL = 'http://localhost:5000/';
const IMAGES = {
  'step1-intro-zh.png': '步骤1-中文自我介绍-初始',
  'step2-intro-en.png': '步骤2-英文自我介绍',
  'step3-translation-start.png': '步骤3-英文翻译-抽题前',
  'step3-translation-done.png': '步骤3-英文翻译-抽题后',
  'step4-professional-start.png': '步骤4-专业问题-抽题前',
  'step4-professional-done.png': '步骤4-专业问题-抽题后',
  'step5-qa.png': '步骤5-综合问答',
  'step6-end.png': '步骤6-考试结束',
  'shortcuts-panel.png': '快捷键面板',
};

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
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });

    // 2. 等待并点击"开始考试"按钮
    const startBtn = page.locator('button.load-btn, text=开始考试').first();
    await startBtn.waitFor({ timeout: 5000 });
    await startBtn.click();
    console.log('已点击"开始考试"');
    await page.waitForTimeout(1000);

    // 3. 截图 step1
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'step1-intro-zh.png'), fullPage: false });
    console.log('截图: step1-intro-zh.png');

    // 4. 点击"下一步"进入步骤2
    const nextBtn = page.locator('.step-controls button, text=下一步').first();
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
    await drawBtn.click();
    await page.waitForTimeout(1500); // 等待题目加载
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

    console.log('\\n所有截图完成！输出目录:', OUTPUT_DIR);
  } catch (err) {
    console.error('脚本执行出错:', err.message);
    // 出错时也尝试截取当前页面
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'error-screenshot.png'), fullPage: false });
  } finally {
    await browser.close();
  }
}

main();
```

- [ ] **Step 2: 验证 Playwright 可用**

Run: `npx playwright --version`
Expected: 输出 playwright 版本号（如 `1.x.x`）

- [ ] **Step 3: 提交**

```bash
git add docs/images/ docs/scripts/screenshot-exam-steps.js
git commit -m "feat: add playwright screenshot script for exam-system-help"
```

---

## Task 2: 运行截图脚本

**依赖:** Task 1 完成

**前提:** 后端服务必须运行于 `http://localhost:5000`

- [ ] **Step 1: 确认后端运行**

Run: `curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/`
Expected: `200`

- [ ] **Step 2: 运行截图脚本**

Run: `node docs/scripts/screenshot-exam-steps.js`
Expected: 控制台输出每张截图的保存信息，最终显示 `所有截图完成！`

- [ ] **Step 3: 验证截图数量**

Run: `ls docs/images/exam-system/*.png | wc -l`
Expected: `9`

- [ ] **Step 4: 检查截图尺寸（确认非空白）**

Run: `ls -lh docs/images/exam-system/`
Expected: 9 个文件，每个文件大小 > 10KB（非空白截图）

---

## Task 3: 添加 step-guide CSS 到 help-docs.css

**文件:**
- 修改: `docs/css/help-docs.css`（在文件末尾追加新样式）

- [ ] **Step 1: 追加 step-guide 样式到 help-docs.css 末尾**

在 `help-docs.css` 最后一行（`}` 结束后）追加：

```css

/* ============================================================
   9. Step Guide（步骤操作指引卡片）
   ============================================================ */
.step-guide {
  margin-top: 20px;
  padding: 16px 20px;
  background: var(--color-surface);
  border-radius: var(--radius);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow);
}

.step-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.step-duration {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
  background: var(--color-bg);
  padding: 3px 10px;
  border-radius: 100px;
  border: 1px solid var(--color-border);
}

.step-type {
  display: inline-flex;
  align-items: center;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-primary);
  background: rgba(79, 70, 229, 0.08);
  padding: 3px 10px;
  border-radius: 100px;
}

.step-guide h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

.step-guide ol {
  padding-left: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.step-guide li {
  font-size: 0.8125rem;
  line-height: 1.6;
  color: var(--color-text-secondary);
  padding-left: 20px;
  position: relative;
}

.step-guide li::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 9px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-primary);
  opacity: 0.5;
}

.step-guide li strong {
  color: var(--color-text);
  font-weight: 600;
}
```

- [ ] **Step 2: 提交**

```bash
git add docs/css/help-docs.css
git commit -m "docs: add step-guide CSS for exam-system-help step cards"
```

---

## Task 4: 重写 exam-system-help.html 流程控制章节

**文件:**
- 修改: `docs/exam-system-help.html`（重写 `#flow` 章节内容 + 更新侧边栏）

### 4.1 更新侧边栏导航

将侧边栏中 `<a href="#modules">` 相关行替换为 6 个步骤锚点：

- [ ] **Step 1: 替换侧边栏 #modules 为 #step1~#step6**

替换这段：
```html
<a href="#modules"><svg ...>功能模块</a>
```

替换为：
```html
<a href="#step1"><svg ...>步骤1：中文自我介绍</a>
<a href="#step2"><svg ...>步骤2：英文自我介绍</a>
<a href="#step3"><svg ...>步骤3：英文翻译</a>
<a href="#step4"><svg ...>步骤4：专业问题</a>
<a href="#step5"><svg ...>步骤5：综合问答</a>
<a href="#step6"><svg ...>步骤6：考试结束</a>
```

SVG 图标使用流程相关 SVG（如 polyline 或 steps 图标），每个步骤标题后面跟随图标表示类型：
- 步骤1、2（自我介绍）: 用户/人员图标
- 步骤3（翻译）: 语言/翻译图标
- 步骤4（专业）: 专业/学术图标
- 步骤5（问答）: 问答图标
- 步骤6（结束）: 完成/对勾图标

### 4.2 重写 #flow 流程控制章节

- [ ] **Step 2: 替换 `#flow` 的 `.section-card-body` 内容**

将现有 `#flow > .section-card-body` 内所有内容替换为 6 个独立的步骤卡片。

每个步骤的 HTML 结构如下（以步骤1为例）：

```html
<!-- 步骤 1：中文自我介绍 -->
<div class="section-card" id="step1">
  <div class="section-card-header">
    <div class="section-card-icon section-card-icon-primary">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
        <circle cx="12" cy="7" r="4"/>
      </svg>
    </div>
    <h2 class="section-card-title">步骤 1：中文自我介绍</h2>
  </div>
  <div class="section-card-body">
    <div class="screenshot-wrap">
      <img src="../images/exam-system/step1-intro-zh.png" alt="步骤1 中文自我介绍界面" loading="lazy">
      <p class="screenshot-caption">图 1：中文自我介绍 — 左侧流程面板高亮当前步骤</p>
    </div>
    <div class="step-guide">
      <div class="step-meta">
        <span class="step-duration">⏱ 2 分钟</span>
        <span class="step-type">自我介绍</span>
      </div>
      <h3>考官操作流程</h3>
      <ol>
        <li>点击<strong>开始考试</strong>按钮初始化考生会话</li>
        <li>系统自动进入步骤1，计时器归零</li>
        <li>点击<strong>开始</strong>按钮启动计时，考生进行自我介绍</li>
        <li>如需暂停，点击<strong>暂停</strong>按钮保留剩余时间</li>
        <li>时间到达或考生完成时，点击<strong>下一步 ▶</strong>进入下一环节</li>
      </ol>
    </div>
  </div>
</div>
```

**步骤2 英文自我介绍结构相同**，替换以下内容：
- id: `step2`
- 图标: 使用语言/英文相关 SVG
- 标题: `步骤 2：英文自我介绍`
- 时长: `⏱ 3 分钟`
- 截图: `step2-intro-en.png`
- 操作指引: 同上

**步骤3 英文翻译结构（含抽题前后两张截图）：**

```html
<!-- 步骤 3：英文翻译 -->
<div class="section-card" id="step3">
  <div class="section-card-header">
    <div class="section-card-icon section-card-icon-cyan2">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M5 8l6 6M4 14l6-6 2-2M2 5h12M7 2v3M22 22l-5-10-5 10M14 18h6"/>
      </svg>
    </div>
    <h2 class="section-card-title">步骤 3：英文翻译</h2>
  </div>
  <div class="section-card-body">
    <div class="screenshot-wrap">
      <img src="../images/exam-system/step3-translation-start.png" alt="步骤3 英文翻译-抽题前" loading="lazy">
      <p class="screenshot-caption">图 3a：英文翻译 — 点击"抽题"前的空白题目区</p>
    </div>
    <div class="screenshot-wrap">
      <img src="../images/exam-system/step3-translation-done.png" alt="步骤3 英文翻译-抽题后" loading="lazy">
      <p class="screenshot-caption">图 3b：英文翻译 — 抽题完成，题目已显示</p>
    </div>
    <div class="step-guide">
      <div class="step-meta">
        <span class="step-duration">⏱ 4 分钟</span>
        <span class="step-type">翻译题</span>
      </div>
      <h3>考官操作流程</h3>
      <ol>
        <li>进入步骤3后，点击<strong>抽题</strong>按钮从题库随机抽取一道翻译题</li>
        <li>题目抽取后不可更改，系统在题目下方显示题目内容</li>
        <li>点击<strong>开始</strong>按钮启动计时，考生进行翻译</li>
        <li>计时结束后或考生完成时，点击<strong>下一步 ▶</strong>进入专业问题</li>
      </ol>
    </div>
  </div>
</div>
```

**步骤4 专业问题结构（含抽题前后两张截图）：**

```html
<!-- 步骤 4：专业问题 -->
<div class="section-card" id="step4">
  <div class="section-card-header">
    <div class="section-card-icon section-card-icon-amber">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
      </svg>
    </div>
    <h2 class="section-card-title">步骤 4：专业问题</h2>
  </div>
  <div class="section-card-body">
    <div class="screenshot-wrap">
      <img src="../images/exam-system/step4-professional-start.png" alt="步骤4 专业问题-抽题前" loading="lazy">
      <p class="screenshot-caption">图 4a：专业问题 — 点击"抽题"前的状态</p>
    </div>
    <div class="screenshot-wrap">
      <img src="../images/exam-system/step4-professional-done.png" alt="步骤4 专业问题-抽题后" loading="lazy">
      <p class="screenshot-caption">图 4b：专业问题 — 抽题完成，题目（含图片）已显示</p>
    </div>
    <div class="step-guide">
      <div class="step-meta">
        <span class="step-duration">⏱ 5 分钟</span>
        <span class="step-type">专业题</span>
      </div>
      <h3>考官操作流程</h3>
      <ol>
        <li>进入步骤4后，点击<strong>抽题</strong>按钮从专业题库随机抽取一道专业问题</li>
        <li>专业题可能包含图片（如算法流程图、内存示意图等），图片会显示在题目下方</li>
        <li>点击<strong>开始</strong>按钮启动计时，考生进行回答</li>
        <li>计时结束后或考生完成时，点击<strong>下一步 ▶</strong>进入综合问答</li>
      </ol>
    </div>
  </div>
</div>
```

**步骤5 综合问答结构：**

```html
<!-- 步骤 5：综合问答 -->
<div class="section-card" id="step5">
  <div class="section-card-header">
    <div class="section-card-icon section-card-icon-green">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    </div>
    <h2 class="section-card-title">步骤 5：综合问答</h2>
  </div>
  <div class="section-card-body">
    <div class="screenshot-wrap">
      <img src="../images/exam-system/step5-qa.png" alt="步骤5 综合问答界面" loading="lazy">
      <p class="screenshot-caption">图 5：综合问答 — 考官自由提问环节</p>
    </div>
    <div class="step-guide">
      <div class="step-meta">
        <span class="step-duration">⏱ 9 分钟</span>
        <span class="step-type">综合问答</span>
      </div>
      <h3>考官操作流程</h3>
      <ol>
        <li>进入步骤5后，系统显示综合问答说明（如考官介绍、研究计划提问等）</li>
        <li>本环节<strong>无固定题目</strong>，由考官根据考生情况自由提问</li>
        <li>本环节<strong>无时间硬性限制</strong>，由考官自行掌握节奏</li>
        <li>问答结束后，点击<strong>下一步 ▶</strong>进入考试结束</li>
      </ol>
    </div>
  </div>
</div>
```

**步骤6 考试结束结构：**

```html
<!-- 步骤 6：考试结束 -->
<div class="section-card" id="step6">
  <div class="section-card-header">
    <div class="section-card-icon section-card-icon-blue">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="20 6 9 17 4 12"/>
      </svg>
    </div>
    <h2 class="section-card-title">步骤 6：考试结束</h2>
  </div>
  <div class="section-card-body">
    <div class="screenshot-wrap">
      <img src="../images/exam-system/step6-end.png" alt="步骤6 考试结束界面" loading="lazy">
      <p class="screenshot-caption">图 6：考试结束 — 考试流程全部完成</p>
    </div>
    <div class="step-guide">
      <div class="step-meta">
        <span class="step-duration">⏱ 即时</span>
        <span class="step-type">完成</span>
      </div>
      <h3>结束流程</h3>
      <ol>
        <li>点击<strong>下一步 ▶</strong>后，系统自动保存考生考试记录</li>
        <li>所有步骤状态更新为已完成，系统显示考试结束界面</li>
        <li>可点击<strong>开始考试</strong>为下一位考生初始化考试</li>
        <li>所有考试记录可在<strong>考试导出</strong>功能中查看和导出</li>
      </ol>
    </div>
  </div>
</div>
```

- [ ] **Step 3: 删除旧的 #flow 内容**

删除 `#flow .section-card-body` 中原有的：
- `h3.step-heading` 六步流程列表
- 左侧流程面板操作说明
- 右侧控制面板操作说明
- warning-box 注意事项

这些内容已被新的步骤卡片取代。

- [ ] **Step 4: 更新页面标题页的描述**

将页面标题描述从 "考试系统流程控制界面详解" 更新为包含步骤截图说明的内容（可保持现有描述不变）。

- [ ] **Step 5: 提交**

```bash
git add docs/exam-system-help.html
git commit -m "docs: rewrite exam-system-help flow section with step-by-step screenshots"
```

---

## Task 5: 整体验证

- [ ] **Step 1: 检查页面在浏览器中渲染**

Run: 启动前端开发服务器后访问 `http://localhost:5000/docs/exam-system-help.html`，验证：
1. 侧边栏显示 6 个步骤锚点链接
2. 滚动到每个步骤，截图正确显示
3. step-guide 样式正常渲染（卡片背景、标签、列表）
4. 无 404 资源错误（图片路径正确）

- [ ] **Step 2: 检查 `prefers-reduced-motion` 支持**

在 help-docs.css 中确认 `.step-guide` 的 transition/motion 被 `@media (prefers-reduced-motion: reduce)` 规则覆盖（如果页面已有此媒体查询，step-guide 无需额外处理）

---

## 依赖关系

```
Task 1 (Playwright脚本创建)
    ↓
Task 2 (运行脚本截图) ← 必须后端运行于 localhost:5000
    ↓
Task 3 (CSS样式)
    ↓
Task 4 (HTML重写) ← 依赖 Task 3 的 CSS
    ↓
Task 5 (验证)
```

---

## 验证命令汇总

```bash
# 验证 Playwright
npx playwright --version

# 验证后端
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/

# 验证截图数量
ls docs/images/exam-system/*.png | wc -l

# 验证截图大小
ls -lh docs/images/exam-system/
```
