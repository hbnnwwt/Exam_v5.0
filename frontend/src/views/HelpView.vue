<template>
  <div class="help-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-left">
        <h1>使用帮助</h1>
      </div>
      <div class="header-right">
        <router-link to="/" class="nav-btn">返回考试</router-link>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="help-container">
        <!-- 目录 -->
        <nav class="help-nav">
          <h3>目录</h3>
          <ul>
            <li><a href="#exam" :class="{ active: currentSection === 'exam' }" @click="currentSection = 'exam'">考试流程</a></li>
            <li><a href="#editor" :class="{ active: currentSection === 'editor' }" @click="currentSection = 'editor'">题库管理</a></li>
            <li><a href="#settings" :class="{ active: currentSection === 'settings' }" @click="currentSection = 'settings'">考试设置</a></li>
            <li><a href="#export" :class="{ active: currentSection === 'export' }" @click="currentSection = 'export'">数据导出</a></li>
          </ul>
        </nav>

        <!-- 内容区 -->
        <div class="help-content">
          <!-- 考试流程 -->
          <section id="exam" class="help-section">
            <h2>一、考试流程</h2>
            <div class="screenshot">
              <img :src="screenshots.exam" alt="考试界面" />
            </div>
            <h3>1.1 开始考试</h3>
            <ul>
              <li>点击"开始考试"按钮，系统自动创建新考生（编号01, 02, 03...）</li>
              <li>考生编号由系统自动分配，无需手动输入</li>
            </ul>

            <h3>1.2 面试流程</h3>
            <ul>
              <li>步骤1：中文自我介绍 - 考生进行1分钟中文自我介绍</li>
              <li>步骤2：英文自我介绍 - 考生进行1分钟英文自我介绍</li>
              <li>步骤3：英文翻译 - 系统抽取英文翻译题目，考生现场翻译</li>
              <li>步骤4：专业问题 - 系统抽取专业问题，考生回答</li>
              <li>步骤5：综合问答 - 考官与考生进行综合交流</li>
              <li>步骤6：考试结束</li>
            </ul>

            <h3>1.3 抽取题目</h3>
            <ul>
              <li>在"英文翻译"和"专业问题"步骤，点击"抽取题目"按钮</li>
              <li>系统从未使用的题目中随机抽取</li>
              <li>专业题目需要先选择科目</li>
            </ul>

            <h3>1.4 下一个考生</h3>
            <ul>
              <li>考试完成后，点击"下一个考生"按钮</li>
              <li>系统自动创建新考生，进入下一场考试</li>
            </ul>
          </section>

          <!-- 题库管理 -->
          <section id="editor" class="help-section">
            <h2>二、题库管理</h2>
            <div class="screenshot">
              <img :src="screenshots.editor" alt="题库管理界面" />
            </div>
            <h3>2.1 功能介绍</h3>
            <ul>
              <li>管理翻译题目和专业题目</li>
              <li>支持题目的添加、编辑、删除</li>
              <li>支持按科目筛选和搜索</li>
            </ul>

            <h3>2.2 操作说明</h3>
            <ul>
              <li>选择题目类型：翻译题目 / 专业题目</li>
              <li>点击"添加题目"创建新题目</li>
              <li>点击题目卡片编辑或删除</li>
              <li>使用搜索框快速查找题目</li>
            </ul>
          </section>

          <!-- 考试设置 -->
          <section id="settings" class="help-section">
            <h2>三、考试设置</h2>
            <div class="screenshot">
              <img :src="screenshots.settings" alt="考试设置界面" />
            </div>
            <h3>3.1 功能介绍</h3>
            <ul>
              <li>设置每个考试步骤的详细内容（步骤标题、描述、时间限制、类型）</li>
              <li>设置考试系统顶部显示的标题</li>
              <li>上传学校Logo和学院Logo图片</li>
              <li>实时预览设置效果</li>
            </ul>

            <h3>3.2 考试步骤设置</h3>
            <ul>
              <li>点击左侧"考试步骤"下的步骤编号选择要编辑的步骤</li>
              <li>在右侧编辑步骤标题、描述、时间限制和类型</li>
              <li>点击"保存设置"按钮保存</li>
            </ul>

            <h3>3.3 Logo设置</h3>
            <ul>
              <li>点击左侧"系统外观"下的"Logo设置"</li>
              <li>输入系统标题</li>
              <li>点击"选择图片"上传学校Logo和学院Logo</li>
              <li>预览效果后点击"保存设置"</li>
            </ul>
          </section>

          <!-- 数据导出 -->
          <section id="export" class="help-section">
            <h2>四、数据导出</h2>
            <div class="screenshot">
              <img :src="screenshots.export" alt="数据导出界面" />
            </div>
            <h3>4.1 功能介绍</h3>
            <ul>
              <li>查看考试统计数据</li>
              <li>导出考生列表为Excel</li>
              <li>导出考试记录</li>
              <li>生成HTML报告</li>
            </ul>

            <h3>4.2 操作说明</h3>
            <ul>
              <li>查看页面上的统计概览</li>
              <li>点击"导出Excel"按钮导出相应数据</li>
              <li>点击"生成报告"按钮生成可打印的HTML报告</li>
            </ul>
          </section>
        </div>
      </div>
    </main>

    <!-- 底部版权 -->
    <footer class="footer">
      <p>{{ footerCopyright || '版权所有 © 2026 北京石油化工学院 | 联系方式：wangwentong@bipt.edu.cn' }}</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

