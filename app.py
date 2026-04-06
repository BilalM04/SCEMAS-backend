import os

import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
from flask_smorest import Api
from controllers.AccountController import create_accounts_blueprint
from controllers.AlertController import create_alerts_blueprint
from controllers.OperationalController import create_operational_blueprint
from controllers.SensorController import create_sensors_blueprint
from providers.AlertDataProvider import AlertDataProvider
from providers.AlertRuleDataProvider import AlertRuleDataProvider
from providers.LogDataProvider import LogDataProvider
from providers.AccountDataProvider import AccountDataProvider
from providers.SensorDataProvider import SensorDataProvider
from providers.SubscriptionDataProvider import SubscriptionDataProvider
from services.OperationalService import OperationalService
from services.AccountService import AccountService
from services.AlertService import AlertService
from services.SensorService import SensorService
from utils.Limiter import limiter
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    limiter.init_app(app)

    # Swagger config
    app.config["API_TITLE"] = "SCEMAS API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/api"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    app.config["API_SPEC_OPTIONS"] = {
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "security": [{"BearerAuth": []}]
    }

    api = Api(app)

    # Custom Swagger description
    api.spec.options.setdefault("info", {})
    api.spec.options["info"]["description"] = (
        "## Authentication Guide (Firebase Bearer Token)\n\n"
        "This API uses Firebase Authentication with JWT Bearer tokens.\n\n"
        "### Firebase Config\n\n"
        f"**Public API Key:** `{os.environ["FIREBASE_PUBLIC_API_KEY"]}`\n\n"
        "### 1. Get a Bearer Token\n\n"
        "Send a **POST** request to Firebase Auth:\n\n"
        "```\n\n"
        "POST https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=API_KEY\n\n"
        "```\n\n"
        "**Content-Type:** application/json\n\n"
        "```json\n\n"
        "{\n"
        '  "email": "user@example.com",\n'
        '  "password": "your-password",\n'
        '  "returnSecureToken": true\n'
        "}\n\n"
        "```\n\n"

        "### 2. Use the Token\n\n"
        "Include the returned `idToken` in your request headers:\n\n"
        "```\n"
        "Authorization: Bearer YOUR_ID_TOKEN\n"
        "```\n\n"

        "### 3. Notes\n\n"
        "- Tokens are issued by Firebase\n"
        "- Expire after ~1 hour\n"
        "- Must be included in all protected endpoints"
    )

    # Firebase config
    if not firebase_admin._apps:
        cred_dict = {
            "type": os.environ["FIREBASE_TYPE"],
            "project_id": os.environ["FIREBASE_PROJECT_ID"],
            "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
            "private_key": os.environ["FIREBASE_PRIVATE_KEY"],
            "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
            "client_id": os.environ["FIREBASE_CLIENT_ID"],
            "auth_uri": os.environ["FIREBASE_AUTH_URI"],
            "token_uri": os.environ["FIREBASE_TOKEN_URI"],
            "auth_provider_x509_cert_url": os.environ["FIREBASE_AUTH_PROVIDER_X509_CERT_URL"],
            "client_x509_cert_url": os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
            "universe_domain": os.environ["FIREBASE_UNIVERSE_DOMAIN"]
        }

        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # Providers
    account_provider = AccountDataProvider()
    log_provider = LogDataProvider(db)
    alert_provider = AlertDataProvider(db)
    alert_rule_provider = AlertRuleDataProvider(db)
    sensor_provider = SensorDataProvider(db)
    subscription_provider = SubscriptionDataProvider(db)

    # Services
    account_service = AccountService(account_provider)
    alert_service = AlertService(alert_provider, alert_rule_provider, subscription_provider)
    operational_service = OperationalService(log_provider)
    sensor_service = SensorService(sensor_provider, alert_service)

    # Controllers
    AccountBlueprint = create_accounts_blueprint(account_service, operational_service)
    OperationalBlueprint = create_operational_blueprint(operational_service)
    AlertBlueprint = create_alerts_blueprint(alert_service, operational_service)
    SensorBlueprint = create_sensors_blueprint(sensor_service, operational_service)

    api.register_blueprint(AlertBlueprint)
    api.register_blueprint(AccountBlueprint)
    api.register_blueprint(OperationalBlueprint)
    api.register_blueprint(SensorBlueprint)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)