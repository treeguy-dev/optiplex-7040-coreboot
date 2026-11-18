import mmap, os, struct
bar=int(open('/sys/bus/pci/devices/0000:00:14.0/resource').readline().split()[0],16)
f=os.open('/dev/mem', os.O_RDONLY)
m=mmap.mmap(f,0x10000,mmap.MAP_SHARED,mmap.PROT_READ,offset=bar & ~0xfff)
rd=lambda o: struct.unpack('<I',m[o:o+4])[0]
names={1:'USB Legacy Support',2:'Supported Protocol',3:'Ext Power Mgmt',
       4:'IO Virtualization',5:'Message Interrupt',6:'Local Memory',
       10:'USB Debug Capability',17:'Ext Message Interrupt'}
off=((rd(0x10)>>16)&0xffff)*4
print("xECP list:")
seen=set()
while off and off not in seen and off < 0xf000:
    seen.add(off)
    v=rd(off); cid=v&0xff; nxt=(v>>8)&0xff
    tag=names.get(cid, 'VENDOR-DEFINED' if cid>=192 else 'reserved/unknown')
    print("  @0x%04x  id=%3d (%s)  next=+0x%x" % (off,cid,tag,nxt*4))
    if cid>=192 or cid not in names:
        for k in range(0,min(nxt*4 if nxt else 32,64),16):
            print("        %04x: %s"%(off+k," ".join("%08x"%rd(off+k+j) for j in (0,4,8,12))))
    if not nxt: break
    off+=nxt*4
m.close(); os.close(f)
