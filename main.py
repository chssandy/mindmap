from dify_plugin import Plugin, DifyPluginEnv

import os
import platform
import subprocess
import shutil
import sys

def run_cmd(cmd, shell=False, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    """执行命令并返回输出"""
    try:
        result = subprocess.run(cmd, shell=shell, check=check, stdout=stdout, stderr=stderr, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {' '.join(cmd) if not shell else cmd}")
        print(f"错误信息: {e.stderr.strip()}")
        return None

def check_command_installed(cmd_name):
    """检查某个命令是否已安装"""
    return shutil.which(cmd_name) is not None

def install_package_linux(package_manager, package_name):
    """使用包管理器安装指定软件包"""
    try:
        if package_manager == "apt":
            run_cmd(["sudo", "apt-get", "update"])
            run_cmd(["sudo", "apt-get", "install", "-y", package_name])
        elif package_manager == "yum":
            run_cmd(["sudo", "yum", "install", "-y", package_name])
        elif package_manager == "dnf":
            run_cmd(["sudo", "dnf", "install", "-y", package_name])
        elif package_manager == "pacman":
            run_cmd(["sudo", "pacman", "-Sy", "--noconfirm", package_name])
        else:
            print(f"⚠️ 不支持的包管理器: {package_manager}")
            return False
        return True
    except Exception as e:
        print(f"安装失败: {e}")
        return False

def detect_linux_distro():
    """检测Linux发行版"""
    try:
        with open("/etc/os-release") as f:
            data = f.read().lower()
            if "ubuntu" in data or "debian" in data:
                return "debian"
            elif "centos" in data or "rhel" in data or "red hat" in data:
                return "redhat"
            elif "fedora" in data:
                return "fedora"
            elif "arch" in data:
                return "arch"
            else:
                return "unknown"
    except:
        return "unknown"

def ensure_curl_installed():
    """确保系统中安装了 curl"""
    if not check_command_installed("curl"):
        print("⚠️ curl 未安装，正在尝试安装...")
        distro = detect_linux_distro()
        if distro == "debian":
            if not install_package_linux("apt", "curl"):
                return False
        elif distro in ["redhat", "fedora"]:
            if not install_package_linux("yum", "curl"):
                return False
        elif distro == "arch":
            if not install_package_linux("pacman", "curl"):
                return False
        else:
            print("无法确定系统类型，请手动安装 curl")
            return False
    return True

def install_node_linux():
    """在Linux上安装Node.js"""
    print("🔍 正在检测系统环境...")
    if not ensure_curl_installed():
        return False

    print("📥 正在下载并安装 NodeSource 安装脚本...")
    node_setup_script = 'https://deb.nodesource.com/setup_16.x'
    result = run_cmd(f"curl -fsSL {node_setup_script} | sudo -E bash -", shell=True)
    if not result:
        return False

    print("📦 正在安装 Node.js...")
    if detect_linux_distro() == "debian":
        if not install_package_linux("apt", "nodejs"):
            return False
    elif detect_linux_distro() in ["redhat", "fedora"]:
        if not install_package_linux("yum", "nodejs"):
            return False
    elif detect_linux_distro() == "arch":
        if not install_package_linux("pacman", "nodejs"):
            return False
    else:
        print("⚠️ 无法识别系统类型，尝试使用通用方式安装 Node.js")
        # 可选：使用 nvm 或手动下载二进制文件的方式

    return True

def install_homebrew():
    """在 macOS 上安装 Homebrew"""
    if not check_command_installed("brew"):
        print("🍺 Homebrew 未安装，正在尝试安装...")
        brew_install_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        result = run_cmd(brew_install_script, shell=True)
        if not result:
            return False
    return True

def install_node_macos():
    """在 macOS 上安装 Node.js"""
    if not install_homebrew():
        return False

    print("📦 正在通过 Homebrew 安装 Node.js...")
    if not run_cmd(["brew", "install", "node"]):
        return False

    return True

def install_node_windows():
    """在 Windows 上安装 Node.js"""
    print("📥 正在尝试下载 Node.js 安装包...")
    import urllib.request
    import tempfile
    import os

    node_url = "https://nodejs.org/dist/v16.20.2/node-v16.20.2-x64.msi"
    temp_dir = tempfile.gettempdir()
    msi_path = os.path.join(temp_dir, "node-installer.msi")

    try:
        print("🌐 正在下载 Node.js 安装包...")
        urllib.request.urlretrieve(node_url, msi_path)
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

    print("⚙️ 正在静默安装 Node.js...")
    try:
        run_cmd(f"msiexec /i {msi_path} /quiet", shell=True)
        print("🎉 安装成功！请重启终端以生效 Node.js 环境变量")
        return True
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return False

def check_node_installed():
    """检查 Node.js 是否已安装"""
    try:
        version = run_cmd(["node", "--version"], check=False)
        if version:
            print(f"✅ Node.js 已安装，版本为: {version}")
            return True
        else:
            print("❌ Node.js 未安装")
            return False
    except:
        return False

def install_node():
    """根据操作系统选择安装方式"""
    os_type = platform.system().lower()

    if os_type == "linux":
        return install_node_linux()
    elif os_type == "darwin":  # macOS
        return install_node_macos()
    elif os_type == "windows":
        return install_node_windows()
    else:
        print(f"🚫 当前系统 ({os_type}) 不支持自动安装 Node.js")
        return False

def main():
    print("=== 🛠️ Node.js 自动检测与安装工具 ===\n")

    if check_node_installed():
        print("✨ 你的环境中已经安装了 Node.js，无需额外操作。")
        return

    print("🔄 正在尝试自动安装 Node.js...\n")

    if install_node():
        print("\n✅ 成功安装 Node.js！")
        if check_node_installed():
            print("🎉 现在你可以正常使用 Node.js 相关的功能了！")
        else:
            print("⚠️ 安装完成后可能需要重新启动终端或设置环境变量。")
    else:
        print("\n❌ Node.js 安装失败，请尝试手动安装。")
        print("🔗 下载地址: https://nodejs.org/zh-cn/download/")


plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))

if __name__ == '__main__':

    # main()
    # 运行插件
    plugin.run()
