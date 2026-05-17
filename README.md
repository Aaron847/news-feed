# AI新闻日报 - 每日邮箱推送

每天早上8点自动抓取新闻，AI生成摘要，推送到邮箱。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件或直接设置环境变量：

```bash
# 必填 - SMTP邮件配置（以QQ邮箱为例）
set SMTP_SERVER=smtp.qq.com
set SMTP_PORT=465
set SMTP_USER=你的QQ邮箱@qq.com
set SMTP_PASSWORD=邮箱授权码          # QQ邮箱→设置→账户→生成授权码
set EMAIL_TO=收件邮箱@example.com

# 可选 - NewsAPI（不配置则跳过该源）
set NEWS_API_KEY=你的NewsAPI密钥       # https://newsapi.org 免费注册

# 可选 - Claude AI摘要（不配置则使用原始标题）
set ANTHROPIC_API_KEY=你的Claude API密钥
```

### 3. 测试运行

```bash
# 立即执行一次，验证流程
python main.py --now
```

### 4. 设置每日定时

**方案A：脚本内定时（需保持运行）**
```bash
python main.py                   # 默认8:00
python main.py --time 07:30      # 自定义时间
```

**方案B：Windows任务计划程序（推荐）**
```bash
# 打开任务计划程序，创建基本任务：
# 触发器：每天 08:00
# 操作：启动程序
#   程序：python
#   参数：D:\claude cc\news_feed\main.py --now
#   起始于：D:\claude cc\news_feed
```

PowerShell一键创建计划任务：
```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "main.py --now" -WorkingDirectory "D:\claude cc\news_feed"
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
Register-ScheduledTask -TaskName "AI新闻日报" -Action $action -Trigger $trigger -Description "每日8点推送AI新闻摘要到邮箱"
```

## 新闻源

| 类别 | 来源 |
|------|------|
| 科技AI | 36氪、机器之心、Ars Technica、The Verge、MIT Tech Review |
| 综合热点 | Reuters、BBC、NYT |
| 财经市场 | 华尔街见闻、FT、Bloomberg |

可在 `config.py` 中自定义RSS源和网页爬取目标。

## 自定义

- 修改 `config.py` 中的 `RSS_FEEDS` 添加/删除RSS源
- 修改 `WEB_SCRAPERS` 配置网页爬取目标
- 修改 `NEWSAPI_QUERIES` 调整NewsAPI查询关键词
- 修改 `NEWS_PER_CATEGORY` 调整每个类别的新闻数量上限
