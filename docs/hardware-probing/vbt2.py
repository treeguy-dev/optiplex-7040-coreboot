import struct
d=open('/root/optiplex7040/data.vbt','rb').read()
bdb_off,=struct.unpack_from('<I',d,0x1c)
bdb_hdr,bdb_size=struct.unpack_from('<HH',d,bdb_off+18)
off=bdb_off+bdb_hdr
while off < bdb_off+bdb_size:
    bid=d[off]; bsz,=struct.unpack_from('<H',d,off+1)
    if bid==2: o=off+3; sz=bsz; break
    off+=3+bsz
cs=d[o+4]
DVO={0:'HDMIA',1:'HDMIB',2:'HDMIC',3:'HDMID',4:'LVDS',5:'TV',6:'CRT',
     7:'DPB',8:'DPC',9:'DPD',10:'DPA',11:'DPE',12:'HDMIE'}
HANDLE={0x0001:'CRT',0x0004:'EFP1',0x0008:'LFP1',0x0010:'EFP4',
        0x0020:'EFP3',0x0040:'EFP2',0x0080:'LFP2'}
print("child_dev_size=%d\n"%cs)
for i in range((sz-5)//cs):
    e=d[o+5+i*cs:o+5+(i+1)*cs]
    h,t=struct.unpack_from('<HH',e,0)
    if h==0 and t==0: continue
    print("entry %d  handle=0x%04x(%s)  device_type=0x%04x"%(i,h,HANDLE.get(h,'?'),t))
    print("   raw: "+" ".join("%02x"%b for b in e))
    # scan for plausible dvo_port bytes
    cands=[(k,e[k]) for k in range(4,cs) if e[k] in DVO]
    print("   dvo_port candidates: "+", ".join("off%d=%s"%(k,DVO[v]) for k,v in cands))
    print()
