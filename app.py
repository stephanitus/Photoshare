import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
from collections import Counter
import flask_login
import os, base64

# Init DB
mysql = MySQL()
app = Flask(__name__)
app.secret_key = '6AC6663F6BCFEB4191481AC41972DBEE4BDF6E7AA43E74F7E64C5F07DE69CE02'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'OMITTED:)'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# Login manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

def get_users_photos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT firstname, lastname, imgdata, caption, name, picture_id, Pictures.album_id FROM (Pictures JOIN Users ON Pictures.user_email = Users.email) JOIN Album ON Pictures.album_id = Album.album_id WHERE email = '{0}'".format(uid))
	return cursor.fetchall()

def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT name FROM Album WHERE user_email = '{0}'".format(uid))
	return cursor.fetchall()

def get_user_friends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT user2_email FROM Friends f WHERE f.user1_email = '{0}'".format(uid))
	return cursor.fetchall()

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

def isAlbumNameUnique(name):
	# use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT * FROM Album A WHERE A.name = '{0}' and A.user_email = '{1}'".format(name,flask_login.current_user.id)):
		# this means there are greater than zero entries with that email
		return False
	else:
		return True

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_all_pictures():
	cursor = conn.cursor()
	cursor.execute("SELECT U.firstname, U.lastname, P.imgdata, P.caption, A.name, P.picture_id, A.album_id FROM Album AS A, Pictures AS P, Users AS U WHERE P.user_email = U.email and A.album_id = P.album_id")
	return cursor.fetchall()

