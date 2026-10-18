# TASK-045 局部验证原始记录

时间：2026-09-14（Asia/Shanghai）  
环境：项目内 `backend/.venv`、项目内 `frontend/node_modules`；临时目录和内存资料仓库，无 PostgreSQL、真实资料、外部调用或新增依赖。

## 后端位置 HTTP 契约

命令（工作目录 `D:\shspic\project_NO3_RetroLume-agent\backend`）：

```text
& '.\.venv\Scripts\python.exe' -m unittest tests.test_locations
```

原始输出：

```text
D:\shspic\project_NO3_RetroLume-agent\backend\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
  from starlette.testclient import TestClient as TestClient  # noqa
....
----------------------------------------------------------------------
Ran 4 tests in 0.282s

OK
```

覆盖：中英文和空白行；LF、CRLF、CR；末尾空行规则；HTML 作为文本；摘录的有效/缺配对/越界范围；替换后旧 `version_id` 返回 409；101 个段落只返回前 100 个元数据。该弃用警告来自测试客户端依赖，未修改依赖且不影响四例结论。

## 前端最终构建

命令（工作目录 `D:\shspic\project_NO3_RetroLume-agent\frontend`）：

```text
npm run build
```

原始输出：

```text
> retrolume-local@0.0.1 build
> npm run typecheck && vite build

> retrolume-local@0.0.1 typecheck
> tsc --noEmit

vite v8.3.0 building client environment for production...
transforming...
✓ 16 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.37 kB │ gzip:  0.29 kB
dist/assets/index-Wn8cZysJ.css    5.33 kB │ gzip:  1.86 kB
dist/assets/index-0ZnBLHcU.js   228.97 kB │ gzip: 72.35 kB

✓ built in 110ms
```

## 被测源码 SHA-256

```text
9D2D8C187344D549A3C1DC2A22E2ECA49EDDF9D5B36FA5882860A19A6ECAECE0  backend\app\materials\locations.py
6163F8F8DC8C2F9F7BAD339AB573143503DB29CA1AEFB4D848BDC1712E975719  backend\app\materials\api.py
5E807E23357095619E07A2D127CBC588CAC096084F66204D1E1B5A618A7A1557  frontend\src\main.tsx
11655C139DF0BBF79700258AAD559889A24E5C83C626C593DB161E7CC2F91730  frontend\src\locations.css
1DDE32A6FBFDFFB2A2C462B0BDBC40C34881EA3DBACD70C02BD2F2C846A7BC9F  backend\tests\test_locations.py
```

## 复核修正：原换行摘录与有界段落累计

复核发现上一版 `excerpt` 用 `"\n".join(...)` 改写了 CRLF/CR，且 `locations` 在截断前建立了全部段落字典。2026-09-14 修正为按原字符串跨度裁切（结束行的终止符不包含在摘录中，所选行之间的原始 CRLF/LF/CR 保留），并在一次行扫描中累计完整段数、只存储前 100 个位置。`newline_style` 也不再构造全量换行列表。

命令（工作目录 `D:\shspic\project_NO3_RetroLume-agent\backend`）：

```text
& '.\.venv\Scripts\python.exe' -m unittest tests.test_locations
```

原始输出：

```text
D:\shspic\project_NO3_RetroLume-agent\backend\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
  from starlette.testclient import TestClient as TestClient  # noqa
.....
----------------------------------------------------------------------
Ran 5 tests in 0.256s

OK
```

新增 CRLF 与 CR 两行摘录反例均断言响应保留原始换行字节序列；没有改前端，故没有重跑前端构建。

修正后源码 SHA-256：

```text
F3E238C127FD0BEDA532E32F80AB40011D03FC2C26DBF1007C23481B215157C5  backend\app\materials\locations.py
6163F8F8DC8C2F9F7BAD339AB573143503DB29CA1AEFB4D848BDC1712E975719  backend\app\materials\api.py
B12965EE51CE1D34972D421715E05D15560801048D4D589BA34A7B7896FFA22A  backend\tests\test_locations.py
```

## 第二次复核修正：阅读器异步视图隔离

复核发现 `readExcerpt` 没有取消或验证在途请求，切换资料后 A 的晚到响应可能写入 B。前端没有现成的异步组件测试框架；为避免安装依赖或启动浏览器，本项采用 B 类代码证据，浏览器级乱序网络验证留给最终集成验收，未宣称已通过。

`frontend/src/main.tsx` 的实际约束：

- `ViewIdentity` 固定 `generation`、`sourceId`、`versionId`；`activateMaterial` 在列表切换和替换成功时同步递增代次、取消现有摘录并清空阅读器状态。
- 原文加载也递增代次，以 `expected_version` 请求；成功、错误和 finally 都须通过代次、来源和版本检查后才写状态。
- 每次摘录先取消上一条摘录请求，捕获当前完整身份；成功响应再次核对身份及响应 `material` 的来源/版本，错误同样被身份检查拦截。`readerMaterial` 只在 `selected` 与 `loaded` 的来源和版本一致时可用于摘录或替换。

命令（工作目录 `D:\shspic\project_NO3_RetroLume-agent\frontend`）：

```text
npm run build
```

原始输出：

```text
> retrolume-local@0.0.1 build
> npm run typecheck && vite build

> retrolume-local@0.0.1 typecheck
> tsc --noEmit

vite v8.3.0 building client environment for production...
transforming...
✓ 16 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.37 kB │ gzip:  0.29 kB
dist/assets/index-Wn8cZysJ.css    5.33 kB │ gzip:  1.86 kB
dist/assets/index-Dndg0kmg.js   229.96 kB │ gzip: 72.60 kB

✓ built in 138ms
```

未重跑后端测试。修正后源码 SHA-256：

```text
E37DE3CF1EEDB66D7844D84195CE16262AA4ACA45B6477A27B0A83AE6DD441E4  frontend\src\main.tsx
```
