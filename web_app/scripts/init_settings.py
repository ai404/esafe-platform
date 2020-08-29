from database import db_session
from database import models

db = db_session()


class Settings:
    """Initialize database with config records."""

    def populate_db(self):
        if not models.AccountStatus.query.all():
            self.set_account_status()
        if not models.Role.query.all():
            self.set_roles()

    @staticmethod
    def set_roles():
        # Roles
        roles = [["Staff", "Staff for a specific location."], ["Staff Manager", "Manager for a specific location."],
                 ["Admin", "Admin for a specific company."]]
        for name, description in roles:
            a = models.Role(role_name=name, role_description=description)
            db.add(a)
            db.commit()

    @staticmethod
    def set_account_status():
        # account_status
        account_status = [["New", "Awaiting activation."], ["Active", "Active user."], ["Inactive", "Inactive user."],
                          ["Suspended", "Suspended user."]]
        for name, description in account_status:
            a = models.AccountStatus(
                status_name=name, status_description=description)
            db.add(a)
            db.commit()


if __name__ == "__main__":
    settings = Settings()
    settings.populate_db()
