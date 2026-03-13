import sys
import os
import importlib.util

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Project.src.audio.stream import AudioStream

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"🎵 {title}")
    print("=" * 70)

def print_footer(effect_name):
    """打印结束信息"""
    print("\n" + "=" * 70)
    print(f"🏁 {effect_name} 已停止")
    print("=" * 70)

def load_effect_class(module_path, class_name):
    """动态导入效果器类"""
    try:
        spec = importlib.util.spec_from_file_location(
            class_name,
            module_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, class_name)
    except Exception as e:
        print(f"❌ 导入失败 {module_path}: {e}")
        return None

def run_effect(effect_class, effect_name, fs=16000, block_size=256, **kwargs):
    """通用效果运行函数"""
    print_header(effect_name)

    # 创建效果器
    try:
        effect = effect_class(fs, **kwargs)
        print(f"✅ 效果器初始化成功")
    except Exception as e:
        print(f"❌ 效果器初始化失败: {e}")
        return

    # 创建音频流
    try:
        stream = AudioStream(
            fs=fs,
            block_size=block_size,
            processor=effect
        )
        print(f"✅ 音频流创建成功")
        print(f"📊 采样率: {fs}Hz, 块大小: {block_size}")
    except Exception as e:
        print(f"❌ 音频流创建失败: {e}")
        return

    print("▶️ 音频流已启动，按 Ctrl+C 停止...")
    print("-" * 70)

    try:
        stream.start()

        import time
        counter = 0
        while True:
            time.sleep(1)
            counter += 1
            if counter % 5 == 0:
                print(f"⏱️ 运行中... {counter}秒")

    except KeyboardInterrupt:
        print("\n👋 检测到中断信号，正在停止程序...")
    except Exception as e:
        print(f"\n❌ 运行时错误: {e}")
    finally:
        print_footer(effect_name)
        sys.exit(0)

# ==========================================
# 效果器映射
# ==========================================
EFFECTS = {
    "1": {
        "name": "卡通音效",
        "path": "src/dsp/effects/special effects/Cartoon.py",
        "class": "CartoonEffect",
        "params": {"pitch_ratio": 1.8}
    },
    "2": {
        "name": "机器人音效",
        "path": "src/dsp/effects/special effects/Robot.py",
        "class": "RobotEffect",
        "params": {"carrier_freq": 200}
    },
    "3": {
        "name": "电话音效",
        "path": "src/dsp/effects/special effects/telephone.py",
        "class": "TelephoneEffect",
        "params": {}
    },
    "4": {
        "name": "房间混响",
        "path": "src/dsp/effects/space effects/early_reflection.py",
        "class": "EarlyReflection",
        "params": {}
    },
    "5": {
        "name": "回声效果",
        "path": "src/dsp/effects/space effects/echo.py",
        "class": "EchoEffect",
        "params": {"delay_ms": 300, "decay": 0.5}
    },
    "6": {
        "name": "大厅混响",
        "path": "src/dsp/effects/space effects/schroeder_reverb.py",
        "class": "SchroederReverb",
        "params": {}
    }
}

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 70)
    print("🎛️  实时音频效果器选择")
    print("=" * 70)
    print("特殊效果:")
    for key in ["1", "2", "3"]:
        print(f"  {key}. {EFFECTS[key]['name']}")
    print("\n空间效果:")
    for key in ["4", "5", "6"]:
        print(f"  {key}. {EFFECTS[key]['name']}")
    print("\n  0. 退出程序")
    print("-" * 70)

def get_effect_by_number(choice):
    """根据数字获取效果器"""
    if choice in EFFECTS:
        return EFFECTS[choice]
    return None

def main():
    """主程序"""
    while True:
        show_menu()
        choice = input("请输入数字选择效果器 (0-6): ").strip()

        if choice == "0":
            print("\n👋 程序退出")
            break

        effect_info = get_effect_by_number(choice)
        if not effect_info:
            print("❌ 无效选择，请重新输入")
            continue

        # 导入效果器类
        module_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            effect_info["path"].replace("/", os.sep)
        )

        if not os.path.exists(module_path):
            print(f"❌ 文件不存在: {module_path}")
            continue

        effect_class = load_effect_class(module_path, effect_info["class"])
        if not effect_class:
            print(f"❌ 无法加载效果器: {effect_info['name']}")
            continue

        # 运行效果器
        run_effect(
            effect_class=effect_class,
            effect_name=effect_info["name"],
            fs=16000,
            block_size=256,
            **effect_info["params"]
        )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
    finally:
        sys.exit(0)