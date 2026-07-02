from cutter import process_video
import os
import re
import importlib
import config

CONFIG_PATH = "config.py"


COLOR_OPTIONS = {
    "1": ("White", "white"),
    "2": ("Black", "black"),
    "3": ("Red", "red"),
    "4": ("Green", "green"),
    "5": ("Blue", "blue"),
    "6": ("Yellow", "yellow"),
    "7": ("Cyan", "cyan"),
    "8": ("Magenta", "magenta"),
    "9": ("Orange", "orange"),
    "10": ("Purple", "purple"),

    "11": ("Navy", "navy"),
    "12": ("Dark Blue", "darkblue"),
    "13": ("Dark Green", "darkgreen"),
    "14": ("Dark Red", "darkred"),
    "15": ("Dark Cyan", "darkcyan"),
    "16": ("Dark Magenta", "darkmagenta"),
    "17": ("Dark Orange", "darkorange"),
    "18": ("Dark Violet", "darkviolet"),
    "19": ("Dark Gray", "darkgray"),
    "20": ("Dark Slate Gray", "darkslategray"),

    "21": ("Light Blue", "lightblue"),
    "22": ("Light Green", "lightgreen"),
    "23": ("Light Pink", "lightpink"),
    "24": ("Light Yellow", "lightyellow"),
    "25": ("Light Gray", "lightgray"),
    "26": ("Light Cyan", "lightcyan"),
    "27": ("Lavender", "lavender"),
    "28": ("Beige", "beige"),
    "29": ("Ivory", "ivory"),
    "30": ("Snow", "snow"),

    "31": ("Royal Blue", "royalblue"),
    "32": ("Deep Sky Blue", "deepskyblue"),
    "33": ("Dodger Blue", "dodgerblue"),
    "34": ("Steel Blue", "steelblue"),
    "35": ("Slate Blue", "slateblue"),
    "36": ("Forest Green", "forestgreen"),
    "37": ("Sea Green", "seagreen"),
    "38": ("Lime Green", "limegreen"),
    "39": ("Gold", "gold"),
    "40": ("Golden Rod", "goldenrod"),

    "41": ("Coral", "coral"),
    "42": ("Tomato", "tomato"),
    "43": ("Salmon", "salmon"),
    "44": ("Chocolate", "chocolate"),
    "45": ("Crimson", "crimson"),
    "46": ("Hot Pink", "hotpink"),
    "47": ("Deep Pink", "deeppink"),
    "48": ("Medium Violet Red", "mediumvioletred"),
    "49": ("Turquoise", "turquoise"),
    "50": ("Aqua", "aqua"),

    "51": ("Neon Blue", "#00BFFF"),
    "52": ("Neon Cyan", "#00E5FF"),
    "53": ("Neon Green", "#00FF7F"),
    "54": ("Neon Pink", "#FF1493"),
    "55": ("Neon Purple", "#C71585"),
    "56": ("Neon Orange", "#FF8C00"),
    "57": ("Neon Yellow", "#FFFF33"),
    "58": ("Neon Red", "#FF3131"),
    "59": ("Midnight Blue", "#071426"),
    "60": ("Royal Navy", "#0B1F3A"),
}


def banner():
    print(r"""
╔══════════════════════════════════════════════════════╗
║                                                      ║
║             AUTO VIDEO CUTTER PRO v2.0              ║
║                                                      ║
║        Square Video 720x720 + Background 9:16        ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
""")


def get_config_value(name, default):
    return getattr(config, name, default)


def update_config(values):
    if not os.path.exists(CONFIG_PATH):
        print("config.py tidak ditemukan.")
        return False

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    for key, value in values.items():
        line = f"{key} = {value}"
        pattern = rf"^{key}\s*=.*$"

        if re.search(pattern, content, flags=re.MULTILINE):
            content = re.sub(
                pattern,
                line,
                content,
                flags=re.MULTILINE
            )
        else:
            content += f"\n{line}"

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

    importlib.reload(config)
    return True


def ask_int(label, default):
    while True:
        value = input(f"{label} [{default}]: ").strip()

        if value == "":
            return int(default)

        if value.isdigit():
            return int(value)

        print("Input harus angka.")


def print_color_menu(label):
    print("\n" + "=" * 54)
    print(f"PILIH {label}")
    print("=" * 54)

    groups = [
        ("BASIC", range(1, 11)),
        ("DARK", range(11, 21)),
        ("LIGHT", range(21, 31)),
        ("PREMIUM", range(31, 51)),
        ("NEON", range(51, 61)),
    ]

    for group_name, nums in groups:
        print(f"\n[{group_name}]")
        for number in nums:
            key = str(number)
            name, value = COLOR_OPTIONS[key]
            print(f"{key:>2}. {name:<22} {value}")


def ask_color(label, default):
    print_color_menu(label)

    while True:
        value = input(f"\nPilih {label} [default: {default}]: ").strip()

        if value == "":
            return f'"{default}"'

        if value in COLOR_OPTIONS:
            color_name, color_value = COLOR_OPTIONS[value]
            print(f"{label} dipilih: {color_name} ({color_value})")
            return f'"{color_value}"'

        print("Nomor warna tidak valid. Pilih 1 sampai 60.")


