from capstone import *
import binascii
import sys


# this script is for x_86 elf files only

# helper function
def get_entry_value(name, special_len_e=None):
    if special_len_e:
        e_length = special_len_e
    else:
        e_length = len_e
    value = ''
    for j in range(addrs[name] + e_length - 1, addrs[name] - 1, -1):
        value += CODE[j]
    return int('0x' + binascii.hexlify(value), 16)

addrs = {}
f = open('test', 'rb')
assemble_codes = []

CODE = f.read()

mode_64 = False


addrs['machine'] = 0x12
addrs['entry'] = 0x18
# affected by mode_64
disasm_mode = CS_MODE_32
len_e = 4
addrs['phoff'] = 0x1C
addrs['shoff'] = 0x20
addrs['phentsize'] = 0x2A
addrs['shentsize'] = 0x2E

e_machine = get_entry_value('machine', 2)
if e_machine == 0x03:
    print 'reading x86 elf ...'
elif e_machine == 0x3e:
    print 'reading x86_64 elf ...'
    mode_64 = True
else:
    print 'incompatible file format ...'
    sys.exit()

if mode_64:
    len_e = 8
    addrs['phoff'] = 0x20
    addrs['shoff'] = 0x28
    addrs['phentsize'] = 0x36
    addrs['shentsize'] = 0x3A
    disasm_mode = CS_MODE_64

e_entry = get_entry_value('entry')
e_phoff = get_entry_value('phoff')
e_shoff = get_entry_value('shoff')
e_phentsize = get_entry_value('phentsize', 2)
e_shentsize = get_entry_value('shentsize', 2)

print hex(e_entry)
print e_phoff
print e_shoff
print e_phentsize
print e_shentsize

# prune the code [,)
CODE = CODE[e_phoff+e_phentsize: e_shoff]
e_entry -= (e_phoff+e_phentsize)
print hex(e_entry)

md = Cs(CS_ARCH_X86, disasm_mode)

for i in md.disasm(CODE, e_entry):
    print("0x%x:\t%s\t%s\t%s" % (i.address, i.mnemonic, i.op_str, ''.join('{:02x}'.format(x) for x in i.bytes)))
