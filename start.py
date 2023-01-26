from flask import Flask, render_template, url_for, redirect, request, session
import json
import os


app= Flask(__name__) # создаем приложение как экземпляр класса Flask
app.config['SECRET_KEY'] = 'sdofijsifjisjbvhs'
UPLOAD_FOLDER = './static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    if 'user_in_system' in session:
        return redirect(url_for('start_page')) # переадресоваться на функцию start_page
    else:
        return render_template('login.html')

@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        country = request.form.get('country')
        city = request.form.get('city')
        age = request.form.get('age')
        with open('data/users.json', encoding='utf-8') as f:
            users = json.load(f)
            id = users[-1]['user_id'] + 1
            users.append({'user_id': id,
                          'user_name': user_name,
                          'password': password,
                          'last_name': last_name,
                          'first_name': first_name,
                          'country': country,
                          'city': city,
                          'age': int(age),
                          'user_avatar': 'https://kartinkin.net/uploads/posts/2022-02/1645097167_34-kartinkin-net-p-kartinki-chelovek-55.png',
                          'about': ' '})
            with open('data/users.json', 'w', encoding='utf-8') as save_file: # открываем файл на запись
                json.dump(users, save_file, ensure_ascii=False, indent=2)
            session['user_in_system'] = user_name
        return redirect(url_for('start_page'))
    else:
        return render_template('registration.html')

@app.route('/login', methods=['post', 'get'])
def login():
    with open('data/users.json', encoding='utf-8') as f: # читаем файл и записываем в переменную
        users = json.load(f)
    if request.method == 'POST': # если была нажата кнопка
        username = request.form.get('username')
        password = request.form.get('password')
        for user in users:
            if user['user_name'] == username and user['password'] == password:
                session['user_in_system'] = username # запоминаем пользователя
                return redirect(url_for('start_page'))
        else: # если пользователь с username и password не найден
            return render_template('login.html', error_text='Пользователь с таким паролем не найден')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')

@app.route('/start_page')
def start_page():
    with open('data/posts.json', encoding='utf-8') as f: # читаем файл и записываем в переменную
        posts = json.load(f)
    with open('data/users.json', encoding='utf-8') as f: # читаем файл и записываем в переменную
        users = json.load(f)
    for post in posts:
        for user in users:
            if post['user_name'] == user['user_name']:
                post['user_avatar'] = user['user_avatar']
                break
    return render_template('start_page.html', posts=posts, user_name=session['user_in_system']) # отображаем html шаблон стартовой страницы


@app.route('/posts/<int:post_id>', methods=['POST', 'GET'])
def one_post(post_id):
    with open('data/posts.json', encoding='utf-8') as f:
        posts = json.load(f)
    with open('data/comments.json', encoding='utf-8') as f:
        comments = json.load(f)
    with open('data/users.json', encoding='utf-8') as f:  # читаем файл и записываем в переменную
        users = json.load(f)

    if request.method == 'POST': # если была нажата кнопка отправки комментария
        comment_text = request.form.get('comment_text')
        comment_id = comments[-1]['comment_id'] + 1
        comments.append({'comment_id': comment_id,
                         'post_id': post_id,
                        'commenter_name': session['user_in_system'],
                        'comment': comment_text})
        with open('data/comments.json', 'w', encoding='utf-8') as save_file:
            json.dump(comments, save_file, ensure_ascii=False, indent=2)
        return redirect(url_for(f"one_post",post_id=post_id))
    else:
        for post in posts:
            for user in users:
                if post['user_name'] == user['user_name']:
                    post['user_avatar'] = user['user_avatar']
                    break
        comments_by_id = []
        for comment in comments:
            if comment['post_id'] == post_id:
                comments_by_id.append(comment)
        for post in posts: # post - словарь, posts - список словарей
            if post['post_id'] == post_id:
                if session['user_in_system']:
                    is_login = True  # вошел ли пользователь, чью страницу мы открыли
                else:
                    is_login = False
                # увеличение количества просмотров
                post['views_count'] += 1
                with open('data/posts.json', 'w', encoding='utf-8') as save_file:
                    json.dump(posts, save_file, ensure_ascii=False, indent=2)
                return render_template('one_post.html', is_login=is_login, post=post, comments=comments_by_id, comments_len=len(comments_by_id))
        else:
            return str("Такого поста еще нет")

@app.route('/users/<user_name>', methods=['POST', 'GET'])
def posts_by_user(user_name):
    if request.method == 'POST':
        with open('data/posts.json', encoding='utf-8') as f:
            posts = json.load(f)
            post_id = posts[-1]['post_id'] + 1
            post_picture = request.files['post_pic'].filename
            request.files['post_pic'].save(os.path.join(app.config['UPLOAD_FOLDER'], post_picture))
            post_text = request.form.get('post_text')
            likes_count = 0
            views_count = 0
            posts.append({'post_id': post_id,
                          'post_picture': os.path.join(app.config['UPLOAD_FOLDER'], post_picture)[1:],
                          'user_name': user_name,
                          'post_text': post_text,
                          'likes_count': likes_count,
                          'views_count': views_count})
            with open('data/posts.json', 'w', encoding='utf-8') as save_f:
                json.dump(posts, save_f, ensure_ascii=False,indent=2)
        return redirect(url_for('start_page'))
    else:
        with open('data/posts.json', encoding='utf-8') as f:
            posts = json.load(f)
        with open('data/users.json', encoding='utf-8') as f: # читаем файл и записываем в переменную
            users = json.load(f)
        for post in posts:
            for user in users:
                if post['user_name'] == user['user_name']:
                    post['user_avatar'] = user['user_avatar']
                    break
        posts_by_user_list = []
        for post in posts:
            if user_name == post['user_name']:
                posts_by_user_list.append(post)
        for user in users:
            if user['user_name'] == user_name:
                found_user = user
                break
        if session['user_in_system'] == user_name:
            is_login = True # вошел ли пользователь, чью страницу мы открыли
        else:
            is_login = False
        return render_template('one_user.html', posts=posts_by_user_list, user_info = found_user, user_in_system=session['user_in_system'], is_login=is_login)


app.run() # запускаем сервер