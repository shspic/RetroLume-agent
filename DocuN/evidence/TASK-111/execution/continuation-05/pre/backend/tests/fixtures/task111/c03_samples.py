"""仅受信合成夹具的域错误与步数上限样本；无任意循环输出。"""
from copy import deepcopy
from .samples import energy,const,op,input_ref,control

def limited(citation):
    value=energy(citation)
    value["title"]="C03 有限域与计算步数"
    value["inputs"]=[control("x","平方根输入",1,1),control("p","有限概率参数",0,1,"range","0.05")]
    value["inputs"][0]["min"]="-1"
    value["calculations"]=[{"id":"hcalc_root","expression":op("sqrt",input_ref("x"))}]
    terms=[op("binomial_pmf",const(20),const(20),input_ref("p")) for _ in range(20)]
    while len(terms)>1:
        terms=[op("add",terms[i],terms[i+1]) if i+1<len(terms) else terms[i] for i in range(0,len(terms),2)]
    value["views"]=[{"id":"hout_root","kind":"readout","label":"平方根","calculation":"hcalc_root","unit":""},
      {"id":"hview_limit","kind":"curve","label":"有限步数曲线","source":{"min":"0","max":"1","samples":128,"expression":terms[0]}}]
    value["calculation_notes"]=[{"formula":"sqrt(x)及有限二项运算曲线","domain":"x范围-1到1，负数拒绝；p在0到1","error":"绝对误差1e-9",
      "samples":[{"input":"x=1,p=0","expected":"平方根1，曲线0"},{"input":"x=-1","expected":"域错误，保留完整上一快照"}],"citations":[citation]}]
    return value
