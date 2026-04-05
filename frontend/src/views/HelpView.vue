<template>
  <div class="help-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-left">
        <h1>使用帮助</h1>
        <span class="version-badge">v3.1</span>
      </div>
      <div class="header-right">
        <a href="/docs/index.html" class="nav-btn nav-btn-secondary" target="_blank" rel="noopener">详细文档中心</a>
        <router-link to="/" class="nav-btn">返回考试</router-link>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content" ref="scrollContainer">
      <div class="help-container">
        <!-- 左侧：搜索 + 目录 -->
        <nav class="help-nav">
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              type="text"
              v-model="searchQuery"
              placeholder="搜索帮助内容..."
              class="search-input"
              @input="onSearch"
            />
            <button v-if="searchQuery" class="search-clear" @click="clearSearch" title="清除搜索">×</button>
          </div>

          <h3>目录</h3>
          <ul>
            <li><a href="#quick-start" :class="{ active: currentSection === 'quick-start', hidden: filteredSections.quickStart === false }" @click.prevent="scrollTo('quick-start')">快速上手</a></li>
            <li><a href="#exam" :class="{ active: currentSection === 'exam', hidden: filteredSections.exam === false }" @click.prevent="scrollTo('exam')">考试流程</a></li>
            <li><a href="#editor" :class="{ active: currentSection === 'editor', hidden: filteredSections.editor === false }" @click.prevent="scrollTo('editor')">题库管理</a></li>
            <li><a href="#settings" :class="{ active: currentSection === 'settings', hidden: filteredSections.settings === false }" @click.prevent="scrollTo('settings')">考试设置</a></li>
            <li><a href="#ai-settings" :class="{ active: currentSection === 'ai-settings', hidden: filteredSections.aiSettings === false }" @click.prevent="scrollTo('ai-settings')">AI 配置</a></li>
            <li><a href="#export" :class="{ active: currentSection === 'export', hidden: filteredSections.export === false }" @click.prevent="scrollTo('export')">数据导出</a></li>
            <li><a href="#shortcuts" :class="{ active: currentSection === 'shortcuts', hidden: filteredSections.shortcuts === false }" @click.prevent="scrollTo('shortcuts')">快捷键参考</a></li>
            <li><a href="#faq" :class="{ active: currentSection === 'faq', hidden: filteredSections.faq === false }" @click.prevent="scrollTo('faq')">常见问题</a></li>
          </ul>
        </nav>

        <!-- 内容区 -->
        <div class="help-content" ref="contentArea">
          <!-- 快速上手 -->
          <section id="quick-start" class="help-section" data-search="快速上手 开始 新手 第一次 入门 三步 开始考试">
            <h2>零、快速上手</h2>
            <div class="quick-start-steps">
              <div class="qs-step">
                <div class="qs-step-num">1</div>
                <div class="qs-step-content">
                  <h4>准备题库</h4>
                  <p>进入"题库管理"，添加翻译题目和专业题目，确保每个科目有足够的题目。</p>
                </div>
              </div>
              <div class="qs-step">
                <div class="qs-step-num">2</div>
                <div class="qs-step-content">
                  <h4>配置 AI（可选）</h4>
                  <p>如需 AI 出题功能，进入"AI 配置"页面，填写至少一个 AI 提供商的 API Key。</p>
                </div>
              </div>
              <div class="qs-step">
                <div class="qs-step-num">3</div>
                <div class="qs-step-content">
                  <h4>开始考试</h4>
                  <p>返回考试页面，点击"开始考试"按钮，系统自动创建考生并进入面试流程。</p>
                </div>
              </div>
            </div>
            <div class="info-box">
              <strong>提示：</strong>首次使用建议先阅读各章节详细说明，或访问 <a href="/docs/index.html" target="_blank" rel="noopener">详细文档中心</a> 获取更完整的图文教程。
            </div>
          </section>

          <!-- 考试流程 -->
          <section id="exam" class="help-section" data-search="考试流程 开始考试 面试 抽取题目 下一个考生 步骤 中文 英文 翻译 专业 综合">
            <h2>一、考试流程</h2>
            <div class="screenshot">
              <img :src="screenshots.exam" alt="考试界面" />
            </div>

            <h3>1.1 开始考试</h3>
            <ul>
              <li>点击"开始考试"按钮，系统自动创建新考生（编号 01, 02, 03...）</li>
              <li>考生编号由系统自动分配，无需手动输入</li>
              <li>刷新页面后，系统自动恢复到最后一位考生的状态</li>
            </ul>

            <h3>1.2 面试流程</h3>
            <table class="step-table">
              <thead>
                <tr>
                  <th>步骤</th>
                  <th>名称</th>
                  <th>默认时长</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>1</td>
                  <td>中文自我介绍</td>
                  <td>1 分钟</td>
                  <td>考生进行中文自我介绍</td>
                </tr>
                <tr>
                  <td>2</td>
                  <td>英文自我介绍</td>
                  <td>1 分钟</td>
                  <td>考生进行英文自我介绍</td>
                </tr>
                <tr>
                  <td>3</td>
                  <td>英文翻译</td>
                  <td>4 分钟</td>
                  <td>系统抽取英文翻译题目，考生现场翻译</td>
                </tr>
                <tr>
                  <td>4</td>
                  <td>专业问题</td>
                  <td>5 分钟</td>
                  <td>系统抽取专业问题，考生回答</td>
                </tr>
                <tr>
                  <td>5</td>
                  <td>综合问答</td>
                  <td>9 分钟</td>
                  <td>考官与考生进行综合交流</td>
                </tr>
                <tr>
                  <td>6</td>
                  <td>考试结束</td>
                  <td>—</td>
                  <td>总结评分，准备下一位考生</td>
                </tr>
              </tbody>
            </table>

            <h3>1.3 抽取题目</h3>
            <ul>
              <li>在"英文翻译"和"专业问题"步骤，点击"抽取题目"按钮</li>
              <li>系统从未使用的题目中随机抽取，确保公平性</li>
              <li>专业题目需要先选择科目</li>
              <li>已抽取的题目会被标记为"已使用"，不会重复抽取</li>
            </ul>
            <div class="warning-box">
              <strong>注意：</strong>题目一旦使用即被标记，如需重新使用所有题目，可通过系统重置功能清除使用状态。
            </div>

            <h3>1.4 下一个考生</h3>
            <ul>
              <li>考试完成后，点击"下一个考生"按钮</li>
              <li>系统自动创建新考生，进入下一场考试</li>
              <li>上一位考生的考试记录已自动保存</li>
            </ul>
          </section>

          <!-- 题库管理 -->
          <section id="editor" class="help-section" data-search="题库管理 翻译题目 专业题目 科目 添加 编辑 删除 搜索 筛选 批量导入 AI批量添加 批量导出 套题 分页">
            <h2>二、题库管理</h2>
            <div class="screenshot">
              <img :src="screenshots.editor" alt="题库管理界面" />
            </div>

            <h3>2.1 功能介绍</h3>
            <ul>
              <li><strong>翻译题目：</strong>管理英文翻译题，支持单题和套题格式</li>
              <li><strong>专业题目：</strong>按科目分类管理专业问答题</li>
              <li><strong>科目管理：</strong>添加、编辑、启用/禁用考试科目</li>
              <li><strong>题目操作：</strong>添加、编辑、删除、搜索、分页浏览</li>
              <li><strong>批量操作：</strong>批量导入、AI 批量添加、批量导出、批量删除、批量修改科目</li>
            </ul>

            <h3>2.2 界面布局</h3>
            <ul>
              <li><strong>左侧边栏：</strong>题目类型切换（翻译题目 / 专业题目 / 科目管理）、科目筛选、添加题目按钮、统计信息</li>
              <li><strong>顶部工具栏：</strong>批量导入、AI 批量添加、批量导出、AI 设置、返回考试、帮助</li>
              <li><strong>题目列表区：</strong>搜索框、全选/批量操作工具栏、题目卡片列表、分页控件</li>
            </ul>

            <h3>2.3 题目操作</h3>
            <ul>
              <li><strong>添加题目：</strong>点击左侧"添加题目"按钮，填写题目内容后保存</li>
              <li><strong>编辑题目：</strong>点击题目卡片右侧的"编辑"按钮修改内容</li>
              <li><strong>删除题目：</strong>点击"删除"按钮，确认后删除</li>
              <li><strong>搜索题目：</strong>在搜索框中输入关键词，实时筛选题目</li>
              <li><strong>套题支持：</strong>题目可以按套题格式组织，一次抽取多道关联题目</li>
            </ul>

            <h3>2.4 科目管理</h3>
            <ul>
              <li>切换到"科目管理"标签页</li>
              <li>点击"添加科目"，填写科目名称、代码和描述</li>
              <li>支持启用/禁用科目（禁用后该科目下的题目不会被抽取）</li>
              <li>每个科目显示关联的题目数量</li>
            </ul>

            <h3>2.5 批量操作</h3>
            <ul>
              <li><strong>批量导入：</strong>从文件批量导入题目，支持指定格式</li>
              <li><strong>AI 批量添加：</strong>使用 AI 智能生成多道题目，自动入库</li>
              <li><strong>批量导出：</strong>将选中的题目导出为文件备份</li>
              <li><strong>批量删除：</strong>勾选多道题目后，点击"批量删除"一次性删除</li>
              <li><strong>批量修改科目：</strong>（仅专业题目）将多道题目批量调整到指定科目</li>
            </ul>
            <div class="warning-box">
              <strong>注意：</strong>删除题目后不可恢复，请谨慎操作。建议定期使用"批量导出"功能备份题库。
            </div>
          </section>

          <!-- 考试设置 -->
          <section id="settings" class="help-section" data-search="考试设置 步骤设置 时间设置 Logo 标题 系统外观 步骤内容 指导内容">
            <h2>三、考试设置</h2>
            <div class="screenshot">
              <img :src="screenshots.settings" alt="考试设置界面" />
            </div>

            <h3>3.1 功能介绍</h3>
            <ul>
              <li>设置每个考试步骤的详细内容（步骤标题、描述、时间限制、类型）</li>
              <li>设置考试系统顶部显示的标题</li>
              <li>上传学校 Logo 和学院 Logo 图片</li>
              <li>设置每个步骤的指导内容，为考生和考官提供操作指引</li>
              <li>实时预览设置效果</li>
            </ul>

            <h3>3.2 考试步骤设置</h3>
            <ul>
              <li>点击左侧"考试步骤"下的步骤编号选择要编辑的步骤</li>
              <li>在右侧编辑步骤标题、描述、时间限制和类型</li>
              <li>点击"保存设置"按钮保存</li>
            </ul>

            <h3>3.3 步骤内容设置</h3>
            <ul>
              <li>点击左侧"步骤内容"进入内容管理</li>
              <li>选择要编辑的考试步骤</li>
              <li>可添加多个内容块，每个内容块包含标题和正文</li>
              <li>支持启用/禁用单个内容块</li>
              <li>内容会在对应考试步骤中展示给考生和考官</li>
            </ul>
            <div class="info-box">
              <strong>建议：</strong>在步骤内容中编写清晰的操作指引，帮助考生了解当前步骤的要求和流程。
            </div>

            <h3>3.4 Logo 设置</h3>
            <ul>
              <li>点击左侧"系统外观"下的"Logo 设置"</li>
              <li>输入系统标题</li>
              <li>点击"选择图片"上传学校 Logo 和学院 Logo</li>
              <li>预览效果后点击"保存设置"</li>
            </ul>
            <div class="info-box">
              <strong>图片要求：</strong>建议使用 PNG 格式，宽度不超过 200px，文件大小不超过 2MB。
            </div>
          </section>

          <!-- AI 配置 -->
          <section id="ai-settings" class="help-section" data-search="AI 配置 提供商 OpenAI Claude Gemini MiniMax ModelScope 硅基流动 API Key 出题 生成题目 自定义">
            <h2>四、AI 配置</h2>

            <h3>4.1 功能介绍</h3>
            <ul>
              <li>配置多个 AI 提供商，支持 AI 智能出题</li>
              <li>支持 OpenAI、Claude、Gemini、MiniMax、ModelScope、硅基流动</li>
              <li>支持自定义 AI 提供商（兼容 OpenAI / Anthropic API 格式）</li>
              <li>可设置默认提供商，出题时自动使用</li>
              <li>支持测试连接，验证配置是否正确</li>
            </ul>

            <div class="screenshot">
              <img :src="screenshots.aiSettings" alt="AI 配置页面" />
            </div>

            <h3>4.2 支持的提供商</h3>
            <table class="step-table">
              <thead>
                <tr>
                  <th>提供商</th>
                  <th>默认模型</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>OpenAI</td>
                  <td><code>gpt-4o</code></td>
                  <td>国际主流，质量稳定</td>
                </tr>
                <tr>
                  <td>Claude</td>
                  <td><code>claude-sonnet-4</code></td>
                  <td>Anthropic 出品，推理能力强</td>
                </tr>
                <tr>
                  <td>Gemini</td>
                  <td><code>gemini-2.0-flash</code></td>
                  <td>Google 出品，速度快</td>
                </tr>
                <tr>
                  <td>MiniMax</td>
                  <td><code>MiniMax-M2.5</code></td>
                  <td>国产大模型，性价比高</td>
                </tr>
                <tr>
                  <td>ModelScope</td>
                  <td><code>qwen3.5-397b</code></td>
                  <td>阿里通义系列，中文能力强</td>
                </tr>
                <tr>
                  <td>硅基流动</td>
                  <td><code>Qwen/Qwen3-8B</code></td>
                  <td>开源模型托管平台</td>
                </tr>
              </tbody>
            </table>

            <h3>4.3 配置步骤</h3>
            <ol>
              <li>进入"AI 配置"页面</li>
              <li>点击要配置的提供商卡片</li>
              <li>填写 API Key（必填）</li>
              <li>展开"高级选项"可自定义 Base URL 和模型</li>
              <li>点击"测试连接"验证配置</li>
              <li>点击"保存配置"完成设置</li>
            </ol>

            <h3>4.4 自定义提供商</h3>
            <ul>
              <li>点击"添加自定义"卡片</li>
              <li>填写提供商名称、API Key、Base URL、模型</li>
              <li>选择 API 格式：OpenAI 兼容 或 Anthropic Messages</li>
              <li>点击"添加"保存</li>
            </ul>

            <h3>4.5 设为默认提供商</h3>
            <ul>
              <li>在已配置的提供商配置面板中，勾选"设为默认"</li>
              <li>系统出题时将自动使用该提供商</li>
            </ul>
            <div class="warning-box">
              <strong>安全提示：</strong>API Key 是敏感信息，请勿泄露给他人。系统会对 Key 进行加密存储。
            </div>
          </section>

          <!-- 数据导出 -->
          <section id="export" class="help-section" data-search="数据导出 导出 Excel 报告 HTML PDF 统计 考试记录 考生列表">
            <h2>五、数据导出</h2>
            <div class="screenshot">
              <img :src="screenshots.export" alt="数据导出界面" />
            </div>

            <h3>5.1 功能介绍</h3>
            <ul>
              <li>查看考试统计数据</li>
              <li>导出考生列表为 Excel</li>
              <li>导出考试记录</li>
              <li>生成 HTML 报告（支持打印和 PDF 导出）</li>
            </ul>

            <h3>5.2 操作说明</h3>
            <ul>
              <li>查看页面上的统计概览</li>
              <li>点击"导出 Excel"按钮导出相应数据</li>
              <li>点击"生成报告"按钮生成可打印的 HTML 报告</li>
            </ul>
          </section>

          <!-- 快捷键参考 -->
          <section id="shortcuts" class="help-section" data-search="快捷键 键盘 快捷方式 空格 Space 计时 抽取 暂停 重置">
            <h2>六、快捷键参考</h2>
            <table class="step-table">
              <thead>
                <tr>
                  <th>功能</th>
                  <th>快捷键</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>开始考试</td>
                  <td><kbd>Space</kbd></td>
                  <td>空格键快速开始</td>
                </tr>
                <tr>
                  <td>上一步</td>
                  <td><kbd>←</kbd></td>
                  <td>左箭头键</td>
                </tr>
                <tr>
                  <td>下一步</td>
                  <td><kbd>→</kbd></td>
                  <td>右箭头键</td>
                </tr>
                <tr>
                  <td>抽取题目</td>
                  <td><kbd>D</kbd></td>
                  <td>Draw 的首字母</td>
                </tr>
                <tr>
                  <td>开始计时</td>
                  <td><kbd>T</kbd></td>
                  <td>Timer 的首字母</td>
                </tr>
                <tr>
                  <td>暂停计时</td>
                  <td><kbd>P</kbd></td>
                  <td>Pause 的首字母</td>
                </tr>
                <tr>
                  <td>重置计时</td>
                  <td><kbd>R</kbd></td>
                  <td>Reset 的首字母</td>
                </tr>
                <tr>
                  <td>完成考试</td>
                  <td><kbd>Ctrl</kbd> + <kbd>Enter</kbd></td>
                  <td>组合键快速结束</td>
                </tr>
              </tbody>
            </table>
            <div class="info-box">
              <strong>提示：</strong>快捷键仅在对应按钮可用时生效，不会重复触发。
            </div>
          </section>

          <!-- 常见问题 -->
          <section id="faq" class="help-section" data-search="常见问题 问题 解答 故障排除 数据库 连接 题目 计时器 恢复 状态 重置">
            <h2>七、常见问题</h2>

            <div class="faq-item">
              <h4>Q: 系统显示"数据库连接失败"怎么办？</h4>
              <div class="faq-answer">
                <ol>
                  <li>确认服务器正常运行（检查控制台是否有错误信息）</li>
                  <li>刷新页面重新连接</li>
                  <li>检查数据库文件是否存在于 assets/data 目录</li>
                </ol>
              </div>
            </div>

            <div class="faq-item">
              <h4>Q: 抽取题目时显示"无可用题目"？</h4>
              <div class="faq-answer">
                <ol>
                  <li>进入题库管理，检查是否有足够的题目</li>
                  <li>确认题目没有全部被标记为"已使用"</li>
                  <li>可通过系统重置清除使用状态</li>
                </ol>
              </div>
            </div>

            <div class="faq-item">
              <h4>Q: 计时器不工作或显示异常？</h4>
              <div class="faq-answer">
                <ol>
                  <li>点击"重置计时"按钮</li>
                  <li>检查系统设置中的时间配置</li>
                  <li>刷新页面重新初始化</li>
                </ol>
              </div>
            </div>

            <div class="faq-item">
              <h4>Q: 如何恢复到某个考生的考试状态？</h4>
              <div class="faq-answer">
                <p>系统会自动保存每位考生的进度。刷新页面后，系统自动恢复到最后一位考生的状态，包括当前步骤和已抽取的题目。</p>
              </div>
            </div>

            <div class="faq-item">
              <h4>Q: AI 出题失败或连接超时？</h4>
              <div class="faq-answer">
                <ol>
                  <li>检查 API Key 是否正确且未过期</li>
                  <li>在"AI 配置"页面点击"测试连接"验证</li>
                  <li>确认网络连接正常</li>
                  <li>尝试切换到其他 AI 提供商</li>
                </ol>
              </div>
            </div>

            <div class="faq-item">
              <h4>Q: 如何备份题库数据？</h4>
              <div class="faq-answer">
                <p>数据库文件位于后端 <code>assets/data/interview_system.db</code>，直接复制该文件即可完成备份。建议定期备份。</p>
              </div>
            </div>

            <div class="faq-item">
              <h4>Q: 导出报告时生成的文件在哪里？</h4>
              <div class="faq-answer">
                <p>导出的文件会自动下载到浏览器的默认下载目录。HTML 报告可在浏览器中直接打开并打印为 PDF。</p>
              </div>
            </div>
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
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import api from '@/api'

