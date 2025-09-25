import sys
import os
import shutil
import subprocess
import argparse
from pathlib import Path
import platform
import signal

# ===== 禁用 Ctrl+Z（防止后台占用端口）=====
try:
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)
except AttributeError:
    pass

# ===== Python 版本检测 =====
MIN_PYTHON = (3, 5)
if sys.version_info < MIN_PYTHON:
    sys.exit("❌ 需要 Python {0}.{1}+，当前为 {2}".format(
        MIN_PYTHON[0], MIN_PYTHON[1], sys.version.split()[0]))
print("🐍 Python {} OK".format(sys.version.split()[0]))

REQUIRED_NODE_MAJOR = 16

project_dir = Path(os.path.abspath(os.path.dirname(__file__)))
node_modules = project_dir / "node_modules"
package_json = project_dir / "package.json"
package_lock = project_dir / "package-lock.json"

def debug_info():
    print("\n===== [DEBUG] 环境信息 =====")
    print("🐍 Python 版本:", sys.version.split()[0])
    print("🐍 Python 路径:", sys.executable)
    print("📂 当前工作目录:", os.getcwd())
    print("🛤 PATH:", os.environ.get("PATH"))
    try:
        node_path = shutil.which("node")
        if node_path:
            node_ver = subprocess.Popen([node_path, "-v"], stdout=subprocess.PIPE, env=os.environ.copy()).communicate()[0]
            print("🟢 Node 路径:", node_path)
            print("🟢 Node 版本:", node_ver.decode().strip())
        else:
            print("⚠️ Node 未找到")
    except Exception:
        print("⚠️ Node 检测出错")
    print("===== [DEBUG END] =====\n")

# ==== 启动前释放端口（Linux/macOS 纯命令） ====
def free_port(port):
    try:
        # -t 仅输出 TCP 连接
        # -i:<port> 只匹配指定端口
        # -sTCP:LISTEN 仅监听状态
        pid_list = subprocess.check_output(
            "lsof -ti:{port} -sTCP:LISTEN".format(port=port),
            shell=True
        ).decode().strip().split("\n")
    except subprocess.CalledProcessError:
        pid_list = []

    for pid in pid_list:
        if pid.strip():
            try:
                print("🔴 端口 {} 被进程 {} 占用，正在结束...".format(port, pid))
                os.kill(int(pid.strip()), signal.SIGTERM)
                print("✅ 已释放端口 {}".format(port))
            except Exception as e:
                print("⚠️ 无法终止进程 {}: {}".format(pid, e))

# ==== 运行命令（支持 Ctrl+C 杀掉整个进程组）====
def run_cmd(cmd, cwd=None, shell=False):
    cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
    print("🔹 执行命令: {}".format(cmd_str))

    process = subprocess.Popen(
        cmd, cwd=cwd, shell=shell, env=os.environ.copy(),
        preexec_fn=os.setsid
    )

    try:
        process.wait()
    except KeyboardInterrupt:
        print("\n🛑 检测到 Ctrl+C，正在终止子进程...")
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except OSError:
            pass
        process.wait()
        print("✅ 子进程已终止，端口已释放")

