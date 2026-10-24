# 贡献指南

## 项目结构

```
website/
├── config/              # Django 项目配置
│   ├── settings.py      # 主设置（数据库、静态文件、存储等）
│   ├── urls.py          # URL 路由
│   └── wsgi.py          # WSGI 入口（Vercel 部署使用）
├── pages/               # 主应用
│   ├── models.py        # 数据模型（Activity, Project）
│   ├── admin.py         # Admin 后台配置
│   ├── views.py         # 视图函数
│   ├── static/pages/    # 静态文件（CSS, JS, 图片）
│   └── templates/pages/ # HTML 模板
├── pyproject.toml       # 依赖管理（uv 使用）
├── requirements.txt     # 自动生成的依赖清单（Vercel 使用）
└── vercel.json          # Vercel 部署配置
```

## 本地开发

### 环境要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 包管理器

### 初始化项目

```bash
# 安装依赖
uv sync

# 运行迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

### 添加新依赖

```bash
# 添加生产依赖
uv add some-package

# 添加开发依赖
uv add --dev pytest some-test-package
```

## 部署流程

### 1. 更新依赖清单

每次添加或更新依赖后，必须重新生成 `requirements.txt`：

```bash
uv pip compile pyproject.toml -o requirements.txt
```

### 2. 提交代码

```bash
git add pyproject.toml requirements.txt uv.lock
git commit -m "Update dependencies"
git push
```

### 3. Vercel 自动构建

推送后 Vercel 会自动：

1. 检测 `config/wsgi.py` → 使用 `@vercel/python` builder
2. 通过 `requirements.txt` 安装依赖（pip）
3. 检测 `STATIC_ROOT` → 自动运行 `collectstatic`
4. 将静态文件上传到 Vercel CDN
5. 部署 WSGI 应用，whitenoise 提供静态文件服务

**无需手动配置 build 脚本或提交 `staticfiles/` 目录。**

## 环境变量配置

在 Vercel Dashboard → Project Settings → Environment Variables 中配置：

### 必需的环境变量

```bash
# 数据库（Neon Postgres）
POSTGRES_URL=postgresql://...

# Cloudinary 存储
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Django 配置
DJANGO_SECRET_KEY=your-secret-key
DEBUG=False
```

### 本地开发环境变量

在项目根目录创建 `.env` 文件：

```bash
POSTGRES_URL=postgresql://...  # 可选，默认使用 SQLite
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
DJANGO_SECRET_KEY=dev-secret-key
DEBUG=True
```

## 首次部署：创建超级用户

新部署的数据库需要创建管理员账号：

### 方法 1：本地连接远程数据库（推荐）

```bash
# 设置环境变量指向远程数据库
export POSTGRES_URL="你的 Neon 数据库 URL"
export DJANGO_SUPERUSER_PASSWORD="你的密码"

# 运行创建超级用户命令
python manage.py create_initial_superuser \
  --username admin \
  --email admin@example.com
```

### 方法 2：使用环境变量文件

创建 `.env.remote` 文件：

```bash
POSTGRES_URL=postgresql://...
DJANGO_SUPERUSER_PASSWORD=your-password
```

然后运行：

```bash
env $(cat .env.remote | xargs) python manage.py create_initial_superuser \
  --username admin \
  --email admin@example.com
```

创建成功后，访问 `https://你的域名.vercel.app/admin/` 登录。

## 静态文件管理

### 开发环境

静态文件存放在 `pages/static/pages/` 目录：

```
pages/static/pages/
├── css/
│   └── style.css
├── js/
│   └── app.js
├── Artboard.png
└── favicon.png
```

### 生产环境

- Vercel 自动运行 `collectstatic`，将所有静态文件收集到 `staticfiles/`
- 静态文件通过 Vercel CDN 提供，无需手动上传
- `staticfiles/` 目录已加入 `.gitignore`，**不要提交到 git**

### 添加新的静态文件

1. 将文件放入 `pages/static/pages/` 对应子目录
2. 在模板中使用 `{% static %}` 标签引用：

```django
{% load static %}
<img src="{% static 'pages/Artboard.png' %}" alt="Logo">
<link rel="stylesheet" href="{% static 'pages/css/style.css' %}">
```

## 数据模型

### Activity（活动）

```python
class Activity(models.Model):
    title = models.CharField("活动名称", max_length=200)
    description = models.TextField("活动描述", blank=True)
    start_date = models.DateField("开始日期")
    end_date = models.DateField("结束日期", blank=True, null=True)
    location = models.CharField("地点", max_length=200, blank=True)
    status = models.CharField("状态", max_length=50, choices=STATUS_CHOICES)
    category = models.CharField("类别", max_length=100, blank=True)
    organizer = models.CharField("组织者", max_length=200, blank=True)
```

### Project（项目）

```python
class Project(models.Model):
    title = models.CharField("项目名称", max_length=200)
    description = models.TextField("项目描述", blank=True)
    video = models.URLField("视频链接", blank=True)  # Cloudinary URL
    link = models.URLField("项目链接", blank=True)
    order = models.PositiveIntegerField("排序", default=0)
```

### 通过 Admin 后台管理数据

1. 登录 `/admin/`
2. 添加/编辑 Activity 和 Project 记录
3. Project 支持拖拽排序（通过 `order` 字段）

## 常见问题

### Q: 为什么需要 `requirements.txt`？

Vercel 的 `@vercel/python` builder 使用 `pip` 安装依赖，需要 `requirements.txt`。`pyproject.toml` 用于本地开发（`uv`），`requirements.txt` 用于生产部署。

### Q: 如何更新依赖版本？

```bash
# 更新所有依赖到最新兼容版本
uv lock --upgrade

# 重新生成 requirements.txt
uv pip compile pyproject.toml -o requirements.txt

# 提交
git add uv.lock requirements.txt
git commit -m "Upgrade dependencies"
```

### Q: 本地测试生产环境配置

```bash
# 设置生产环境变量
export DEBUG=False
export POSTGRES_URL="你的 Neon URL"
export VERCEL_ENV=production

# 运行 collectstatic
python manage.py collectstatic --noinput

# 启动服务器
python manage.py runserver
```

### Q: 静态文件 404 错误

1. 检查 `STATIC_ROOT` 是否正确配置（`config/settings.py`）
2. 确认 `VERCEL_ENV` 或 `PRODUCTION` 环境变量已设置
3. 查看 Vercel 构建日志，确认 `collectstatic` 是否成功运行
4. 检查文件是否在 `pages/static/pages/` 目录下

## 技术栈

- **后端框架**: Django 6.1+
- **包管理**: uv + pyproject.toml
- **数据库**: Neon Postgres（生产）/ SQLite（本地开发）
- **文件存储**: Cloudinary（生产）/ 本地文件系统（开发）
- **静态文件**: WhiteNoise + Vercel CDN
- **部署平台**: Vercel（@vercel/python builder）

## 开发规范

- 使用中文作为模型字段的 `verbose_name`
- 所有模型添加 `class Meta` 配置 `verbose_name` 和 `verbose_name_plural`
- 视图函数使用 `@require_GET` 或 `@require_POST` 装饰器
- 模板文件使用 `{% load static %}` 引用静态资源
- 提交前运行 `python manage.py check` 检查配置错误
