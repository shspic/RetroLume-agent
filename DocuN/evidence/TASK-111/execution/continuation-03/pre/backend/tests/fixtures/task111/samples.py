"""冻结公式和独立手算期望；只提供合成数据，不冒真实模型质量。"""
from copy import deepcopy


def const(value):return {"op":"const","value":str(value)}
def input_ref(name):return {"op":"input","id":"hctl_"+name}
def op(name,*args):return {"op":name,"args":list(args)}
def control(name,label,default,maximum,kind="number",step="1"):
    return {"id":"hctl_"+name,"kind":kind,"label":label,"description":"合成资料限定参数","min":"0","max":str(maximum),"step":step,"default":str(default)}


def energy(citation="lc_synthetic_energy"):
    return {"schema":"interactive_description.v1","title":"机械能交互","concept":"合成材料定义E=mgh，g=9.8，数值及柱高按输入重算。",
      "inputs":[control("m","质量 m",2,10),control("h","高度 h",3,10)],"constraints":[],
      "calculations":[{"id":"hcalc_energy","expression":op("mul",op("mul",input_ref("m"),const("9.8")),input_ref("h"))}],
      "views":[{"id":"hout_energy","kind":"readout","label":"能量","calculation":"hcalc_energy","unit":"J"},
               {"id":"hview_energy","kind":"bar","label":"能量柱形图","source":{"kind":"values","values":[{"label":"E","value":{"op":"result","id":"hcalc_energy"}}]}}],
      "actions":[{"id":"hact_reset","kind":"reset","label":"恢复默认参数"}],
      "calculation_notes":[{"formula":"E=mgh，g=9.8","domain":"m/h均为0到10","error":"绝对误差1e-9","samples":[{"input":"m=2,h=3","expected":"58.8 J"},{"input":"h=0","expected":"0 J"}],"citations":[citation]}],
      "limitations":["只是冻结资料的公式交互，不证明全学科正确性"],"citations":[citation]}


def binomial(citation="lc_synthetic_binomial"):
    value=energy(citation);value["title"]="二项概率交互 <script>alert(1)</script>";value["concept"]="独立试验的二项分布；脚本闭合文本 </script><img src=x onerror=alert(1)> 仅显示文字。"
    value["inputs"]=[control("n","试验次数 n",3,5,"integer"),control("k","成功次数 k",2,5,"integer"),control("p","成功概率 p","0.5",1,"range","0.05")]
    value["inputs"][0]["min"]="1";value["constraints"]=[{"kind":"le","left":"hctl_k","right":"hctl_n"}]
    value["calculations"]=[{"id":"hcalc_pmf","expression":op("binomial_pmf",input_ref("n"),input_ref("k"),input_ref("p"))}]
    value["views"]=[{"id":"hout_probability","kind":"readout","label":"恰好k次成功概率","calculation":"hcalc_pmf","unit":""},
     {"id":"hview_distribution","kind":"bar","label":"全部概率柱形图","source":{"kind":"binomial_distribution","n":input_ref("n"),"p":input_ref("p")}}]
    value["calculation_notes"]=[{"formula":"P(X=k)=C(n,k)p^k(1-p)^(n-k)","domain":"n整数1到5，k整数0到n，p在0到1","error":"绝对误差1e-9",
     "samples":[{"input":"n=3,k=2,p=0.5","expected":"0.375"},{"input":"p=0,k=0","expected":"1"}],"citations":[citation]}]
    return value


def invalid_cases():
    cases=[]
    def add(name,change):v=deepcopy(energy());change(v);cases.append((name,v))
    for key,text in (("html","<script>location.hash='x'</script>"),("script","while(true){}"),("css","body{background:url(file:///etc/passwd)}"),("iframe","about:blank")):
        add("unknown_"+key,lambda v,k=key,t=text:v.update({k:t}))
    for scheme in ("#x","history","data:text/html,x","blob:x"):
        add("navigation_"+scheme,lambda v,s=scheme:v["actions"].append({"id":"hact_bad","kind":"navigate","url":s}))
    for name in ("http://example.invalid","file:///etc/passwd","window.open","parent.location"):
        add("capability_"+name,lambda v,n=name:v["calculations"][0].update({"expression":{"op":n,"args":[]}}))
    for key in ("__proto__","constructor","prototype","selector"):
        add("object_"+key,lambda v,k=key:v["inputs"][0].update({k:{"value":1}}))
    add("bool_samples",lambda v:v["views"].append({"id":"hview_bad","kind":"curve","label":"bad","source":{"min":"0","max":"1","samples":True,"expression":const("1")}}))
    add("float_const",lambda v:v["calculations"][0].update({"expression":{"op":"const","value":9.8}}))
    add("bad_utf8_scalar",lambda v:v.update({"title":"\ud800"}))
    add("nul_text",lambda v:v.update({"title":"a\0b"}))
    add("node_size",lambda v:v.update({"concept":"a"*1025}))
    add("forward_reference",lambda v:v["calculations"][0].update({"expression":{"op":"result","id":"hcalc_future"}}))
    add("sample_outside_curve",lambda v:v["calculations"][0].update({"expression":{"op":"sample_x"}}))
    add("unknown_citation",lambda v:v.update({"citations":["unknown"]}))
    add("default_step",lambda v:v["inputs"][0].update({"default":"0.2","step":"0.3"}))
    add("negative_zero",lambda v:v["inputs"][0].update({"default":"-0"}))
    add("range_over100",lambda v:v["inputs"][0].update({"kind":"range","step":"0.01"}))
    add("duplicate_id",lambda v:v["inputs"][1].update({"id":"hctl_m"}))
    add("bad_relation",lambda v:v.update({"constraints":[{"kind":"le","left":"hctl_missing","right":"hctl_m"}]}))
    add("too_many_inputs",lambda v:v["inputs"].extend([control(str(i),"x",0,1) for i in range(8)]))
    add("arity",lambda v:v["calculations"][0].update({"expression":op("mul",const("1"))}))
    add("arbitrary_svg",lambda v:v["views"].append({"kind":"svg","id":"hview_bad","label":"svg","source":"<svg/>"}))
    return cases
