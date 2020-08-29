from .. import bp_account
from ..forms import ProfileForm, UploadPhotoForm

from flask import render_template, request, flash, jsonify, g, current_app
from flask_login import login_required, current_user
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
import os


@bp_account.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Profile controller"""
    user_profile = current_user.profile

    photo_form = UploadPhotoForm()
    form = ProfileForm(request.form)

    if request.method == "POST":
        if form.validate():
            form.populate_obj(user_profile)
            g.session.add(user_profile)
            g.session.commit()
            flash("Profile updated successfully!", 'info')
    else:
        form = ProfileForm(obj=user_profile)
    return render_template("account/profile.pug", photo_form=photo_form, form=form)


@bp_account.route('/profile/picture/update', methods=['POST'])
@login_required
def picture_update():
    """Update profile picture"""
    photo_form = UploadPhotoForm(
        CombinedMultiDict((request.files, request.form)))
    if photo_form.validate():
        filename = photo_form.picture.data.filename
        uid = current_user.id
        fileext = secure_filename(filename).rsplit(".")[1]

        upload_fname = f'users/{uid}/pictures/{uid}.{fileext}'
        photo_form.picture.data.save(current_app.config["UPLOAD_FOLDER"]+upload_fname)

        user_profile = current_user.profile
        user_profile.picture = os.path.normpath(upload_fname)
        g.session.add(user_profile)
        g.session.commit()
        flash("Picture updated successfully", "info")

    else:
        flash("Something went wrong! your account picture couldn't be updated", "error")
    return jsonify(success=True)
