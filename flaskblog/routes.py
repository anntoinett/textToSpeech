import multiprocessing
import os
import secrets

import nltk
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from gtts import gTTS

from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm  # forms created by us
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required, AnonymousUserMixin

from flaskblog.textProcessing import TextProcessing
from flaskblog.textReading import TextReading

reading_threads = []
lastFragmentVar = multiprocessing.Value('i', 0) #shared value to update database's post's last_part once after processes stop working
last_post_id = None
parent_dir = "flaskblog/mp3_user_fragments/" #ręcznie stworzony na pliczki

@app.after_request
def after_request(response):
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return response


# route decorator- what we type into our browser
# here home/root page
@app.route("/")
@app.route("/home")
# passing argument to html
def home():
    if len(reading_threads) > 0:
        for t in reading_threads:
            if isinstance(t, multiprocessing.Process):
                if t.is_alive():
                    t.terminate()
                    global last_post_id
                    if last_post_id is not None:
                        #print("update bazy z home")
                        post = Post.query.get_or_404(last_post_id)
                        post.last_part = lastFragmentVar.value
                        db.session.commit()
    page = request.args.get('page', default=1, type=int)
    # user = User.query.filter_by(id=current_user.id).first()
    # has_posts = user.posts
    # print("****************" + has_posts)
    num_of_posts = 0
    if current_user.is_authenticated:  # and has_posts != []:
        posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).paginate(page=page,
                                                                                                         per_page=5)
        num_of_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).count()
    else:
        posts = []

    return render_template('home.html', posts=posts, num_of_posts=num_of_posts)


@app.route("/about")
def about():
    if len(reading_threads) > 0:
        for t in reading_threads:
            if isinstance(t, multiprocessing.Process):
                if t.is_alive():
                    t.terminate()
                    global last_post_id
                    if last_post_id is not None:
                        post = Post.query.get_or_404(last_post_id)
                        post.last_part = lastFragmentVar.value
                        db.session.commit()
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])  # allowed methods of passing arguments
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! Now you can log in!', 'success')  # second argument -category
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    userD = "Tosia"
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)  # true if checked
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Log in unsuccessful. Please check email and password!", 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    if len(reading_threads) > 0:
        for t in reading_threads:
            if isinstance(t, multiprocessing.Process):
                if t.is_alive():
                    t.terminate()
                    global last_post_id
                    if last_post_id is not None:
                        post = Post.query.get_or_404(last_post_id)
                        post.last_part = lastFragmentVar.value
                        db.session.commit()
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    if len(reading_threads) > 0:
        for t in reading_threads:
            if isinstance(t, multiprocessing.Process):
                if t.is_alive():
                    t.terminate()
                    global last_post_id
                    if last_post_id is not None:
                        post = Post.query.get_or_404(last_post_id)
                        post.last_part = lastFragmentVar.value
                        db.session.commit()
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))  # get request
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)  # post request

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    if len(reading_threads) > 0:
        for t in reading_threads:
            if isinstance(t, multiprocessing.Process):
                if t.is_alive():
                    t.terminate()
                    global last_post_id
                    if last_post_id is not None:
                        post = Post.query.get_or_404(last_post_id)
                        post.last_part = lastFragmentVar.value
                        db.session.commit()
    form = PostForm()
    if form.validate_on_submit():
        uploaded_file = form.file.data
        if uploaded_file.filename != '':
            # print(uploaded_file.read())
            extension = os.path.splitext(uploaded_file.filename)[1]
            new_filename = current_user.username + extension
            uploaded_file.save(os.path.join("flaskblog/texts/", new_filename))
            # uploaded_file.save(os.path.join(uploaded_file.filename))
            # content = read_text(uploaded_file)
            content, num_of_parts = TextProcessing.convert_to_txt(new_filename)

            detector = nltk.data.load('tokenizers/punkt/english.pickle')
            detector._params.abbrev_types.add('e.g')
            sentences = detector.tokenize(content)
            fragments = []

            # dividing text for smaller fragments
            while (len(sentences) > 0):
                if (len(sentences) > 4):
                    fragments.append(sentences[0] + sentences[1] + sentences[2] + sentences[3] + sentences[4])
                    for i in range(5):
                        sentences.pop(0)
                else:
                    fragments.append(" ".join(sentences))
                    for i in range(len(sentences)):
                        sentences.pop(0)
            if not os.path.exists(f"{parent_dir}{current_user.username}"):
                os.makedirs(f"{parent_dir}{current_user.username}")
            post_path = os.path.join(parent_dir, f"{current_user.username}/{form.title.data}")
            os.mkdir(post_path)
            for i in range(len(fragments)):
                tts = gTTS(fragments.pop(0), lang='en', tld="com")
                tts.save(f'{post_path}/{i+1}.mp3')

            post = Post(title=form.title.data, content=content, author=current_user,
                        number_of_parts=num_of_parts)  # author works because of relationship in user model?
            db.session.add(post)
            db.session.commit()
            flash('Text added succesfully!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New text',
                           form=form, legend='New Text')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    global last_post_id
    last_post_id = post_id
    if len(reading_threads) > 0:
        for t in reading_threads:
            if isinstance(t, multiprocessing.Process):
                if t.is_alive():
                    t.terminate()
                    post.last_part = lastFragmentVar.value
                    db.session.commit()
    detector = nltk.data.load('tokenizers/punkt/english.pickle')
    detector._params.abbrev_types.add('e.g')
    tokens = detector.tokenize(post.content)
    last_sentence = tokens[post.last_part * 5] + ".."
    return render_template('post.html', title=post.title, post=post, last_sentence=last_sentence)


