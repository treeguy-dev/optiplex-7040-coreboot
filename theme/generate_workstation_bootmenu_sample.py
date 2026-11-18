#!/usr/bin/env python3
"""
Generator for the 'Workstation Pro' GRUB2 gfxmenu theme and grub_payload.cfg
for Dell OptiPlex 7040 MT (Coreboot Open Firmware).
"""
import os
import struct
import subprocess
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080


def find_font(candidates, size, index=0):
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size, index=index)
            except Exception:
                pass
    return ImageFont.load_default()


SANS_REG_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/SFNS.ttf",
]
SANS_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/SFNS.ttf",
]
MONO_REG_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/System/Library/Fonts/SFNSMono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
]


def draw_icon(name, size=28):
    """Render 4x supersampled anti-aliased 28x28 white icon matching Workstation Pro."""
    S = size * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = (240, 246, 252, 255)
    lw = 7

    if name == "mx":
        pad = 12
        d.ellipse([pad, pad, S - pad, S - pad], outline=col, width=lw)
        d.ellipse([pad + 22, pad, S - pad - 22, S - pad], outline=col, width=lw - 1)
        d.line([pad, S // 2, S - pad, S // 2], fill=col, width=lw - 1)
        d.line([S // 2, pad, S // 2, S - pad], fill=col, width=lw - 1)
    elif name == "submenu":
        d.arc([S - 54, 12, S - 12, 54], start=35, end=305, fill=col, width=lw)
        d.line([20, S - 20, S - 36, 36], fill=col, width=lw + 3)
        d.ellipse([12, S - 32, 32, S - 12], outline=col, width=lw)
    elif name == "usb":
        cx = S // 2
        d.line([cx, 16, cx, S - 18], fill=col, width=lw)
        d.polygon([(cx, 10), (cx - 12, 26), (cx + 12, 26)], fill=col)
        d.ellipse([cx - 11, S - 28, cx + 11, S - 6], fill=col)
        d.line([cx, S - 38, cx - 24, S - 56], fill=col, width=lw - 1)
        d.line([cx - 24, S - 56, cx - 24, 42], fill=col, width=lw - 1)
        d.ellipse([cx - 32, 30, cx - 16, 46], fill=col)
        d.line([cx, S - 46, cx + 24, S - 64], fill=col, width=lw - 1)
        d.line([cx + 24, S - 64, cx + 24, 50], fill=col, width=lw - 1)
        d.rectangle([cx + 16, 36, cx + 32, 52], fill=col)
    elif name == "tools":
        p = 28
        d.rounded_rectangle([p, p, S - p, S - p], radius=8, outline=col, width=lw)
        d.rectangle([p + 14, p + 14, S - p - 14, S - p - 14], fill=col)
        for off in (S // 2 - 14, S // 2 + 14):
            d.line([off, 10, off, p], fill=col, width=lw - 1)
            d.line([off, S - p, off, S - 10], fill=col, width=lw - 1)
            d.line([10, off, p, off], fill=col, width=lw - 1)
            d.line([S - p, off, S - 10, off], fill=col, width=lw - 1)
    elif name == "power":
        pad = 16
        d.arc([pad, pad + 6, S - pad, S - pad + 4], start=300, end=240, fill=col, width=lw)
        d.line([S // 2, 10, S // 2, S // 2 + 4], fill=col, width=lw)

    return img.resize((size, size), Image.Resampling.LANCZOS)


def make_background(font_sans_bold_20, font_sans_bold_19, font_mono_18, font_mono_17):
    img = Image.new("RGBA", (W, H), (10, 14, 22, 255))
    d = ImageDraw.Draw(img)

    for y in range(H):
        r = 10 + int(3 * (1.0 - abs(y - H / 2) / (H / 2)))
        g = 14 + int(5 * (1.0 - abs(y - H / 2) / (H / 2)))
        b = 22 + int(8 * (1.0 - abs(y - H / 2) / (H / 2)))
        d.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # Top Header Bar (y = 0..76)
    d.rectangle([0, 0, W, 76], fill=(16, 23, 36, 255))
    d.line([0, 76, W, 76], fill=(32, 45, 66, 255), width=2)

    # DELL Badge (x = 56..142, y = 20..56)
    d.rounded_rectangle([56, 20, 142, 56], radius=6, fill=(2, 132, 199, 255))
    d.text((99, 38), "DELL", font=font_sans_bold_19, fill=(255, 255, 255, 255), anchor="mm")

    # Header Title
    d.text(
        (164, 38),
        "OPTIPLEX 7040 MT — COREBOOT OPEN FIRMWARE",
        font=font_sans_bold_20,
        fill=(241, 245, 249, 255),
        anchor="lm",
    )

    # Header Right BIOS Version
    d.text(
        (W - 56, 38),
        "BIOS: 25.09-CB • Q170",
        font=font_mono_18,
        fill=(124, 142, 166, 255),
        anchor="rm",
    )

    # Center Table Container (x = 156..1764, y = 212..712)
    tx0, ty0, tx1, ty1 = 156, 212, 1764, 712
    d.rounded_rectangle([tx0, ty0, tx1, ty1], radius=8, fill=(13, 19, 31, 255), outline=(40, 55, 77, 255), width=2)

    # Table Header Bar (y = 212..275)
    d.rounded_rectangle([tx0 + 1, ty0 + 1, tx1 - 1, 275], radius=7, fill=(20, 29, 45, 255))
    d.rectangle([tx0 + 1, 260, tx1 - 1, 275], fill=(20, 29, 45, 255))
    d.line([tx0, 275, tx1, 275], fill=(40, 55, 77, 255), width=2)

    # Table Column Titles
    d.text((190, 244), "BOOT DEVICE / PAYLOAD ENTRY", font=font_mono_17, fill=(132, 148, 172, 255), anchor="lm")
    d.text((1730, 244), "CATEGORY", font=font_mono_17, fill=(132, 148, 172, 255), anchor="rm")

    # Subtle row separator lines in table background (5 rows of 87px: 276..711)
    for row in range(1, 5):
        ry = 276 + row * 87
        d.line([tx0 + 1, ry, tx1 - 1, ry], fill=(34, 47, 68, 255), width=1)

    # Bottom Footer Bar (y = 1004..1080)
    d.rectangle([0, 1004, W, H], fill=(16, 23, 36, 255))
    d.line([0, 1004, W, 1004], fill=(32, 45, 66, 255), width=2)

    # Footer Key Hints
    d.text(
        (56, 1042),
        "[↑/↓] Move Highlight  [Enter] Select  [E] Edit  [C] Shell",
        font=font_mono_18,
        fill=(148, 163, 184, 255),
        anchor="lm",
    )

    return img


def make_slices(out_dir):
    for suffix, w in [("w", 32), ("c", 8), ("e", 32)]:
        im = Image.new("RGBA", (w, 86), (2, 132, 199, 255))
        d = ImageDraw.Draw(im)
        d.line([0, 0, w, 0], fill=(56, 189, 248, 255), width=1)
        d.line([0, 85, w, 85], fill=(56, 189, 248, 255), width=1)
        im.save(os.path.join(out_dir, f"select_{suffix}.png"))

    for suffix, w in [("w", 32), ("c", 8), ("e", 32)]:
        im = Image.new("RGBA", (w, 86), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.line([0, 85, w, 85], fill=(34, 47, 68, 255), width=1)
        im.save(os.path.join(out_dir, f"item_{suffix}.png"))

    for suffix in ["nw", "n", "ne", "w", "c", "e", "sw", "s", "se"]:
        im = Image.new("RGBA", (6, 6), (13, 19, 31, 245))
        d = ImageDraw.Draw(im)
        if "n" in suffix:
            d.line([0, 0, 5, 0], fill=(2, 132, 199, 255), width=2)
        if "s" in suffix:
            d.line([0, 5, 5, 5], fill=(2, 132, 199, 255), width=2)
        if "w" in suffix:
            d.line([0, 0, 0, 5], fill=(2, 132, 199, 255), width=2)
        if "e" in suffix:
            d.line([5, 0, 5, 5], fill=(2, 132, 199, 255), width=2)
        im.save(os.path.join(out_dir, f"terminal_box_{suffix}.png"))


def parse_pf2_widths(pf2_path):
    with open(pf2_path, "rb") as f:
        data = bytearray(f.read())
    pos = 0
    chix = {}
    while pos < len(data):
        tag = data[pos : pos + 4].decode("ascii", "replace")
        length = struct.unpack(">I", data[pos + 4 : pos + 8])[0]
        pos += 8
        if tag == "DATA":
            break
        if tag == "CHIX":
            for i in range(0, length, 9):
                cp, flags, off = struct.unpack(">IBI", data[pos + i : pos + i + 9])
                w, h, xo, yo, dw = struct.unpack(">HHhhh", data[off : off + 10])
                chix[cp] = (off, w, h, xo, yo, dw)
        pos += length
    return data, chix


def string_width_pf2(chix, s):
    total = 0
    for ch in s:
        cp = ord(ch)
        if cp in chix:
            total += chix[cp][5]
        elif 0x20 in chix:
            total += chix[0x20][5]
    return total


def patch_pf2_spacers(pf2_path, entries, target_width=1495):
    data, chix = parse_pf2_widths(pf2_path)
    for idx, (left_text, right_cat) in enumerate(entries):
        cp = 0x2000 + idx
        if cp not in chix:
            continue
        off = chix[cp][0]
        w_left = string_width_pf2(chix, left_text)
        w_right = string_width_pf2(chix, right_cat)
        gap = max(16, target_width - w_left - w_right)
        struct.pack_into(">HHhhh", data, off, 0, 0, 0, 0, gap)
    with open(pf2_path, "wb") as f:
        f.write(data)


def write_grub_cfg(cfg_path):
    s0, s1, s2, s3, s4 = "\u2000", "\u2001", "\u2002", "\u2003", "\u2004"
    cfg = f"""serial --unit=0 --speed=115200 --word=8 --parity=no --stop=1
terminal_input serial at_keyboard usb_keyboard

insmod all_video
insmod gfxterm
insmod gfxmenu
insmod png
insmod bitmap_scale
insmod gzio
insmod ahci
insmod part_gpt
insmod part_msdos
insmod ext2
insmod fat
insmod search_fs_uuid
insmod configfile
insmod normal
insmod reboot
insmod halt
insmod cbtime
insmod cbmemc
insmod cbls
insmod lspci
insmod lsmmap
insmod lsacpi

set gfxmode=1920x1080,auto
set gfxpayload=keep

loadfont (memdisk)/boot/grub/fonts/unicode.pf2
loadfont (memdisk)/boot/grub/themes/Workstation-Bootmenu-Sample/workstation_sans_20.pf2
loadfont (memdisk)/boot/grub/themes/Workstation-Bootmenu-Sample/workstation_bold_20.pf2
loadfont (memdisk)/boot/grub/themes/Workstation-Bootmenu-Sample/workstation_mono_18.pf2

terminal_output serial gfxterm
set theme=(memdisk)/boot/grub/themes/Workstation-Bootmenu-Sample/theme.txt
export theme

set timeout=8
set default=0

menuentry "MX Linux 25 (6.12.117+deb13-amd64){s0}DEFAULT" --class mx --class gnu-linux --class os {{
    search --no-floppy --fs-uuid --set=root f26a31e7-9b95-494b-bd02-6446bcc61fdf
    if [ -e ($root)/vmlinuz-6.12.117+deb13-amd64 ]; then
        echo "Booting MX Linux 25 (6.12.117+deb13-amd64)..."
        linux ($root)/vmlinuz-6.12.117+deb13-amd64 root=UUID=9c81a671-fd68-4304-a282-753b91feaa3f ro iomem=relaxed console=ttyS0,115200n8 console=tty0
        initrd ($root)/initrd.img-6.12.117+deb13-amd64
    elif [ -e ($root)/grub/grub.cfg ]; then
        configfile ($root)/grub/grub.cfg
    fi
}}

submenu "MX Linux 25 — Advanced & Recovery{s1}SUBMENU" --class submenu {{
    menuentry "MX 25.3 Infinity — Linux 6.12.117+deb13-amd64 (systemd)" --class mx {{
        search --no-floppy --fs-uuid --set=root f26a31e7-9b95-494b-bd02-6446bcc61fdf
        linux ($root)/vmlinuz-6.12.117+deb13-amd64 root=UUID=9c81a671-fd68-4304-a282-753b91feaa3f ro iomem=relaxed console=ttyS0,115200n8 console=tty0
        initrd ($root)/initrd.img-6.12.117+deb13-amd64
    }}
    menuentry "MX 25.3 Infinity — Linux 6.12.117+deb13-amd64 (sysvinit)" --class submenu {{
        search --no-floppy --fs-uuid --set=root f26a31e7-9b95-494b-bd02-6446bcc61fdf
        linux ($root)/vmlinuz-6.12.117+deb13-amd64 root=UUID=9c81a671-fd68-4304-a282-753b91feaa3f ro iomem=relaxed console=ttyS0,115200n8 console=tty0 init=/lib/sysvinit/init
        initrd ($root)/initrd.img-6.12.117+deb13-amd64
    }}
    menuentry "MX 25.3 Infinity — Linux 6.12.116+deb13-amd64" --class mx {{
        search --no-floppy --fs-uuid --set=root f26a31e7-9b95-494b-bd02-6446bcc61fdf
        linux ($root)/vmlinuz-6.12.116+deb13-amd64 root=UUID=9c81a671-fd68-4304-a282-753b91feaa3f ro iomem=relaxed console=ttyS0,115200n8 console=tty0
        initrd ($root)/initrd.img-6.12.116+deb13-amd64
    }}
    menuentry "MX 25.3 Infinity — Linux 6.12.107+deb13-amd64" --class mx {{
        search --no-floppy --fs-uuid --set=root f26a31e7-9b95-494b-bd02-6446bcc61fdf
        linux ($root)/vmlinuz-6.12.107+deb13-amd64 root=UUID=9c81a671-fd68-4304-a282-753b91feaa3f ro iomem=relaxed console=ttyS0,115200n8 console=tty0
        initrd ($root)/initrd.img-6.12.107+deb13-amd64
    }}
    menuentry "MX 25.3 Infinity — Linux 6.12.90+deb13-amd64" --class mx {{
        search --no-floppy --fs-uuid --set=root f26a31e7-9b95-494b-bd02-6446bcc61fdf
        linux ($root)/vmlinuz-6.12.90+deb13-amd64 root=UUID=9c81a671-fd68-4304-a282-753b91feaa3f ro iomem=relaxed console=ttyS0,115200n8 console=tty0
        initrd ($root)/initrd.img-6.12.90+deb13-amd64
    }}
    menuentry "Chainload Disk /boot/grub/grub.cfg" --class submenu {{
        search --no-floppy --fs-uuid --set=root f26a31e7-9b95-494b-bd02-6446bcc61fdf
        configfile ($root)/grub/grub.cfg
    }}
}}

menuentry "Boot from External USB Drive{s2}USB" --class usb {{
    insmod usbms
    insmod ehci
    insmod xhci
    echo "Scanning external USB storage devices..."
    for dev in (usb0) (usb0,gpt1) (usb0,gpt2) (usb0,msdos1) (hd0,gpt1) (hd0,msdos1); do
        if [ -e $dev/boot/grub/grub.cfg ]; then
            set root=$dev
            configfile $dev/boot/grub/grub.cfg
        elif [ -e $dev/EFI/BOOT/grub.cfg ]; then
            set root=$dev
            configfile $dev/EFI/BOOT/grub.cfg
        fi
    done
    echo "No bootable USB GRUB config found. Press Enter to return."
    read
}}

submenu "Coreboot & Hardware Diagnostics{s3}TOOLS" --class tools {{
    menuentry "Coreboot Boot Timestamps (cbtime)" --class tools {{
        cbtime
        echo "Press Enter to return to menu..."
        read
    }}
    menuentry "Coreboot Firmware Console Log (cbmemc)" --class tools {{
        cbmemc
        echo "Press Enter to return to menu..."
        read
    }}
    menuentry "CBFS Flash Region Layout (cbls)" --class tools {{
        cbls
        echo "Press Enter to return to menu..."
        read
    }}
    menuentry "PCIe & Skylake Q170 Bus Topology (lspci)" --class tools {{
        lspci
        echo "Press Enter to return to menu..."
        read
    }}
    menuentry "System Memory Map (lsmmap) & ACPI (lsacpi)" --class tools {{
        lsmmap
        lsacpi
        echo "Press Enter to return to menu..."
        read
    }}
}}

submenu "System Power Off / Reboot{s4}POWER" --class power {{
    menuentry "Reboot OptiPlex 7040 MT" --class power {{
        reboot
    }}
    menuentry "Power Off OptiPlex 7040 MT" --class power {{
        halt
    }}
}}
"""
    with open(cfg_path, "w", encoding="utf-8") as f:
        f.write(cfg)


def generate_all(theme_dir, grub_mkfont_bin=None, preview_path=None, cfg_path=None):
    os.makedirs(os.path.join(theme_dir, "icons"), exist_ok=True)

    font_sans_20 = find_font(SANS_REG_CANDIDATES, 20)
    font_sans_bold_20 = find_font(SANS_BOLD_CANDIDATES, 20)
    font_sans_bold_19 = find_font(SANS_BOLD_CANDIDATES, 19)
    font_mono_18 = find_font(MONO_REG_CANDIDATES, 18)
    font_mono_17 = find_font(MONO_REG_CANDIDATES, 17)

    bg = make_background(font_sans_bold_20, font_sans_bold_19, font_mono_18, font_mono_17)
    bg.save(os.path.join(theme_dir, "background.png"))
    make_slices(theme_dir)

    icons = {}
    for ic in ["mx", "submenu", "usb", "tools", "power"]:
        icon_im = draw_icon(ic, size=28)
        icon_im.save(os.path.join(theme_dir, "icons", f"{ic}.png"))
        icons[ic] = icon_im

    entries = [
        ("MX Linux 25 (6.12.117+deb13-amd64)", "DEFAULT", "mx"),
        ("MX Linux 25 — Advanced & Recovery", "SUBMENU", "submenu"),
        ("Boot from External USB Drive", "USB", "usb"),
        ("Coreboot & Hardware Diagnostics", "TOOLS", "tools"),
        ("System Power Off / Reboot", "POWER", "power"),
    ]

    if grub_mkfont_bin and os.path.exists(grub_mkfont_bin):
        rng = "0x0-0x7f,0x80-0xff,0x2000-0x206f,0x2190-0x21ff,0x2500-0x25ff"
        reg_pf2 = os.path.join(theme_dir, "workstation_sans_20.pf2")
        bold_pf2 = os.path.join(theme_dir, "workstation_bold_20.pf2")
        mono_pf2 = os.path.join(theme_dir, "workstation_mono_18.pf2")
        subprocess.run(
            [grub_mkfont_bin, "-n", "Workstation Sans", "-r", rng, "-s", "20", "-o", reg_pf2, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
            check=True,
        )
        subprocess.run(
            [grub_mkfont_bin, "-n", "Workstation Sans", "-r", rng, "-s", "20", "-o", bold_pf2, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
            check=True,
        )
        subprocess.run(
            [grub_mkfont_bin, "-n", "Workstation Mono", "-r", rng, "-s", "18", "-o", mono_pf2, "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"],
            check=True,
        )
        pair_list = [(e[0], e[1]) for e in entries]
        patch_pf2_spacers(reg_pf2, pair_list, target_width=1495)
        patch_pf2_spacers(bold_pf2, pair_list, target_width=1495)

    theme_txt = """# Workstation-Bootmenu-Sample GRUB2 Theme (Proof-of-Concept) for Dell OptiPlex 7040 MT (Coreboot)
title-text: ""
desktop-image: "background.png"
desktop-color: "#0a0e16"
terminal-box: "terminal_box_*.png"
terminal-font: "Workstation Mono Regular 18"
terminal-left: "10%"
terminal-top: "12%"
terminal-width: "80%"
terminal-height: "76%"

+ boot_menu {
    left = 157
    top = 276
    width = 1606
    height = 435
    item_font = "Workstation Sans Regular 20"
    item_color = "#cbd5e1"
    selected_item_font = "Workstation Sans Bold 20"
    selected_item_color = "#ffffff"
    item_height = 86
    item_padding = 0
    item_spacing = 1
    icon_width = 28
    icon_height = 28
    item_icon_space = 18
    item_pixmap_style = "item_*.png"
    selected_item_pixmap_style = "select_*.png"
    scrollbar = false
}

+ label {
    id = "__timeout__"
    left = 1400
    top = 1030
    width = 464
    height = 28
    align = "right"
    font = "Workstation Mono Regular 18"
    color = "#38bdf8"
    text = "Auto-boot: %ds"
}
"""
    with open(os.path.join(theme_dir, "theme.txt"), "w") as f:
        f.write(theme_txt)

    if cfg_path:
        write_grub_cfg(cfg_path)

    if preview_path:
        prev = bg.copy()
        d = ImageDraw.Draw(prev)
        for idx, (title, cat, ic_name) in enumerate(entries):
            ry = 276 + idx * 87
            if idx == 0:
                d.rectangle([157, ry, 1763, ry + 86], fill=(2, 132, 199, 255))
                d.line([157, ry, 1763, ry], fill=(56, 189, 248, 255), width=1)
                d.line([157, ry + 85, 1763, ry + 85], fill=(56, 189, 248, 255), width=1)
                fnt = font_sans_bold_20
                tcol = (255, 255, 255, 255)
                ccol = (255, 255, 255, 255)
            else:
                fnt = font_sans_20
                tcol = (203, 213, 225, 255)
                ccol = (132, 148, 172, 255)
            prev.paste(icons[ic_name], (189, ry + (86 - 28) // 2), icons[ic_name])
            d.text((235, ry + 43), title, font=fnt, fill=tcol, anchor="lm")
            d.text((1730, ry + 43), cat, font=font_sans_bold_19 if idx == 0 else font_mono_17, fill=ccol, anchor="rm")
        d.text((W - 56, 1042), "Auto-boot: 8s", font=font_mono_18, fill=(56, 189, 248, 255), anchor="rm")
        prev.save(preview_path)


if __name__ == "__main__":
    import sys
    out_theme = sys.argv[1] if len(sys.argv) > 1 else "Workstation-Bootmenu-Sample"
    mkfont = sys.argv[2] if len(sys.argv) > 2 else None
    prev = sys.argv[3] if len(sys.argv) > 3 else "Workstation-Bootmenu-Sample-preview.png"
    cfg = sys.argv[4] if len(sys.argv) > 4 else None
    generate_all(out_theme, mkfont, prev, cfg)
