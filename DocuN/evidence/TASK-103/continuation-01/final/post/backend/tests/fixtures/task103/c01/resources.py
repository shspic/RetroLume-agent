"""按精确旧CID和旧标签、新许可账复用，不创建资源。"""
from ..resources import OwnedDocker as BaseDocker,owned_witness,port_available,IMAGE
from .control import Control,BudgetDenied
class OwnedDocker(BaseDocker):
 def __init__(self,control=None):super().__init__(control or Control())
 def create(self,slot):raise BudgetDenied('续作没有创建容器/卷许可')
