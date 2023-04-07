import os, io, csv, shutil, sys
from ftplib import FTP
from zipfile import ZipFile
from jdfc import JDFC as jc, JDFZInfo

pth = '../cisjr'

class UnZip:
  def __init__(self):
    self.crcs = {}
    self.fp = jc.fp(os.path.join(pth, 'log', 'crcs.txt'), 'a+')
    self.fp.seek(0)
    for c,f in csv.reader(self.fp):
      self.crcs[c] = f

  def unzip(self, p):
    zf = ZipFile(p)
    nic,d,t = (bn:=os.path.basename(p)).split('_')
    t = t[0]
    flog = os.path.join(pth, 'log','JDF'+t, d[:4], bn[:-4]+'.txt')
    if os.path.exists(flog):
      return
    llog = []
    print('unzip', bn)
    zlen = len(zf.namelist())
    pos = 0
    for n in zf.namelist():
      pos += 1
      j = JDFZInfo(io.BytesIO(b:=zf.read(n)))
      c = j.crcs()
      if c not in self.crcs:
        print(('%.2f' %(pos/zlen*100))+'%', end=' ')
        name = j.linky().name(d[2:], t[:1])
        name = self.save(name, c, b)
        self.fp.write(c+','+name+'\r\n')
        self.crcs[c] = name

      llog.append(self.crcs.get(c)+','+n)
    jc.fp(flog).write('\r\n'.join(llog))
    print()

  def save(self, name, c, b):
    k = jc.kraj(name)
    p = os.path.join(pth, 'arch', k, name[:6])
    for f,fp in jc.ldr(p).items():
      if f.startswith(name[:24]):
        if c == JDFZInfo(fp).crcs():
          print('return', f[:-4])
          return f[:-4]
    _n = name; x = 1
    while os.path.exists(np := os.path.join(p, name+'.zip') ):
      name = _n+'_x'+str(x)
      x += 1
    jc.fp(np, 'wb').write(b)
    #jc.fp(UnZip.getp(name+'.zip', 'akt'), 'wb').write(b) # test
    print('save:', name)
    return name

  def getp(self, f, a, k=None):
    f = os.path.basename(f)
    if not k:
      k = jc.kraj(f)
    if a == 'arch':
      k += '/'+f[:6]
    return os.path.join(pth, a, k, f)

  def batch(self, p):
    for f,p in sorted(jc.ldr(p).items()):
      if p.endswith('.zip'):
        self.unzip(p)

  def cpakt(self):
    ml = {}
    for x in 'MB':
       d = jc.ldr(os.path.join(pth, 'log/JDF'+x))
       if d:
         k,v = max(d.items()); ml[k] = v
    k = '-'.join(sorted(ml))
    fplog = os.path.join(pth, 'log/log-akt', k)
    if not os.path.exists(fplog):
      sadd = set()
      akt = jc.ldr(os.path.join(pth, 'akt'))
      sdel = akt.copy()
      llog = []
      for f in ml.values():
        for f,n in csv.reader(open(f)):
          fz = f+'.zip'
          if fz not in akt:
            sadd.add(fz)
          if fz in sdel:
            sdel.pop(fz)
      ln = len(sadd); pos = 0
      for f in sorted(sadd):
        k = jc.kraj(f)
        src = self.getp(f, 'arch', k)
        dst = self.getp(f, 'akt', k)
        pos += 1
        print('cp akt','%.2f' % (pos/ln*100)+'%', f[:-4])
        llog.append('add '+f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
      for f,p in sorted(sdel.items()):
        llog.append(s:='delete: '+f)
        print(s)
        os.remove(p)
      jc.fp(fplog).write('\r\n'.join(llog))

#############

from threading import Thread
import time

dsize = 0
size = 0
jdfsrc = '../ftpcis'
def down(host, dct):
  global size
  global dsize
  ftp = FTP(host)
  ftp.login()
  for i, (loc,rtr) in enumerate(dct.items()):
    dsize = 0
    date = ftp.voidcmd('MDTM '+rtr).strip()[4:12]
    m2 = int(date[4:6])
    if m2%2 == 0:
      m2 -= 1
    m2 = str(m2).zfill(2)
    fn = '_'.join(['JDF', date, loc+'.zip'])
    pp = os.path.join(jdfsrc, 'jdf'+date[2:4]+'-'+m2,'JDF'+loc, fn)
    if os.path.exists(pp):
      print(str(i+1)+'/'+str(len(dct)), fn, 'už mám')
      continue
    try:
      size = ftp.size(rtr)
    except:
      print('???')
      size = 0
    fp = jc.fp(pp+'.tmp','wb')
    def handle(block):
      global dsize
      dsize += len(block)
      fp.write(block)
    def prnt():
      a = '%.2f' % (dsize/1000000)
      s=p = '?'
      if size != 0:
        p = '%.2f' % (dsize*100/size)
        s = ('%.2f' % (size/1000000))
      s = s+' MB '+ p+'%'
      print(str(i+1)+'/'+str(len(dct)), fn, a+'/'+s)
    def thr():
      while True:
        prnt()
        time.sleep(0.2)
        if not bol:
          break
    bol = True
    t = Thread(target=thr)
    t.start()
    try:
      ftp.retrbinary('RETR '+rtr, handle)
      bol = False
      prnt()
      fp.close()
      print('testzip')
      if not ZipFile(pp+'.tmp').testzip():
        print('ok')
        os.rename(pp+'.tmp', pp)
    finally:
      bol = False
  ftp.close()

if __name__ == '__main__':
  arg = list(sys.argv)
  arg.pop(0)
  u = None
  if 'd' in arg:
    d = {'M': 'draha/mestske/JDF.zip', 'B': 'JDF/JDF.zip'}; h = 'ftp.cisjr.cz'
    down(h, d)
  if 'u' in arg:
    u = UnZip()
    u.batch('../ftpcis')
  if 'a' in arg:
    if not u:
      u = UnZip()
    u.cpakt()