def render_string_query(tuples):
	output = []
	for tuple in tuples:
		output.append(tuple[0])
	return output

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
				<a href='/' style="text-align:center;">Home</a>
			   <form action='login' method='POST' style="text-align:center; margin: 30vh;">
				<input type='text' name='email' id='email' placeholder='email' style="padding: 10px; margin: 5px;"></input> <br/>
				<input type='password' name='password' id='password' placeholder='password' style="padding: 10px; margin: 5px;"></input> <br/>
				<input type='submit' name='submit' style="padding: 5px; margin: 5px; width: 48%;"></input>
			   </form></br>
		   
			   '''
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return redirect('/')

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return redirect('/')

@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		firstname=request.form.get('firstname')
		lastname=request.form.get('lastname')
		dob=request.form.get('dob')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
		email=request.form.get('email')
		password=request.form.get('password')
	except:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password, firstname, lastname, dob, hometown, gender) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password, firstname, lastname, dob, hometown, gender)))
		conn.commit()
		user = User()
		user.id = email
		flask_login.login_user(user)
		conn.commit()
		return redirect('/')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

@app.route('/profile')
@flask_login.login_required
def protected():
	cursor = conn.cursor()
	cursor.execute("SELECT firstname, lastname, contribution FROM Users WHERE email = '{0}'".format(flask_login.current_user.id))
	user = cursor.fetchone()
	cursor.execute("SELECT name, album_id FROM Album WHERE user_email = '{0}'".format(flask_login.current_user.id))
	albums = cursor.fetchall()
	cursor.execute("SELECT DISTINCT tag_data FROM Tags T, Pictures P, Users U WHERE T.picture_id = P.picture_id AND P.user_email = U.email AND U.email = '{0}'".format(flask_login.current_user.id))
	tags = cursor.fetchall()
	return render_template('profile.html', firstname=user[0], lastname=user[1], photos=get_users_photos(flask_login.current_user.id), contribution=user[2], albums=albums, tags=tags, base64=base64)

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = flask_login.current_user.id
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		album_name = request.form.get('album')
		tags = request.form.get('tags').split()
		photo_data = imgfile.read()
		cursor = conn.cursor()
		# Create album if new
		if isAlbumNameUnique(album_name):
			cursor.execute('''INSERT INTO Album (user_email, name) VALUES (%s, %s)''', (flask_login.current_user.id, album_name))
			conn.commit()
		# Get album ID 
		cursor.execute("SELECT A.album_id FROM Album AS A WHERE A.name = '{0}' and A.user_email = '{1}'".format(album_name, flask_login.current_user.id))
		album_id = cursor.fetchone()
		cursor.execute('''INSERT INTO Pictures (imgdata, user_email, caption, album_id) VALUES (%s, %s, %s, %s )''', (photo_data, uid, caption, album_id))
		# Get picture ID
		cursor.execute('''SELECT picture_id FROM Pictures P WHERE P.imgdata = %s AND P.caption = %s AND P.user_email = %s AND P.album_id = %s''', (photo_data, caption, uid, album_id))
		picture_id = cursor.fetchone()
		# Create tags
		for tag in tags:
			cursor.execute("INSERT INTO Tags (picture_id, tag_data) VALUES ('{0}', '{1}')".format(picture_id[0], tag))
			conn.commit()
		# Update contribution
		cursor.execute("UPDATE Users SET contribution=contribution+1 WHERE email='{0}'".format(uid))
		conn.commit()
		return redirect('/')
	else:
		uid = flask_login.current_user.id
		albumlist = getUsersAlbums(uid)
		return render_template('upload.html', albums=albumlist)

@app.route("/friends", methods=['GET'])
@flask_login.login_required
def friends():
	# Generate recommendations
	current_friends = render_string_query(get_user_friends(flask_login.current_user.id))
	candidate_friends = []
	if len(current_friends) > 0:
		for friend in current_friends:
			candidate_friends.extend(render_string_query(get_user_friends(friend)))
	candidate_friends = [f for f in candidate_friends if f != flask_login.current_user.id and (f not in current_friends)]
	frequency = Counter(candidate_friends)
	recommendations = render_string_query(frequency.most_common(3))
	return render_template('friends.html', user_friends=current_friends, recommendations=recommendations)

@app.route("/like/<int:picture_id>")
@flask_login.login_required
def like_photo(picture_id):
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Likes (user_email, picture_id) SELECT '{0}', '{1}' WHERE NOT EXISTS (SELECT * FROM Likes l WHERE l.user_email = '{0}' AND l.picture_id = '{1}')".format(flask_login.current_user.id, picture_id))
	conn.commit()
	return redirect('/')

@app.route("/viewlikes/<int:picture_id>")
def view_likes(picture_id):
	cursor = conn.cursor()
	cursor.execute("SELECT firstname, lastname FROM Users JOIN Likes ON Users.email = Likes.user_email WHERE picture_id = {0}".format(picture_id))
	likes = cursor.fetchall()
	return render_template('viewlikes.html', likes=likes)

@app.route("/viewcomments/<int:picture_id>")
def view_comments(picture_id):
	cursor = conn.cursor()
	cursor.execute("SELECT firstname, lastname, comment_data FROM Users JOIN Comments ON Users.email = Comments.user_email WHERE picture_id = {0}".format(picture_id))
	comments = cursor.fetchall()
	return render_template('viewcomments.html', comments=comments, picture_id=picture_id)

@app.route("/postcomment/<int:picture_id>", methods=["POST"])
def postcomment(picture_id):
	cursor = conn.cursor()
	if flask_login.current_user.is_active:
		# Check if picture owner is comment poster
		cursor.execute("SELECT user_email FROM Pictures WHERE picture_id={0}".format(picture_id))
		user_email = cursor.fetchone()[0]
		if user_email == flask_login.current_user.id:
			cursor.execute("SELECT firstname, lastname, comment_data FROM Users JOIN Comments ON Users.email = Comments.user_email WHERE picture_id = {0}".format(picture_id))
			comments = cursor.fetchall()
			return render_template('viewcomments.html', comments=comments, picture_id=picture_id, message="You can not comment on your own picture!")
	comment = request.form.get('comment')
	user_email = ""
	if flask_login.current_user.is_active:
		user_email = flask_login.current_user.id 
	else:
		user_email = "anonymous"
	cursor.execute("INSERT INTO Comments (comment_data, user_email, picture_id) VALUES ('{0}', '{1}', '{2}')".format(comment, user_email, picture_id))
	conn.commit()
	cursor.execute("SELECT firstname, lastname, comment_data FROM Users JOIN Comments ON Users.email = Comments.user_email WHERE picture_id = {0}".format(picture_id))
	comments = cursor.fetchall()
	return render_template('viewcomments.html', comments=comments, picture_id=picture_id)

@app.route("/topusers")
def top10():
	cursor = conn.cursor()
	cursor.execute("SELECT firstname, lastname, contribution FROM users ORDER BY contribution DESC LIMIT 10")
	topusers = cursor.fetchall()
	return render_template('topusers.html', topusers=topusers)

@app.route("/viewalbum/<string:aid>")
def view_album(aid):
	cursor = conn.cursor()
	cursor.execute("SELECT U.firstname, U.lastname, P.imgdata, P.caption, A.name, P.picture_id, A.album_id FROM Album AS A, Pictures AS P, Users AS U WHERE P.user_email = U.email AND A.album_id = P.album_id AND A.album_id = {0}".format(aid))
	photos = cursor.fetchall()
	return render_template('home.html', photos=photos, base64=base64)

@app.route("/viewtag/<string:tag>")
def view_tag(tag):
	cursor = conn.cursor()
	cursor.execute("SELECT U.firstname, U.lastname, P.imgdata, P.caption, A.name, P.picture_id, A.album_id FROM Tags AS T, Pictures AS P, Users AS U, Album AS A WHERE P.user_email = U.email AND T.tag_data = '{0}' AND T.picture_id = P.picture_id AND P.album_id = A.album_id".format(tag))
	photos = cursor.fetchall()
	return render_template('home.html', photos=photos, base64=base64)

@app.route("/view_user_tag/<string:tag>")
def view_user_tag(tag):
	cursor = conn.cursor()
	cursor.execute("SELECT U.firstname, U.lastname, P.imgdata, P.caption, A.name, P.picture_id, A.album_id FROM Tags AS T, Pictures AS P, Users AS U, Album AS A WHERE P.user_email = U.email AND T.tag_data = '{0}' AND T.picture_id = P.picture_id AND P.album_id = A.album_id AND U.email = '{1}'".format(tag, flask_login.current_user.id))
	photos = cursor.fetchall()
	return render_template('home.html', photos=photos, base64=base64)


@app.route("/delete_photo/<int:picture_id>")
def delete_photo(picture_id):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Tags WHERE picture_id = {0}".format(picture_id))
	conn.commit()
	cursor.execute("DELETE FROM Pictures WHERE picture_id = {0}".format(picture_id))
	conn.commit()
	return redirect('/profile')

@app.route("/delete_album/<int:album_id>")
def delete_album(album_id):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM Pictures WHERE album_id = {0}".format(album_id))
	pid = cursor.fetchall()
	for picture_id in pid:
		cursor.execute("DELETE FROM Tags WHERE picture_id = {0}".format(picture_id))
		conn.commit()
	cursor.execute("DELETE FROM Pictures WHERE album_id = {0}".format(album_id))
	conn.commit()
	cursor.execute("DELETE FROM Album WHERE album_id = {0}".format(album_id))
	conn.commit()
	return redirect('/profile')

@app.route("/search_tags", methods=['GET'])
def search_tags():
	tags = request.args.get('search', "")
	tags = tags.split()
	# SELECT all picture_id
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM Pictures")
	pids = set(cursor.fetchall())
	# for each tag, query picture_id with tag and intersect
	for tag in tags:
		cursor.execute("SELECT P.picture_id FROM Tags T, Pictures P WHERE T.picture_id = P.picture_id AND T.tag_data = '{0}'".format(tag))
		results = set(cursor.fetchall())
		pids = pids.intersection(results)
	photos = []
	for pid in pids:
		cursor.execute("SELECT U.firstname, U.lastname, P.imgdata, P.caption, A.name, P.picture_id, A.album_id FROM Album AS A, Pictures AS P, Users AS U WHERE P.user_email = U.email and A.album_id = P.album_id AND P.picture_id = {0}".format(pid[0]))
		photos.append(cursor.fetchone())
	return render_template('home.html', photos=photos, base64=base64)

@app.route("/search_comments", methods=['GET'])
def search_comments():
	comment = request.args.get('search', "")
	print(comment)
	cursor = conn.cursor()
	cursor.execute("SELECT firstname, lastname, COUNT(*) as ccount FROM (Comments JOIN Users ON Comments.user_email = Users.email) WHERE comment_data = '{0}' ORDER BY ccount DESC".format(comment))
	users = cursor.fetchall()
	return render_template('topusers.html', topusers=users)

@app.route("/add_friend", methods=['POST'])
def add_friend():
	email = request.form.get('email')
	print(email)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Friends (user1_email, user2_email) VALUES ('{0}', '{1}')".format(flask_login.current_user.id, email))
	conn.commit()
	return redirect('/friends')

@app.route("/recommended")
def recommended():
	# Get top 5 most used tags for current user
	cursor = conn.cursor()
	cursor.execute("SELECT tag_data FROM Tags T, Pictures P, Users U WHERE T.picture_id = P.picture_id AND P.user_email = U.email AND U.email = '{0}'".format(flask_login.current_user.id))
	tags = render_string_query(cursor.fetchall())
	top5tags = render_string_query(Counter(tags).most_common(5))
	# Query each tag individually, user_email <> flask_login.current_user.id
	pids = []
	for tag in top5tags:
		cursor.execute("SELECT Pictures.picture_id FROM Pictures JOIN Tags ON Pictures.picture_id = Tags.picture_id WHERE user_email <> '{0}' AND tag_data = '{1}'".format(flask_login.current_user.id, tag))
		pids.extend(render_string_query(cursor.fetchall()))
	hot_pids = Counter(pids).most_common(10)
	# Retrieve photo data from pid
	photos = []
	for pid in hot_pids:
		cursor.execute("SELECT U.firstname, U.lastname, P.imgdata, P.caption, A.name, P.picture_id, A.album_id FROM Album AS A, Pictures AS P, Users AS U WHERE P.user_email = U.email and A.album_id = P.album_id AND P.picture_id = {0}".format(pid[0]))
		photos.append(cursor.fetchone())
	return render_template('home.html', photos=photos, base64=base64)

@app.template_filter()
def get_tags(picture_id):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_data FROM Tags WHERE picture_id = {0}".format(picture_id))
	tags = cursor.fetchall()
	return tags

@app.template_filter()
def top5tags(*args):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_data, COUNT(tag_id) FROM Tags GROUP BY tag_data ORDER BY COUNT(tag_id) DESC LIMIT 5")
	tags = cursor.fetchall()
	return tags

@app.route("/", methods=['GET'])
def home():
	return render_template('home.html', photos=get_all_pictures(), base64=base64)

if __name__ == "__main__":
	app.run(port=5000, debug=True)
