from metadata import *
writeup={'at':stamp(),'root1':'FAIL，完整原件保留','actual_cause':'HostConfig.Binds也保存命名卷语法；原fixture把任何非空Binds误当host bind','observed_same_owned_resource':True,'original_assertion_stack_not_saved':'首版仅异常类型/空message，诊断记录从实际字段与完整as-run源码定位，未伪造旧栈','new_predicate':'精确单一Mounts.Type=volume、Name/Destination不变；Binds仅允许这个已核命名卷字符串','cids_stopped_pid_zero':True,'resource_starts_in_root1':0,'business_writes':0,'fixed_deadline_and_counts_preserved':True,'helper_correction_number':1}
save('root01-correction-basis.json',writeup)
finish('named-volume-predicate-correction',writeup)