def show_current_settings():
    print("\n" + "=" * 54)
    print("SETTING SAAT INI")
    print("=" * 54)
    print(f"MIN_DURATION      : {get_config_value('MIN_DURATION', '-')}")
    print(f"MAX_DURATION      : {get_config_value('MAX_DURATION', '-')}")
    print(f"FONT_SIZE         : {get_config_value('FONT_SIZE', '-')}")
    print(f"FONT_SIZE_PART    : {get_config_value('FONT_SIZE_PART', '-')}")
    print(f"WM_SIZE           : {get_config_value('WM_SIZE', '-')}")
    print(f"BG_COLOR          : {get_config_value('BG_COLOR', '-')}")
    print(f"FONT_COLOR        : {get_config_value('FONT_COLOR', '-')}")
    print(f"PART_FONT_COLOR   : {get_config_value('PART_FONT_COLOR', '-')}")
    print(f"BORDER_COLOR      : {get_config_value('BORDER_COLOR', '-')}")
    print(f"SHADOW_COLOR      : {get_config_value('SHADOW_COLOR', '-')}")
    print("=" * 54)


def setup_settings():
    print("\nATUR ULANG VIDEO ANDA")
    print("Tekan ENTER kalau ingin memakai nilai lama.\n")

    min_duration = ask_int(
        "MIN_DURATION",
        get_config_value("MIN_DURATION", 145)
    )

    max_duration = ask_int(
        "MAX_DURATION",
        get_config_value("MAX_DURATION", 229)
    )

    font_size = ask_int(
        "FONT_SIZE",
        get_config_value("FONT_SIZE", 45)
    )

    font_size_part = ask_int(
        "FONT_SIZE_PART",
        get_config_value("FONT_SIZE_PART", 60)
    )

    wm_size = ask_int(
        "WM_SIZE / ukuran watermark",
        get_config_value("WM_SIZE", 700)
    )

    bg_color = ask_color(
        "BG_COLOR",
        get_config_value("BG_COLOR", "#0d5dde")
    )

    font_color = ask_color(
        "FONT_COLOR",
        get_config_value("FONT_COLOR", "white")
    )

    part_font_color = ask_color(
        "PART_FONT_COLOR",
        get_config_value("PART_FONT_COLOR", "#00E5FF")
    )

    border_color = ask_color(
        "BORDER_COLOR",
        get_config_value("BORDER_COLOR", "black")
    )

    shadow_color = ask_color(
        "SHADOW_COLOR",
        get_config_value("SHADOW_COLOR", "black")
    )

    values = {
        "MIN_DURATION": min_duration,
        "MAX_DURATION": max_duration,
        "FONT_SIZE": font_size,
        "FONT_SIZE_PART": font_size_part,
        "WM_SIZE": wm_size,
        "BG_COLOR": bg_color,
        "FONT_COLOR": font_color,
        "PART_FONT_COLOR": part_font_color,
        "BORDER_COLOR": border_color,
        "SHADOW_COLOR": shadow_color,
    }

    print("\n" + "=" * 54)
    print("KONFIRMASI SETTING BARU")
    print("=" * 54)

    for key, value in values.items():
        print(f"{key:<17}: {value}")

    save = input("\nSimpan setting ini ke config.py? (y/n): ").strip().lower()

    if save == "y":
        if update_config(values):
            print("Setting berhasil disimpan.")
        else:
            print("Setting gagal disimpan.")
    else:
        print("Setting tidak disimpan.")


def reset_default():
    values = {
        "MIN_DURATION": 145,
        "MAX_DURATION": 229,
        "FONT_SIZE": 45,
        "FONT_SIZE_PART": 60,
        "WM_SIZE": 700,
        "BG_COLOR": '"#0d5dde"',
        "FONT_COLOR": '"white"',
        "PART_FONT_COLOR": '"#00E5FF"',
        "BORDER_COLOR": '"black"',
        "SHADOW_COLOR": '"black"',
    }

    confirm = input("Reset setting ke default? (y/n): ").strip().lower()

    if confirm == "y":
        if update_config(values):
            print("Setting berhasil direset.")
        else:
            print("Reset gagal.")
    else:
        print("Reset dibatalkan.")


def process_all_videos():
    print("\nBot mulai jalan...\n")

    judul = input("Masukkan Judul: ").strip()

    if judul == "":
        print("Judul tidak boleh kosong.")
        return

    input_folder = get_config_value("INPUT_FOLDER", "video")
    output_folder = get_config_value("OUTPUT_FOLDER", "cut")

    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    files = [
        f for f in os.listdir(input_folder)
        if f.lower().endswith((".mp4", ".mov", ".mkv", ".avi"))
    ]

    if not files:
        print(f"Folder {input_folder} kosong.")
        return

    for file in files:
        filepath = os.path.join(input_folder, file)

        print(f"\nProses file: {file}")

        results = process_video(filepath, judul)

        for output, caption in results:
            print(f"Video selesai di cut: {output}")

    print(f"\nSemua video selesai diproses dan tersimpan di folder '{output_folder}'")


def main():
    while True:
        banner()

        print("1. Atur ulang video anda")
        print("2. Gunakan settingan yang tersimpan")
        print("3. Lihat setting saat ini")
        print("4. Reset setting ke default")
        print("5. Keluar")

        pilihan = input("\nPilih menu [1-5]: ").strip()

        if pilihan == "1":
            setup_settings()
            process_all_videos()
            break

        elif pilihan == "2":
            print("Menggunakan settingan tersimpan dari config.py")
            process_all_videos()
            break

        elif pilihan == "3":
            show_current_settings()
            input("\nTekan ENTER untuk kembali ke menu...")

        elif pilihan == "4":
            reset_default()
            input("\nTekan ENTER untuk kembali ke menu...")

        elif pilihan == "5":
            print("Keluar.")
            break

        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()