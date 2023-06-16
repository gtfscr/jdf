def tt(p):
  fp = open(p, 'rb')
  def tl(li):
    b = sk().decode('cp1250')
    return [b[li[i-1]:li[i]] for i in range(1,len(li))]
  def tli(c,ln=4):
    return [int.from_bytes(c[i:i+ln],'little') for i in range(0,len(c),ln)]
  def gl():
    return int.from_bytes(fp.read(4), 'little')
  def sk():
    x = gl()
    if x != 0:
      y = gl()
      return fp.read(x)
  def ch(c):
    for x in range(c):
      sk()
  fp.read(100)
  fp.read(gl())
  ch(6)
  while (fp.read(1)) != b'\x00': pass
  fp.read(8)
  gl()
  st = tl(tli(sk()))
  ci = tli(sk())
  ch(5)
  if (c := sk()):
    cci = tli(c, 2)
    cc = tl(tli(sk()))
  for e, name in enumerate(st):
    print(str(ci[e])+',"'+name.replace('"', '\\"')+'",'+(cc[cci[e]] if c else ''))

def ttm(path):
  b = open(path, 'rb').read()
  def ti(b):
    return int.from_bytes(b, 'little', signed=True)
  def srch():
    for e,x in enumerate(b):
      if x&1==1:
        for ee,c in enumerate(range(e, len(b), 12)):
          if b[c]&1==0:
            break
          if ee==200:
            return e-7
  s = srch()
  ln = ti(b[s-8:s-4])
  for i in range(s, s+ln, 4):
    print(abs(ti(b[i:i+4])), end=None if i%3==0 else ',')

import sys
if __name__ == "__main__":
  p = sys.argv[1]
  if p.endswith('.tt'):
    tt(p)
  elif p.endswith('.ttm'):
    ttm(p)