import examSystemMain from '@/assets/exam-system-main.png'
import databaseEditorMain from '@/assets/database-editor-main.png'
import examSettingsMain from '@/assets/exam-settings-main.png'
import exportExamMain from '@/assets/export-exam-main.png'
import aiSettingsMain from '@/assets/ai-settings-main.png'

const currentSection = ref('quick-start')
const searchQuery = ref('')
const scrollContainer = ref(null)

const filteredSections = reactive({
  quickStart: true,
  exam: true,
  editor: true,
  settings: true,
  aiSettings: true,
  export: true,
  shortcuts: true,
  faq: true
})

const footerCopyright = ref('')

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

const scrollTo = (id) => {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const onSearch = () => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) {
    filteredSections.quickStart = true
    filteredSections.exam = true
    filteredSections.editor = true
    filteredSections.settings = true
    filteredSections.aiSettings = true
    filteredSections.export = true
    filteredSections.shortcuts = true
    filteredSections.faq = true
    return
  }

  const sections = document.querySelectorAll('.help-section')
  sections.forEach(section => {
    const searchData = (section.getAttribute('data-search') || '') + ' ' + section.textContent.toLowerCase()
    const match = searchData.includes(query)
    section.style.display = match ? '' : 'none'
  })

  const hasMatch = (id) => {
    const el = document.getElementById(id)
    return el && el.style.display !== 'none'
  }
  filteredSections.quickStart = hasMatch('quick-start')
  filteredSections.exam = hasMatch('exam')
  filteredSections.editor = hasMatch('editor')
  filteredSections.settings = hasMatch('settings')
  filteredSections.aiSettings = hasMatch('ai-settings')
  filteredSections.export = hasMatch('export')
  filteredSections.shortcuts = hasMatch('shortcuts')
  filteredSections.faq = hasMatch('faq')
}

