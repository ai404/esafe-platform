from flask import render_template, g, request, flash, redirect, url_for
from flask.views import View

from werkzeug.datastructures import CombinedMultiDict

from database.models.account import User

from web_app.helpers.views.base import getter


class BaseView(View):

    @classmethod
    def init_view(cls, variables):
        raise NotImplementedError

    @classmethod
    def get_endpoint(cls):
        raise NotImplementedError

    @classmethod
    def add_url_rule(cls, blueprint, variables, decorators):
        view_func = cls.init_view(variables)

        for decorator in decorators:
            view_func = decorator(view_func)

        blueprint.add_url_rule(cls.get_endpoint(),
                               view_func=view_func
                               )


class BaseUserItems(BaseView):
    url_name = "user_items"

    def __init__(self, title, kind):
        self.title = title
        self.kind = kind

    def get_context(self):
        return {
            "title": self.title,
            "kind": self.kind,
            "items": self.processed_items()
        }

    def processed_items(self):
        return self.get_items()

    def get_items(self):
        raise NotImplementedError

    def get_template_name(self):
        return 'base/show_items.pug'

    def render_template(self, **kwargs):
        return render_template(self.get_template_name(), **kwargs)

    def dispatch_request(self):
        context = self.get_context()
        return self.render_template(**context)

    @classmethod
    def init_view(cls, variables):
        return cls.as_view(cls.url_name,
                           title=variables.title,
                           kind=variables.kind
                           )

    @classmethod
    def get_endpoint(cls):
        return '/user-panel/'


class BaseLister(BaseUserItems):
    url_name = "lister"

    def __init__(self, title, kind, column_ids, column_titles):
        super().__init__(title, kind)
        self.column_ids = column_ids
        self.column_titles = column_titles

    def get_context(self):
        context = super().get_context()
        context.update({
            "column_titles": self.column_titles
        })

        return context

    def processed_items(self):
        items = self.get_items()
        return [(item.id, getter(item, self.column_ids)) for item in items]

    def get_template_name(self):
        return 'base/lister.pug'

    @classmethod
    def init_view(cls, variables):
        return cls.as_view(cls.url_name,
                           title=variables.title,
                           kind=variables.kind,
                           column_titles=variables.column_titles,
                           column_ids=variables.column_ids
                           )

    @classmethod
    def get_endpoint(cls):
        return '/list/'


class BaseAction(BaseView):
    methods = ['GET', 'POST']
    mode = ""

    def __init__(self, title, kind, form, model):
        self.title = title
        self.kind = kind
        self.form = form
        self.model = model

    def get_context(self):
        return {
            "title": self.title,
            "kind": self.kind,
            "mode": self.mode
        }

    def set_special_attributes(self, form, record, **kwargs):
        pass

    def post_transaction(self, form, record, **kwargs):
        pass

    def get_template_name(self):
        return 'base/adder.pug'

    def render_template(self, **kwargs):
        return render_template(self.get_template_name(), **kwargs)

    def build_form(self, **kwargs):
        return self.form

    def preprocess_form(self, form):
        pass

    def get_record(self, **kwargs):
        id = kwargs.get("id", None)
        if id:
            return self.model.query.get(id)
        else:
            return self.model()

    def prepopulate_special_fields(self, form, record):
        pass

    def before_validation_preprocess(self, form, record):
        pass

    def dispatch_request(self, **kwargs):
        # TODO: use a decorator
        #role = Role.query.get(id)
        # if not role or role.id > current_user.role_id:

        record = self.get_record(**kwargs)
        form_class = self.build_form(**kwargs)

        if request.method == 'POST':
            form = form_class(CombinedMultiDict((request.files, request.form)))
            self.before_validation_preprocess(form, record)
            if form.validate():
                self.preprocess_form(form)
                form.populate_obj(record)
                self.set_special_attributes(form, record, **kwargs)

                g.session.add(record)
                g.session.commit()

                self.post_transaction(form, record, **kwargs)

                return redirect(url_for(".lister"))
        elif self.mode == "edit":

            form = form_class(obj=record)
            self.prepopulate_special_fields(form, record)
        else:
            form = form_class()
        context = self.get_context()
        context["form"] = form
        context["item"] = record

        return self.render_template(**context)


