from odoo.exceptions import UserError


def rfp_state_flow(from_state):
    # Decorator to restrict the flow of actions on RFPs based on their state.
    def rfp_state_flow_decorator(func):
        def wrapper(self, *args, **kwargs):
            if self.state != from_state:
                raise UserError(f"This action can be performed on RFPs in '{from_state}' state.")
            return func(self, *args, **kwargs)
        return wrapper
    return rfp_state_flow_decorator