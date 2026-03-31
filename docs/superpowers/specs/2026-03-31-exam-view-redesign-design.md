# 考生面试界面重新设计 - 设计文档

**项目**: 研究生复试面试系统 UI 优化
**日期**: 2026-03-31
**范围**: 考生面试界面 (ExamView.vue)

---

## 1. 设计目标

- **核心目标**: 提升专业形象，让面试系统看起来更庄重、更专业
- **用户价值**: 考生和面试官都能感受到更正式、更有仪式感的面试体验
- **成功标准**:
  - 视觉上呈现"庄重面试风"
  - 流程步骤清晰可见
  - 交互流畅有反馈

---

## 2. 当前状态分析

### 2.1 现有 UI 问题

| 问题 | 现状 | 影响 |
|------|------|------|
| 主色调 | Bootstrap 蓝色 (#007bff) | 缺乏专业感，像内部工具 |
| 字体 | 微软雅黑 | 缺乏现代感 |
| 流程步骤 | 简单蓝色高亮 | 仪式感不足 |
| 动画 | 无 | 交互单调 |
| 整体风格 | 十年前的内部管理系统 | 影响学校形象 |

### 2.2 技术栈

- Vue 3 + Composition API
- 纯 CSS（无 Tailwind）
- 无动画库
- 响应式设计（基本支持）

---

## 3. 设计方案

### 3.1 色彩体系

**核心原则**: 沉稳、庄重、专业

```
主色调: Slate-900 (#0f172a) - 深石板灰，用于标题、重要文字
次要色: Slate-700 (#334155) - 次要文字、边框
强调色: Amber-600 (#d97706) - 金色，用于当前步骤、高亮操作
背景色: Slate-50 (#f8fafc) - 页面背景
卡片色: White (#ffffff) - 内容卡片
成功色: Emerald-600 (#059669) - 完成状态
```

**CSS 变量更新**:

```css
:root {
  --color-primary: #0f172a;      /* 深石板灰替代蓝色 */
  --color-primary-hover: #1e293b;
  --color-accent: #d97706;        /* 金色强调 */
  --color-accent-hover: #b45309;
  --color-surface: #ffffff;
  --color-background: #f8fafc;
  --color-border: #e2e8f0;
  --color-text-primary: #0f172a;
  --color-text-secondary: #475569;
  --color-success: #059669;
}
```

### 3.2 字体系统

```
中文: "Noto Serif SC", "Source Han Serif CN", serif
英文/数字: "Inter", -apple-system, sans-serif
等宽: "JetBrains Mono", monospace (用于计时器)
```

**排版层级**:

| 层级 | 样式 | 用途 |
|------|------|------|
| H1 | 28px, 700, 庄重衬线 | 页面主标题 |
| H2 | 22px, 600, 无衬线 | 区块标题 |
| H3 | 16px, 600 | 小节标题 |
| Body | 15px, 400 | 正文 |
| Caption | 13px, 400 | 辅助文字 |

### 3.3 布局结构

保持现有三栏布局，优化视觉层次：

```
+------------------------------------------------------------------+
|  [Logo]  研究生复试面试系统           当前考生: XXX  | 设置按钮  |  <- 头部
+------------------------------------------------------------------+
|        |                                    |                    |
| 流程   |        中间内容区                  |    控制面板       |
| 面板   |  (考生输入 / 考试内容)            |    (状态/操作)    |
| 250px  |        flex: 1                     |    250px          |
|        |                                    |                    |
+------------------------------------------------------------------+
|                         页脚版权信息                              |
+------------------------------------------------------------------+
```

### 3.4 流程步骤设计（核心改进）

**当前状态**:
- 蓝色背景高亮
- 简单数字编号

**升级后**:
- 数字编号使用圆形图标
- 当前步骤: 金色边框 + 底部指示条 + 微光效果
- 完成步骤: 绿色背景 + 对勾图标
- 未完成步骤: 灰色边框 + 数字

**视觉规范**:

```css
.step-item {
  border-radius: 8px;
  border: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-item.active {
  border-color: var(--color-accent);
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  box-shadow: 0 0 20px rgba(217, 119, 6, 0.15);
}

.step-item.completed {
  background: #ecfdf5;
  border-color: #059669;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-weight: 600;
}
```

### 3.5 考试开始卡片

**当前**: 简单按钮

**升级后**: 正式感卡片

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
  border: 1px solid var(--color-border);
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
  font-family: var(--font-serif);
  font-size: 28px;
  color: var(--color-text-primary);
  margin-bottom: 12px;
}

.start-card .subtitle {
  color: var(--color-text-secondary);
  margin-bottom: 32px;
}

.start-btn {
  padding: 14px 48px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.start-btn:hover {
  background: var(--color-primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.2);
}

.start-btn:active {
  transform: translateY(0);
}
```

### 3.6 交互反馈

**按钮触觉反馈**:

```css
.control-btn:active:not(:disabled) {
  transform: translateY(-1px);
}

.start-btn:active:not(:disabled) {
  transform: scale(0.98);
}
```

**面板动画**:

```css
.left-panel,
.right-panel {
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.3s ease;
}
```

**步骤切换过渡**:

```css
.step-content {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

### 3.7 状态徽章

```css
.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
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

---

## 4. 组件变更清单

### 4.1 ExamView.vue

| 变更项 | 类型 | 说明 |
|--------|------|------|
| 色彩变量 | 修改 | 全局 CSS 变量更新 |
| 字体引入 | 修改 | 添加 Google Fonts |
| 头部样式 | 修改 | 深色背景，金色强调 |
| 流程面板 | 修改 | 步骤样式升级 |
| 开始卡片 | 修改 | 正式感卡片设计 |
| 按钮样式 | 修改 | 添加触觉反馈 |
| 过渡动画 | 新增 | 面板、内容切换动画 |
| 状态徽章 | 修改 | 新色彩方案 |

### 4.2 main.css

| 变更项 | 类型 | 说明 |
|--------|------|------|
| CSS 变量 | 新增 | 庄重配色系统 |
| 字体栈 | 修改 | 添加衬线字体 |
| 全局过渡 | 新增 | 默认过渡曲线 |

---

## 5. 实施顺序

1. **第一步**: 更新 `main.css` 全局色彩变量
2. **第二步**: 重构 `ExamView.vue` 样式
3. **第三步**: 添加过渡动画
4. **第四步**: 测试响应式布局
5. **第五步**: 验证无障碍访问

---

## 6. 验收标准

- [ ] 整体视觉呈现"庄重面试风"
- [ ] 流程步骤清晰可辨，当前/完成/未完成状态明确
- [ ] 考试开始有正式感
- [ ] 按钮点击有触觉反馈
- [ ] 面板收起展开有平滑动画
- [ ] 响应式布局在 768px 以下正常工作
- [ ] 暗色模式仍可正常显示（可选）
- [ ] 无 broken links 或 console errors

---

## 7. 风险与约束

- **兼容性**: 仅支持现代浏览器（Chrome 90+, Firefox 88+, Safari 14+）
- **性能**: 动画使用 CSS transform/opacity，不触发布局重排
- **无障碍**: 保持现有的 ARIA 支持，颜色对比度符合 WCAG AA

---

## 8. 后续扩展

如果初次改进效果良好，可考虑：
- 添加 Framer Motion 实现更复杂动画
- 其他页面（EditorView、SettingsView 等）统一风格
- 添加主题切换（庄重深色 / 简洁浅色）