class BaseAdder(BaseAction):
    mode = "add"
    url_name = "adder"

    def get_record(self, **kwargs):
        return self.model()

    def post_transaction(self, form, record, **kwargs):
        flash(f"A new record: {self.title} is created!", 'info')

    @classmethod
    def init_view(cls, variables):
        return cls.as_view(cls.url_name,
                           title=variables.title,
                           kind=variables.kind,
                           form=variables.form,
                           model=variables.model
                           )

    @classmethod
    def get_endpoint(cls):
        return '/add/'


class BaseEditer(BaseAction):
    mode = "edit"
    url_name = "editer"

    def get_record(self, **kwargs):
        id = kwargs["id"]
        return self.model.query.get(id)

    def post_transaction(self, form, record, **kwargs):
        flash(f"A record: {self.title} is updated!", 'info')

    @classmethod
    def init_view(cls, variables):
        form = variables.form_edit if hasattr(
            variables, "form_edit") else variables.form

        return cls.as_view(cls.url_name,
                           title=variables.title,
                           kind=variables.kind,
                           form=form,
                           model=variables.model
                           )

    @classmethod
    def get_endpoint(cls):
        return '/edit/<id>'


class BasePreAdder(BaseView):
    methods = ['GET', 'POST']
    url_name = "adder"

    def __init__(self, title, kind, form):
        self.title = title
        self.kind = kind
        self.form = form

    def get_context(self):
        return {
            "title": self.title,
            "kind": self.kind,
        }

    def get_template_name(self):
        return 'base/adder.pug'

    def dispatch_request(self):
        form = self.form(request.form)
        if request.method == 'POST':
            if form.validate():
                return redirect(url_for(".adder_step2", **form.to_dict()))

        context = self.get_context()
        context["form"] = form
        return render_template("base/adder.pug", **context)

    @classmethod
    def init_view(cls, variables):
        return cls.as_view(cls.url_name,
                           title=variables.title,
                           kind=variables.kind,
                           form=variables.form_preadd,
                           )

    @classmethod
    def get_endpoint(cls):
        return '/add'


class BaseDeleter(BaseView):
    methods = ['POST']
    url_name = "delete"

    def __init__(self, title, kind, model):
        self.title = title
        self.kind = kind
        self.model = model

    def get_items(self):
        raise NotImplementedError

    def dispatch_request(self):
        ids = request.form.get('id', None)
        if ids is None:
            return render_template("404.pug")

        ids = ids.split("|")
        user_items = self.get_items()
        for id in ids:
            # TODO: optimize get call
            item = self.model.query.get(id)
            if not item or item not in user_items:
                continue
            g.session.delete(item)
        g.session.commit()

        # TODO Use Decorator for plural
        s, p = ("", "is") if len(ids) == 1 else ("s", "are")
        flash(f"{len(ids)} record{s} of type {self.title} {p} deleted!", 'info')
        return redirect(url_for(".lister"))

    @classmethod
    def init_view(cls, variables):
        return cls.as_view('delete',
                           title=variables.title,
                           kind=variables.kind,
                           model=variables.model
                           )

    @classmethod
    def get_endpoint(cls):
        return '/delete/'


class BasePanel(BaseView):
    method = ['GET', 'POST']
    url_name = "panel"

    def __init__(self, kind, form=None):
        self.kind = kind
        self.form = form

    def get_item(self, id):
        raise NotImplementedError

    def is_valid_item(self, item):
        raise NotImplementedError

    def get_template_name(self):
        return 'base/panel.pug'

    def post_template_name(self):
        return "404.pug"

    def render_template(self, **kwargs):
        return render_template(self.get_template_name(), **kwargs)

    def post_request(self, id):
        return render_template(self.post_template_name(), **self.post_extra_context(id))

    def get_extra_context(self, id):
        return {}

    def post_extra_context(self, id):
        return {}

    def get_request(self, item, id):
        if isinstance(item, User):
            form = self.form(item.role_id)(obj=item)
            del form.password
            del form.password_confirm
        else:
            form = self.form(obj=item) if self.form else None
        return self.render_template(
            kind=self.kind, item=item, form=form, **self.get_extra_context(id))

    def dispatch_request(self, id):
        item = self.get_item(id)

        if not self.is_valid_item(item):
            return render_template("404.pug")

        if request.method == "POST":
            return self.post_request(id)

        return self.get_request(item, id)

    @classmethod
    def init_view(cls, variables):
        form = variables.form_edit if hasattr(
            variables, "form_edit") else variables.form
        return cls.as_view(cls.url_name,
                           kind=variables.kind,
                           form=form
                           )

    @classmethod
    def get_endpoint(cls):
        return '/panel/<id>'
