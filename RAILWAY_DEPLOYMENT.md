# Railway 部署完整指南

## 📋 部署前准备

### 1. 注册 Railway 账号
访问 [Railway.app](https://railway.app/) 并注册账号（支持 GitHub 登录）

### 2. 准备 Qwen API Key
- 访问 [阿里云百炼平台](https://dashscope.aliyun.com/)
- 注册并获取 API Key
- 记录你的 API Key（格式：`sk-xxxxxx`）

---

## 🚀 方式一：通过 Railway Web 界面部署（推荐新手）

### 步骤 1: 创建新项目

1. 登录 Railway 控制台
2. 点击 **"New Project"**
3. 选择 **"Deploy from GitHub repo"**
4. 授权 Railway 访问你的 GitHub
5. 选择 `k12/backend` 仓库

### 步骤 2: 添加 PostgreSQL 数据库

1. 在项目页面点击 **"+ New"**
2. 选择 **"Database"** → **"Add PostgreSQL"**
3. Railway 会自动创建数据库并注入 `DATABASE_URL` 环境变量

### 步骤 3: 添加 Redis 缓存

1. 再次点击 **"+ New"**
2. 选择 **"Database"** → **"Add Redis"**
3. Railway 会自动创建 Redis 并注入 `REDIS_URL` 环境变量

### 步骤 4: 配置环境变量

点击你的应用服务（backend），进入 **"Variables"** 标签页，添加以下环境变量：

#### 必需的环境变量：

```bash
# Qwen API 配置（必填）
QWEN_API_KEY=sk-your-actual-api-key-here
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_TEXT_MODEL=qwen-max
QWEN_OCR_MODEL=qwen-vl-max
QWEN_EMBEDDING_MODEL=text-embedding-v3

# 应用配置
APP_NAME=智能学习助手
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# 安全配置（重要：请修改为随机字符串）
SECRET_KEY=your-random-secret-key-change-this-in-production
JWT_SECRET_KEY=your-random-jwt-secret-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS 配置（根据你的前端域名修改）
# 方式1: 允许所有来源（仅用于开发/测试）
CORS_ORIGINS=*

# 方式2: 指定单个域名
# CORS_ORIGINS=https://your-frontend.com

# 方式3: 指定多个域名（用逗号分隔）
# CORS_ORIGINS=https://your-frontend.com,https://www.your-frontend.com,https://app.your-domain.com

# 限流配置
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Agent 配置
AGENT_TIMEOUT_SECONDS=30
AGENT_RETRY_ATTEMPTS=3
AGENT_MAX_TOKENS=4000

# 缓存配置
CACHE_TTL_SECONDS=3600
ANALYSIS_CACHE_TTL=3600
```

#### 自动注入的环境变量（无需手动添加）：
- `DATABASE_URL` - PostgreSQL 连接地址（自动）
- `REDIS_URL` - Redis 连接地址（自动）
- `PORT` - 应用端口（自动）

### 步骤 5: 生成安全密钥

在本地终端运行以下命令生成随机密钥：

```bash
# 生成 SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成 JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

将生成的密钥复制到 Railway 的环境变量中。

### 步骤 6: 部署

1. 环境变量配置完成后，Railway 会自动触发部署
2. 在 **"Deployments"** 标签页查看部署进度
3. 等待部署完成（约 3-5 分钟）

### 步骤 7: 验证部署

部署成功后：

1. 点击 **"Settings"** → **"Generate Domain"** 生成公开访问域名
2. 访问 `https://your-app.railway.app/health` 检查健康状态
3. 访问 `https://your-app.railway.app/docs` 查看 API 文档

---

## 🖥️ 方式二：通过 Railway CLI 部署（推荐开发者）

### 步骤 1: 安装 Railway CLI

```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# 或使用 npm
npm i -g @railway/cli

# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex
```

### 步骤 2: 登录 Railway

```bash
railway login
```

浏览器会打开，完成授权后返回终端。

### 步骤 3: 初始化项目

```bash
# 在项目根目录执行
cd /Users/tew/Projects/k12/backend

# 创建新项目
railway init

# 或链接到已有项目
railway link
```

### 步骤 4: 添加数据库服务

```bash
# 添加 PostgreSQL
railway add --plugin postgresql

# 添加 Redis
railway add --plugin redis
```

### 步骤 5: 配置环境变量

```bash
# 方式 A: 逐个设置
railway variables set QWEN_API_KEY=sk-your-actual-api-key-here
railway variables set QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
railway variables set QWEN_TEXT_MODEL=qwen-max
railway variables set QWEN_OCR_MODEL=qwen-vl-max
railway variables set QWEN_EMBEDDING_MODEL=text-embedding-v3
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=INFO

# 生成并设置安全密钥
railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# 设置 CORS（根据你的前端域名修改）
railway variables set CORS_ORIGINS=https://your-frontend.com

# 方式 B: 从本地 .env 文件批量导入
# 先创建 .env.production 文件，然后：
railway variables set --from-file .env.production
```

### 步骤 6: 部署应用

```bash
# 部署到 Railway
railway up

# 或者使用 GitHub 自动部署
railway up --detach
```

### 步骤 7: 查看部署状态

```bash
# 查看日志
railway logs

# 查看服务状态
railway status

# 打开项目控制台
railway open
```

### 步骤 8: 生成公开域名

```bash
# 生成域名
railway domain

# 或在 Web 界面操作
railway open
# 然后在 Settings → Networking → Generate Domain
```

---

## 🔧 部署后配置

### 1. 运行数据库迁移

Railway 会在部署时自动运行 `scripts/railway_init.sh`，该脚本会：
- 等待数据库就绪
- 自动运行 `alembic upgrade head`

如果需要手动运行：

```bash
# 通过 CLI
railway run alembic upgrade head

# 或在 Web 界面的 Shell 中执行
```

### 2. 查看应用日志

```bash
# 实时查看日志
railway logs --follow

# 查看最近的日志
railway logs --tail 100
```

### 3. 连接到数据库

```bash
# 获取数据库连接信息
railway variables

# 使用 Railway CLI 连接
railway connect postgres

# 或使用本地工具连接（复制 DATABASE_URL）
```

---

## 📊 监控和维护

### 查看资源使用情况

1. 登录 Railway 控制台
2. 进入项目页面
3. 查看 **"Metrics"** 标签页
   - CPU 使用率
   - 内存使用
   - 网络流量
   - 请求数量

### 免费额度说明

Railway 免费计划提供：
- **$5/月** 使用额度
- 约 **500 小时** 运行时间
- **100GB** 出站流量

超出后需要升级到付费计划（$5/月起）。

### 优化建议

1. **启用休眠**（可选）：如果流量不大，可以配置在无请求时自动休眠
2. **监控日志**：定期检查错误日志
3. **备份数据库**：定期导出数据库备份

---

## 🐛 常见问题

### 1. 部署失败：找不到 Dockerfile

**解决方案**：确保 `Dockerfile` 在项目根目录，且 `railway.json` 配置正确。

### 2. 数据库连接失败

**解决方案**：
- 检查 `DATABASE_URL` 是否正确注入
- 确保 PostgreSQL 服务已启动
- 查看 `railway logs` 获取详细错误

### 3. Qwen API 调用失败

**解决方案**：
- 检查 `QWEN_API_KEY` 是否正确设置
- 确认 API Key 有足够的额度
- 检查网络连接（Railway 服务器在海外，确保能访问阿里云 API）

### 4. CORS 错误

**解决方案**：
- 在 `CORS_ORIGINS` 中添加你的前端域名
- 确保格式正确：`https://domain.com`（不要加尾部斜杠）

### 5. 内存不足

**解决方案**：
- 升级到付费计划获得更多内存
- 优化代码减少内存使用
- 调整 `DATABASE_POOL_SIZE` 等配置

---

## 🔄 更新部署

### 自动部署（推荐）

1. 在 Railway 项目设置中启用 **"Auto Deploy"**
2. 每次 push 到 GitHub 主分支时自动部署

### 手动部署

```bash
# 使用 CLI
railway up

# 或在 Web 界面点击 "Deploy"
```

---

## 📝 环境变量检查清单

部署前请确认以下环境变量已设置：

- [ ] `QWEN_API_KEY` - Qwen API 密钥（必需）
- [ ] `SECRET_KEY` - 应用密钥（必需，随机生成）
- [ ] `JWT_SECRET_KEY` - JWT 密钥（必需，随机生成）
- [ ] `CORS_ORIGINS` - 前端域名（必需）
- [ ] `ENVIRONMENT=production` - 生产环境标识
- [ ] `LOG_LEVEL=INFO` - 日志级别
- [ ] `DATABASE_URL` - 自动注入（无需手动设置）
- [ ] `REDIS_URL` - 自动注入（无需手动设置）

---

## 🎉 部署完成

部署成功后，你的 API 将在以下地址可用：

- **API 文档**: `https://your-app.railway.app/docs`
- **健康检查**: `https://your-app.railway.app/health`
- **API 端点**: `https://your-app.railway.app/api/v1/`

---

## 📞 获取帮助

- Railway 文档: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- 项目 Issues: 提交到你的 GitHub 仓库

---

## 🔐 安全提示

1. **不要**将 `.env` 文件提交到 Git
2. **定期更换** SECRET_KEY 和 JWT_SECRET_KEY
3. **限制** CORS_ORIGINS 只允许可信域名
4. **启用** Railway 的访问日志监控
5. **定期检查** Qwen API 使用量，避免超额

---

祝部署顺利！🚀
