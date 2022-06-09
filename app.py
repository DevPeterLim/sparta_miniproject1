from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)
from pymongo import MongoClient
import jwt
from bs4 import BeautifulSoup
import requests
import datetime
import hashlib
from datetime import datetime, timedelta
from bson.objectid import ObjectId


app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"
# 아래 URL을 본인의 몽고DBURL로 변경후 test 해주세요
mongodburl = '몽고 DB'
client = MongoClient(mongodburl)
db = client.dbsparta_plus_miniproject_real

SECRET_KEY = 'HANGHAE'


@app.route('/')
def main():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'username': payload['id']})
        blog_infos = list(db.blogs.find())
        count_list = []
        for blog_info in blog_infos:
            comment_list = blog_info['comments']
            count_list.append(len(comment_list))
        return render_template('mainpage.html', id=user_info['username'], count_list=count_list, blog_infos=blog_infos)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

# 댓글 수정
@app.route('/edit_comment', methods=['POST'])
def edit_comment():
    listNum_receive = request.form['listNum_give']  # 댓글 리스트 번호
    id_receive = request.form['_id_give']  # 해당 블로그 '_id'
    blog_info = db.blogs.find_one({"_id": ObjectId(id_receive)})
    comment_list = blog_info['comments']  # 블로그 찾고 해당 comment 리스트 가져오기
    bf_comments = comment_list[int(listNum_receive)]
    edit_receive = request.form['edit_comment_give']

    bf_comments.update({'comment': edit_receive})

    db.blogs.update_one({'_id': ObjectId(id_receive)}, {'$set': {'comments': comment_list}})

    return jsonify({'msg': '수정완료!'})

@app.route('/edit_blog', methods=['POST'])
def edit_blog():
    id_receive = request.form['id_give']  # 해당 블로그 '_id'
    summary_receive = request.form['summary_give']
    text_receive = request.form['text_give']

    db.blogs.update_one({'_id': ObjectId(id_receive)}, {'$set': {'summary': summary_receive}})
    db.blogs.update_one({'_id': ObjectId(id_receive)}, {'$set': {'text': text_receive}})

    return jsonify({'msg': '수정완료!'})

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
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

##임시
@app.route('/searchblog/<keyword>')
def blogsearch(keyword):
    token_receive = request.cookies.get('mytoken')
    id = keyword
    try:
        a = bool(db.blogs.find_one({'_id': ObjectId(id)}))
        if a:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({'username': payload['id']})  # 토큰을 통해 유저 정보 확인
            blog_list = db.blogs.find_one({'_id': ObjectId(id)})
            comment_list = blog_list['comments']
            comment_count = len(comment_list)
            return render_template('detail_blog.html', blog=blog_list, comments=comment_list, id=user_info['username'], comment_count=comment_count)
        else:
            return redirect(url_for("main", msg="해당 블로그를 불러올 수 없습니다."))
    except:
        return redirect(url_for("blogg", msg="해당 블로그를 불러올 수 없습니다."))


# 블로그 추가 저장

@app.route('/blogg')
def blogg():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'id': payload['id']})  # 토큰을 통해 유저 정보 확인
        blog_info = list(db.blogs.find())
        return render_template('index1.html' , blog = blog_info[1])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))



    ##### 임시
@app.route('/bloggcomment')
def blogg_comment():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'username': payload['id']})  # 토큰을 통해 유저 정보 확인
        user_id = user_info['username'] # 유저 id

        blog_info = list(db.blogs.find())
        return render_template('index2.html' , id=blog_info[0] )
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

    ### 임시


