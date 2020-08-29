from . import bp_main

from flask.views import MethodView
from flask import render_template, request, url_for, redirect, g
from flask_login import login_required, current_user

from database.models import Role_dict, Alert, Location, Entity, Access

from sqlalchemy import func
import datetime as dt
from collections import defaultdict


@bp_main.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("main/dashboard.pug")


@bp_main.route('r/<name>/edit/', methods=['GET', 'POST'])
@login_required
def edit_dispatcher(name):
    id = request.args.get('id', None)
    if id is None:
        return render_template("404.pug")
    return redirect(url_for(f"{name}.editer", id=id))


class BaseDashboard(MethodView):
    alerts_categories = ["distancing", "mask"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alerts_query = None
        self.response = {}

    def _build_base_query(self, _filter, time_range):
        """Prepare Base Query to filter Alerts

        Args:
            _filter (str): Define the scope for statistics (all, one entity, one location).
            time_range (str): Time range for which the stats are calculated.

        Returns:
            boolean: True when the base query is built.
        """
        now = dt.datetime.now()

        # Build the query
        if time_range == "today":
            base_query = Alert.query.filter(func.to_char(
                Alert.created_on, 'YYYY-MM-DD') == now.strftime("%Y-%m-%d"))
        elif time_range.isdigit():
            base_query = Alert.query.filter(func.to_char(
                Alert.created_on, 'YYYY-MM-DD') >= (now-dt.timedelta(int(time_range))).strftime("%Y-%m-%d"))
        else:
            return False

        # filter alerts based on user's role
        if current_user.role_id <= Role_dict.MANAGER:
            base_query = base_query.join(Entity).join(Location).join(
                Access).filter(Access.user_id == current_user.id)
        elif current_user.role_id == Role_dict.ADMIN:
            base_query = base_query.join(Entity).join(Location).filter(
                Location.company_id == current_user.company_id)
        else:
            return False

        # filter alerts based on selected scope
        if _filter == "all":
            self.alerts_query = base_query
        elif _filter.startswith("entity"):
            id_str = _filter.split(":")[-1]
            if not id_str.isdigit():
                return False
            id = int(id_str)
            self.alerts_query = base_query.filter(Alert.entity_id == id)
        elif _filter.startswith("loc"):
            id_str = _filter.split(":")[-1]
            if not id_str.isdigit():
                return False
            id = int(id_str)
            self.alerts_query = base_query.filter(Entity.location_id == id)
        else:
            return False
        return True

    def _prepare_stats(self, _filter, time_range):
        """Aggregate on Base Query to generate stats

        Args:
            _filter (str): Define the scope for statistics (all, one entity, one location).
            time_range (str): Time range for which the stats are calculated.
        """
        pass
    
    def _save_as_dict(self, data):
        """save results as a dictionary"""
        results_dict = defaultdict(lambda: defaultdict(int))
        for child_key, parent_key, value in data:
            results_dict[parent_key][child_key] = round(value)
        
        return results_dict

    def get(self, _filter, time_range="100"):
        self._build_base_query(_filter, time_range)
        self._prepare_stats(_filter, time_range)
        return self.response

    def post(self, _filter, time_range):
        pass


class HourlyHistoryMixin:

    def _prepare_stats(self, _filter, time_range):
        super()._prepare_stats(_filter, time_range)
        if self.alerts_query:
            
            # alerts count per day per hour per type
            date = func.to_char(Alert.created_on, 'YYYY-MM-DD').label("date_")
            time = func.to_char(Alert.created_on, 'HH24').label("time")
            counts = func.count(Alert.id).label("counts")
            alert_type = Alert.alert_type.label("alert_type")
            group_by = [time, date, alert_type]
            subq_gby_time = self.alerts_query.with_entities(*group_by, counts).group_by(*group_by).subquery()
            
            # alerts daily avg per hour per type
            avg_counts = func.avg(subq_gby_time.c.counts).label("avg_counts")
            group_by_time = g.session.query(subq_gby_time.c.time, subq_gby_time.c.alert_type, avg_counts).group_by("time", "alert_type")
            
            # save results as a dictionary
            results_dict = self._save_as_dict(group_by_time.all())

            # handle empty stats
            for category in self.alerts_categories:
                for n in range(24):
                    results_dict[category]["%02d"%n]

            self.response[f"group_by_time"] = results_dict


class DailyHistoryMixin(object):

    def _generate_dates(self, n_days=100):
        """Generate a list of dates within a range from today's date"""
        date = dt.datetime.today()
        for _ in range(n_days):
            yield date.strftime('%d %b')
            date = date - dt.timedelta(days=1)

    def _prepare_stats(self, _filter, time_range):
        super()._prepare_stats(_filter, time_range)
        if self.alerts_query and time_range != "today":

            date = func.to_char(Alert.created_on, 'DD Mon').label("date_")
            counts = func.count(Alert.id).label("counts")
            alert_type = Alert.alert_type.label("alert_type")

            _group_by = [date, alert_type]
            group_by_days = self.alerts_query.with_entities(*_group_by, counts).group_by(*_group_by)

            # save results as a dictionary
            results_dict = self._save_as_dict(group_by_days.all())

            # handle empty stats
            for category in self.alerts_categories:
                for day in self._generate_dates(int(time_range)):
                    results_dict[category][day]

            self.response["group_by_days"] = results_dict


class DistributionStatsMixin(object):

    def _prepare_stats(self, _filter, time_range):
        super()._prepare_stats(_filter, time_range)
        if self.alerts_query and time_range != "today":

            counts = func.count(Alert.id).label("counts")
            _group_by = [Entity.id, Entity.name]
            group_by_entity = self.alerts_query.with_entities(*_group_by, counts).group_by(*_group_by)
            self.response["group_by_entity"] = list(
                map(list, group_by_entity.all()))


class Dashboard(DailyHistoryMixin, HourlyHistoryMixin, BaseDashboard):
    pass


bp_main.add_url_rule('/insights/<_filter>/<time_range>',
                     view_func=login_required(Dashboard.as_view('insights_time')))

bp_main.add_url_rule('/insights/<_filter>/',
                     view_func=login_required(Dashboard.as_view('insights')))
