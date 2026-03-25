import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.audio.stream import AudioStream
from engine.processor import AudioProcessor
from engine.routing import AudioRouting

# ==========================================
# 🎛️ 菜单 UI
# ==========================================
def show_menu():
    print("\n" + "=" * 70)
    print("🎛️ 实时变声系统")
    print("=" * 70)

    print("\n🎤 音色风格（可选1个）:")
    print("  1. normal")
    print("  2. doll（娃娃音）")
    print("  3. girl（少女音）")
    print("  4. lady（御姐音）")
    print("  5. boy（正太音）")
    print("  6. deep（磁性音）")
    print("  7. smoky（烟嗓）")

    print("\n🏠 空间效果（可选1个）:")
    print("  8. 房间反射（reflect）")
    print("  9. 回声（echo）")
    print(" 10. 大厅混响（reverb）")

    print("\n🤖 特殊效果（可选1个）:")
    print(" 11. 机器人")
    print(" 12. 电话")
    print(" 13. 卡通")

# ==========================================
# 🎯 解析用户输入
# ==========================================
def parse_choices(choice_list, routing: AudioRouting):

    voice_map = {
        "1": "normal",
        "2": "doll",
        "3": "girl",
        "4": "lady",
        "5": "boy",
        "6": "deep",
        "7": "smoky",
    }

    space_map = {
        "8": "reflect",
        "9": "echo",
        "10": "reverb",
    }

    special_map = {
        "11": "robot",
        "12": "telephone",
        "13": "cartoon",
    }

    # ⭐ 重置状态
    routing.reset()

    for choice in choice_list:

        # ===== 音色 =====
        if choice in voice_map:
            routing.set_voice(voice_map[choice])

        # ===== 空间 =====
        elif choice in space_map:
            routing.set_space(space_map[choice])

        # ===== 特效 =====
        elif choice in special_map:
            routing.set_special(special_map[choice])

        else:
            print(f"⚠️ 无效选项: {choice}")

def prompt_echo_ratio(routing: AudioRouting):
    while True:
        raw = input("请输入回声比例（0.0 ~ 0.95，直接回车使用 0.4）: ").strip()

        if raw == "":
            routing.set_echo_ratio(0.4)
            print("✅ 已使用默认回声比例: 0.4")
            return

        try:
            ratio = float(raw)
        except ValueError:
            print("⚠️ 请输入合法数字，例如 0.35")
            continue

        if 0.0 <= ratio <= 0.95:
            routing.set_echo_ratio(ratio)
            print(f"✅ 回声比例已设置为: {ratio}")
            return

        print("⚠️ 回声比例必须在 0.0 ~ 0.95 之间")

# ==========================================
# 🎧 运行
# ==========================================
def run_stream(processor):

    stream = AudioStream(
        fs=16000,
        block_size=1024,
        processor=processor
    )

    print("\n▶️ 音频流启动（Ctrl+f2 停止）")
    print("-" * 70)

    try:
        stream.start()

        counter = 0
        while True:
            time.sleep(1)
            counter += 1
            if counter % 5 == 0:
                print(f"⏱️ 运行中... {counter}s")

    except KeyboardInterrupt:
        print("\n👋 停止运行")
    finally:
        sys.exit(0)


# ==========================================
# 🚀 主程序
# ==========================================
def main():

    processor = AudioProcessor(fs=16000)
    routing = AudioRouting(processor)

    while True:
        show_menu()

        user_input = input("请输入组合: ").strip()

        if user_input == "0":
            print("👋 退出程序")
            break

        choices = user_input.split()

        # 🎯 应用组合
        parse_choices(choices, routing)

        if "9" in choices:
            prompt_echo_ratio(routing)

        # 🚀 启动处理
        run_stream(processor)


if __name__ == "__main__":
    main()