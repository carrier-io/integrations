from pylon.core.tools import log

from flask import request
from pydantic import ValidationError

from tools import api_tools, auth, db, serialize, store_secrets
from ...models.integration import IntegrationProject, IntegrationAdmin
from ...models.pd.integration import IntegrationPD


class ProjectAPI(api_tools.APIModeHandler):
    @auth.decorators.check_api({
        "permissions": ["configuration.integrations.integration.details"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": True, "editor": True},
            "default": {"admin": True, "viewer": True, "editor": True},
            "developer": {"admin": False, "viewer": False, "editor": False},
        }})
    def get(self, project_id: int, integration_uid: int, **kwargs):
        integration = self.module.get_by_uid(
            integration_uid=integration_uid,
            project_id=project_id,
            check_all_projects=False
        )
        if not integration:
            integration = self.module.get_by_uid(
                integration_id=integration_uid,
            )
            if not integration:
                return None, 404
        return serialize(IntegrationPD.from_orm(integration)), 200
        # try:
        #     settings = integration.settings_model.parse_obj(request.json)
        # except ValidationError as e:
        #     return e.errors(), 400

    @auth.decorators.check_api(
        {
            "permissions": ["configuration.integrations.integrations.create"],
            "recommended_roles": {
                "administration": {"admin": True, "viewer": False, "editor": True},
                "default": {"admin": True, "viewer": False, "editor": True},
                "developer": {"admin": False, "viewer": False, "editor": False},
            }
        },
        project_id_in_request_json=True
    )
    def post(self, integration_name: str):
        project_id = request.json.get('project_id')
        if not project_id:
            return {'error': 'project_id not provided'}, 400
        integration = self.module.get_by_name(integration_name)
        if not integration:
            return {'error': 'integration not found'}, 404
        try:
            settings = integration.settings_model.parse_obj(request.json)
        except ValidationError as e:
            return e.errors(), 400

        with db.with_project_schema_session(project_id) as tenant_session:
            settings = settings.dict()
            store_secrets(settings, project_id=project_id)
            db_integration = IntegrationProject(
                name=integration_name,
                project_id=request.json.get('project_id'),
                settings=serialize(settings),
                section=integration.section,
                config=request.json.get('config'),
                status=request.json.get('status', 'success'),
            )
            db_integration.insert(tenant_session)
            if request.json.get('is_default'):
                self.module.make_default_integration(db_integration, project_id)
            try:
                return serialize(IntegrationPD.from_orm(db_integration)), 200
            except ValidationError as e:
                return e.errors(), 400

    @auth.decorators.check_api(
        {
            "permissions": ["configuration.integrations.integrations.edit"],
            "recommended_roles": {
                "administration": {"admin": True, "viewer": False, "editor": True},
                "default": {"admin": True, "viewer": False, "editor": True},
                "developer": {"admin": False, "viewer": False, "editor": False},
            }
        },
        project_id_in_request_json=True
    )
    def put(self, integration_id: int):
        project_id = request.json.get('project_id')
        if not project_id:
            return {'error': 'project_id not provided'}, 400
        with db.with_project_schema_session(project_id) as tenant_session:
            db_integration = tenant_session.query(IntegrationProject).filter(
                IntegrationProject.id == integration_id).first()
            integration = self.module.get_by_name(db_integration.name)
            if not integration or not db_integration:
                return {'error': 'integration not found'}, 404
            try:
                settings = integration.settings_model.parse_obj(request.json)
            except ValidationError as e:
                return e.errors(), 400

            if request.json.get('is_default'):
                self.module.make_default_integration(db_integration, project_id)
                # db_integration.make_default(tenant_session)

            db_integration.settings = serialize(settings.dict())
            db_integration.config = request.json.get('config')
            db_integration.insert(tenant_session)
            return serialize(IntegrationPD.from_orm(db_integration)), 200

    @auth.decorators.check_api({
        "permissions": ["configuration.integrations.integrations.edit"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": False, "editor": True},
            "default": {"admin": True, "viewer": False, "editor": True},
            "developer": {"admin": False, "viewer": False, "editor": False},
        }})
    def patch(self, project_id: int, integration_id: int):
        if request.json.get('local'):
            with db.with_project_schema_session(project_id) as tenant_session:
                db_integration = tenant_session.query(IntegrationProject).filter(
                    IntegrationProject.id == integration_id).first()
                integration = self.module.get_by_name(db_integration.name)
                if not integration or not db_integration:
                    return {'error': 'integration not found'}, 404
                self.module.make_default_integration(db_integration, project_id)
        else:
            with db.get_session() as session:
                db_integration = session.query(IntegrationAdmin).where(
                    IntegrationAdmin.id == integration_id).first()
                integration = self.module.get_by_name(db_integration.name)
                if not integration or not db_integration:
                    return {'error': 'integration not found'}, 404
                db_integration.project_id = None
                self.module.make_default_integration(db_integration, project_id)
        return {'msg': 'integration set as default'}, 200

    @auth.decorators.check_api({
        "permissions": ["configuration.integrations.integrations.delete"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": False, "editor": False},
            "default": {"admin": True, "viewer": False, "editor": False},
            "developer": {"admin": False, "viewer": False, "editor": False},
        }})
    def delete(self, project_id: int, integration_id: int):
        with db.with_project_schema_session(project_id) as tenant_session:
            db_integration = tenant_session.query(IntegrationProject).filter(
                IntegrationProject.id == integration_id).first()
            if db_integration:
                tenant_session.delete(db_integration)
                tenant_session.commit()
                self.module.delete_default_integration(db_integration, project_id)
        return integration_id, 204


