"""只把现有请求与本地意图入口接到选择上下文，不改业务语义。"""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[4]


def main():
    request_files=['frontend/src/main.tsx','frontend/src/pdf/PdfReviewPanel.tsx',
        'frontend/src/activities/ActivityWorkspace.tsx','frontend/src/activities/teachingApi.ts',
        'frontend/src/activities/interviewApi.ts','frontend/src/activities/memoryApi.ts','frontend/src/explanations/htmlApi.ts']
    for name in request_files:
        path=ROOT/name;text=path.read_text(encoding='utf-8-sig')
        if 'dataFetch' in text:continue
        prefix='./data/context' if name.endswith('/main.tsx') else '../data/context'
        text=f'import {{dataFetch}} from "{prefix}";\n'+text
        # 会话 GET 由 main 明确装载新上下文，其余请求统一带代次并拒迟到。
        text=re.sub(r'\bfetch\(', 'dataFetch(',text)
        if name.endswith('/main.tsx'):text=text.replace('dataFetch("/api/session")','fetch("/api/session")')
        path.write_text(text,encoding='utf-8')
    mappings={
      'frontend/src/activities/pendingIntents.ts':{'STORAGE_KEY':'retrolume.pending-intents.v1'},
      'frontend/src/activities/teachingIntents.ts':{'SUMMARY_KEY':'retrolume.teaching-intents.v1','DB_NAME':'retrolume-teaching','EDITOR_OWNER_KEY':'retrolume.teaching-editor-owner.v1'},
      'frontend/src/activities/interviewIntents.ts':{'KEY':'retrolume.interview.intents.v1','DB':'retrolume-interview-drafts'},
      'frontend/src/activities/memoryIntents.ts':{'SUMMARY':'retrolume.memory-intents.v1','DB':'retrolume-memory'},
      'frontend/src/explanations/htmlIntents.ts':{'KEY':'retrolume.html11.intents.v2'},
    }
    for name,variables in mappings.items():
        path=ROOT/name;text=path.read_text(encoding='utf-8-sig')
        if 'dataStorageKey' in text:continue
        for variable,base in variables.items():
            text=re.sub(r'\b'+variable+r'\b',variable+'()',text)
            pattern=re.escape(variable+'()')+r'\s*=\s*"'+re.escape(base)+r'"'
            text,count=re.subn(pattern,variable+' = () => dataStorageKey("'+base+'")',text)
            if count!=1:raise RuntimeError('意图键身份漂移 '+name+' '+variable)
        text='import {dataStorageKey} from "../data/context";\n'+text
        path.write_text(text,encoding='utf-8')
    print('请求和意图入口已按明确列表接入')


if __name__=='__main__':main()
