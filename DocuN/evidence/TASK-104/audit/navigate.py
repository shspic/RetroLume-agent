from metadata import *
index=load(ROOT/'DocuN/evidence/TASK-104/orchestration-setup-20261007/audit-input.json')
nav=load(ROOT/'DocuN/evidence/TASK-104/orchestration-setup-20261007/raw-evidence-navigation.json')
print(json.dumps({'current_first':next(iter(index['current_files'].items())),'goal_contracts':index['goal_contracts'],'rules':index['rules_and_contracts'],'changed_existing':[x['relative_path'] for x in index['product_scope_changed_existing']],'new_product':[x['relative_path'] for x in index['product_scope_new']],'navigation':nav,'resource_permit':load(index['resource_permit'])},ensure_ascii=False,indent=2))
