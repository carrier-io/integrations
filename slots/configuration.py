from flask import render_template



from pylon.core.tools import web, log

from tools import auth
from tools import theme


class Slot:  # pylint: disable=E1101,R0903
    """
        Slot Resource

        self is pointing to current Module instance

        web.slot decorator takes one argument: slot name
        Note: web.slot decorator must be the last decorator (at top)

        Slot resources use check_slot auth decorator
        auth.decorators.check_slot takes the following arguments:
        - permissions
        - scope_id=1
        - access_denied_reply=None -> can be set to content to return in case of 'access denied'

    """

    # @web.slot('security_app_content')
    # @auth.decorators.check_slot(
    #     [],
    #     access_denied_reply=theme.access_denied_part
    # )
    # def content(self, context, slot, payload):
    #     log.info('slot: [%s] || payload: [%s]', slot, payload)
    #     with context.app.app_context():
    #         return self.descriptor.render_template(
    #             'app/content.html',
    #         )
    #
    # @web.slot('security_app_scripts')
    # def scripts(self, context, slot, payload):
    #     log.info('slot: [%s] || payload: [%s]', slot, payload)
    #     with context.app.app_context():
    #         return self.descriptor.render_template(
    #             'app/scripts.html',
    #         )
    #
    # @web.slot('security_app_styles')
    # def styles(self, context, slot, payload):
    #     log.info('slot: [%s] || payload: [%s]', slot, payload)
    #     with context.app.app_context():
    #         return self.descriptor.render_template(
    #             'app/styles.html',
    #         )

    @web.slot('configuration_integrations_add_button')
    def add_button(self, context, slot, payload):
        with context.app.app_context():
            return render_template(
                'integrations:configuration/add_button.html',
                config=payload
            )

    @web.slot('configuration_integrations_content')
    def configuration_content(self, context, slot, payload):
        log.warning('config payload %s', payload)
        # results = context.rpc_manager.call.integrations_get_project_integrations(payload['id'])
        #
        # payload['existing_integrations'] = results
        # payload['integrations_section_list'] = context.rpc_manager.call.integrations_section_list()
        with context.app.app_context():
            return render_template(
                'integrations:configuration/content.html',
                config=payload
            )

    @web.slot('configuration_integrations_styles')
    def configuration_content(self, context, slot, payload):
        with context.app.app_context():
            return render_template(
                'integrations:configuration/styles.html',
                config=payload
            )

    @web.slot('configuration_integrations_scripts')
    def configuration_content(self, context, slot, payload):
        with context.app.app_context():
            return render_template(
                'integrations:configuration/scripts.html',
                config=payload
            )