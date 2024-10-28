from flask import request

from tools import auth, api_tools


class ProjectAPI(api_tools.APIModeHandler):
    ...


class AdminAPI(api_tools.APIModeHandler):
    ...


class API(api_tools.APIBase):
    url_params = [
        '<int:project_id>',
        '<string:mode>/<int:project_id>',
        '<string:project_id>',
        '<string:mode>/<string:project_id>'
    ]

    mode_handlers = {
        'default': ProjectAPI,
        'administration': AdminAPI,
    }

    def get(self, **kwargs):
        sections = [i.strip() for i in request.args.get('section', '').split(',')]
        result = []
        if sections:
            for s in sections:
                result.extend(self.module.list_integrations_by_section(s))
            return result, 200
        return list(self.module.list_integrations()), 200
