import struct
d=open('/root/optiplex7040/me_deguard_7040.bin','rb').read()
off=d.find(b'$FPT')
num=struct.unpack_from('<I',d,off+4)[0]
print("FPT @0x%x, %d partitions:"%(off,num))
base=off+0x20
names=[]
for i in range(num):
    e=base+i*32
    name=d[e:e+4].rstrip(b'\x00').decode('latin1')
    poff,plen=struct.unpack_from('<II',d,e+8)
    if name: names.append(name); print("  %-4s off=0x%06x len=0x%06x"%(name,poff,plen))
print("\nMFS present:", "MFS" in names)
print("FTPR present:", "FTPR" in names)
