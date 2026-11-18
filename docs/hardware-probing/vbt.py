import struct
d=open('/root/optiplex7040/data.vbt','rb').read()
print("sig:", d[:20].decode('latin1').strip())
ver,hdr_sz,vbt_sz = struct.unpack_from('<HHH', d, 0x14)
bdb_off, = struct.unpack_from('<I', d, 0x1c)
print("VBT version %d  header %d  size %d  bdb_offset 0x%x" % (ver,hdr_sz,vbt_sz,bdb_off))
bdb_ver,bdb_hdr, bdb_size = struct.unpack_from('<HHH', d, bdb_off+16)
print("BDB '%s' version %d header %d size %d" % (d[bdb_off:bdb_off+16].decode('latin1').strip(), bdb_ver,bdb_hdr,bdb_size))

off = bdb_off + bdb_hdr
blocks={}
while off < bdb_off + bdb_size:
    bid = d[off]; bsz, = struct.unpack_from('<H', d, off+1)
    blocks[bid]=(off+3,bsz)
    off += 3+bsz
print("BDB blocks present:", sorted(blocks))

DVO={0:'HDMIA',1:'HDMIB',2:'HDMIC',3:'HDMID',4:'LVDS',5:'TV',6:'CRT',
     7:'DPB',8:'DPC',9:'DPD',10:'DPA',11:'DPE',12:'HDMIE',13:'DPF',14:'HDMIF'}
def devtype(t):
    f=[]
    for bit,name in ((15,'analog'),(14,'digital'),(12,'displayport'),(11,'video_signaling'),
                     (4,'lvds_signaling'),(3,'tmds_signaling'),(2,'content_protect'),
                     (10,'not_hdmi'),(13,'internal')):
        if t>>bit & 1: f.append(name)
    return ",".join(f) or "-"

if 2 in blocks:
    o,sz = blocks[2]
    print("\n--- BDB block 2: General Definitions (size %d) ---" % sz)
    child_sz = d[o+4]
    print("child_dev_size = %d" % child_sz)
    n=(sz-5)//child_sz
    print("child device entries = %d\n" % n)
    for i in range(n):
        e = d[o+5+i*child_sz : o+5+(i+1)*child_sz]
        handle, dtype = struct.unpack_from('<HH', e, 0)
        if handle==0 and dtype==0: continue
        dvo = e[15] if child_sz>15 else None
        ddc = e[6]; aux = e[26] if child_sz>26 else None
        print("  [%d] handle=0x%04x device_type=0x%04x (%s)" % (i,handle,dtype,devtype(dtype)))
        print("       dvo_port=%s(%d)  ddc_pin=0x%02x  aux_ch=0x%02x"
              % (DVO.get(dvo,'?'), dvo if dvo is not None else -1, ddc, aux if aux is not None else 0))
