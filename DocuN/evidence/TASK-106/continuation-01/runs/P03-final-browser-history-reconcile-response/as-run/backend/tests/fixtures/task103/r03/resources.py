"""只复用精确pg1；pg2/3仅只读身份，创建0。"""
from ..resources import OwnedDocker as BaseDocker,port_available,IMAGE
from .control import Control,BudgetDenied,require_entry
class OwnedDocker(BaseDocker):
 def __init__(self,control=None):super().__init__(control or Control())
 def create(self,slot):raise BudgetDenied('本许可创建0')
 def start(self,resource):
  require_entry()
  if resource['slot']!=1 or resource['cid']!='4889202d9a58c622fb7cd2bd3087e5bceb7ad20a049c6550f4bd3588ff66ac11':raise BudgetDenied('仅允许pg1启动')
  return super().start(resource)
