# Quantum Studio VPS 部署方案

> **服务器**: RackNerd KVM | Ubuntu 24.04 | 6GB RAM | 140GB Disk  
> **IP**: 107.172.78.150  
> **目标**: 部署 Backend (FastAPI) + Frontend (Next.js) + 定时任务

---

## Phase 1: 服务器初始化（SSH 后立即做）

```bash
# 1.1 更新系统
apt update && apt upgrade -y

# 1.2 创建非 root 用户
adduser deploy
usermod -aG sudo deploy

# 1.3 配置 SSH 安全
# 本地生成密钥: ssh-keygen -t ed25519
# 上传公钥到服务器:
ssh-copy-id deploy@107.172.78.150

# 修改 SSH 配置
nano /etc/ssh/sshd_config
# → PermitRootLogin no
# → PasswordAuthentication no
# → Port 2222  (改端口)
systemctl restart sshd

# 1.4 防火墙
ufw allow 2222/tcp   # SSH
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS
ufw enable
```

---

## Phase 2: 环境安装

```bash
# 2.1 Node.js 20 (前端)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt install -y nodejs

# 2.2 Python 3.12 (后端)
apt install -y python3.12 python3.12-venv python3-pip

# 2.3 Nginx (反向代理)
apt install -y nginx

# 2.4 Git
apt install -y git

# 2.5 其他工具
apt install -y htop curl unzip
```

---

## Phase 3: 代码部署

```bash
# 3.1 上传代码（从本地 Windows）
# 方法 A: Git (推荐)
# 在服务器:
su - deploy
mkdir -p ~/apps && cd ~/apps
git clone <你的仓库地址> quantum-studio
# 或 方法 B: scp 直传
# scp -P 2222 -r D:\AI_Projects\2026001\* deploy@107.172.78.150:~/apps/quantum-studio/

# 3.2 后端环境
cd ~/apps/quantum-studio/backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # 需要先生成，见下面

# 3.3 前端构建
cd ~/apps/quantum-studio/frontend
npm install
npm run build
```

---

## Phase 4: 配置文件

### 4.1 后端环境变量

```bash
# 创建 backend/.env
cat > ~/apps/quantum-studio/backend/.env << 'EOF'
# === API Keys ===
ARK_API_KEY=你的火山引擎Key
SURF_API_KEY=你的SurfAPI Key
GOOGLE_GENAI_API_KEY=你的Gemini Key
GROK_API_KEY=你的Grok Key

# === Google Sheets ===
# 凭证文件放在 backend/config/google_service_account.json
EOF
```

### 4.2 前端环境变量

```bash
# 创建 frontend/.env.local
cat > ~/apps/quantum-studio/frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://107.172.78.150:8000
EOF
# 如果配域名+SSL 则改为 https://你的域名
```

### 4.3 Google Sheets 凭证

```bash
# 从本地上传 service account JSON
scp -P 2222 "D:\AI_Projects\2026001\backend\config\google_service_account.json" \
  deploy@107.172.78.150:~/apps/quantum-studio/backend/config/
```

---

## Phase 5: Systemd 服务（进程守护）

### 5.1 后端服务

```bash
sudo tee /etc/systemd/system/quantum-backend.service << 'EOF'
[Unit]
Description=Quantum Studio Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/home/deploy/apps/quantum-studio/backend
Environment=PATH=/home/deploy/apps/quantum-studio/backend/venv/bin:/usr/bin
ExecStart=/home/deploy/apps/quantum-studio/backend/venv/bin/uvicorn \
  app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable quantum-backend
sudo systemctl start quantum-backend
```

### 5.2 前端服务

```bash
sudo tee /etc/systemd/system/quantum-frontend.service << 'EOF'
[Unit]
Description=Quantum Studio Frontend (Next.js)
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/home/deploy/apps/quantum-studio/frontend
ExecStart=/usr/bin/npm run start -- -p 3000
Restart=always
RestartSec=5
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable quantum-frontend
sudo systemctl start quantum-frontend
```

---

## Phase 6: Nginx 反向代理

```bash
sudo tee /etc/nginx/sites-available/quantum << 'EOF'
server {
    listen 80;
    server_name 107.172.78.150;  # 或你的域名

    # 前端
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 600;  # 管道运行需要长超时
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/quantum /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
```

---

## Phase 7: 定时任务

```bash
# 投研管道每天早上 9:00 北京时间 (UTC+8 → VPS 用 UTC)
crontab -e

# 添加:
0 1 * * * cd /home/deploy/apps/quantum-studio/backend && \
  /home/deploy/apps/quantum-studio/backend/venv/bin/python \
  scripts/test_full_pipeline.py >> /tmp/daily_research.log 2>&1
```

---

## Phase 8: 上线前检查清单

### 🔴 必须做

| # | 检查项 | 命令 |
|---|--------|------|
| 1 | **生成 requirements.txt** | 本地: `pip freeze > requirements.txt` |
| 2 | **API Keys 配置** | 检查 `.env` 中所有 Key 是否正确 |
| 3 | **Google Sheets 凭证** | 确认 `config/google_service_account.json` 已上传 |
| 4 | **Git 排除敏感文件** | `.gitignore` 加 `.env`, `config/`, `venv/` |
| 5 | **后端启动测试** | `curl http://127.0.0.1:8000/docs` |
| 6 | **前端构建测试** | `npm run build` 无报错 |
| 7 | **Surf API 余额** | 确认余额充足 |
| 8 | **Nginx 配置测试** | `sudo nginx -t` |

### 🟡 建议做

| # | 检查项 | 说明 |
|---|--------|------|
| 9 | 配域名 + SSL | Cloudflare 免费 DNS + Let's Encrypt |
| 10 | 日志轮转 | `logrotate` 防止日志撑爆磁盘 |
| 11 | 监控告警 | `htop` / UptimeRobot 免费监控 |
| 12 | 自动备份 | 每周打包 `reports/` 目录 |

---

## 上线执行顺序（一步步来）

```
① SSH 到服务器 → Phase 1 安全初始化
② Phase 2 安装环境
③ 本地先生成 requirements.txt
④ Phase 3 上传代码 + 安装依赖
⑤ Phase 4 配置 .env + 凭证
⑥ 手动测试: uvicorn 启动 → curl 测 API
⑦ 手动测试: npm start → 浏览器访问
⑧ Phase 5-6 配置 systemd + nginx
⑨ Phase 7 设置定时任务
⑩ 完整管道测试
```

---

## 注意事项

> [!CAUTION]
> **绝对不要**把 `.env` 和 `google_service_account.json` 提交到 Git！

> [!WARNING]
> 服务器在美国，调用火山引擎 API（中国大陆）可能有延迟。
> 如果延迟严重，考虑改用 Grok 或 OpenAI 等海外 API 替代 volcengine。

> [!TIP]
> 你的服务器 6GB RAM 完全够用。估计资源占用：
> - Backend: ~200MB
> - Frontend (build): ~300MB
> - 空闲时 CPU 几乎为 0，只在管道运行时占用
