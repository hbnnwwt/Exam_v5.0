# 帮助文档入口链接总结

本文档总结了在系统各个页面中添加的帮助文档入口链接。

## 📚 帮助文档结构

### 主要文档
- `docs/index.html` - 帮助文档中心主页
- `docs/exam-system-help.html` - 考试系统详细使用指南
- `docs/database-editor-help.html` - 数据库题库编辑器详细使用指南
- `docs/header-setting-help.html` - 顶部设置使用指南
- `docs/page-content-setting-help.html` - 步骤内容设置指南
- `docs/export-exam-help.html` - 考试导出使用指南

### 截图文件
- `docs/exam-system-main.png` - 考试系统主界面
- `docs/exam-system-settings.png` - 系统设置界面
- `docs/database-editor-main.png` - 数据库编辑器主界面
- `docs/database-editor-professional.png` - 专业题管理界面
- `docs/database-editor-edit.png` - 题目编辑界面
- `docs/header-setting-main.png` - 顶部设置主界面
- `docs/page-content-setting-main.png` - 步骤内容设置主界面
- `docs/page-content-setting-edit.png` - 内容编辑界面
- `docs/export-exam-main.png` - 考试导出主界面

## 🔗 添加的入口链接

### 1. 考试系统主页面 (index.html)

#### 顶部导航区域
- **位置**: header-controls 区域
- **按钮**: "📖 帮助" 按钮
- **功能**: 点击打开帮助文档中心 (docs/index.html)
- **样式**: 蓝色信息按钮 (btn-info)
- **JavaScript**: `openHelpCenter()` 函数

#### 设置模态框
- **位置**: 系统管理部分
- **标题**: "帮助文档"
- **描述**: "查看系统使用指南和题库编辑器帮助文档"
- **链接**: "📖 打开帮助中心" → docs/index.html

### 2. 数据库编辑器 (database-editor.html)

#### 顶部导航区域
- **原有链接**: "📖 帮助文档" → docs/editor.html (已更新)
- **新增链接1**: "📖 编辑器帮助" → docs/database-editor-help.html
- **新增链接2**: "📚 帮助中心" → docs/index.html

### 3. 考试导出页面 (export_exam.html)

#### 顶部导航区域
- **新增链接**: "📚 帮助中心" → docs/index.html
- **位置**: 在"返回考试系统"和"题库管理"链接之前

### 4. 顶部设置页面 (header_setting.html)

#### 底部按钮区域
- **新增链接**: "📖 帮助中心" → docs/index.html
- **样式**: 蓝色信息按钮 (btn-info)
- **位置**: 在"返回主页"按钮之前

### 5. 顶部设置页面 (header_setting.html)

#### 底部按钮区域
- **新增链接1**: "❓ 使用帮助" → docs/header-setting-help.html
- **新增链接2**: "📖 帮助中心" → docs/index.html
- **样式**: 绿色成功按钮 (btn-success) 和蓝色信息按钮 (btn-info)
- **位置**: 在"返回主页"按钮之前

### 6. 步骤内容设置页面 (page_content_setting.html)

#### 顶部导航区域
- **新增链接1**: "❓ 使用帮助" → docs/page-content-setting-help.html
- **新增链接2**: "📚 帮助中心" → docs/index.html
- **位置**: 在"返回主页"和"题库编辑"链接之前

### 7. 考试导出页面 (export_exam.html)

#### 顶部导航区域
- **新增链接1**: "❓ 使用帮助" → docs/export-exam-help.html
- **新增链接2**: "📚 帮助中心" → docs/index.html
- **位置**: 在"返回考试系统"和"题库管理"链接之前

## 🎨 样式和设计

### 按钮样式
```css
.btn-info {
    background: #17a2b8;
    color: white;
    border: none;
}

.btn-info:hover {
    background: #138496;
}
```

### 图标使用
- 📚 - 帮助中心/文档中心
- 📖 - 具体帮助文档
- ❓ - 帮助按钮图标

## 🔧 技术实现

### JavaScript函数
```javascript
// 打开帮助中心
function openHelpCenter() {
    window.open('docs/index.html', '_blank');
}
```

### HTML结构示例
```html
<!-- 顶部帮助按钮 -->
<button class="control-btn btn-info" onclick="openHelpCenter()" title="帮助文档">
    <i class="bi bi-question-circle"></i> 帮助
</button>

<!-- 设置中的帮助链接 -->
<div class="management-item">
    <label>帮助文档</label>
    <p>查看系统使用指南和题库编辑器帮助文档</p>
    <a href="docs/index.html" target="_blank" class="btn-link">
        <i class="bi bi-book"></i> 打开帮助中心
    </a>
</div>
```

## 📱 用户体验

### 访问路径
1. **主要入口**: 考试系统顶部的"帮助"按钮
2. **设置入口**: 系统设置 → 系统管理 → 帮助文档
3. **编辑器入口**: 数据库编辑器顶部导航
4. **其他页面**: 各功能页面的导航区域

### 链接行为
- 所有帮助链接都在新标签页中打开 (`target="_blank"`)
- 保持原页面状态，不影响用户当前操作
- 提供清晰的图标和文字说明

## 🔄 维护说明

### 更新帮助文档
1. 修改 `docs/` 目录下的相应HTML文件
2. 更新截图文件（如需要）
3. 检查所有链接是否正常工作

### 添加新的帮助入口
1. 在目标页面添加链接HTML
2. 确保链接指向正确的帮助文档
3. 保持样式一致性
4. 测试链接功能

## ✅ 测试清单

- [x] 考试系统主页面帮助按钮
- [x] 设置模态框帮助链接
- [x] 数据库编辑器帮助链接
- [x] 导出页面帮助链接
- [x] 顶部设置页面帮助链接
- [x] 步骤内容设置页面帮助链接
- [x] 顶部设置专门帮助文档
- [x] 步骤内容设置专门帮助文档
- [x] 考试导出专门帮助文档
- [x] 帮助文档中心更新
- [x] 所有链接在新标签页打开
- [x] 帮助文档正常显示
- [x] 截图文件正确加载

## 📞 技术支持

如需添加更多帮助入口或修改现有链接，请参考本文档的实现方式，保持一致的用户体验和技术标准。

---
**文档版本**: v1.0  
**最后更新**: 2025年7月14日  
**维护者**: 王文通 (wangwentong@bipt.edu.cn)
