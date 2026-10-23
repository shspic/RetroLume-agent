"""Narrow regressions for the original-instance interview JSON boundary."""
import copy,unittest
from app.capabilities.q_protocol import canonical
from app.capabilities.q_context import validate_provenance
from app.capabilities.contracts import AdmissionDenied
from tests.fixtures.task120.offline import store,AID,TEXT

class InterviewStructureTests(unittest.TestCase):
    def test_closed_context_property_names_do_not_authorize_unapproved_text(self):
        authority=store(template_atoms_extra=('interview_profile','context_json'))
        source=authority.manifest.sources[0]
        state={'activity':{'id':AID},'sources':[{'source_id':source['source_id'],'version_id':source['source_version_id']}],'commands':[]}
        request={'goal':TEXT,'interview_profile':{'context_json':canonical({'goal_body':{'target':TEXT},'parent_record_refs':[],'material_roles':[],'input_policy':''})}}
        validate_provenance(authority,request,{},state,[],[TEXT],'first')
        for name,text in (('answer_text','unapproved answer'),('target','unapproved history'),('text','unapproved memory'),('title','unapproved title')):
            other=copy.deepcopy(request)
            other['interview_profile']['context_json']=canonical({'goal_body':{name:text}})
            with self.assertRaises(AdmissionDenied):validate_provenance(authority,other,{},state,[],[TEXT],'first')
        other=copy.deepcopy(request);other['interview_profile']['context_json']=canonical({'unknown_structure':None})
        with self.assertRaises(AdmissionDenied):validate_provenance(authority,other,{},state,[],[TEXT],'first')

class RetainedInterviewCatalogTests(unittest.TestCase):
    def test_actual_retained_request_uses_validated_frozen_catalog(self):
        import json
        from tests.fixtures.task120 import resources as r
        from app.data_exit.control import ControlHub
        from app.data_exit.q_store import QAuthority
        from app.capabilities.contracts import ModelCallRequest
        if not (r.PRIVATE/'flow/q-root.json').exists():self.skipTest('requires explicit retained TASK120 artifact')
        authority=QAuthority(ControlHub(r.PRIVATE/'flow/control'))
        rows=[x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['domain']=='interview']
        self.assertTrue(rows)
        artifact=authority.artifact(rows[0]);request=ModelCallRequest.model_validate_json(json.dumps(artifact['request']))
        self.assertFalse(hasattr(request.interview_profile,'catalog'))
        authority.manifest.check_model(request,artifact['payload'])
        changed=request.model_copy(update={'messages':(request.messages[0],request.messages[1].model_copy(update={'content':request.messages[1].content+' '}))})
        with self.assertRaises(AdmissionDenied):authority.manifest.check_model(changed,artifact['payload'])
