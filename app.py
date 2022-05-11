from flask import Flask, render_template, request, jsonify, request, redirect, url_for
app = Flask(__name__)
from pymongo import MongoClient
import jwt
from bs4 import BeautifulSoup
import datetime
import hashlib
from datetime import datetime, timedelta


app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

client = MongoClient('mongodb+srv://test:starta@cluster0.zpbc3.mongodb.net/cluster0?retryWrites=true&w=majority')
db = client.dbsparta_plus_miniproject_real

SECRET_KEY = 'HANGHAE'

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": ""                                          # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/main')
def main():
    return render_template('main.html')

#블로그 저장
@app.route('/blog/saveBlog', methods=['POST'])
def save_blog():
    token_receive = request.cookies.get('mytoken')
    
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithm=['HS256'])
        user_info = db.userdb.find_one({'id': payload['id']})
        writer_name = user_info['id']  # 토큰에서 ID 정보 가져오기
        
        url_receive =  request.form['url_give']
        desc_receive = request.form['desc_give']
       
        
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(url_receive, headers=headers)
        
        soup = BeautifulSoup(data.text, 'html.parser')
        
        og_image = soup.select_one('meta[property="og:image"]')  
        og_title = soup.select_one('meta[property="og:title"]')
        
        
        image = og_image['content']
        title = og_title['content']
        
        
        doc ={
            'blog_desc': desc_receive,
            'url':url_receive,
            'image': image,
            'title': title,
        }
        
        client.blogs.bloglist.insert_one(doc)
        return jsonify({'msg' : '저장 완료 !!'}) 
    
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))

    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 올바르지 않습니다."))

#저장된 블로그 불러오기 
@app.route('/<url>')
def show_clicked_post(url):
    token_receive = request.cookies.get('mytoken')
    print(token_receive)
    
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.userdb.find_one({'id': payload['id']})
        user_id = user_info['id']
        
        data = db.bloglist.find_one({'id':id, })
        user_id = data['user_id']
        url = data['url']
        blog_desc = data['blog_desc']
        image = data['image']
        title = data['title']  
        
        return render_template("main.html",
                               user_id=user_id,
                               url=url,
                               blog_desc=blog_desc,
                               image=image,
                               title=title) 

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))

    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 올바르지 않습니다."))

    
    # bloglist = list(client.blogs.bloglist.find({},{'_id':False}))
    
    # return jsonify({'blogs':bloglist})
    
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
