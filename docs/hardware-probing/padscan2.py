import re
src="/root/optiplex7040/inteltool_gpio_7040.txt"
pads=[];group=None
for line in open(src):
    m=re.match(r'-+ GPIO Group (\S+) -+',line)
    if m: group=m.group(1); continue
    m=re.match(r'^0x([0-9a-f]+): 0x([0-9a-f]{16})\s+(\S+)\s*(.*?)\s*$',line)
    if not m: continue
    v=int(m.group(2),16)
    pads.append(dict(group=group,pad=m.group(3),fn=m.group(4).strip(),
                     dw0=v&0xffffffff,dw1=v>>32))
RST={0:'RSMRST',1:'DEEP',2:'PLTRST',3:'RSVD11'}
PULL={0x0:'NONE',0x2:'DN_5K',0x4:'DN_20K',0x9:'UP_1K',0xa:'UP_5K',0xb:'UP_2K',
      0xc:'UP_20K',0xd:'UP_667',0xf:'NATIVE'}
for p in pads:
    d0,d1=p['dw0'],p['dw1']
    p['pmode']=(d0>>10)&7; p['txdis']=(d0>>8)&1; p['rxdis']=(d0>>9)&1
    p['tx']=d0&1; p['rst']=RST[(d0>>30)&3]; p['pull']=PULL.get((d1>>10)&0xf,hex((d1>>10)&0xf))
    p['route']=''.join(c for c,b in (('N',17),('S',18),('C',19),('A',20)) if (d0>>b)&1)
    p['rxev']=(d0>>25)&3
    p['native']=p['pmode']!=0
    # parked-low: GPIO mode, rx disabled, driving 0, no pull, no routing
    p['parked']= (not p['native']) and p['rxdis'] and p['tx']==0 and p['pull']=='NONE' and not p['route']

notable=[p for p in pads if (not p['native']) and not p['parked']]
print("PAD CENSUS: %d total | %d native-function | %d parked-low | %d NOTABLE GPIO"
      % (len(pads), sum(p['native'] for p in pads), sum(p['parked'] for p in pads), len(notable)))

print("\n===== NOTABLE GPIO PADS (board-specific: straps, inputs, driven enables) =====")
print("%-9s %-7s %-8s %-8s %-4s %-6s %s"%("PAD","DIR","RESET","PULL","TX","ROUTE","raw DW0"))
for p in notable:
    d = 'IN' if (p['txdis'] and not p['rxdis']) else ('OUT' if (not p['txdis'] and p['rxdis']) else
        ('BIDIR' if not p['txdis'] and not p['rxdis'] else 'HIZ'))
    print("%-9s %-7s %-8s %-8s %-4d %-6s 0x%08x"%(p['pad'],d,p['rst'],p['pull'],p['tx'],p['route'] or '-',p['dw0']))

print("\n===== NATIVE FUNCTION PADS grouped by subsystem =====")
buckets={}
def bucket(fn):
    f=fn.upper()
    for key,pat in (('LPC / SuperIO',('LAD','LFRAME','SERIRQ','CLKOUT_LPC','PIRQ','RCIN','LDRQ','SUS')),
                    ('SMBus / I2C',('SMB','I2C','ML_')),
                    ('SATA',('SATA',)),
                    ('USB',('USB','OC')),
                    ('PCIe / CLKREQ',('SRCCLK','CLKREQ','PCIE')),
                    ('Display / DDI',('DDP','DDI','HDMI','EDP','DP_')),
                    ('Audio / HDA',('HDA','AZ_','SNDW')),
                    ('SPI / flash',('SPI','GSPI')),
                    ('Power / clocks',('CLK','PM_','SLP','SUSWARN','SUSACK','PLTRST','WAKE','BATLOW','PRDY','PREQ','SYS_PWROK','CPUPWRGD')),
                    ('UART / serial',('UART','RXD','TXD','RTS','CTS')),
                    ('Thermal / misc',('TEMP','THERM','ALERT','TACH','PWM','SML','GBE','NFC','ISH'))):
        if any(s in f for s in pat): return key
    return 'Other native'
for p in pads:
    if p['native']:
        buckets.setdefault(bucket(p['fn']),[]).append(p)
for k in sorted(buckets):
    v=buckets[k]
    print("\n-- %s (%d)"%(k,len(v)))
    print("   "+", ".join("%s:%s"%(x['pad'],x['fn']) for x in v))

print("\n===== RESERVED RESET-CONFIG (must hand-fix) =====")
for p in pads:
    if ((p['dw0']>>30)&3)==3: print("   %s  fn=%s  DW0=0x%08x DW1=0x%08x"%(p['pad'],p['fn'],p['dw0'],p['dw1']))
