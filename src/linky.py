import requests
import time, re, os
import json
import shutil
from datetime import datetime
import zipfile
from jdfc import JDFC as jc
import gzip
import sys, subprocess

pp = '../'
portal = 'portal'
linky = 'seznamy/linky'

url = "http://portal.idos.cz/Search.aspx?c=7&mi=2&io=-1&sv=&p="
url_inf = "http://portal.idos.cz/Info.aspx?mi=8&c=7"

def info(s):
  i = {}
  akt = 'aktIDX_val'
  for k in [akt, 'aktTT_val', 'kombinaceTT_val', 'linCnt_val', 'pdfCnt_val']:
    val = re.search(k+'.*>(.*)<', s)
    if val:
      i[k] = val.group(1)
  if akt in i:
    i['aktid'] = datetime.strptime(i[akt], "%H:%M %d.%m.%Y").strftime('%Y%m%d_%H%M')
  return i

def infz(zf, n):
  if n in zf.namelist():
    return info(zf.read(n).decode())

def get(url):
  for x in range(5):
    try:
      d = requests.get(url).text
      return d
    except:
      s = x * x
      print("error, sleep:", x, str(s)+"s")
      time.sleep(s)

def down(url, url_inf, redown='n', r2=400):
  ias = get(url_inf)
  ia = info(ias)
  akt = ia['aktid']
  ad = datetime.today().strftime("%Y%m%d_%H%M%S")
  zf = zipfile.ZipFile(pth('zip_tmp', akt+'-'+ad+'.zip'), 'w',compression=zipfile.ZIP_DEFLATED, compresslevel=9)
  zf.writestr('inf0', ias)
  jsl = pthl('json', akt)
  if os.path.exists(jsl):
    print('aktid', akt, 'už mám')
    if redown == 'q':
      redown = input('Prejete si pokracovat? y/N: ')
    if redown != 'y':
      zf.close()
      os.rename(zf.filename, zf.filename+'.cancel')
      return
  for i in range(0, r2):
    print('down page:', i)
    s = get(url + str(i))
    zf.writestr(str(i).zfill(4), s)
    #break #test
    if s.find("btn-arrow-next") == -1:
      break
  zf.writestr('inf', get(url_inf))
  zf.close()
  shutil.move(zf.filename, cp:=pth('zip', zf.filename))
  export(cp)

def export(p, mx = '-mx9'):
  jsp = pth('json', p)[:-4]+'.json'
  print('export', p, '>', jsp)
  
  d = {}
  zf = zipfile.ZipFile(p)
  lst = zf.namelist()
  pdfc = 0; pdfs = set()
  for i in range(0, 500):
    n = str(i).zfill(4)
    if n not in lst:
      break
    s = zf.read(n).decode()
    #m = re.findall('pdf/L(.*)\\.pdf', s)
    m = re.findall('pdf/L(.*)', s)
    for x in m:
      i = re.split('_|\\.', x, 3)
      r = i[0]
      if r not in d:
        d[r] = []
      a = {'id': i[2], 'od': i[1]}
      hod = re.search('\d{1,2}\\.\d{1,2}\\.\d{4}', x)
      if hod != None:
        #a['html_od'] = hod.group(0)
        dt = datetime.strptime(hod.group(0), '%d.%m.%Y').strftime('%y%m%d')
        if dt != i[1]: # vždycky je to stejné;)
          a['html_od'] = dt
          print('HTML')
      d[r].append(a)
      pdfc += 1; pdfs.add(i[2])
  ia = infz(zf, 'inf0')
  ib = infz(zf, 'inf')
  lincnt = str(len(d)); pdfcnt = str(pdfc)
  err = True if ib != ia or ia.get('linCnt_val') != lincnt or ia.get('pdfCnt_val') != pdfcnt else False
  if err:
    print('err', err, lincnt, pdfcnt, len(pdfs))
    ia.update({'lincnt': lincnt, 'pdfcnt': pdfcnt, 'pdfset': str(len(pdfs)), 'info2': ib })
  dd = {'info': ia, 'data': d}
  js = json.dumps(dd, indent=1)
  open(jsp, 'w').write(js)
  if not err:
    fpjs = pthl('json', ia['aktid'])
    gzjs = pthl('gzip', jsp)+'.gz'
    if not os.path.exists(fpjs):
      jc.fp(fpjs).write(js)
      print('7z', mx, gzjs)
      subprocess.check_output(' '.join(['7z a', mx, gzjs, fpjs]), shell=True)
    jsl = os.path.join(pp, os.path.dirname(linky), 'linky.json')
    if os.path.exists(jsl):
      aktl = ia.get('aktid')
      print('A', aktl)
      x  = json.load(open(jsl))
      if aktl <= x.get('info').get('aktid'):
        print('nekopiruji', jsl)
        return
    print('copy', jsl, 'from', fpjs)
    shutil.copy(fpjs, jsl)
    shutil.copy(gzjs, jsl+'.gz')

def pth(sb, f):
  f = os.path.basename(f)
  fp = os.path.join(pp, portal, sb, f[:4], f)
  os.makedirs(os.path.dirname(fp), exist_ok=True)
  return fp

def pthl(sb, f):
  fn = os.path.basename(f).split('-')[0]
  return os.path.join(pp, linky, sb, fn[:4], 'linky-'+fn+'.json')
  
def batch():
  for f,p in reversed(sorted(jc.ldr(os.path.join(pp, portal, 'zip')).items())):
    print(f)
    jsf = pth('json', f)[:-4]+'.json'
    if not os.path.exists(jsf):
      export(p)

if __name__ == "__main__":
    arg = list(sys.argv)
    arg.pop(0)
    if 'b' in arg:
      batch()
    q = 'n'
    if 'y' in arg:
      q = 'y'
    if 'q' in arg:
      q = 'q'
    if 'nd' not in arg:
      down(url, url_inf, q)
