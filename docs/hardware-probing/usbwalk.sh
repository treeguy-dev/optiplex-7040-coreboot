#!/bin/bash
# Logs every USB connect/disconnect on the root hubs with port index + speed.
# Run in background; plug one device per physical connector, then read the log.
LOG=/root/optiplex7040/usbwalk.log
prev=""
echo "=== usbwalk started $(date -Is) ===" >> $LOG
while true; do
  cur=""
  for d in /sys/bus/usb/devices/[0-9]-[0-9]*; do
    [ -e "$d/product" ] || continue
    b=$(basename "$d")
    case "$b" in *:*) continue;; esac
    cur="$cur$b|$(cat $d/speed 2>/dev/null)|$(cat $d/product 2>/dev/null 2>&1)
"
  done
  if [ "$cur" != "$prev" ]; then
    echo "--- $(date +%H:%M:%S) ---" >> $LOG
    if [ -z "$cur" ]; then echo "    (nothing connected)" >> $LOG; fi
    echo "$cur" | while IFS='|' read -r p s pr; do
      [ -z "$p" ] && continue
      bus=${p%%-*}; port=${p#*-}
      if [ "$bus" = "1" ]; then
        kind="USB2  -> coreboot usb2_ports[$((port-1))]"
      else
        kind="USB3  -> coreboot usb3_ports[$((port-1))]"
      fi
      printf "    %-8s %5s Mbps  %-28s %s\n" "$p" "$s" "$pr" "$kind" >> $LOG
    done
    prev="$cur"
  fi
  sleep 0.5
done