const clearSearch = () => {
  searchQuery.value = ''
  onSearch()
}

let observer = null

onMounted(async () => {
  loadFooterCopyright()

  await nextTick()

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          currentSection.value = entry.target.id
        }
      })
    },
    {
      root: scrollContainer.value,
      rootMargin: '-80px 0px -60% 0px',
      threshold: 0
    }
  )

  const sections = document.querySelectorAll('.help-section')
  sections.forEach(section => observer.observe(section))
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})

const screenshots = {
  exam: examSystemMain,
  editor: databaseEditorMain,
  settings: examSettingsMain,
  export: exportExamMain,
  aiSettings: aiSettingsMain
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

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header h1 {
  margin: 0;
  font-size: 20px;
}

.version-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-btn {
  padding: 8px 16px;
  background: rgba(255,255,255,0.2);
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 14px;
}

.nav-btn-secondary {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.nav-btn:hover {
  background: rgba(255,255,255,0.3);
}

.nav-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.25);
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
  width: 220px;
  position: sticky;
  top: 20px;
  height: fit-content;
}

.search-box {
  position: relative;
  margin-bottom: 16px;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #999;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 8px 32px 8px 32px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  background: white;
  color: #333;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.search-clear {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  width: 22px;
  height: 22px;
  border: none;
  background: #e9ecef;
  color: #666;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.search-clear:hover {
  background: #dee2e6;
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
  margin-bottom: 4px;
}

