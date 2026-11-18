#!/usr/bin/env bash
# Applies the Dell OptiPlex 7040 MT board port, GRUB2 Binutils 2.46 fix,
# and optional Workstation-Bootmenu-Sample 1920x1080 theme to an upstream Coreboot tree.
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 /path/to/coreboot"
    exit 1
fi

CB_DIR="$(cd "$1" && pwd)"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> [1/4] Copying OptiPlex 7040 MT mainboard variant files..."
cp -r "$REPO_DIR/board/src/mainboard/dell/sklkbl_desktops/variants/optiplex_7040" \
      "$CB_DIR/src/mainboard/dell/sklkbl_desktops/variants/"
cp "$REPO_DIR/board/src/mainboard/dell/sklkbl_desktops/Kconfig" \
   "$CB_DIR/src/mainboard/dell/sklkbl_desktops/Kconfig"
cp "$REPO_DIR/board/src/mainboard/dell/sklkbl_desktops/Kconfig.name" \
   "$CB_DIR/src/mainboard/dell/sklkbl_desktops/Kconfig.name"

echo "==> [2/4] Applying GRUB2 payload Makefile patches (Binutils 2.46 -Ttext + .PHONY)..."
git -C "$CB_DIR" apply "$REPO_DIR/patches/0002-payloads-GRUB2-Fix-binutils-2.46-image-base-and-PHONY.patch" || true

echo "==> [3/4] Installing Coreboot .config and GRUB2 runtime config..."
cp "$REPO_DIR/configs/optiplex_7040.config" "$CB_DIR/.config"
cp "$REPO_DIR/configs/grub_payload.cfg" /root/grub_payload.cfg 2>/dev/null || true

echo "==> [4/4] Done! Next steps:"
echo "    1. Place your extracted blobs (ifd_hap.bin, flashregion_3_gbe.bin, me_deguard_7040.bin) in /root/optiplex7040/"
echo "    2. Run: python3 $REPO_DIR/docs/verify_and_build.py"
