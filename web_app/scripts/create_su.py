import sys
import os

sys.path.append(os.path.abspath(__file__).rsplit("/",3)[0])
from database import db_session
from database import models

import argparse

parser = argparse.ArgumentParser(description='Create Super Admin.')
parser.add_argument('email', type=str,
                    help='Super Admin email address')
parser.add_argument('password', type=str,
                    help='Super Admin password')


def main(args):
    db = db_session()

    company = models.Company()
    company.company_name = "default_company"
    company.company_description = "A dummy company"

    db.add(company)
    db.commit()

    if models.User.query.filter_by(email=args.email).count()>0:
        print(">>> Given email already exist!")
        sys.exit(0)

    su = models.User(args.email, args.password, confirmed=True)
    su.role_id = models.Role_dict.ADMIN
    su.is_su = True
    su.confirmed = True
    su.approved = True
    su.company_id = company.id
    db.add(su)
    db.commit()

    su_profile = models.Profile("Super", "Admin", su.id)

    db.add(su_profile)
    db.commit()

    print(f"Super admin created! user id: {su.id}")

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
