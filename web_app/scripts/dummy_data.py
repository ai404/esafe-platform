import sys
import os
sys.path.append(os.path.abspath(__file__).rsplit("/",3)[0])

from database import models, db_session

import datetime as dt
import random

db = db_session()


def create_company():
    company = models.Company()
    company.company_name = "default_company"
    company.company_description = "A dummy company"
    db.add(company)
    db.commit()

    return company

def create_location(company):
    location = models.Location()
    location.company_id = company.id
    location.location_name = "Location One"
    location.location_address = "123 Snowden, Montreal"
    location.lat = "10.098"
    location.lng = "9.098"

    db.add(location)
    db.commit()

    return location


def create_entity(name, location):
    entity = models.Entity()
    entity.name = name
    entity.location_id = location.id

    db.add(entity)
    db.commit()

    return entity


def create_camera(entity_id, name):
    camera = models.Camera()
    camera.entity_id = entity_id
    camera.description = name
    camera.streaming_uri = "streaming_url"
    db.add(camera)
    db.commit()

    return camera


def create_alert(entity_id, camera_id, date):
    alert = models.Alert()
    alert.entity_id = entity_id
    alert.camera_id = camera_id
    alert.source_id = "CAM"
    alert.alert_type = "distancing" if random.random() > 0.1 else "mask"
    alert.created_on = date
    
    db.add(alert)
    db.commit()

    return alert


def main(args):

    company = models.Company.query.first()
    if not company:
        company = create_company()

    location = create_location(company)

    for entity_n in range(1, 5):
        entity = create_entity(f"Entity {entity_n}", location)
        camera = create_camera(entity.id, f"Camera {entity_n}")

        for day_offset in range(100):
            n_alerts = random.randint(50//entity_n, 100//entity_n)
            for _ in range(n_alerts):
                date = dt.datetime.now() - dt.timedelta(days=day_offset, hours=random.randint(7, 18))
                create_alert(entity.id, camera.id, date)


if __name__ == "__main__":
    main(None)
