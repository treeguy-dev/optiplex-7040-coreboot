import re, sys
src = "/root/optiplex7040/inteltool_gpio_7040.txt"
pads = []
group = None
for line in open(src):
    m = re.match(r'-+ GPIO Group (\S+) -+', line)
    if m:
        group = m.group(1); continue
    m = re.match(r'^0x([0-9a-f]+): 0x([0-9a-f]{16})\s+(\S+)\s*(.*?)\s*$', line)
    if not m: continue
    off, val, pad, fn = m.group(1), int(m.group(2),16), m.group(3), m.group(4).strip()
    dw0 = val & 0xffffffff
    dw1 = val >> 32
    pads.append(dict(group=group, pad=pad, fn=fn, dw0=dw0, dw1=dw1))

RST = {0:'RSMRST/POW', 1:'DEEP', 2:'PLTRST', 3:'RESERVED(0b11)'}
PULL = {0x0:'NONE',0x2:'DN_5K',0x4:'DN_20K',0x9:'UP_1K',0xa:'UP_5K',0xb:'UP_2K',
        0xc:'UP_20K',0xd:'UP_667',0xf:'NATIVE'}

def cls(p):
    dw0=p['dw0']
    pmode=(dw0>>10)&7
    txdis=(dw0>>8)&1; rxdis=(dw0>>9)&1
    if pmode!=0: return 'NF%d'%pmode
    if txdis and rxdis: return 'PARKED'
    if not txdis and rxdis: return 'OUTPUT'
    if txdis and not rxdis: return 'INPUT'
    return 'BIDIR'

out=[]
for p in pads:
    dw0,dw1=p['dw0'],p['dw1']
    k=cls(p)
    p['kind']=k
    p['rst']=RST[(dw0>>30)&3]
    p['pull']=PULL.get((dw1>>10)&0xf, hex((dw1>>10)&0xf))
    p['txval']=dw0&1
    p['rxval']=(dw0>>1)&1
    p['nmi']=(dw0>>17)&1; p['smi']=(dw0>>18)&1
    p['sci']=(dw0>>19)&1; p['apic']=(dw0>>20)&1
    out.append(p)

def show(kinds,title):
    sel=[p for p in out if p['kind'] in kinds]
    print("\n===== %s (%d) =====" % (title,len(sel)))
    for p in sel:
        routes=''.join(c for c,f in (('N','nmi'),('S','smi'),('C','sci'),('A','apic')) if p[f])
        print("%-10s %-8s %-14s rst=%-11s pull=%-7s tx=%d rx=%d %s" %
              (p['pad'], p['kind'], p['fn'] or '-', p['rst'], p['pull'],
               p['txval'], p['rxval'], ('route='+routes) if routes else ''))

show(['OUTPUT'],'GPIO OUTPUTS  (LEDs / enables / resets)')
show(['INPUT'],'GPIO INPUTS   (straps / presence / buttons)')
show(['BIDIR'],'GPIO BIDIRECTIONAL')
print("\n===== PARKED (unused) : %d =====" % len([p for p in out if p['kind']=='PARKED']))
print("===== NATIVE FUNCTION : %d =====" % len([p for p in out if p['kind'].startswith('NF')]))
print("\n=== reserved reset-config pads (need hand fix) ===")
for p in out:
    if p['rst'].startswith('RESERVED'): print("  ",p['pad'],p['fn'],hex(p['dw0']))
