from flask_wtf import FlaskForm


class BaseForm(FlaskForm):
    """Custom Form to ignore disabled fields when populating objects"""

    def populate_obj(self, obj):
        for name, field in self._fields.items():
            if not field.flags.disabled:
                field.populate_obj(obj, name)
