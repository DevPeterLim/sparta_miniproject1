from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.ov5wg.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.blogs

# SECRET_KEY = 'HANGHAE'

import requests
from bs4 import BeautifulSoup



@app.route('/main')
def main():
    return render_template('main.html')

#블로그 저장
@app.route('/blog/saveBlog', methods=['POST'])
def save_blog():
    # token_receive = request.cookies.get('mytoken')
    
    # try:
        # payload = jwt.decode(token_receive, SECRET_KEY, algorithm=['HS256'])
        # user_info = db.userdb.find_one({'id': payload['id']})
        # writer_name = user_info['id']  # 토큰에서 ID 정보 가져오기
        
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
    
    # except jwt.ExpiredSignatureError:
    #     return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))

    # except jwt.exceptions.DecodeError:
    #     return redirect(url_for("login", msg="로그인 정보가 올바르지 않습니다."))

#저장된 블로그 불러오기 
@app.route('/blog/bloglist', methods=['GET'])
def get_bloglist():
    bloglist = list(client.blogs.bloglist.find({},{'_id':False}))
    
    return jsonify({'blogs':bloglist})
    
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)