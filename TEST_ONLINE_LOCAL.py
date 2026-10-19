"""Smoke checks for private preview mode. No external service required."""
import base64, http.cookiejar, json, os, pathlib, socket, subprocess, sys, tempfile, time, urllib.request, urllib.error
ROOT=pathlib.Path(__file__).resolve().parent/'HSG_Tin_Hoc_AI'
with socket.socket() as s:
 s.bind(('127.0.0.1',0));port=s.getsockname()[1]
with tempfile.TemporaryDirectory() as d:
 env=os.environ.copy();env.update({'HOST':'0.0.0.0','PORT':str(port),'HSG_PUBLIC_PREVIEW':'1','HSG_PREVIEW_PASSWORD':'DemoPreview-Only-12345!','HSG_SECRET':'secret-for-local-test-only','HSG_DB_PATH':str(pathlib.Path(d)/'test.sqlite3')})
 proc=subprocess.Popen([sys.executable,'app.py'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 try:
  base=f'http://127.0.0.1:{port}'
  for _ in range(60):
   try:
    urllib.request.urlopen(base+'/auth/login', timeout=.5)
   except urllib.error.HTTPError as e:
    if e.code==401:break
   except Exception:pass
   if proc.poll() is not None:raise AssertionError('Server stopped unexpectedly')
   time.sleep(.1)
  def req(path,payload=None,auth=True,origin=None,opener=None):
   headers={}
   if auth:headers['Authorization']='Basic '+base64.b64encode(b'preview:DemoPreview-Only-12345!').decode()
   if payload is not None:headers['Content-Type']='application/json'
   if origin:headers['Origin']=origin
   r=urllib.request.Request(base+path,data=None if payload is None else json.dumps(payload).encode(),headers=headers)
   try:
    with (opener.open if opener else urllib.request.urlopen)(r,timeout=5) as res:return res.status,res.read()
   except urllib.error.HTTPError as e:return e.code,e.read()
  assert req('/auth/login',auth=False)[0]==401
  for p in ['/','/auth/login','/auth/register','/student/portal','/dashboard','/references','/style.css','/app.js']:
   status,_=req(p);assert status==200,(p,status)
  assert req('/api/register',{'name':'X','username':'xxx','password':'123456','role':'teacher'})[0]==403
  jar=http.cookiejar.CookieJar();opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
  status,_=req('/api/login',{'username':'giaovien','password':'Demo@12345'},opener=opener);assert status==200,status
  for p in ['/api/me','/api/topics','/api/problems','/api/classes','/api/contests','/api/assignments','/api/submissions']:
   status,_=req(p,opener=opener);assert status==200,(p,status)
  status,body=req('/api/classes',{'name':'Lop demo'},origin=f'http://evil.example',opener=opener);assert status==403,(status,body)
  print('PASS: preview authentication, routes, static files, restricted signup, teacher login, data API, CSRF origin checks')
 finally:
  proc.terminate()
  try:proc.wait(5)
  except subprocess.TimeoutExpired:proc.kill()