class AdminAPI(api_tools.APIModeHandler):
    @auth.decorators.check_api({
        "permissions": ["configuration.integrations.integration.details"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": True, "editor": True},
            "default": {"admin": True, "viewer": True, "editor": True},
            "developer": {"admin": False, "viewer": False, "editor": False},
        }})
    def get(self, project_id: int, integration_uid: int, **kwargs):
        integration = self.module.get_by_uid(
            integration_uid=integration_uid,
        )
        if not integration:
            return None, 404
        return serialize(IntegrationPD.from_orm(integration)), 200

    @auth.decorators.check_api({
        "permissions": ["configuration.integrations.integrations.create"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": False, "editor": True},
            "default": {"admin": True, "viewer": False, "editor": True},
            "developer": {"admin": False, "viewer": False, "editor": False},
        }})
    def post(self, integration_name: str, **kwargs):
        integration = self.module.get_by_name(integration_name)
        if not integration:
            return {'error': 'integration not found'}, 404
        try:
            settings = integration.settings_model.parse_obj(request.json)
        except ValidationError as e:
            return e.errors(), 400

        settings = settings.dict()
        store_secrets(settings, project_id=None)
        db_integration = IntegrationAdmin(
            name=integration_name,
            # project_id=request.json.get('project_id'),
            # mode=request.json.get('mode', 'default'),
            settings=serialize(settings),
            section=integration.section,
            config=request.json.get('config'),
            status=request.json.get('status', 'success'),
        )

        with db.get_session() as session:
            db_integration.insert(session)
            if request.json.get('is_default'):
                db_integration.make_default(session)
            return serialize(IntegrationPD.from_orm(db_integration)), 200

    @auth.decorators.check_api({
        "permissions": ["configuration.integrations.integrations.edit"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": False, "editor": True},
            "default": {"admin": True, "viewer": False, "editor": True},
            "developer": {"admin": False, "viewer": False, "editor": False},
        }})
    def put(self, integration_id: int, **kwargs):
        with db.get_session() as session:
            db_integration = session.query(IntegrationAdmin).where(IntegrationAdmin.id == integration_id).first()
            integration = self.module.get_by_name(db_integration.name)
            if not integration or not db_integration:
                return {'error': 'integration not found'}, 404
            try:
                settings = integration.settings_model.parse_obj(request.json)
            except ValidationError as e:
                return e.errors(), 400

            db_integration.settings = settings.dict()
            db_integration.config = request.json.get('config')
            db_integration.insert(session=session)

            if request.json.get('is_default'):
                db_integration.make_default(session=session)
            session.commit()
            return serialize(IntegrationPD.from_orm(db_integration)), 200

    @auth.decorators.check_api({
        "permissions": ["configuration.integrations.integrations.edit"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": False, "editor": True},
            "default": {"admin": True, "viewer": False, "editor": True},
            "developer": {"admin": False, "viewer": False, "editor": False},
        }})
    def patch(self, integration_id: int, **kwargs):
        with db.get_session() as session:
            db_integration: IntegrationAdmin = session.query(IntegrationAdmin).where(
                IntegrationAdmin.id == integration_id).first()
            integration = self.module.get_by_name(db_integration.name)
            if not integration or not db_integration:
                return {'error': 'integration not found'}, 404
            db_integration.make_default(session=session)
            session.commit()
            return {'msg': 'integration set as default'}, 200

    @auth.decorators.check_api({
        "permissions": ["configuration.integrations.integrations.delete"],
        "recommended_roles": {
            "administration": {"admin": True, "viewer": False, "editor": False},
            "default": {"admin": True, "viewer": False, "editor": False},
            "developer": {"admin": False, "viewer": False, "editor": False},
        }})
    def delete(self, integration_id: int, **kwargs):
        with db.get_session() as session:
            del_id = session.query(IntegrationAdmin.id).where(IntegrationAdmin.id == integration_id).delete()
            session.commit()
            return del_id, 204


class API(api_tools.APIBase):
    url_params = [
        '<string:integration_name>',
        '<string:mode>/<string:integration_name>',

        '<int:integration_id>',
        '<string:mode>/<int:integration_id>',

        '<int:project_id>/<int:integration_id>',
        '<string:mode>/<int:project_id>/<int:integration_id>',

        '<int:project_id>/<string:integration_uid>',
        '<string:mode>/<int:project_id>/<string:integration_uid>',
    ]

    mode_handlers = {
        'default': ProjectAPI,
        'administration': AdminAPI,
    }
