# 考试系统帮助页截图增强方案

> **Spec version:** 1.0
> **Date:** 2026-04-04
> **Status:** Approved

## 1. 目标

将 `exam-system-help.html` 的"流程控制详解"章节从纯文字升级为图文并茂的详细步骤指南，每个考试步骤配有 Playwright 自动截图，文档结构调整为步骤卡片式布局。

## 2. 截图清单（共 9 张）

截图保存路径：`docs/images/exam-system/`

| # | 文件名 | 截取时机 | 说明 |
|---|--------|----------|------|
| 1 | `step1-intro-zh.png` | 步骤1 中文自我介绍 | 左侧流程面板高亮当前步骤 |
| 2 | `step2-intro-en.png` | 步骤2 英文自我介绍 | 高亮英文自我介绍步骤 |
| 3 | `step3-translation-start.png` | 步骤3 未抽题 | 显示抽题按钮和空白题目区 |
| 4 | `step3-translation-done.png` | 步骤3 抽题后 | 显示英文翻译题目内容 |
| 5 | `step4-professional-start.png` | 步骤4 未抽题 | 显示专业题抽题状态 |
| 6 | `step4-professional-done.png` | 步骤4 抽题后 | 显示专业题目（含图片） |
| 7 | `step5-qa.png` | 步骤5 综合问答 | 显示综合问答说明 |
| 8 | `step6-end.png` | 步骤6 考试结束 | 显示完成状态 |
| 9 | `shortcuts-panel.png` | 任意步骤 | 快捷键面板截图 |

## 3. Playwright 脚本逻辑

**脚本路径：** `docs/scripts/screenshot-exam-steps.js`

**前置条件：** 后端服务运行于 `http://localhost:5000`

**执行步骤：**
1. 启动 chromium（headless: false，方便人工介入）
2. 访问 `http://localhost:5000/`
3. 若显示登录页 → 截图 `login.png` → 执行登录
4. 进入系统后，等待左侧流程面板加载
5. 按顺序操作并截图：
   - 当前默认为步骤1 → 截图 `step1-intro-zh.png`
   - 点击右侧"下一步" → 等待步骤切换 → 截图 `step2-intro-en.png`
   - 点击右侧"下一步" → 进入步骤3 → 截图 `step3-translation-start.png`
   - 点击"抽题"按钮 → 等待题目加载 → 截图 `step3-translation-done.png`
   - 点击右侧"下一步" → 进入步骤4 → 截图 `step4-professional-start.png`
   - 点击"抽题"按钮 → 等待题目+图片加载 → 截图 `step4-professional-done.png`
   - 点击右侧"下一步" → 进入步骤5 → 截图 `step5-qa.png`
   - 点击右侧"下一步" → 进入步骤6 → 截图 `step6-end.png`
6. 打开快捷键说明（如果有） → 截图 `shortcuts-panel.png`
7. 所有图片保存到 `docs/images/exam-system/`
8. 关闭浏览器

**关键等待策略：**
- 步骤切换后等待 `.step-active` 类出现
- 抽题后等待 `.question-content` 或 `.question-text` 出现
- 每步切换后 `page.waitForTimeout(500)` 确认动画完成

## 4. 文档结构调整

### 4.1 侧边栏导航更新

移除 `#modules`，替换为 6 个步骤锚点：

```html
<a href="#step1"><svg ...>中文自我介绍</a>
<a href="#step2"><svg ...>英文自我介绍</a>
<a href="#step3"><svg ...>英文翻译</a>
<a href="#step4"><svg ...>专业问题</a>
<a href="#step5"><svg ...>综合问答</a>
<a href="#step6"><svg ...>考试结束</a>
```

### 4.2 内容区结构调整

将现有 `#flow > .section-card-body` 内容替换为：

```
#flow 流程控制详解
  ├── 步骤1（#step1）
  │   ├── screenshot: step1-intro-zh.png
  │   ├── 操作指引卡片
  │   └── 计时说明
  ├── 步骤2（#step2）
  │   ├── screenshot: step2-intro-en.png
  │   └── ...
  ├── 步骤3（#step3）
  │   ├── screenshot: step3-translation-start.png
  │   ├── screenshot: step3-translation-done.png
  │   └── 抽题流程指引
  ├── 步骤4（#step4）
  │   ├── screenshot: step4-professional-start.png
  │   ├── screenshot: step4-professional-done.png
  │   └── 专业题说明
  ├── 步骤5（#step5）
  │   ├── screenshot: step5-qa.png
  │   └── 综合问答说明
  └── 步骤6（#step6）
      ├── screenshot: step6-end.png
      └── 结束说明
```

### 4.3 每个步骤的 HTML 结构

```html
<div class="section-card" id="step1">
  <div class="section-card-header">
    <div class="section-card-icon section-card-icon-primary">...</div>
    <h2 class="section-card-title">步骤 1：中文自我介绍</h2>
  </div>
  <div class="section-card-body">
    <div class="screenshot-wrap">
      <img src="../images/exam-system/step1-intro-zh.png" alt="步骤1 中文自我介绍界面">
      <p class="screenshot-caption">图 X：中文自我介绍界面</p>
    </div>
    <div class="step-guide">
      <div class="step-meta">
        <span class="step-duration">⏱ 2 分钟</span>
        <span class="step-type">自我介绍</span>
      </div>
      <h3>考官操作流程</h3>
      <ol>
        <li>确认考生就位后，点击<strong>开始</strong>按钮启动计时</li>
        <li>计时开始后，考生进行自我介绍</li>
        <li>如需暂停，点击<strong>暂停</strong>按钮</li>
        <li>时间到达或考生完成时，点击<strong>下一步</strong>进入下一环节</li>
      </ol>
    </div>
  </div>
</div>
```

## 5. 新增 CSS 规则

```css
.step-guide {
  margin-top: 20px;
  padding: 16px;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}
.step-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}
.step-duration {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
}
.step-type {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-primary);
}
.step-guide h3 {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 8px;
}
.step-guide ol {
  padding-left: 20px;
}
.step-guide li {
  font-size: 0.8125rem;
  line-height: 1.7;
  color: var(--color-text-secondary);
}
```

## 6. 依赖确认

- 后端服务运行：`http://localhost:5000`
- Playwright 已安装：`npx playwright --version`
- 截图输出目录：`docs/images/exam-system/`（需创建）
- 截图脚本：`docs/scripts/screenshot-exam-steps.js`（需创建）

## 7. 文件变更清单

| 操作 | 文件路径 |
|------|----------|
| 创建 | `docs/images/exam-system/`（目录） |
| 创建 | `docs/scripts/screenshot-exam-steps.js` |
| 修改 | `docs/exam-system-help.html` |
| 创建 | 9 张截图文件 |
