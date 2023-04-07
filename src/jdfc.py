import os, zipfile
import csv

root = '../'
jdfsrc = 'ftpcis'

class JDFC:
  def fp(p, mode='w'):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return open(p, mode)
  
  def ldr(pth):
    d = {}
    for root, dirs, files in os.walk(pth):
      for name in files:
        p = os.path.join(root, name)
        if p.find('/.') == -1:
          d[name] = p
    return d

  def d(s):
    return s[4:8]+s[2:4]+s[:2]

  def kraj(s):
    r = int(s[0:3])
    if r < 100:
        return "MAD"
    if r < 200:
        return "PHA"
    if r < 319:
        return "STC"
    if r < 349:
        return "JHC"
    if r < 360:
        return "VYS"
    if r < 400:
        return "JHC"
    if r < 410:
        return "PLK"
    if r < 430:
        return "KVK"
    if r < 480:
        return "PLK"
    if r < 490:
        return "KVK"
    if r < 500:
        return "PLK"
    if r < 510:
        return "LBC"
    if r < 530:
        return "ULK"
    if r < 550:
        return "LBC"
    if r < 600:
        return "ULK"
    if r < 610:
        return "VYS"
    if r < 620:
        return "HKK"
    if r < 630:
        return "PAK"
    if r < 650:
        return "HKK"
    if r < 660:
        return "PAK"
    if r < 670:
        return "HKK"
    if r < 680:
        return "LBC"
    if r < 690:
        return "PAK"
    if r < 700:
        return "HKK"
    if r < 710:
        return "PAK"
    if r < 760:
        return "JMK"
    if r < 770:
        return "VYS"
    if r < 780:
        return "ZLK"
    if r < 790:
        return "OLK"
    if r < 800:
        return "VYS"
    if r < 810:
        return "ZLK"
    if r < 820: 
        return "JMK"
    if r < 830:
        return "ZLK"
    if r < 840:
        return "JMK"
    if r < 850:
        return "VYS"
    if r < 890:
        return "MSK"
    if r < 900:
        return "OLK"
    if r < 920:
        return "MSK"
    if r < 940:
        return "OLK"
    if r < 950:
        return "ZLK"
    if r < 960:
        return "OLK"

class JDFZInfo(zipfile.ZipFile):
  nl = None
  _crcs = None
  def crcs(self):
    if not self._crcs:
      s = set()
      for i in self.infolist():
        fn = i.filename.upper()
        if fn != 'VERZEJDF.TXT':
          s.add( fn[:4]+':'+ hex(i.CRC)[2:] )
      self._crcs = '-'.join(sorted(s))
    return self._crcs
    
  def gets(self, name):
    return self.read(self.nlist().get(name.upper())).decode('cp1250')
    
  def getc(self, name):
    return csv.reader([self.gets(name)])

  def nlist(self):
    if not self.nl:
      self.nl = {}
      for n in self.namelist():
        self.nl[ n[:-4].upper() ] = n
    return self.nl

  def linky(self):
    return Linky(list(self.getc('linky'))[0])
      

class Linky:
  def __init__(self, lst):
    self.rid = lst[0]
    self.vjr = '2'
    d = len(lst)-2
    if d > 8:
            d -= 2
            self.vjr = lst[5]
    self.od = JDFC.d(lst[d])
    self.do = JDFC.d(lst[d+1])
    
  def name(self, jdate, typ):
    return '_'.join( [self.rid, self.od, self.do, jdate, typ, self.vjr] )