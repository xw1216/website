from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
import os
import datetime
from app.database import db, User, Activity
from app.image import basedir, allowed_file
from werkzeug.utils import secure_filename


bp = Blueprint('act', __name__)

# TO-DO complete the activity info transfer to database
# fill in the blank like 'src=' or 'href'

@bp.route('/new', methods=['POST', 'GET'])  # 新建活动
def new():
    if session['usertype'] != 'admin' and session['usertype'] != 'teacher':
        return redirect(url_for('home'))

    if request.method == 'GET':
        
        return render_template("teacher/pubActivity.html")
    else:
        name = request.form.get('name')
        description = request.form.get('description')
        # cover_image_path = request.form.get('cover_image_path')
        cover_image_name = request.form.get('cover_image_name')
        label = request.form.get('label')
        lead_teacher = request.form.get('lead_teacher')
        score = request.form.get('score')
        # participants = request.form.get('participants')
        # upload image
        cover_image_path = os.path.join('.', 'static', 'img', 'activity')

        f = request.files['image']

        if name == "":
            flash('请填入活动名称')
            return render_template("teacher/pubActivity.html")
        if label == "":
            flash('请填入活动类型')
            return render_template("teacher/pubActivity.html")
        if lead_teacher == "":
            flash('请填入带队老师')
            return render_template("teacher/pubActivity.html")

        cover_image_name = ""

        if f and allowed_file(f.filename):
            # securitify the filename
            fname = secure_filename(f.filename)
            ext = fname.rsplit('.', 1)[1]
            nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 生成当前时间
            cover_image_name = nowTime + '.' + ext

            cover_image_path += os.sep
            cover_image_path = cover_image_path.replace('\\', '/')
            path = os.path.abspath(os.path.join(cover_image_path, cover_image_name))

            f.save(path)

            # complete feedback
            flash('Upload succeeded!')
            # TO-DO redact the url to prevent from 404
        else:
            flash('The image format is not supported. Please try again.')

        acti = Activity(name=name, description=description, cover_image_path=cover_image_path,
                        cover_image_name=cover_image_name, label=label, lead_teacher=lead_teacher, score=score,
                       # participants=participants
                       )

        db.session.add(acti)
        db.session.commit()

    return redirect(url_for('act.activity', id=acti.id))

@bp.route('/<int:id>/', methods=['POST', 'GET'])
def activity(id):
    act = Activity.query.filter(Activity.id == id).first()
    args = {
        'session': session,
        'act': act
        }
    if act is None:
        return redirect(url_for("home"))
    if 'usertype' not in session:
        return render_template("activity-demo.html", **args, activity=act, isApplied='')
    # if (request.method == 'POST'):
    if session['usertype'] != 'student':#teacher和admin可以删除活动
        return render_template("activity-demo.html", **args, activity=act, operation='Delete')
    elif session['usertype'] == 'student':#studendt可以报名
        student = User.query.filter(User.id == g.userid).first()#取当前用户的id？
        if student not in act.participants:#判断正确性存疑？
            return render_template("activity-demo.html", **args, activity=act, operation='Apply')
        else:
            return render_template("activity-demo.html", **args, activity=act, operation='Abort')
    return render_template("activity-demo.html", **args, activity=act, isApplied='')

@bp.route('/apply/<int:activity_id>')
def apply(activity_id):
    act = Activity.query.filter(Activity.id == activity_id).first()
    student = User.query.filter(User.id == g.userid).first()
    act.participants.append(student)
    db.session.commit()
    return redirect(url_for('act.activity', id=activity_id))

@bp.route('/abort/<int:activity_id>')
def abort(activity_id):
    act = Activity.query.filter(Activity.id == activity_id).first()
    student = User.query.filter(User.id == g.userid).first()
    act.participants.remove(student)
    db.session.commit()
    return redirect(url_for('act.activity', id=activity_id))

@bp.route('/delete/<int:activity_id>')
def delete(activity_id):
    act = Activity.query.filter(Activity.id == activity_id).first()
    db.session.delete(act)
    db.session.commit()
    return redirect(url_for("home"))

@bp.route('/complete/<int:activity_id>')
def complete(activity_id):
    act = Activity.query.filter(Activity.id == activity_id).first()
    act.status = 'finished'
    db.session.commit()
    return redirect(url_for('act.activity', id=activity_id))

@bp.route('/revise/<int:activity_id>', methods=['POST', 'GET'])
def revise(activity_id):
    act = Activity.query.filter(Activity.id == activity_id).first()
    if act is None:
        return redirect(url_for("home"))
    if request.method == 'GET':

        return render_template("teacher/reviseActivity.html", activity_id=activity_id, act=act)
    else:
        name = request.form.get('name')
        description = request.form.get('description')
        # cover_image_path = request.form.get('cover_image_path')
        # cover_image_name = request.form.get('cover_image_name')
        label = request.form.get('label')
        lead_teacher = request.form.get('lead_teacher')
        score = request.form.get('score')
        # participants = request.form.get('participants')
        # upload image
        cover_image_path = os.path.join('.', 'static', 'img', 'activity')

        f = request.files['image']

        if name == "":
            flash('请填入活动名称')
            return render_template("teacher/reviseActivity.html", activity_id=activity_id, act=act)
        if label == "":
            flash('请填入活动类型')
            return render_template("teacher/reviseActivity.html", activity_id=activity_id, act=act)
        if lead_teacher == "":
            flash('请填入带队老师')
            return render_template("teacher/reviseActivity.html", activity_id=activity_id, act=act)

        cover_image_name = ""

        if f and allowed_file(f.filename):
            # securitify the filename
            fname = secure_filename(f.filename)
            ext = fname.rsplit('.', 1)[1]
            nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 生成当前时间
            cover_image_name = nowTime + '.' + ext

            # path = os.path.abspath(os.path.join(cover_image_path, cover_image_name))
            # path = path.replace('\\', '/')
            cover_image_path += os.sep
            cover_image_path = cover_image_path.replace('\\', '/')
            path = os.path.abspath(os.path.join(cover_image_path, cover_image_name))

            f.save(path)

            # complete feedback
            flash('Upload succeeded!')
            # TO-DO redact the url to prevent from 404
        else:
            flash('The image format is not supported. Please try again.')


        act.name = name
        act.description = description
        act.cover_image_path = cover_image_path
        act.cover_image_name = cover_image_name
        act.label = label
        act.lead_teacher = lead_teacher
        act.score = score
        db.session.commit()

    return redirect(url_for('act.activity', id=activity_id))
