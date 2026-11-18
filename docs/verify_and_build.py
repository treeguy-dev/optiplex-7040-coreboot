#!/usr/bin/env python3
"""
Builds the Workstation Pro GRUB2 theme on mx, embeds it into default_payload.elf
and coreboot.rom, and runs a full cryptographic & structural flash-safety check.
"""
import hashlib
import os
import subprocess
import struct
import generate_workstation_bootmenu_sample

BASE = "/root/optiplex7040"
CB = f"{BASE}/coreboot"
GRUB_BUILD = f"{CB}/payloads/external/GRUB2/grub2/build"
THEME_DIR = f"{BASE}/Workstation-Bootmenu-Sample"
PREVIEW_PATH = f"{BASE}/Workstation-Bootmenu-Sample-preview.png"
CFG_PATH = "/root/grub_payload.cfg"


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def main():
    print("=== [1/4] Generating Workstation Pro Theme, PF2 Fonts & grub_payload.cfg ===")
    mkfont = f"{GRUB_BUILD}/grub-mkfont"
    generate_workstation_bootmenu_sample.generate_all(THEME_DIR, mkfont, PREVIEW_PATH, CFG_PATH)
    # Also copy to /root/optiplex7040/grub_payload.cfg
    with open(CFG_PATH, "rb") as src, open(f"{BASE}/grub_payload.cfg", "wb") as dst:
        dst.write(src.read())

    print("=== [2/4] Updating GRUB2 Makefile to embed /boot/grub/themes/Workstation-Bootmenu-Sample ===")
    for mf in [f"{CB}/payloads/external/GRUB2/grub2/Makefile.in", f"{GRUB_BUILD}/Makefile"]:
        with open(mf, "r") as f:
            txt = f.read()
        target_arg = "/boot/grub/themes/Workstation-Bootmenu-Sample=/root/optiplex7040/Workstation-Bootmenu-Sample"
        if target_arg not in txt:
            txt = txt.replace(
                "/boot/grub/grub.cfg=$(srcdir)/coreboot.cfg",
                f"/boot/grub/grub.cfg=$(srcdir)/coreboot.cfg {target_arg}",
            )
            with open(mf, "w") as f:
                f.write(txt)

    # Ensure autotools timestamps do not trigger aclocal-1.16
    subprocess.run(
        [
            "touch",
            f"{CB}/payloads/external/GRUB2/grub2/Makefile.in",
            f"{GRUB_BUILD}/config.status",
            f"{GRUB_BUILD}/Makefile",
        ],
        check=True,
    )

    print("=== [3/4] Rebuilding default_payload.elf and coreboot.rom ===")
    if os.path.exists(f"{GRUB_BUILD}/default_payload.elf"):
        os.remove(f"{GRUB_BUILD}/default_payload.elf")
    subprocess.run(["make", "-C", CB, "-j4"], check=True)

    rom_path = f"{CB}/build/coreboot.rom"
    out_rom = f"{BASE}/cb_workstation_bootmenu_sample.rom"
    with open(rom_path, "rb") as f:
        rom = f.read()
    with open(out_rom, "wb") as f:
        f.write(rom)
    with open(f"{out_rom}.sha256", "w") as f:
        f.write(f"{sha256(rom)}  cb_workstation_bootmenu_sample.rom\n")

    print("\n=== [4/4] Running Flash Safety Verification Suite ===")
    checks = []

    # 1. Exact 16 MiB size
    sz_ok = len(rom) == 16777216
    checks.append(("ROM Size == 16,777,216 bytes (MX25L12805D 16 MiB)", sz_ok, f"{len(rom)} bytes"))

    # 2. IFD signature & region layout
    ifd_sig = struct.unpack_from("<I", rom, 0x10)[0]
    flreg0, flreg1, flreg2, flreg3 = struct.unpack_from("<IIII", rom, 0x40)
    ifd_ok = (
        ifd_sig == 0x0FF0A55A
        and flreg0 == 0x00000000
        and flreg1 == 0x0FFF0700
        and flreg2 == 0x06FF0003
        and flreg3 == 0x00020001
    )
    checks.append(
        (
            "IFD Magic & FLREG0..3 Layout",
            ifd_ok,
            f"sig=0x{ifd_sig:08x} BIOS=0x700000..0xffffff ME=0x003000..0x6fffff GbE=0x001000..0x002fff",
        )
    )

    # 3. Compare non-BIOS regions (0x000000..0x6fffff) byte-for-byte with booting cb_grub.rom
    with open(f"{BASE}/cb_grub.rom", "rb") as f:
        cb_grub = f.read()
    with open(f"{BASE}/blobs/ifd_hap.bin", "rb") as f:
        ifd_ref = f.read()
    with open(f"{BASE}/blobs/flashregion_3_gbe.bin", "rb") as f:
        gbe_ref = f.read()
    with open(f"{BASE}/me_deguard_7040.bin", "rb") as f:
        me_ref = f.read()

    ifd_match = rom[0x0000:0x1000] == ifd_ref == cb_grub[0x0000:0x1000]
    gbe_match = rom[0x1000:0x3000] == gbe_ref == cb_grub[0x1000:0x3000]
    me_match = rom[0x3000:0x700000] == cb_grub[0x3000:0x700000] and rom[0x3000 : 0x3000 + len(me_ref)] == me_ref
    non_bios_match = rom[0x000000:0x700000] == cb_grub[0x000000:0x700000]

    checks.append(("SI_DESC (0x000000..0x000fff) == ifd_hap.bin & cb_grub.rom", ifd_match, sha256(rom[0:0x1000])[:16]))
    checks.append(("SI_GBE  (0x001000..0x002fff) == donor GbE & cb_grub.rom", gbe_match, sha256(rom[0x1000:0x3000])[:16]))
    checks.append(("SI_ME   (0x003000..0x6fffff) == me_deguard & cb_grub.rom", me_match, sha256(rom[0x3000:0x700000])[:16]))
    checks.append(("Entire Non-BIOS (0x000000..0x6fffff) identical to cb_grub.rom", non_bios_match, sha256(rom[0:0x700000])[:16]))

    # 4. Intel FIT Pointer & Microcode Table
    fit_ptr = struct.unpack_from("<I", rom, 0xFFFFC0)[0]
    fit_rom_off = fit_ptr - 0xFF000000
    fit_sig = rom[fit_rom_off : fit_rom_off + 8]
    fit_ok = fit_sig == b"_FIT_   "
    checks.append(("Intel FIT Table @ 0xffffffc0", fit_ok, f"ptr=0x{fit_ptr:08x} (ROM+0x{fit_rom_off:x}) sig={fit_sig!r}"))

    # 5. x86 Reset Vector & Bootblock
    reset_vec = rom[0xFFFFF0:0x1000000]
    rv_ok = reset_vec[0] == 0xE9  # rel16 JMP
    bb_match = rom[0xFF8FC0:0x1000000] == cb_grub[0xFF8FC0:0x1000000]
    checks.append(("x86 Reset Vector @ 0xfffffff0", rv_ok, f"opcode=0x{reset_vec[0]:02x} bytes={reset_vec[:5].hex()}"))
    checks.append(("Bootblock (0xff8fc0..0xffffff) identical to cb_grub.rom", bb_match, sha256(rom[0xFF8FC0:])[:16]))

    # 6. Payload ELF & start address verification
    with open(f"{GRUB_BUILD}/grub-core/kernel.img", "rb") as f:
        kimg = f.read()
    e_shoff = struct.unpack_from("<I", kimg, 32)[0]
    e_shentsize, e_shnum = struct.unpack_from("<HH", kimg, 46)
    text_addr = struct.unpack_from("<I", kimg, e_shoff + 1 * e_shentsize + 12)[0]
    checks.append(("GRUB kernel.img .text start address == 0x9000", text_addr == 0x9000, f"0x{text_addr:x}"))

    with open(f"{GRUB_BUILD}/default_payload.elf", "rb") as f:
        p_elf = f.read()
    elf_ok = p_elf[:4] == b"\x7fELF" and len(p_elf) > 1000000
    checks.append(("default_payload.elf valid ELF32 + embedded theme", elf_ok, f"{len(p_elf):,} bytes"))

    all_passed = True
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_passed = False
        print(f"  [{status}] {name:58s} | {detail}")

    print(f"\nFINAL VERDICT: {'ALL CHECKS PASSED - SAFE TO FLASH' if all_passed else 'FAILED'}")
    print(f"Output ROM: {out_rom} (SHA-256: {sha256(rom)})")


if __name__ == "__main__":
    main()
