# 🚀 Web 前端启动脚本与使用说明

一键检测/安装 Node.js、自动安装依赖、释放端口并启动 **Vite 开发服务器** 的 Python 脚本。

适用于：
- **Linux**（支持自动安装 Node.js）
- **macOS**（已安装 Node.js 时可用）
- **Windows**（已安装 Node.js 时可用）

---

## ✨ 特性

1. **自动安装 Node.js（Linux）**
   - 优先使用 **nvm**（无 sudo）安装到 `~/.nvm`
   - 必要时尝试系统包管理器（apt / yum）
2. **自动修正 PATH**  
   确保 Node/npm 可被 Python 子进程调用
3. **自动安装 npm 依赖**  
   仅在 `package.json` 改动或首次运行时执行
4. **启动前释放端口**  
   查占用并杀掉对应进程（lsof / fuser）
5. **启动 Vite 开发服务器**
6. **Ctrl+C** 安全退出  
   杀掉进程组，端口立即释放

---

## 📦 环境要求

- Python **3.5+**
- Node.js **>=16.20.0**  
  建议 LTS 版本（[Node 下载](https://nodejs.org/en/download/)）
- npm **>=8**
- 系统工具：
  - `curl`（安装 Node.js 时用）
  - `lsof` 或 `fuser`（释放端口时用）
  - `git`（从源码安装包时用）

**查看当前版本**
```bash
node -v
npm -v
python --version
```

## ⚡ 快速开始
```bash
git clone <your-repo-url>
cd your-repo/web
python run.py
```
启动后会自动：
- 检查 Node
- 自动安装依赖
- 启动 Vite Dev Server

| 平台    | 自动安装 Node.js | 自动修复 PATH | 自动释放端口 | 备注 |
|---------|-----------------|---------------|--------------|------|
| Linux   | ✅ 支持（nvm 无 sudo / apt / yum） | ✅ | ✅ | 推荐平台 |
| macOS   | ❌ （需手动安装 Node.js） | ✅ | ✅ | 可正常使用启动 |
| Windows | ❌ （需手动安装 Node.js） | ❌ | ✅ |  |


## 🔧 脚本使用方法
- **1. 修改后端服务URL及前端服务端口号**
编辑 `.env.development`修改后端服务地址
编辑 `vite.config.ts` 中的 `server.port`修改前端服务端口

- **2.默认启动** 默认启动（8080 端口或自动分配空闲端口）
```bash
python run.py
```

- **3.指定启动端口** （自动递增找空闲）
```bash
python run.py --port 8080
```

- **4.指定端口 + 严格固定** （占用时报错退出）
```bash
python run.py --port 8080 --strict
```

- **5.调试模式**
```bash
python run.py --debug
```

## ⚙️ 启动脚本流程图
脚本会执行以下逻辑：
1. **检测并安装 Node.js**  
   - 优先使用 **nvm（无 sudo）** 安装到 `$HOME/.nvm`，避免权限错误  
   - 必要时尝试用系统包管理器（apt/yum）安装
2. **自动修正 PATH**  
   - 安装完成后或检测到 nvm 安装的 Node，会自动将其加入到全局 PATH
3. **安装 `@rollup/rollup-linux-x64-gnu`**（仅 Linux x86_64）  
4. **自动检查并安装 npm 依赖**
5. **启动前释放端口**  
   - 检测指定端口占用情况（使用 `lsof`），如被占会杀掉占用进程
6. **启动 Vite 开发服务器**
7. **Ctrl+C 完整退出**  
   - 结束整个进程组，保证端口立即释放  

## 📄 项目结构
```bash
project/
│
├── run.py                   # Python 启动脚本（自动检测/安装 Node、依赖、释放端口并启动前端服务）
├── package.json             # 前端依赖与 npm 脚本配置
├── vite.config.ts           # Vite 构建工具配置文件
├── package-lock.json        # 依赖版本锁定文件（npm 自动生成）
├── public/                  # 公共静态资源（构建时会原样复制到最终输出目录）
├── src/                     # 前端项目源码
│   ├── api/                 # 接口配置与 API 请求封装
│   ├── components/          # 公共组件（可复用的 UI 组件）
│   ├── hooks/               # 自定义 Hooks（React）
│   ├── locales/             # 国际化语言配置文件
│   ├── redux/               # Redux 状态管理相关文件
│   ├── router/              # 路由配置与页面导航
│   ├── styles/              # 全局通用样式（CSS/SCSS）
│   ├── utils/               # 工具函数与通用方法
│   ├── views/               # 页面组件（按功能模块划分）
│   ├── App.tsx              # React 根组件
│   ├── main.tsx             # 项目入口文件，挂载 React 应用
│   ├── index.html           # HTML 模板文件（Vite 会将脚本注入此模板）
│   ├── .env.development     # 开发环境变量配置（如 API 请求地址）
│   ├── .env.production      # 生产环境变量配置
└── README.md                # 项目说明文档
```

## 🔧 开发者常用配置

在开发或部署前，可以根据需要修改以下文件的配置：

- **修改后端 API 地址**
  - **开发环境**：编辑 `.env.development`  
    例：
    ```env
    VITE_PROXY_TARGET=http://localhost:8080   # 你的开发环境后端地址
    ```
  - **生产环境**：编辑 `.env.production`  
    例：
    ```env
    VITE_API_BASE_URL=https://api.example.com
    ```

- **修改前端启动端口**
  - 编辑 `vite.config.ts` 中的 `server.port`  
    例：
    ```ts
    export default defineConfig({
      server: {
        port: 8080,        // 此处修改端口
        host: "0.0.0.0"
      }
    });
    ```

> 💡 提示：（环境变量 `.env.*` 文件的修改需要重启服务才能生效）


## 🛠 Linux 手动安装 Node（备用方案）
如果自动安装失败，可以手动安装 Node.js（≥16 LTS）：
### 方式 1：NodeSource 官方脚本
```bash
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs  # 或 apt install
```
### 方式 2：nvm 安装
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
source ~/.bashrc
nvm install 16
nvm use 16
nvm alias default 16
```

## 🚀 直接用现有Node启动（跳过 run.py）
```bash
npm install
npm install @rollup/rollup-linux-x64-gnu   # Linux x86_64 需要
npm run dev
```

## ❗ 常见问题
Q: 启动时报 node: command not found
A:
- Linux：直接运行 python3 run.py 自动安装 Node
- macOS/Windows：手动安装 Node.js 官网
Q: 启动时端口占用
A: 脚本会调用 lsof/fuser 自动释放，如系统无该命令，请安装：
```bash
sudo apt-get install -y lsof    # Debian/Ubuntu
sudo yum install -y lsof        # CentOS/RHEL
```
Q: 如何切换 Node 版本（nvm）
```bash
nvm install 16
nvm use 16
nvm alias default 16
```