// 导入截图
import examSystemMain from '@/assets/exam-system-main.png'
import databaseEditorMain from '@/assets/database-editor-main.png'
import examSettingsMain from '@/assets/exam-settings-main.png'
import headerSettingMain from '@/assets/logo-setting-main.png'
import exportExamMain from '@/assets/export-exam-main.png'

const currentSection = ref('exam')

// 底部版权信息
const footerCopyright = ref('')

// 加载版权信息
const loadFooterCopyright = async () => {
  try {
    const response = await api.get('/api/header-settings')
    if (response.success && response.data && response.data.footerCopyright) {
      footerCopyright.value = response.data.footerCopyright
    }
  } catch (error) {
    console.error('加载版权信息失败:', error)
  }
}

onMounted(() => {
  loadFooterCopyright()
})

// 导出图片路径供模板使用
const screenshots = {
  exam: examSystemMain,
  editor: databaseEditorMain,
  settings: examSettingsMain,
  export: exportExamMain
}
</script>

<style scoped>
.help-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #007bff;
  color: white;
}

.header h1 {
  margin: 0;
  font-size: 20px;
}

.nav-btn {
  padding: 8px 16px;
  background: rgba(255,255,255,0.2);
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 14px;
}

.main-content {
  flex: 1;
  overflow-y: auto;
}

.help-container {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  gap: 30px;
}

.help-nav {
  width: 200px;
  position: sticky;
  top: 20px;
  height: fit-content;
}

.help-nav h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.help-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.help-nav li {
  margin-bottom: 8px;
}

.help-nav a {
  display: block;
  padding: 10px 15px;
  color: #666;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s;
}

.help-nav a:hover {
  background: #e9ecef;
  color: #007bff;
}

.help-nav a.active {
  background: #007bff;
  color: white;
}

.help-content {
  flex: 1;
}

.help-section {
  background: white;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 30px;
}

.help-section h2 {
  margin: 0 0 20px 0;
  color: #333;
  padding-bottom: 10px;
  border-bottom: 2px solid #007bff;
}

.help-section h3 {
  margin: 25px 0 15px 0;
  color: #555;
}

.help-section ul {
  margin: 0;
  padding-left: 20px;
}

.help-section li {
  margin-bottom: 8px;
  color: #666;
  line-height: 1.6;
}

.screenshot {
  margin: 20px 0;
  text-align: center;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.screenshot img {
  max-width: 100%;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.placeholder-img {
  padding: 60px 20px;
  background: #e9ecef;
  border-radius: 8px;
  color: #6c757d;
  font-size: 14px;
}

/* 底部 */
.footer {
  text-align: center;
  padding: 15px;
  background: #fff;
  border-top: 1px solid #e5e7eb;
  color: #6b7280;
  font-size: 14px;
}
</style>
