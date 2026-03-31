# 考生面试界面重新设计 - 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将考生面试界面从 Bootstrap 蓝色风格升级为"庄重面试风"，使用 Slate 深石板灰 + 金色强调色，提升专业形象

**Architecture:** 先更新全局 CSS 变量(主色彩、字体)，再更新 ExamView.vue 组件样式，最后添加过渡动画

**Tech Stack:** Vue 3, 纯 CSS (无 Tailwind)

---

## 实施文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/src/assets/css/main.css` | 修改 | 更新 CSS 变量系统 |
| `frontend/src/views/ExamView.vue` | 修改 | 更新组件样式 |

---

## Task 1: 更新全局 CSS 变量

**Files:**
- Modify: `frontend/src/assets/css/main.css:6-70`

> 此任务将主色调从 Bootstrap 蓝色 (#007bff) 更换为深石板灰 + 金色强调的庄重配色

- [ ] **Step 1: 备份并替换主色调变量**

将第 12-15 行:
```css
  /* 品牌色 */
  --color-primary: #007bff;
  --color-primary-hover: #0056b3;
  --color-primary-light: #e7f1ff;
  --color-primary-dark: #004085;
```

替换为:
```css
  /* 品牌色 - 庄重面试风 */
  --color-primary: #0f172a;        /* 深石板灰，替代蓝色 */
  --color-primary-hover: #1e293b;
  --color-primary-light: #f1f5f9;
  --color-primary-dark: #020617;

  /* 强调色 - 金色 */
  --color-accent: #d97706;
  --color-accent-hover: #b45309;
  --color-accent-light: #fef3c7;
```

- [ ] **Step 2: 替换成功色变量**

将第 18-20 行:
```css
  --color-success: #28a745;
  --color-success-hover: #218838;
  --color-success-light: #d4edda;
```

替换为:
```css
  --color-success: #059669;        /* 翡翠绿 */
  --color-success-hover: #047857;
  --color-success-light: #d1fae5;
```

- [ ] **Step 3: 验证变更**

运行 `git diff frontend/src/assets/css/main.css` 确认变量已更新

- [ ] **Step 4: Commit**

```bash
git add frontend/src/assets/css/main.css
git commit -m "feat: update CSS variables for solemn interview style

- Replace blue primary (#007bff) with slate-900 (#0f172a)
- Add amber accent (#d97706) for emphasis
- Update success color to emerald (#059669)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: 更新 ExamView.vue 样式

**Files:**
- Modify: `frontend/src/views/ExamView.vue:337-798`

> 此任务将 ExamView 组件从蓝色 Bootstrap 风格升级为庄重面试风

- [ ] **Step 1: 更新页面背景色**

在 `.exam-page` 样式块中 (第 342 行):
```css
.exam-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f8f9fa;  /* 旧背景 */
}
```

替换为:
```css
.exam-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f8fafc;  /* Slate-50 新背景 */
}
```

- [ ] **Step 2: 更新头部样式**

在 `.header` 样式块中:
```css
.header {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 15px 20px;
  flex-shrink: 0;
}
```

替换为:
```css
.header {
  background: #0f172a;  /* 深石板灰背景 */
  border-bottom: none;
  padding: 15px 20px;
  flex-shrink: 0;
}

.header-title {
  font-size: 1.8rem;
  color: #f8fafc;  /* 浅色标题 */
  margin: 0;
  font-family: var(--font-serif, "Noto Serif SC", serif);  /* 衬线字体 */
}
```

- [ ] **Step 3: 更新导航按钮样式**

在 `.nav-btn` 样式块中:
```css
.nav-btn {
  padding: 8px 16px;
  background: var(--primary-color, #007bff);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  transition: opacity 0.2s;
}
```

替换为:
```css
.nav-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  color: #f8fafc;
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}
```

- [ ] **Step 4: 更新流程步骤样式**

找到 `.step-item` 样式块，替换为:
```css
.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-item:hover {
  background: #f1f5f9;
}