.help-nav a {
  display: block;
  padding: 8px 15px;
  color: #666;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s;
  font-size: 14px;
}

.help-nav a:hover {
  background: #e9ecef;
  color: #007bff;
}

.help-nav a.active {
  background: #007bff;
  color: white;
}

.help-nav a.hidden {
  display: none;
}

.help-content {
  flex: 1;
  min-width: 0;
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

.help-section h4 {
  margin: 0 0 8px 0;
  color: #444;
}

.help-section ul,
.help-section ol {
  margin: 0;
  padding-left: 20px;
}

.help-section li {
  margin-bottom: 8px;
  color: #666;
  line-height: 1.6;
}

/* Quick start */
.quick-start-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.qs-step {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #007bff;
}

.qs-step-num {
  width: 32px;
  height: 32px;
  background: #007bff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.qs-step-content h4 {
  margin: 0 0 4px 0;
  color: #333;
  font-size: 15px;
}

.qs-step-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

/* Tables */
.step-table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  font-size: 14px;
}

.step-table th,
.step-table td {
  border: 1px solid #e5e7eb;
  padding: 10px 14px;
  text-align: left;
}

.step-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.step-table td {
  color: #666;
}

.step-table tbody tr:hover {
  background: #fafbfc;
}

/* kbd */
kbd {
  display: inline-block;
  padding: 2px 6px;
  font-size: 12px;
  font-family: 'Consolas', monospace;
  background: #f1f3f5;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  color: #333;
  box-shadow: 0 1px 0 #adb5bd;
  line-height: 1.4;
}

