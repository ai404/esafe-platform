from environs import Env

env = Env()


class Base(object):
    UPLOAD_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    UPLOAD_FOLDER = "media/"
    UPLOAD_URL = "/media/"

    # Enable protection against CSRF
    WTF_CSRF_ENABLED = True

    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_TIME_LIMIT = None

    USE_GRPC = env.bool("USE_GRPC", False)

    REDIS_SERVER = env("REDIS_SERVER", "redis://")
    TF_SERVE_SERVER = env("TF_SERVE_SERVER", "localhost")
    REQUIRE_EMAIL_CONFIRMATION = env.bool(
        "REQUIRE_EMAIL_CONFIRMATION", False)

env_type = env("APP_ENV", "development")
if env_type == "production":
    class ProductionConfig(Base):
        DEBUG = False
        SQLALCHEMY_DATABASE_URI = env('DATABASE_URL')

        # Secret key for signing cookies
        SECRET_KEY = env('SECRET_KEY')
        SECURITY_PASSWORD_SALT = env('SECURITY_PASSWORD_SALT')

        # Mail Config
        MAIL_SERVER = env('MAILGUN_SMTP_SERVER', 'smtp.mailgun.org')
        MAIL_PORT = env.int('MAILGUN_SMTP_PORT', 587)
        MAILGUN_KEY = env('MAILGUN_KEY', "key-*")
        MAILGUN_DOMAIN = env('MAILGUN_DOMAIN', "app-*.mailgun.org")
        MAIL_USERNAME = env('MAILGUN_SMTP_LOGIN',
                            "postmaster@app-*.mailgun.org")
        MAIL_PASSWORD = env('MAILGUN_SMTP_PASSWORD',
                            "xxxxxxxxxxxxxxxxxxxxxxxxxx")

        MAIL_DEFAULT_SENDER = env(
            'MAIL_DEFAULT_SENDER', "no-reply@my-domain.com")
        MAIL_USE_TLS = env.bool('MAIL_USE_TLS', True)

    Config = ProductionConfig
else:
    class DevelopmentConfig(Base):
        DEBUG = True
        SQLALCHEMY_DATABASE_URI = env(
            'DATABASE_URL', "postgresql://postgres:password@localhost/esafe_dev")

        # Secret key for signing cookies
        SECRET_KEY = env('SECRET_KEY', "ThisIsASecretKey")
        SECURITY_PASSWORD_SALT = env(
            'SECURITY_PASSWORD_SALT', "DoNotShareMeWithAnyOne")

        # Mail Config
        MAIL_SERVER = env('SMTP_SERVER', 'smtp.gmail.com')
        MAIL_PORT = env.int('SMTP_PORT', 587)
        MAIL_USE_TLS = env.bool('MAIL_USE_TLS', True)
        MAIL_USERNAME = env('MAIL_USERNAME', "username@gmail.com")
        MAIL_PASSWORD = env('MAIL_PASSWORD', "password")
        MAIL_DEFAULT_SENDER = env('MAIL_DEFAULT_SENDER', "username@gmail.com")


    Config = DevelopmentConfig