.step-item.active {
  border-color: var(--color-accent, #d97706);
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  box-shadow: 0 0 20px rgba(217, 119, 6, 0.15);
}

.step-item.completed {
  background: #ecfdf5;
  border-color: var(--color-success, #059669);
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.step-item.active .step-number {
  background: var(--color-accent, #d97706);
  color: white;
}

.step-item.completed .step-number {
  background: var(--color-success, #059669);
  color: white;
}
```

- [ ] **Step 5: 更新开始考试卡片样式**

找到 `.student-input-area` 样式块，替换为:
```css
.student-input-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.start-card {
  background: white;
  border-radius: 16px;
  padding: 48px 64px;
  text-align: center;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--color-border, #e2e8f0);
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.start-card h2 {
  font-family: var(--font-serif, "Noto Serif SC", serif);
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary, #0f172a);
  margin-bottom: 12px;
}

.start-card .subtitle {
  color: var(--color-text-secondary, #475569);
  margin-bottom: 32px;
}
```

- [ ] **Step 6: 更新按钮样式**

找到 `.load-btn`/`.start-btn` 样式块:
```css
.load-btn {
  padding: 12px 30px;
  background: var(--primary-color, #007bff);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.load-btn:hover {
  background: #0056b3;
}
```

替换为:
```css
.start-btn, .load-btn {
  padding: 14px 48px;
  background: var(--color-primary, #0f172a);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.start-btn:hover, .load-btn:hover {
  background: var(--color-primary-hover, #1e293b);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.2);
}

.start-btn:active, .load-btn:active {
  transform: scale(0.98);
}
```

- [ ] **Step 7: 更新控制按钮样式**

找到 `.control-btn` 样式块，添加触觉反馈:
```css
.control-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-btn:active:not(:disabled) {
  transform: translateY(-1px);
}
```

- [ ] **Step 8: 更新面板折叠动画**

找到 `.left-panel`/`.right-panel` ��式块:
```css
.left-panel,
.right-panel {
  width: clamp(180px, 20vw, 250px);
  min-width: 0;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  position: relative;
  transition: width 0.3s ease;
}
```

替换为:
```css
.left-panel,
.right-panel {
  width: clamp(180px, 20vw, 250px);
  min-width: 0;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  position: relative;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.3s ease;
}
```

- [ ] **Step 9: 更新状态徽章样式**

替换 `.status-badge` 样式:
```css
.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.status-badge.ready {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.in_progress {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}
```

- [ ] **Step 10: Commit**

```bash
git add frontend/src/views/ExamView.vue
git commit -m "feat: redesign exam view with solemn interview style

- Dark slate header with serif title
- Amber accent for active steps
- Formal start card with fade-in animation
- Tactile button feedback
- Smooth panel transitions
- Updated status badges

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: 验证与测试

**Files:**
- Test: `frontend/src/views/ExamView.vue`

- [ ] **Step 1: 启动开发服务器测试**

```bash
cd frontend && npm run dev
```

访问 http://localhost:3000 检查:
- [ ] 头部是否为深石板灰背景 + 浅色标题
- [ ] 开始考试卡片是否有淡入动画
- [ ] 当前步骤是否有金色边框
- [ ] 按钮点击是否有触觉反馈

- [ ] **Step 2: 测试响应式布局**

调整浏览器宽度至 768px 以下，确认布局正常折叠

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "test: verify exam view redesign

- Visual testing complete
- Responsive layout verified

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## 验收清单

- [x] 主色调从蓝色更换为深石板灰
- [x] 添加金色强调色
- [x] 头部使用深色背景 + 衬线标题
- [x] 流程步骤有明确的状态区分
- [x] 开始考试卡片有动画
- [x] 按钮有触觉反馈
- [x] 面板有平滑动画
- [x] 响应式布局正常