# ==== 检测 Node 版本（自动加载 nvm，并修正 PATH）====
def get_node_version():
    env = os.environ.copy()
    nvm_sh = Path.home() / ".nvm" / "nvm.sh"

    if nvm_sh.exists():
        try:
            node_path = subprocess.check_output(
                "bash -c 'source {} && which node'".format(nvm_sh),
                shell=True
            ).decode().strip()
            if node_path:
                node_bin_dir = os.path.dirname(node_path)
                env["PATH"] = node_bin_dir + os.pathsep + env["PATH"]
                os.environ["PATH"] = node_bin_dir + os.pathsep + os.environ["PATH"]
                print("🛠 已将 {} 添加到全局 PATH".format(node_bin_dir))
        except subprocess.CalledProcessError:
            pass

    try:
        result = subprocess.Popen(["node", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        out, _ = result.communicate()
        ver = out.decode("utf-8").strip().lstrip("v")
        major = int(ver.split(".")[0])
        return major, ver
    except (OSError, ValueError):
        return None, None

# ==== 无 sudo 安装 Node ====
def install_node_linux():
    print("📦 开始安装 Node.js (优先无 sudo 模式)...")

    home = str(Path.home())
    nvm_dir = os.path.join(home, ".nvm")

    if not Path(nvm_dir).exists():
        print("💡 下载并安装 NVM（Gitee 源，无 sudo 安全模式）...")
        run_cmd(
            "export PROFILE=/dev/null && "
            "curl -o- https://gitee.com/RubyMetric/nvm-cn/raw/main/install.sh | bash",
            shell=True
        )

    nvm_sh = os.path.join(nvm_dir, "nvm.sh")
    if Path(nvm_sh).exists():
        print("🔹 使用 NVM 安装 Node.js 16 LTS (国内镜像)")
        run_cmd(
            "bash -c 'export NVM_NODEJS_ORG_MIRROR=https://npmmirror.com/mirrors/node "
            "&& source {} && nvm install 16 --lts --no-use && nvm alias default 16 && nvm use default'".format(nvm_sh),
            shell=True
        )
        run_cmd("bash -c 'source {} && npm config set registry https://registry.npmmirror.com'".format(nvm_sh), shell=True)
        print("✅ Node.js 已安装到用户目录: {}".format(nvm_dir))

        # 删除 nvm-update.sh 文件
        nvm_update_paths = [
            Path.home() / "nvm-update.sh",
            Path(nvm_dir) / "nvm-update.sh"
        ]
        for p in nvm_update_paths:
            if p.exists():
                try:
                    p.unlink()
                    print("🗑 已删除 {}".format(p))
                except Exception as e:
                    print("⚠️ 删除 {} 失败: {}".format(p, e))

        try:
            node_path = subprocess.check_output("bash -c 'source {} && which node'".format(nvm_sh), shell=True).decode().strip()
            node_bin_dir = os.path.dirname(node_path)
            os.environ["PATH"] = node_bin_dir + os.pathsep + os.environ["PATH"]
            print("🛠 已将 {} 添加到全局 PATH".format(node_bin_dir))
        except subprocess.CalledProcessError:
            print("⚠️ 无法获取 nvm node 路径，可能导致 npm 调用失败")

        return

    print("⚠️ NVM 安装失败或 nvm.sh 不存在，尝试全局安装（需 sudo）")

    def has_sudo():
        try:
            subprocess.check_call(
                ["sudo", "-n", "true"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    if shutil.which("apt-get") and has_sudo():
        print("🔹 使用 apt-get 安装 Node.js 16 LTS")
        run_cmd("curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -", shell=True)
        run_cmd(["sudo", "apt-get", "install", "-y", "nodejs"])
        return

    if shutil.which("yum") and has_sudo():
        print("🔹 使用 yum 安装 Node.js 16 LTS")
        run_cmd("curl -fsSL https://rpm.nodesource.com/setup_16.x | sudo bash -", shell=True)
        run_cmd(["sudo", "yum", "install", "-y", "nodejs"])
        return

    sys.exit("❌ 无法自动安装 Node.js，请手动安装 16.x 版本: https://nodejs.org/en/download/")

# ==== Node 检查 ====
def check_node_version_and_install():
    cur_major, cur_full = get_node_version()

    if cur_major is None:
        print("❌ 未检测到 Node.js，开始安装...")
        if platform.system() == "Linux":
            install_node_linux()
        else:
            sys.exit("⚠️ 请手动安装 Node.js >=16: https://nodejs.org/en/download/")
    elif cur_major < REQUIRED_NODE_MAJOR:
        print("⚠️ 检测到 Node.js {} 版本过低，正在升级...".format(cur_full))
        if platform.system() == "Linux":
            install_node_linux()
        else:
            sys.exit("⚠️ 请升级 Node.js >= {}: https://nodejs.org/en/download/".format(REQUIRED_NODE_MAJOR))
    else:
        print("🟢 Node.js {} OK（跳过安装）".format(cur_full))

# ==== Rollup 安装 ====
def install_linux_rollup():
    if platform.system() == "Linux" and platform.machine() == "x86_64":
        try:
            subprocess.check_call(
                ["npm", "list", "@rollup/rollup-linux-x64-gnu"], 
                cwd=project_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ.copy()
            )
            print("✅ @rollup/rollup-linux-x64-gnu 已安装（跳过）")
        except subprocess.CalledProcessError:
            print("📦 安装 @rollup/rollup-linux-x64-gnu...")
            run_cmd(["npm", "install", "@rollup/rollup-linux-x64-gnu", "--save-dev"], cwd=project_dir)
    else:
        print("ℹ️ 当前平台不是 Linux x86_64，跳过 rollup 安装")

# ==== 安装依赖 ====
def install_deps():
    def mtime(path):
        try:
            return os.path.getmtime(path)
        except OSError:
            return 0

    if (not node_modules.exists() or
        mtime(package_json) > mtime(node_modules) or
        (package_lock.exists() and mtime(package_lock) > mtime(node_modules))):
        print("📦 安装 npm 依赖中...")
        run_cmd(["npm", "install"], cwd=project_dir)
    else:
        print("✅ 依赖已安装（跳过 npm install）")

# ==== 启动开发服务器 ====
def start_dev(port=None, strict=False, open_browser=False):
    if port:
        free_port(port)  # 启动前释放端口

    print("🚀 当前环境已准备就绪，启动开发服务器...")
    cmd = ["npm", "run", "dev"]

    if port:
        cmd.extend(["--", "--port={}".format(port), "--host=0.0.0.0"])
    else:
        cmd.extend(["--", "--host=0.0.0.0"])

    if open_browser:
        cmd.append("--open")

    if strict:
        cmd.append("--strictPort")

    run_cmd(cmd, cwd=project_dir)

# ==== 主入口 ====
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="启动 Web 项目")
    parser.add_argument("--port", type=int, help="启动端口")
    parser.add_argument("--strict", action="store_true", help="严格端口模式（不自动+1）")
    parser.add_argument("--debug", action="store_true", help="打印调试信息")
    parser.add_argument("--open-browser", action="store_true", help="启动时自动打开浏览器（默认不开）")
    args = parser.parse_args()

    if args.debug:
        debug_info()

    check_node_version_and_install()
    install_linux_rollup()
    install_deps()
    start_dev(port=args.port, strict=args.strict, open_browser=args.open_browser)