/* Code */
code {
  background: #f1f3f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
  color: #d63384;
}

/* Info box */
.info-box {
  background: #d1ecf1;
  padding: 14px 18px;
  border-radius: 6px;
  border-left: 4px solid #17a2b8;
  margin: 16px 0;
  color: #0c5460;
  font-size: 14px;
  line-height: 1.6;
}

.info-box a {
  color: #007bff;
  text-decoration: underline;
}

/* Warning box */
.warning-box {
  background: #f8d7da;
  padding: 14px 18px;
  border-radius: 6px;
  border-left: 4px solid #dc3545;
  margin: 16px 0;
  color: #721c24;
  font-size: 14px;
  line-height: 1.6;
}

/* FAQ */
.faq-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.faq-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.faq-item h4 {
  color: #333;
  margin-bottom: 10px;
  font-size: 15px;
}

.faq-answer {
  color: #666;
  font-size: 14px;
  line-height: 1.7;
  padding-left: 16px;
}

.faq-answer ol,
.faq-answer ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.faq-answer li {
  margin-bottom: 4px;
}

.faq-answer p {
  margin: 0;
}

/* Screenshot */
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

.screenshot-placeholder {
  border: 2px dashed #ced4da;
  background: #f8f9fa;
  min-height: 240px;
}

.screenshot-placeholder .placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.screenshot-placeholder .placeholder-icon {
  width: 48px;
  height: 48px;
  color: #adb5bd;
}

.screenshot-placeholder .placeholder-text {
  color: #495057;
  font-size: 14px;
  font-weight: 500;
}

.screenshot-placeholder .placeholder-hint {
  color: #868e96;
  font-size: 12px;
}

.screenshot-placeholder .placeholder-hint code {
  background: #e9ecef;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 12px;
  color: #495057;
}

/* Footer */
.footer {
  text-align: center;
  padding: 15px;
  background: #fff;
  border-top: 1px solid #e5e7eb;
  color: #6b7280;
  font-size: 14px;
}
</style>
