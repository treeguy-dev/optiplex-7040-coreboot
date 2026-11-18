import struct
me=open("/root/optiplex7040/regions/flashregion_2_intel_me.bin","rb").read()
assert me[16:20]==b"$FPT", me[16:20]
n=me[20]
print("FPT entries:",n)
off=48
parts={}
for i in range(n):
    e=me[off:off+32]; name=e[0:4].decode("latin1").strip("\x00")
    o,l=struct.unpack("<II",e[8:16])
    if name:
        print("  %-5s off=0x%06x len=0x%06x (%dK)"%(name,o,l,l//1024))
        parts[name]=l
    off+=32
nftp=parts.get("NFTP",0)
print("\nNFTP=%dK -> SKU guess: %s"%(nftp//1024, "5M (corporate/AMT)" if nftp>1024*1024*2 else "2M (consumer)"))
