"""HSG Tin Hoc AI - local demonstration app. Python 3.10+, no pip packages required."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sqlite3, json, hashlib, hmac, secrets, base64, os, time, mimetypes, urllib.request, urllib.error, pathlib, threading, csv, io, webbrowser, socket, re

ROOT=pathlib.Path(__file__).resolve().parent
DB=pathlib.Path(os.environ.get('HSG_DB_PATH',str(ROOT/'hsg.sqlite3')))
PUBLIC_PREVIEW=os.environ.get('HSG_PUBLIC_PREVIEW')=='1'
PREVIEW_PASSWORD=os.environ.get('HSG_PREVIEW_PASSWORD','')
HOST=os.environ.get('HOST','127.0.0.1'); PORT=int(os.environ.get('PORT','8765'))
KEY=os.environ.get('HSG_SECRET') or secrets.token_hex(32)
JUDGE_URL=os.environ.get('JUDGE0_URL','').rstrip('/')
JUDGE_KEY=os.environ.get('JUDGE0_API_KEY','')
JUDGE_HOST=os.environ.get('JUDGE0_HOST','')
JUDGE_AUTH=os.environ.get('JUDGE0_AUTH_HEADER','X-Auth-Token')
JUDGE_TIMEOUT=int(os.environ.get('JUDGE0_POLL_SECONDS','65'))
LOCK=threading.Lock()

def db():
 c=sqlite3.connect(DB,timeout=15);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');return c

def hash_pw(p,s=None):
 s=s or secrets.token_hex(16)
 return s+':'+hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),180000).hex()
def check_pw(p,h):
 try:s,stored=h.split(':');return hmac.compare_digest(hash_pw(p,s),h)
 except:return False

def init():
 with db() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('teacher','student')));
CREATE TABLE IF NOT EXISTS topics(id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS problems(id INTEGER PRIMARY KEY, topic_id INTEGER NOT NULL REFERENCES topics(id), title TEXT NOT NULL, description TEXT NOT NULL, input_spec TEXT NOT NULL, output_spec TEXT NOT NULL, sample_in TEXT NOT NULL, sample_out TEXT NOT NULL, difficulty TEXT NOT NULL, created_by INTEGER REFERENCES users(id));
CREATE TABLE IF NOT EXISTS test_cases(id INTEGER PRIMARY KEY, problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE, input_text TEXT NOT NULL, output_text TEXT NOT NULL, points INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS submissions(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), problem_id INTEGER NOT NULL REFERENCES problems(id), language TEXT NOT NULL, source TEXT NOT NULL, verdict TEXT NOT NULL, score REAL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS contests(id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, created_by INTEGER REFERENCES users(id), created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS contest_problems(contest_id INTEGER REFERENCES contests(id) ON DELETE CASCADE, problem_id INTEGER REFERENCES problems(id), position INTEGER NOT NULL, PRIMARY KEY(contest_id,problem_id));''')
  c.executescript('''CREATE TABLE IF NOT EXISTS classes(id INTEGER PRIMARY KEY, name TEXT NOT NULL, join_code TEXT NOT NULL UNIQUE, teacher_id INTEGER NOT NULL REFERENCES users(id), created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS class_members(class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE, student_id INTEGER NOT NULL REFERENCES users(id), joined_at TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(class_id,student_id));
CREATE TABLE IF NOT EXISTS assignments(id INTEGER PRIMARY KEY, class_id INTEGER NOT NULL REFERENCES classes(id), title TEXT NOT NULL, due_at TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS assignment_problems(assignment_id INTEGER REFERENCES assignments(id) ON DELETE CASCADE, problem_id INTEGER REFERENCES problems(id), PRIMARY KEY(assignment_id,problem_id));
CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id,created_at);
CREATE INDEX IF NOT EXISTS idx_tests_problem ON test_cases(problem_id);''')
  if c.execute('SELECT count(*) FROM users').fetchone()[0]==0:
   c.executemany('INSERT INTO users(name,username,password,role) VALUES (?,?,?,?)', [('Giáo viên Demo','giaovien',hash_pw('Demo@12345'),'teacher'),('Học sinh Demo','hocsinh',hash_pw('Demo@12345'),'student')])
  if c.execute('SELECT count(*) FROM topics').fetchone()[0]==0:
   topics=[('Lập trình cơ bản','Kiểu dữ liệu, rẽ nhánh, vòng lặp, hàm và tệp'),('Đại số và số học','Số nguyên tố, chính phương, chia hết, ước số và bội số'),('Hình học tính toán','Điểm, đường thẳng, tam giác và các công thức hình học'),('Xâu ký tự và mảng','Xâu, mảng một chiều và hai chiều'),('Dãy số và đoạn con','Fibonacci, dãy con, đoạn con'),('Sắp xếp và tìm kiếm','Các thuật toán tìm kiếm, sắp xếp'),('Thuật toán nâng cao','Duyệt nhị phân, hoán vị, chia để trị')]
   c.executemany('INSERT INTO topics(title,description) VALUES(?,?)',topics)
  if c.execute('SELECT count(*) FROM problems').fetchone()[0]==0:
   c.execute('''INSERT INTO problems(topic_id,title,description,input_spec,output_spec,sample_in,sample_out,difficulty,created_by) VALUES(?,?,?,?,?,?,?,?,1)''',(2,'Kiểm tra số nguyên tố','Cho số nguyên N. Xác định N có phải số nguyên tố hay không.','Một số nguyên N (1 ≤ N ≤ 10^9).','In YES nếu là số nguyên tố, ngược lại in NO.','17','YES','Cơ bản'))
   c.executemany('INSERT INTO test_cases(problem_id,input_text,output_text,points) VALUES(1,?,?,?)',[('2','YES',1),('4','NO',1),('1','NO',1),('97','YES',1),('100','NO',1)])
   c.execute('''INSERT INTO problems(topic_id,title,description,input_spec,output_spec,sample_in,sample_out,difficulty,created_by) VALUES(?,?,?,?,?,?,?,?,1)''',(5,'Tổng đoạn con','Cho N số nguyên, tìm tổng lớn nhất của một đoạn con liên tiếp không rỗng.','Dòng 1: N (1 ≤ N ≤ 100000). Dòng 2: N số nguyên.','Một số nguyên là tổng lớn nhất.','5\n-2 3 -1 5 -4','7','Nâng cao'))
   c.executemany('INSERT INTO test_cases(problem_id,input_text,output_text,points) VALUES(2,?,?,?)',[('5\n-2 3 -1 5 -4','7',1),('3\n-5 -2 -7','-2',1),('1\n8','8',1)])
  if c.execute('SELECT count(*) FROM problems').fetchone()[0]==2:
   samples=[
    (3,'Diện tích hình chữ nhật','Cho chiều dài a và chiều rộng b là các số nguyên dương. Tính diện tích hình chữ nhật.','Hai số nguyên dương a, b (1 ≤ a,b ≤ 10000).','In ra a*b.','3 5','15','Cơ bản',[('3 5','15'),('1 1','1'),('10000 10000','100000000')]),
    (4,'Đếm chữ số trong xâu','Cho một dòng văn bản không chứa xuống dòng. Đếm số ký tự là chữ số từ 0 đến 9.','Một dòng có độ dài không quá 10000.','In số ký tự là chữ số.','Tin9hoc2026','5','Cơ bản',[('abc123','3'),('hello','0'),('00a9','3')]),
    (6,'Tìm kiếm tuyến tính','Cho N số nguyên và số X. Hãy tìm vị trí đầu tiên của X trong dãy, đánh số từ 1. Nếu không có, in -1.','Dòng 1: N và X. Dòng 2: N số nguyên (1 ≤ N ≤ 10000).','Vị trí đầu tiên hoặc -1.','5 7\n2 7 4 7 9','2','Cơ bản',[('5 7\n2 7 4 7 9','2'),('3 6\n1 2 3','-1'),('1 5\n5','1')]),
    (5,'Số Fibonacci thứ N','Tính F(N) với F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2).','Một số nguyên N (0 ≤ N ≤ 40).','In F(N).','8','21','Vận dụng',[('0','0'),('1','1'),('8','21'),('40','102334155')])]
   for tid,title,description,ins,outs,sin,sout,diff,tests in samples:
    cur=c.execute('INSERT INTO problems(topic_id,title,description,input_spec,output_spec,sample_in,sample_out,difficulty,created_by) VALUES (?,?,?,?,?,?,?,?,1)',(tid,title,description,ins,outs,sin,sout,diff))
    c.executemany('INSERT INTO test_cases(problem_id,input_text,output_text,points) VALUES (?,?,?,1)',[(cur.lastrowid,a,b) for a,b in tests])
  if c.execute('SELECT count(*) FROM contests').fetchone()[0]==0:
   c.execute("INSERT INTO contests(title,description,created_by) VALUES('Đề thử HSG Tin học lớp 9','Mẫu đề để bổ sung 4 bài, mỗi bài 5 điểm.',1)")
   c.execute('INSERT INTO contest_problems VALUES(1,1,1)');c.execute('INSERT INTO contest_problems VALUES(1,2,2)')
  seed_extra(c)
  if PUBLIC_PREVIEW:seed_preview_evidence(c)


def seed_preview_evidence(c):
 """Illustrative records for contest demonstration; NEVER actual grading or learner scores."""
 c.execute("""CREATE TABLE IF NOT EXISTS demo_judge_events(id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),problem_id INTEGER NOT NULL REFERENCES problems(id),
  language TEXT NOT NULL,verdict TEXT NOT NULL,score REAL NOT NULL,created_at TEXT NOT NULL)""")
 teacher=c.execute("SELECT id FROM users WHERE username='giaovien' AND role='teacher'").fetchone()
 student=c.execute("SELECT id FROM users WHERE username='hocsinh' AND role='student'").fetchone()
 if not teacher or not student:return
 teacher,student=teacher[0],student[0]
 row=c.execute("SELECT id FROM classes WHERE teacher_id=? AND join_code='DEMO2026'",(teacher,)).fetchone()
 if row:cid=row[0]
 else:cid=c.execute("INSERT INTO classes(name,join_code,teacher_id) VALUES('Lớp bồi dưỡng HSG 9 – MINH HỌA','DEMO2026',?)",(teacher,)).lastrowid
 c.execute('INSERT OR IGNORE INTO class_members(class_id,student_id) VALUES(?,?)',(cid,student))
 sample=[('Buổi 1 · Số học và điều kiện',[1,7,8]),('Buổi 2 · Xâu và mảng',[4,11,12]),('Buổi 3 · Dãy số và tìm kiếm',[2,6,20])]
 for title,ids in sample:
  row=c.execute('SELECT id FROM assignments WHERE class_id=? AND title=?',(cid,title)).fetchone()
  if row:aid=row[0]
  else:aid=c.execute('INSERT INTO assignments(class_id,title,due_at) VALUES(?,?,NULL)',(cid,title)).lastrowid
  for pid in ids:
   if c.execute('SELECT 1 FROM problems WHERE id=?',(pid,)).fetchone():c.execute('INSERT OR IGNORE INTO assignment_problems(assignment_id,problem_id) VALUES(?,?)',(aid,pid))
 if c.execute('SELECT 1 FROM demo_judge_events WHERE user_id=?',(student,)).fetchone():return
 rows=[(1,'cpp','AC',5,'2026-10-15 08:12'),(7,'python','WA',2,'2026-10-15 08:26'),(7,'python','AC',5,'2026-10-15 08:39'),(4,'cpp','AC',5,'2026-10-16 09:10'),(6,'pascal','CE',0,'2026-10-17 14:05'),(6,'pascal','AC',5,'2026-10-17 14:32'),(2,'cpp','TLE',0,'2026-10-18 10:01'),(2,'cpp','WA',3,'2026-10-18 10:25')]
 for pid,lang,v,score,at in rows:
  if c.execute('SELECT 1 FROM problems WHERE id=?',(pid,)).fetchone():
   c.execute('INSERT INTO demo_judge_events(user_id,problem_id,language,verdict,score,created_at) VALUES(?,?,?,?,?,?)',(student,pid,lang,v,score,at))

def seed_extra(c):
 rows=[(1, 'Tổng N số tự nhiên', 'Tính 1+2+...+N với N không âm.', 'N (0 ≤ N ≤ 10^9)', 'Một số nguyên biểu diễn tổng.', '5', '15', 'Cơ bản', [('0', '0'), ('10', '55'), ('100', '5050')]), (1, 'Kiểm tra năm nhuận', 'Cho năm Y dương, in YES nếu là năm nhuận, ngược lại NO.', 'Một số nguyên Y từ 1 đến 100000', 'YES hoặc NO', '2024', 'YES', 'Cơ bản', [('1900', 'NO'), ('2000', 'YES'), ('2023', 'NO')]), (1, 'Tổng các chữ số', 'Tính tổng các chữ số thập phân của N.', 'N nguyên không âm (N ≤ 10^18)', 'Tổng chữ số', '12345', '15', 'Cơ bản', [('0', '0'), ('9999', '36'), ('10020', '3')]), (1, 'Ước chung lớn nhất', 'Cho hai số nguyên không âm A,B, tìm UCLN; giả sử ít nhất một số khác 0.', 'A B (0 ≤ A,B ≤ 10^9)', 'UCLN(A,B)', '18 24', '6', 'Vận dụng', [('7 13', '1'), ('100 25', '25'), ('0 10', '10')]), (2, 'Số chính phương', 'Cho N không âm, xác định N có phải số chính phương.', 'Một số nguyên N (0 ≤ N ≤ 10^12)', 'YES hoặc NO', '49', 'YES', 'Cơ bản', [('0', 'YES'), ('15', 'NO'), ('1000000', 'YES')]), (2, 'Đếm ước số', 'Đếm số ước nguyên dương của N.', 'Một số N (1 ≤ N ≤ 10^9)', 'Số ước dương', '12', '6', 'Vận dụng', [('1', '1'), ('36', '9'), ('97', '2')]), (2, 'Bội chung nhỏ nhất', 'Cho A,B nguyên dương, tính BCNN(A,B).', 'A B (1 ≤ A,B ≤ 10^9)', 'BCNN(A,B)', '6 8', '24', 'Vận dụng', [('3 7', '21'), ('10 10', '10'), ('12 18', '36')]), (3, 'Chu vi hình chữ nhật', 'Cho hai cạnh nguyên dương A,B, tính chu vi hình chữ nhật.', 'A B (1 ≤ A,B ≤ 10^9)', 'Chu vi', '3 5', '16', 'Cơ bản', [('1 1', '4'), ('10 20', '60'), ('100 7', '214')]), (3, 'Diện tích tam giác vuông', 'Cho hai cạnh góc vuông A,B nguyên dương. In diện tích dưới dạng số thực với đúng 1 chữ số thập phân.', 'A B (1 ≤ A,B ≤ 10^6)', 'Diện tích với 1 chữ số sau dấu chấm', '3 4', '6.0', 'Vận dụng', [('1 1', '0.5'), ('2 7', '7.0'), ('10 10', '50.0')]), (3, 'Ba cạnh tam giác', 'Cho ba số nguyên dương A,B,C. Kiểm tra chúng tạo thành tam giác không suy biến.', 'A B C (1 ≤ A,B,C ≤ 10^9)', 'YES hoặc NO', '3 4 5', 'YES', 'Cơ bản', [('1 2 3', 'NO'), ('5 5 9', 'YES'), ('1 1 3', 'NO')]), (4, 'Đảo ngược xâu', 'Nhập một dòng ký tự không chứa ký tự xuống dòng, in các ký tự theo thứ tự ngược.', 'Một dòng độ dài không quá 10000', 'Xâu đảo ngược', 'abc123', '321cba', 'Cơ bản', [('hello', 'olleh'), ('A', 'A'), ('a b', 'b a')]), (4, 'Đếm nguyên âm', 'Cho xâu chỉ gồm chữ cái tiếng Anh, đếm số nguyên âm a,e,i,o,u không phân biệt hoa thường.', 'Một dòng không quá 10000 ký tự', 'Số nguyên âm', 'Hello', '2', 'Cơ bản', [('AI', '2'), ('xyz', '0'), ('Education', '5')]), (4, 'Phần tử lớn nhất', 'Cho N số nguyên, tìm phần tử lớn nhất.', 'Dòng 1 N (1 ≤ N ≤ 100000); dòng 2 gồm N số nguyên', 'Giá trị lớn nhất', '5\n2 -1 7 3 4', '7', 'Cơ bản', [('1\n-9', '-9'), ('4\n-3 -1 -2 -4', '-1'), ('3\n10 10 5', '10')]), (4, 'Tổng đường chéo chính', 'Cho ma trận vuông N×N số nguyên. Tính tổng các phần tử trên đường chéo chính.', 'Dòng 1 N (1 ≤ N ≤ 100); sau đó N hàng, mỗi hàng N số nguyên', 'Tổng đường chéo chính', '2\n1 2\n3 4', '5', 'Vận dụng', [('1\n9', '9'), ('3\n1 2 3\n4 5 6\n7 8 9', '15'), ('2\n-1 5\n4 -2', '-3')]), (5, 'Tổng các số chẵn trong dãy', 'Cho N số nguyên. Tính tổng các phần tử chẵn.', 'Dòng 1 N (1 ≤ N ≤ 100000), dòng 2 gồm N số', 'Tổng các số chẵn', '5\n1 2 3 4 5', '6', 'Cơ bản', [('3\n1 3 5', '0'), ('4\n-2 0 3 8', '6'), ('1\n10', '10')]), (5, 'Dãy tăng liên tiếp dài nhất', 'Cho N số nguyên. Tìm độ dài đoạn liên tiếp dài nhất tăng nghiêm ngặt.', 'Dòng 1 N (1 ≤ N ≤ 100000), dòng 2 N số nguyên', 'Độ dài đoạn tăng dài nhất', '6\n1 2 5 3 4 6', '3', 'Nâng cao', [('1\n9', '1'), ('5\n5 4 3 2 1', '1'), ('4\n1 2 3 4', '4')]), (6, 'Tìm kiếm nhị phân', 'Cho dãy N số nguyên đã sắp xếp tăng không giảm và giá trị X. In vị trí đầu tiên của X (đánh số từ 1), hoặc -1.', 'Dòng 1 N X; dòng 2 N số nguyên (N ≤ 100000)', 'Vị trí đầu tiên, hoặc -1', '5 7\n1 3 7 7 9', '3', 'Vận dụng', [('4 4\n1 2 3 5', '-1'), ('1 8\n8', '1'), ('5 2\n2 2 2 2 2', '1')]), (6, 'Phần tử nhỏ thứ K', 'Cho N số nguyên và K, tìm số nhỏ thứ K sau khi sắp xếp tăng dần, tính cả phần tử lặp.', 'Dòng 1 N K (1 ≤ K ≤ N ≤ 100000); dòng 2 N số', 'Số nhỏ thứ K', '5 3\n5 1 4 3 2', '3', 'Vận dụng', [('3 2\n7 7 1', '7'), ('1 1\n-5', '-5'), ('4 4\n2 1 3 2', '3')]), (6, 'Đếm phần tử khác nhau', 'Cho N số nguyên, đếm số giá trị phân biệt.', 'Dòng 1 N (1 ≤ N ≤ 100000); dòng 2 N số', 'Số giá trị phân biệt', '6\n1 2 2 3 1 4', '4', 'Vận dụng', [('1\n7', '1'), ('4\n5 5 5 5', '1'), ('5\n-1 0 1 -1 0', '3')]), (7, 'Đếm chuỗi nhị phân độ dài N', 'Tính số chuỗi nhị phân có độ dài N, kể cả chuỗi toàn số 0.', 'N (0 ≤ N ≤ 60)', 'Số chuỗi nhị phân', '3', '8', 'Vận dụng', [('0', '1'), ('1', '2'), ('10', '1024')]), (7, 'Lũy thừa nhanh modulo', 'Cho A,N,M, tính A^N mod M.', 'A N M (0 ≤ A ≤ 10^9; 0 ≤ N ≤ 10^9; 1 ≤ M ≤ 10^9)', 'Kết quả chia dư', '2 10 1000', '24', 'Nâng cao', [('10 0 7', '1'), ('3 3 5', '2'), ('5 4 1', '0')]), (7, 'Tổng các tập con', 'Cho N số nguyên (N ≤ 20) và số S. In YES nếu tồn tại một tập con (có thể rỗng) có tổng bằng S, ngược lại NO.', 'Dòng 1 N S; dòng 2 N số nguyên', 'YES hoặc NO', '3 5\n1 2 4', 'YES', 'Nâng cao', [('3 8\n1 2 4', 'NO'), ('2 0\n2 4', 'YES'), ('4 6\n-1 3 4 2', 'YES')])]
 existing={r[0] for r in c.execute("SELECT title FROM problems")}
 for tid,title,description,ins,outs,sin,sout,diff,tests in rows:
  if title in existing:continue
  cur=c.execute("INSERT INTO problems(topic_id,title,description,input_spec,output_spec,sample_in,sample_out,difficulty,created_by) VALUES (?,?,?,?,?,?,?,?,1)",(tid,title,description,ins,outs,sin,sout,diff))
  c.executemany("INSERT INTO test_cases(problem_id,input_text,output_text,points) VALUES (?,?,?,1)",[(cur.lastrowid,a,b) for a,b in tests])

def sign(value):return hmac.new(KEY.encode(),value.encode(),hashlib.sha256).hexdigest()
def token(user):
 payload=base64.urlsafe_b64encode(json.dumps({'id':user['id'],'exp':int(time.time())+12*3600}).encode()).decode().rstrip('=');return payload+'.'+sign(payload)
def get_user(cookie):
 try:
  cookies=dict(i.strip().split('=',1) for i in cookie.split(';') if '=' in i)
  t=cookies.get('session','');p,s=t.rsplit('.',1)
  if not hmac.compare_digest(s,sign(p)):return None
  obj=json.loads(base64.urlsafe_b64decode(p+'='*(-len(p)%4)))
  if obj['exp']<time.time():return None
  with db() as c:
   row=c.execute('SELECT id,name,username,role FROM users WHERE id=?',(obj['id'],)).fetchone()
   return dict(row) if row else None
 except:return None

def judge_request(path, payload=None, timeout=10):
 if not JUDGE_URL:raise RuntimeError('Chưa thiết lập JUDGE0_URL trong cấu hình.')
 headers={'Content-Type':'application/json', 'Accept':'application/json'}
 if JUDGE_KEY:headers[JUDGE_AUTH]=JUDGE_KEY
 if JUDGE_HOST:headers['X-RapidAPI-Host']=JUDGE_HOST
 req=urllib.request.Request(JUDGE_URL+path, headers=headers, data=json.dumps(payload).encode('utf-8') if payload is not None else None, method='POST' if payload is not None else 'GET')
 try:
  with urllib.request.urlopen(req,timeout=timeout) as response:return json.load(response)
 except urllib.error.HTTPError as err:
  try:detail=err.read(500).decode('utf-8','replace')
  except:detail=''
  raise RuntimeError(f'Judge0 HTTP {err.code}: {detail[:180]}') from err
 except (urllib.error.URLError, TimeoutError, socket.timeout) as err:raise RuntimeError('Không thể kết nối Judge0. Kiểm tra URL, mạng, khóa API và máy chấm.') from err
 except (ValueError,KeyError) as err:raise RuntimeError('Judge0 trả dữ liệu không hợp lệ.') from err

def judge_languages():
 data=judge_request('/languages',timeout=10)
 if not isinstance(data,list):raise RuntimeError('Judge0 không trả danh sách ngôn ngữ.')
 return [{'id':i.get('id'),'name':i.get('name','')} for i in data if isinstance(i,dict)]

def judge_language_id(language,items):
 patterns={
  'cpp': lambda n: ('c++' in n and ('g++' in n or 'gcc' in n or 'clang' in n)) or 'c++17' in n,
  'python':lambda n:'python' in n and ('3.' in n or ' 3' in n),
  'pascal':lambda n:'pascal' in n or '(fpc' in n,
 }
 if language not in patterns:raise RuntimeError('Ngôn ngữ không hợp lệ.')
 match=[i for i in items if patterns[language](i['name'].lower())]
 if not match:raise RuntimeError('Máy chấm chưa cài ngôn ngữ '+language+'.')
 # Prefer C++17+ when available; use actual ID reported by host
 if language=='cpp':match.sort(key=lambda i:('17' not in i['name'] and '20' not in i['name'] and '23' not in i['name']))
 return match[0]['id']

def judge(source,language,stdin, langid=None):
 if langid is None:langid=judge_language_id(language,judge_languages())
 # Judge0 limits are per test, and output is compared on our backend.
 data={'source_code':source,'language_id':langid,'stdin':stdin, 'cpu_time_limit':2,'wall_time_limit':6,'memory_limit':131072,'max_file_size':2048,'enable_network':False}
 response=judge_request('/submissions?base64_encoded=false&wait=false',data,timeout=15)
 tok=response.get('token') if isinstance(response,dict) else None
 if not tok or not re.fullmatch(r'[A-Za-z0-9-]{8,100}',str(tok)):raise RuntimeError('Judge0 không trả token hợp lệ.')
 deadline=time.monotonic()+max(10,min(120,JUDGE_TIMEOUT))
 while time.monotonic()<deadline:
  time.sleep(.75)
  r=judge_request('/submissions/'+tok+'?base64_encoded=false',timeout=12)
  if isinstance(r,dict) and (r.get('status') or {}).get('id',0)>2:return r
 raise RuntimeError('Judge0 chưa xử lý xong trong thời gian chờ. Không ghi nhận điểm.')

def normalize_output(s):
 # Ignore trailing whitespace on each line; do not ignore differences inside output.
 return '\n'.join(line.rstrip() for line in str(s or '').replace('\r\n','\n').replace('\r','\n').strip().split('\n'))

def judge_health():
 if not JUDGE_URL:return {'configured':False,'connected':False,'message':'Chưa cấu hình JUDGE0_URL. Cần một Judge0 riêng đang hoạt động.'}
 try:
  langs=judge_languages();choices={}
  for lang in ('cpp','python','pascal'):
   try:choices[lang]=judge_language_id(lang,langs)
   except RuntimeError:choices[lang]=None
  return {'configured':True,'connected':True,'languages':choices,'message':'Kết nối danh sách ngôn ngữ thành công. Cần chạy thử để xác nhận worker hoạt động.'}
 except Exception as exc:return {'configured':True,'connected':False,'message':str(exc)}

def outcome(r):
 status=r.get('status') or {};v=status.get('description','Unknown');return v

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def preview_gate(self):
  if not PUBLIC_PREVIEW:return True
  supplied=self.headers.get('Authorization','')
  expected='Basic '+base64.b64encode(('preview:'+PREVIEW_PASSWORD).encode()).decode()
  if hmac.compare_digest(supplied,expected):return True
  self.send_response(401)
  self.send_header('WWW-Authenticate','Basic realm="HSG Tin Hoc AI Preview"')
  self.send_header('Content-Type','text/plain; charset=utf-8')
  self.send_header('Cache-Control','no-store')
  self.end_headers()
  self.wfile.write('Can mat khau xem truoc. Khong dung tai khoan hoc sinh that.'.encode())
  return False

 def send(self,status=200,data=None,cookie=None):
  body=json.dumps(data if data is not None else {},ensure_ascii=False).encode()
  self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('X-Frame-Options','DENY');self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'")
  if cookie:self.send_header('Set-Cookie',cookie)
  self.end_headers();self.wfile.write(body)
 def read_json(self):
  try:
   n=int(self.headers.get('Content-Length',0))
   if n>100000:return None
   return json.loads(self.rfile.read(n))
  except:return None
 def fail(self,msg,status=400):self.send(status,{'error':msg})
 def auth(self,role=None):
  u=get_user(self.headers.get('Cookie',''))
  if not u:self.fail('Vui lòng đăng nhập.',401);return None
  if role and u['role']!=role:self.fail('Không có quyền thực hiện.',403);return None
  return u
 def do_GET(self):
  if not self.preview_gate():return
  p=urlparse(self.path).path
  if p.startswith('/api/'):
   u=get_user(self.headers.get('Cookie',''))
   if p=='/api/me':return self.send(200,{'user':u,'judgeReady':bool(JUDGE_URL)})
   if p=='/api/judge/status':return self.send(200,judge_health())
   if p=='/api/catalog':
    with db() as c:
     ts=[dict(x) for x in c.execute('SELECT id,title,description FROM topics ORDER BY id')]
     ps=[dict(x) for x in c.execute('SELECT p.id,p.topic_id,p.title,p.description,p.input_spec,p.output_spec,p.sample_in,p.sample_out,p.difficulty,t.title AS topic FROM problems p JOIN topics t ON t.id=p.topic_id ORDER BY p.id')]
    return self.send(200,{'topics':ts,'problems':ps})
   if not u:return self.fail('Vui lòng đăng nhập.',401)
   with db() as c:
    if p=='/api/classes':
     if u['role']=='teacher':
      rows=c.execute('SELECT * FROM classes WHERE teacher_id=? ORDER BY id DESC',(u['id'],)).fetchall()
     else:
      rows=c.execute('SELECT c.* FROM classes c JOIN class_members m ON m.class_id=c.id WHERE m.student_id=? ORDER BY c.id DESC',(u['id'],)).fetchall()
     result=[]
     for row in rows:
      obj=dict(row)
      obj['students']=[dict(x) for x in c.execute('SELECT u.id,u.name,u.username FROM class_members m JOIN users u ON u.id=m.student_id WHERE m.class_id=? ORDER BY u.name',(row['id'],))] if u['role']=='teacher' else []
      result.append(obj)
     return self.send(200,{'items':result})
    if p=='/api/assignments':
     if u['role']=='teacher':
      rows=c.execute('SELECT a.*,c.name class_name FROM assignments a JOIN classes c ON c.id=a.class_id WHERE c.teacher_id=? ORDER BY a.id DESC',(u['id'],))
     else:
      rows=c.execute('SELECT a.*,c.name class_name FROM assignments a JOIN classes c ON c.id=a.class_id JOIN class_members m ON m.class_id=c.id WHERE m.student_id=? ORDER BY a.id DESC',(u['id'],))
     items=[]
     for row in rows:
      obj=dict(row);obj['problems']=[dict(x) for x in c.execute('SELECT p.id,p.title FROM assignment_problems ap JOIN problems p ON p.id=ap.problem_id WHERE ap.assignment_id=?',(row['id'],))];items.append(obj)
     return self.send(200,{'items':items})
    if p=='/api/analytics':
     rows=c.execute('SELECT p.id,p.title,COUNT(s.id) attempts,ROUND(MAX(s.score),2) best FROM problems p LEFT JOIN submissions s ON p.id=s.problem_id AND s.user_id=? GROUP BY p.id ORDER BY p.id DESC',(u['id'],)).fetchall() if u['role']=='student' else []
     if u['role']=='teacher':
      # Teacher sees only scores of classes they own (avoid disclosing unrelated learners).
      rows=c.execute('SELECT p.id,p.title,COUNT(s.id) attempts,ROUND(MAX(s.score),2) best FROM problems p LEFT JOIN submissions s ON p.id=s.problem_id AND s.user_id IN (SELECT student_id FROM class_members m JOIN classes cl ON cl.id=m.class_id WHERE cl.teacher_id=?) WHERE p.created_by=? GROUP BY p.id ORDER BY p.id DESC',(u['id'],u['id'])).fetchall()
     return self.send(200,{'items':[dict(x) for x in rows]})
    if p=='/api/topics':return self.send(200,{'items':[dict(x) for x in c.execute('SELECT * FROM topics ORDER BY id')]})
    if p=='/api/problems':return self.send(200,{'items':[dict(x) for x in c.execute('SELECT p.*,t.title AS topic FROM problems p JOIN topics t ON t.id=p.topic_id ORDER BY p.id DESC')]})
    if p.startswith('/api/problems/'):
     try:pid=int(p.rsplit('/',1)[1]);r=c.execute('SELECT p.*,t.title AS topic FROM problems p JOIN topics t ON t.id=p.topic_id WHERE p.id=?',(pid,)).fetchone()
     except:return self.fail('Mã bài không hợp lệ.')
     if not r:return self.fail('Không tìm thấy bài.',404)
     return self.send(200,{'item':dict(r)})
    if p=='/api/demo/evidence':
     # Preview-only: isolated from real submissions, scores and analytics.
     if not PUBLIC_PREVIEW or u['username'] not in ('giaovien','hocsinh'):return self.fail('Không có dữ liệu minh họa.',404)
     if u['role']=='student':filter_sql='WHERE e.user_id=?';params=(u['id'],)
     else:
      filter_sql='WHERE e.user_id IN (SELECT m.student_id FROM class_members m JOIN classes cl ON m.class_id=cl.id WHERE cl.teacher_id=?)';params=(u['id'],)
     q='''SELECT e.id,e.problem_id,p.title AS problem,e.language,e.verdict,e.score,e.created_at,u.name AS student
          FROM demo_judge_events e JOIN problems p ON e.problem_id=p.id JOIN users u ON e.user_id=u.id '''
     items=[dict(x) for x in c.execute(q+filter_sql+' ORDER BY e.created_at DESC',params)]
     totals={'count':len(items),'ac':sum(x['verdict']=='AC' for x in items),'wa':sum(x['verdict']=='WA' for x in items),'ce':sum(x['verdict']=='CE' for x in items),'tle':sum(x['verdict']=='TLE' for x in items)}
     by_problem={}
     for x in items:
      a=by_problem.setdefault(x['problem_id'],{'id':x['problem_id'],'title':x['problem'],'attempts':0,'best':0})
      a['attempts']+=1;a['best']=max(a['best'],x['score'])
     return self.send(200,{'demo':True,'label':'DỮ LIỆU MINH HỌA – KHÔNG PHẢI KẾT QUẢ CHẤM THẬT','items':items,'totals':totals,'byProblem':list(by_problem.values())})
    if p=='/api/submissions':
     q='''SELECT s.id,s.problem_id,p.title AS problem,s.language,s.verdict,s.score,s.created_at,u.name AS student FROM submissions s JOIN problems p ON p.id=s.problem_id JOIN users u ON u.id=s.user_id'''
     if u['role']=='student':q+=' WHERE s.user_id=?';rows=c.execute(q+' ORDER BY s.id DESC LIMIT 200',(u['id'],))
     else:rows=c.execute(q+' WHERE s.user_id IN (SELECT student_id FROM class_members m JOIN classes cl ON cl.id=m.class_id WHERE cl.teacher_id=?) ORDER BY s.id DESC LIMIT 200',(u['id'],))
     return self.send(200,{'items':[dict(x) for x in rows]})
    if p=='/api/contests':
     items=[]
     for r in c.execute('SELECT * FROM contests ORDER BY id DESC'):
      o=dict(r);o['problems']=[dict(x) for x in c.execute('SELECT p.id,p.title,cp.position FROM contest_problems cp JOIN problems p ON p.id=cp.problem_id WHERE contest_id=? ORDER BY position',(r['id'],))];items.append(o)
     return self.send(200,{'items':items})
    if p=='/api/stats':
     return self.send(200,{'topics':c.execute('SELECT count(*) FROM topics').fetchone()[0],'problems':c.execute('SELECT count(*) FROM problems').fetchone()[0],'students':c.execute("SELECT count(*) FROM users WHERE role='student'").fetchone()[0],'submissions':c.execute('SELECT count(*) FROM submissions'+(' WHERE user_id=?' if u['role']=='student' else ''),(u['id'],) if u['role']=='student' else ()).fetchone()[0]})
   return self.fail('Không tìm thấy API.',404)
  fp=(ROOT/'static'/('index.html' if p=='/' else p.lstrip('/'))).resolve()
  if not fp.is_relative_to((ROOT/'static').resolve()) or not fp.exists() or not fp.is_file():
   fp=ROOT/'static'/'index.html'
  raw=fp.read_bytes();self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(fp.name)[0] or 'text/html');self.send_header('Content-Length',str(len(raw)));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw)
 def do_POST(self):
  if not self.preview_gate():return
  p=urlparse(self.path).path;d=self.read_json()
  if not isinstance(d,dict):return self.fail('Dữ liệu không hợp lệ.')
  if p=='/api/login':
   with db() as c:r=c.execute('SELECT * FROM users WHERE username=?',(str(d.get('username','')).strip(),)).fetchone()
   if not r or not check_pw(str(d.get('password','')),r['password']):return self.fail('Sai tài khoản hoặc mật khẩu.',401)
   return self.send(200,{'ok':True},'session='+token(r)+'; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200'+('; Secure' if PUBLIC_PREVIEW else ''))
  if p=='/api/register' and PUBLIC_PREVIEW:return self.fail('Đăng ký chưa được mở trong bản online xem thử.',403)
  if p=='/api/logout':return self.send(200,{'ok':True},'session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0'+('; Secure' if PUBLIC_PREVIEW else ''))
  u=self.auth()
  if not u:return
  # Restrict writes to local same-origin browser requests.
  origin=self.headers.get('Origin','');
  if origin:
   host=self.headers.get('Host','')
   allowed=('http://127.0.0.1:'+str(PORT),'http://localhost:'+str(PORT))
   if origin not in allowed and not (PUBLIC_PREVIEW and origin=='https://'+host):return self.fail('Nguồn yêu cầu không hợp lệ.',403)

  if p=='/api/classes':
   if u['role']!='teacher':return self.fail('Chỉ giáo viên được tạo lớp.',403)
   name=str(d.get('name','')).strip()
   if not 2<=len(name)<=120:return self.fail('Tên lớp phải có 2–120 ký tự.')
   code=secrets.token_hex(4).upper()
   with db() as c:
    cur=c.execute('INSERT INTO classes(name,join_code,teacher_id) VALUES(?,?,?)',(name,code,u['id']))
    return self.send(201,{'id':cur.lastrowid,'join_code':code})
  if p=='/api/classes/join':
   if u['role']!='student':return self.fail('Chỉ học sinh được tham gia lớp.',403)
   code=str(d.get('join_code','')).strip().upper()
   with db() as c:
    row=c.execute('SELECT id FROM classes WHERE join_code=?',(code,)).fetchone()
    if not row:return self.fail('Không tìm thấy mã lớp.',404)
    c.execute('INSERT OR IGNORE INTO class_members(class_id,student_id) VALUES(?,?)',(row['id'],u['id']))
    return self.send(200,{'ok':True})
  if p=='/api/assignments':
   if u['role']!='teacher':return self.fail('Chỉ giáo viên được giao bài.',403)
   try:cid=int(d.get('class_id'));ids=list(dict.fromkeys(int(x) for x in d.get('problem_ids',[])))
   except:return self.fail('Thông tin bài giao không hợp lệ.')
   if not ids or len(ids)>30:return self.fail('Hãy chọn từ 1 đến 30 bài.')
   title=str(d.get('title','')).strip()
   if not 2<=len(title)<=120:return self.fail('Tiêu đề phải có 2–120 ký tự.')
   due=str(d.get('due_at','')).strip() or None
   with db() as c:
    if not c.execute('SELECT 1 FROM classes WHERE id=? AND teacher_id=?',(cid,u['id'])).fetchone():return self.fail('Bạn không quản lý lớp này.',403)
    if c.execute('SELECT COUNT(*) FROM problems WHERE id IN ('+','.join('?'*len(ids))+')',ids).fetchone()[0]!=len(ids):return self.fail('Bài tập không tồn tại.')
    cur=c.execute('INSERT INTO assignments(class_id,title,due_at) VALUES(?,?,?)',(cid,title,due))
    c.executemany('INSERT INTO assignment_problems(assignment_id,problem_id) VALUES(?,?)',[(cur.lastrowid,x) for x in ids]);return self.send(201,{'id':cur.lastrowid})
  if p=='/api/tests':
   if u['role']!='teacher':return self.fail('Chỉ giáo viên quản lý test.',403)
   try:pid=int(d.get('problem_id'));pts=int(d.get('points',1))
   except:return self.fail('Dữ liệu test không hợp lệ.')
   raw_in=str(d.get('input_text',''));raw_out=str(d.get('output_text',''))
   if not 1<=pts<=100 or len(raw_in)>20000 or len(raw_out)>20000:return self.fail('Giới hạn test không hợp lệ.')
   with db() as c:
    r=c.execute('SELECT created_by FROM problems WHERE id=?',(pid,)).fetchone()
    if not r or r['created_by']!=u['id']:return self.fail('Bạn không có quyền sửa bộ test này.',403)
    cur=c.execute('INSERT INTO test_cases(problem_id,input_text,output_text,points) VALUES(?,?,?,?)',(pid,raw_in,raw_out,pts));return self.send(201,{'id':cur.lastrowid})
  if p=='/api/problems':
   if u['role']!='teacher' :return self.fail('Chỉ giáo viên được tạo bài.',403)
   fields=('title','description','input_spec','output_spec','sample_in','sample_out','difficulty')
   if not all(str(d.get(x,'')).strip() for x in fields):return self.fail('Hãy điền đủ thông tin bài tập.')
   try:topic=int(d.get('topic_id'))
   except:return self.fail('Chuyên đề không hợp lệ.')
   with db() as c:
    try:
     cur=c.execute('INSERT INTO problems(topic_id,title,description,input_spec,output_spec,sample_in,sample_out,difficulty,created_by) VALUES (?,?,?,?,?,?,?,?,?)',(topic,*(str(d[x])[:10000] for x in fields),u['id']))
     return self.send(201,{'id':cur.lastrowid})
    except sqlite3.IntegrityError:return self.fail('Chuyên đề không tồn tại.')
  if p=='/api/contests':
   if u['role']!='teacher':return self.fail('Chỉ giáo viên được tạo đề.',403)
   ids=d.get('problem_ids',[])
   if not isinstance(ids,list) or not 1<=len(ids)<=4 or len(set(map(str,ids)))!=len(ids):return self.fail('Chọn 1 đến 4 bài không trùng nhau.')
   if not str(d.get('title','')).strip():return self.fail('Thiếu tên đề.')
   with db() as c:
    try:
     cur=c.execute('INSERT INTO contests(title,description,created_by) VALUES(?,?,?)',(str(d['title'])[:120],str(d.get('description',''))[:1000],u['id']))
     for i,pid in enumerate(ids,1):c.execute('INSERT INTO contest_problems VALUES(?,?,?)',(cur.lastrowid,int(pid),i))
     return self.send(201,{'id':cur.lastrowid})
    except (ValueError,sqlite3.IntegrityError):return self.fail('Mã bài không hợp lệ.')
  if p in ('/api/run','/api/submit'):
   source=str(d.get('source',''));lang=d.get('language');pid=d.get('problem_id')
   if lang not in ('cpp','python','pascal') or not source.strip() or len(source)>30000:return self.fail('Mã nguồn hoặc ngôn ngữ không hợp lệ.')
   if not JUDGE_URL:return self.fail('Chưa cấu hình Judge0. Bạn vẫn có thể lưu mã nguồn bằng cách sao chép; không có điểm chấm giả.',503)
   if p=='/api/run':
    if len(str(d.get('stdin','')))>10000:return self.fail('Input quá dài.')
    try:
     r=judge(source,lang,str(d.get('stdin','')))
     return self.send(200,{'verdict':outcome(r),'stdout':r.get('stdout'),'stderr':r.get('stderr'),'compile_output':r.get('compile_output'),'time':r.get('time'),'memory':r.get('memory')})
    except Exception as e:return self.fail(str(e),502)
   try:pid=int(pid)
   except:return self.fail('Bài không hợp lệ.')
   with db() as c:
    if not c.execute('SELECT 1 FROM problems WHERE id=?',(pid,)).fetchone():return self.fail('Không tìm thấy bài.')
    tests=c.execute('SELECT * FROM test_cases WHERE problem_id=? ORDER BY id',(pid,)).fetchall()
   if not tests:return self.fail('Bài chưa có bộ test.',422)
   score=0;total=sum(t['points'] for t in tests);statuses=[]
   try:
    langid=judge_language_id(lang,judge_languages())
    for t in tests:
     r=judge(source,lang,t['input_text'],langid);v=outcome(r)
     passed=(r.get('status',{}).get('id')==3 and normalize_output(r.get('stdout'))==normalize_output(t['output_text']))
     if passed:score+=t['points']
     statuses.append('AC' if passed else ('WA' if r.get('status',{}).get('id')==3 else v))
    pct=round(score/total*5,2);verdict='AC' if score==total else ('WA' if 'WA' in statuses else statuses[0])
    with db() as c:
     cur=c.execute('INSERT INTO submissions(user_id,problem_id,language,source,verdict,score) VALUES (?,?,?,?,?,?)',(u['id'],pid,lang,source,verdict,pct))
     return self.send(200,{'id':cur.lastrowid,'verdict':verdict,'score':pct,'total':5,'passed':sum(x=='AC' for x in statuses),'testCount':len(statuses)})
   except Exception as e:return self.fail('Không thể hoàn thành chấm bài: '+str(e),502)
  return self.fail('Không tìm thấy chức năng.',404)

if __name__=='__main__':
 if PUBLIC_PREVIEW and (len(PREVIEW_PASSWORD)<16 or not os.environ.get('HSG_SECRET') or HOST=='127.0.0.1'):
  raise SystemExit('PUBLIC PREVIEW: can HSG_PREVIEW_PASSWORD >= 16 ky tu, HSG_SECRET va HOST=0.0.0.0')
 if HOST!='127.0.0.1' and not PUBLIC_PREVIEW:
  raise SystemExit('Tu choi mo cong khai khi chua bat HSG_PUBLIC_PREVIEW=1 va cai mat khau.')
 init()
 try:
  with ThreadingHTTPServer((HOST,PORT),Handler) as server:
   print(f'\nHSG Tin hoc AI da san sang: http://{HOST}:{PORT}\nGiao vien: giaovien / Demo@12345\nHoc sinh: hocsinh / Demo@12345\nGIU NGUYEN cua so nay khi dung Web App. Nhan Ctrl+C de dung.\n', flush=True)
   if os.name=='nt':
    timer=threading.Timer(1.2,lambda: webbrowser.open(f'http://{HOST}:{PORT}'))
    timer.daemon=True
    timer.start()
   try:server.serve_forever()
   except KeyboardInterrupt:print('\nDa dung Web App binh thuong. Cam on ban!')
 except OSError as e:
  print(f'\nKHONG THE KHOI DONG: {e}')
  print(f'Neu cong {PORT} dang ban, hay dong cua so Web App cu va mo lai.')
  raise SystemExit(1)
