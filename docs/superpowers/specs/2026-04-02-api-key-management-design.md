# API Key 安全管理设计方案

## 背景

当前 `ai_providers.json` 含真实 API Key，已加入 `.gitignore` 防止泄露。但存在两个问题：

1. **密钥与 Provider 配置耦合** — key 存在 JSON 里，结构不清
2. **发布包含数据风险** — `interview_system.db` 可能被误打包进 release，泄露考生数据
3. **多场景需求** — 需兼顾单机部署（ENV）、便携分发（DB）、用户自配（UI）

## 目标

- API Key 完全与代码分离，不随任何发布包分发
- 用户可通过 UI 配置 key，换电脑不丢（存数据库）
- 开发者/运维可通过 ENV 注入 key，优先于数据库
- 发布包绝对不包含真实数据（数据库 + 密钥文件）

## 架构设计

### 读取优先级（层层递进）

```
1. .env 环境变量（最高优先，生产部署用）
2. settings 表 / api_keys 表（便携场景，用户 UI 配置）
3. ai_providers.json 模板（仅含模型名/URL，无 key）
```

### 新建 api_keys 表

```sql
CREATE TABLE api_keys (
  id TEXT PRIMARY KEY,        -- provider id: minimax, modelscope, siliconflow, openai, claude, gemini
  api_key TEXT,              -- 密文存储
  base_url TEXT,
  default_model TEXT,
  is_default INTEGER DEFAULT 0,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### .env 示例文件（不提交 git）

```env
# AI Provider Keys - 生产部署用
MINIMAX_API_KEY=sk-cp-xxx
MINIMAX_API_FORMAT=anthropic
MODELSCOPE_API_KEY=ms-xxx
SILICONFLOW_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-xxx
GEMINI_API_KEY=xxx
```

### 初始化行为

| 场景 | ENV 有 key | DB 有 key | JSON 模板 | 最终结果 |
|------|-----------|-----------|-----------|---------|
| 生产部署 | ✅ | - | - | 用 ENV |
| 便携/换电脑 | ❌ | ✅ | ✅ | 用 DB |
| 新用户首次 | ❌ | ❌ | ✅ | 用模板（key 为空） |

## 数据库表设计

### settings 表（已有，复用）
- 存系统级配置（标题、Logo、版权）
- 与 api_keys 表职责分离

### api_keys 表（新建）
- 存储用户配置的 key，按 provider id 隔离
- `is_default = 1` 表示默认 provider

## 安全边界

### 发布包排除清单（更新 `exclude_list.txt`）

```
backend\apis\config\ai_providers.json
backend\assets\data\interview_system.db
backend\assets\data\*.db
```

### 构建产物

| 包类型 | 包含内容 | 不含 |
|--------|---------|------|
| Source.zip | git HEAD 快照 | 无 DB（git 不跟踪）|
| Release.zip | 前端 build + backend（不含 DB/key）| DB、ENV |
| Portable.zip | 前端 build + backend + python_portable | DB、ENV |

### 数据库初始化逻辑

- `init_db.py` 检查 `assets/data/` 目录
- 如果 `interview_system.db` 不存在 → 创建空数据库 + 插入默认步骤
- 如果存在 → 不改动，保持数据完整

## 前端 UI 改动

### AI 设置页面
- 当前：直接编辑 `ai_providers.json`
- 改为：调用 `/ai-api/providers` 保存到数据库

### 后端 API 改动
- `config.py` 新增 `load_api_key(provider_id)` — 优先 ENV → DB → JSON
- `save_provider()` — 改为写入数据库
- GET `/providers` — 返回 DB 中配置（不含 key 明文）/ 仅 id/name 返回

## 实现步骤

### Phase 1: 数据库迁移
1. 新增 `api_keys` 表
2. 实现 `load_api_key(provider_id)` 读取函数
3. 实现 `save_api_key(provider_id, key_data)` 保存函数
4. 更新 `generate.py` 调用新函数

### Phase 2: UI 适配
1. 前端 API 层改为调用数据库端点
2. AI 设置页面 UI 保持不变（只需改后端）
3. 默认 provider 选择逻辑适配

### Phase 3: 构建脚本
1. 更新 `exclude_list.txt` 排除 DB 文件
2. 添加 ENV 示例文件生成（`env.example`）
3. 验证三个发布包均不含敏感数据

### Phase 4: 文档
1. 更新 README 说明 key 配置方式
2. 添加 `env.example` 模板

## 已知约束

- 用户首次使用 AI 功能前，必须先在 UI 填 key 或配置 ENV
- 已有的 `ai_providers.json` 结构保持兼容，只是 key 读取路径变更