@app.route('/blogg/saveBlog', methods=['POST'])
def save_blogg():
    token_receive = request.cookies.get('mytoken') #토큰 받기

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'username': payload['id']}) # 토큰을 통해 유저 정보 확인
        user_id = user_info['username'] # 유저 id
        date_receive = request.form['date_give']
        url_receive = request.form['url_give']
        text_receive = request.form['text_give']
        summary_receive = request.form['summary_give'] # ajax로 받은 데이터, 블로그 url, 요약, 추가 날짜
        comment_receive = [] # 댓글 추가 할 빈 리스트
        like_receive = []
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(url_receive, headers=headers)

        soup = BeautifulSoup(data.text, 'html.parser')
        try:
            img = (soup.select_one('meta[property= "og:image"]')['content'])
            doc = {
                'date': date_receive,
                'img': img,
                'username': user_id,
                'url': url_receive,
                'summary': summary_receive,
                'text': text_receive,
                'comments': comment_receive,
                'like': like_receive
            }
            db.blogs.insert_one(doc)
            return jsonify({'msg': '저장 완료 !!'})
        except:
            doc = {
                'date': date_receive,
                'img': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1024px-No_image_available.svg.png',
                'username': user_id,
                'url': url_receive,
                'summary': summary_receive,
                'text': text_receive,
                'comments': comment_receive,
                'like': like_receive
            }
            db.blogs.insert_one(doc)
            return jsonify({'msg': '저장 완료 !!'})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 해당 블로그 삭제 '_id'값으로 비교
@app.route('/delBlog', methods=['POST'])
def del_blog():
    id_receive = request.form['id_give'] # 해당 블로그 '_id' 값
    db.blogs.delete_one({'_id': ObjectId(id_receive)}) # 블로그 db에서 삭제

    return jsonify({'msg' : '삭제되었습니다!'})

# 댓글 작성
@app.route('/savecomment', methods=['POST'])
def save_comment():
    token_receive = request.cookies.get('mytoken')  # 토큰 받기
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'username': payload['id']})  # 토큰을 통해 유저 정보 확인
        user_id = user_info['username']  # 유저 id
        id_receive = request.form['id_give']  # 댓글 달 블로그 '_id'
        date_receive = request.form['date_give'] # 작성 날짜
        comment_receive = request.form['comment_give'] # 작성 글
        #
        docs = {
            'user': user_id,
            'date': date_receive,
            'comment': comment_receive
        }  # comment에 저장될 딕셔너리
        blog = db.blogs.find_one({'_id': ObjectId(id_receive)})  # 등록할 블로그 찾기
        comment_dict = blog['comments']
        comment_dict.append(docs)
        db.blogs.update_one({'_id': ObjectId(id_receive)}, {'$set': {'comments': comment_dict}})  #블로그 comment에 추가 된 딕셔너리 추가 및 db 수정
        return jsonify({'msg': '댓글 달기 성공 !!'})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/delcomment', methods=['POST'])
def del_comment():
    listNum_receive = request.form['listNum_give']  # 댓글 리스트 번호
    id_receive = request.form['_id_give']  # 해당 블로그 '_id'
    blog_info = db.blogs.find_one({"_id": ObjectId(id_receive)})
    comment_list = blog_info['comments'] #  블로그 찾고 해당 comment 리스트 가져오기
    comment_list.remove(comment_list[int(listNum_receive)])
    db.blogs.update_one({'_id': ObjectId(id_receive)}, {'$set': {'comments': comment_list}})  # 댓글 삭제 및 변경된 값 수정

    return jsonify({'msg' : '삭제되었습니다!'})

@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요 수 변경
        user_info = db.users.find_one({"username": payload["id"]})
        id_receive = request.form["_id_give"]
        action_receive = request.form["action_give"]

        blog_info = db.blogs.find_one({"_id": ObjectId(id_receive)})
        like_list = blog_info['like']

        if action_receive == "like":
            like_list.append(user_info['username'])
            db.blogs.update_one({'_id': ObjectId(id_receive)}, {'$set': {'like': like_list}})
        else:
            like_list.remove(user_info['username'])
            db.blogs.update_one({'_id': ObjectId(id_receive)}, {'$set': {'like': like_list}})
        count = len(like_list)
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