@app.route("/post/<int:post_id>reading")
@login_required
def start_reading(post_id):
    sound_path = os.path.join(parent_dir, f"{current_user.username}")
    thr = multiprocessing.Process(target=TextReading.read, args=(post_id, lastFragmentVar, sound_path), kwargs={})
    reading_threads.append(thr)
    if not any(t.is_alive() for t in reading_threads):
        thr.start()
    return '', 204


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if len(reading_threads) > 0:
        for t in reading_threads:
            if isinstance(t, multiprocessing.Process):
                if t.is_alive():
                    t.terminate()
                    post.last_part = lastFragmentVar.value
                    db.session.commit()

    if post.author != current_user:
        abort(403)  # http forbidden route
    form = PostForm()
    if form.validate_on_submit():
        uploaded_file = form.file.data
        if uploaded_file.filename != '':
            extension = os.path.splitext(uploaded_file.filename)[1]
            new_filename = current_user.username + extension
            uploaded_file.save(os.path.join("flaskblog/texts/", new_filename))
            # post.file = form.file.data
            post.title = form.title.data
            content, num_of_parts = TextProcessing.convert_to_txt(new_filename)
            post.content = content
            post.number_of_parts = num_of_parts
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if len(reading_threads) > 0:
        for t in reading_threads:
            if isinstance(t, multiprocessing.Process):
                if t.is_alive():
                    t.terminate()
                    post.last_part = lastFragmentVar.value
                    db.session.commit()
    if post.author != current_user:
        abort(403)  # http forbidden route
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/post/<int:post_id>stopped")
@login_required
def stop_reading(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # http forbidden route
    if len(reading_threads) > 0:
        for t in reading_threads:
            if isinstance(t, multiprocessing.Process):
                if t.is_alive():
                    t.terminate()
                    #print("uaktualniam baze:" + str(str(lastFragmentVar.value)))
                    post.last_part = lastFragmentVar.value
                    db.session.commit()
    return '', 204


@app.route("/post/<int:post_id>")
@login_required
def read_next(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # http forbidden route


@app.route("/post/<int:post_id>")
@login_required
def read_previous(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # http forbidden route


@app.route("/post/<int:post_id>reset")
@login_required
def reset_reading(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # http forbidden route
    if len(reading_threads) > 0:
        for t in reading_threads:
            if isinstance(t, multiprocessing.Process):
                if t.is_alive():
                    t.terminate()
                    # print("uaktualniam baze:" + str(str(lastFragmentVar.value)))
                    if post.last_part != 0:
                        lastFragmentVar.value = 0
                        post.last_part = 0
                        db.session.commit()
                else:
                    if post.last_part != 0:
                        lastFragmentVar.value = 0
                        post.last_part = 0
                        db.session.commit()
    else:
        if post.last_part != 0:
            lastFragmentVar.value = 0
            post.last_part = 0
            db.session.commit()
    return '', 204


@app.route("/user/<string:username>")
# passing argument to html
def user_posts(username):
    if len(reading_threads) > 0:
        for t in reading_threads:
            if isinstance(t, multiprocessing.Process):
                if t.is_alive():
                    t.terminate()
                    global last_post_id
                    if last_post_id is not None:
                        post = Post.query.get_or_404(last_post_id)
                        post.last_part = lastFragmentVar.value
                        db.session.commit()
    page = request.args.get('page', default=1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    # means without break
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

@app.route('/getReadingData', methods=['POST'])
#tu na podstawie tytulu i usera wyciagac z bazy aktualny fragment i tekst,
# odeslac do javascripta i zaktualizowac last_partna bazie - pomyslec jak z zakonczeniem odczytu razem z js
def send_data():
    if not request.json:
        abort(400)
    response = {
        'id': "hejka",
        'title': request.json
    }
    print(request.json)
    return jsonify({'message': 'jest dobrze'}), 201