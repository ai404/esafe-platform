from flask import render_template, request
from flask.views import View

from flask_login import current_user

from web_app.modules._base_views import BasePanel

class BaseLocPanel(BasePanel):
    methods = ["GET", "POST"]
    def get_alerts(self, id, offset=None, limit=10):
        raise NotImplementedError

    def get_items(self):
        raise NotImplementedError

    def get_template_name(self):
        return "location/panel.pug"
    
    def post_template_name(self):
        return "partials/_alerts.pug"

    def post_extra_context(self, id):
        try:
            offset = int(request.form.get("offset"))
            alerts = self.get_alerts(id, offset)
        except:
            alerts = []
        return {
            "alerts": alerts
        }
    
    def get_extra_context(self, id):
        alerts = self.get_alerts(id)
        offset = alerts[-1].id if alerts else -1
        return {
            "alerts":alerts,
            "offset":offset
        }

    def is_valid_item(self, item):
        return item in self.get_items()