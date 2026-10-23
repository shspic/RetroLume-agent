"""Only the two08 boundaries, within the inherited finite resources/window."""
from . import resources as r
from .audit07 import case


def execute(mode):
    if r.state()['current_permit_id']!='TASK-120-Q-PREP-TARGETED-REPAIR-08-20261021':raise RuntimeError('repair08_permit_required')
    if mode=='permissions':
        from .repair08_permissions import exercise
        return exercise()
    if mode=='memory':
        from .repair08_memory import exercise
        return exercise()
    if mode=='final':
        from .api_runtime import financials
        value=financials('audit07-main')
        assert value['requests']<=16
        return case('final08-main-financial',lambda:value)
    raise RuntimeError('repair08_unknown_phase')
