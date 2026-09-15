"""Local proxy/dashboard for Financial Services Commission credit-card statistics."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlencode, unquote, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json, os, sys, time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
BASE = "https://apis.data.go.kr/1160100/service/GetCredCardCompInfoService"
ENDPOINTS = {"general":"getCredCardCompGeneInfo", "financial":"getCredCardCompFinaInfo", "management":"getCredCardCompKeyManaIndi", "business":"getCredCardCompMajoBusiActi"}
NUMERIC = {"general":["xcsmCnt"], "financial":["astSmryStfnpsAcitAmt"], "management":["cpaqItemValCtt"], "business":["crcdUzAtrsItemCmtlAmt","crcdUzAtrsItemThqrAmt"]}

def parse_xml(raw):
    root = ET.fromstring(raw)
    special = root.find(".//cmmMsgHeader")
    if special is not None:
        return {"header":{"resultCode":special.findtext("returnReasonCode", ""), "resultMsg":special.findtext("returnAuthMsg", "") or special.findtext("errMsg", "")},"items":[],"totalCount":0}
    header = {x.tag:x.text or "" for x in root.findall("./header/*")}
    table = root.find("./body/table")
    if table is None: return {"header":header,"items":[],"totalCount":0}
    items = [{x.tag:x.text or "" for x in node} for node in table.findall("./items/item")]
    return {"header":header,"items":items,"totalCount":table.findtext("totalCount", "0")}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT),**kw)
    def do_GET(self):
        parsed=urlparse(self.path)
        if parsed.path=="/api/cards": return self.api(parse_qs(parsed.query))
        self.path="/index.html" if parsed.path=="/" else self.path
        super().do_GET()
    def send_json(self,status,payload):
        data=json.dumps(payload,ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(data)
    def request_page(self,kind,params,page):
        url=f"{BASE}/{ENDPOINTS[kind]}?"+urlencode(dict(params,pageNo=str(page)))
        last=None
        for attempt in range(3):
            try:
                with urlopen(Request(url,headers={"User-Agent":"CreditCardDashboard/1.0"}),timeout=20) as response:
                    return parse_xml(response.read().decode("utf-8",errors="replace"))
            except (URLError,TimeoutError) as error:
                last=error
                if attempt<2: time.sleep(.7*(attempt+1))
        raise last
    def all_pages(self,kind,params):
        items=[]; page=1; header={}; total=0
        while page<=200:
            result=self.request_page(kind,params,page); header=result["header"]
            if header.get("resultCode", "00")!="00": return result
            part=result["items"]; items.extend(part)
            try: total=int(result["totalCount"])
            except (ValueError,TypeError): total=len(items)
            if not part or len(items)>=total: break
            page+=1
        return {"header":header,"items":items,"totalCount":len(items)}
    def aggregate(self,kind,items):
        companies={}
        for item in items:
            name=item.get("fncoNm") or "회사명 미상"
            if name not in companies:
                companies[name]=dict(item); companies[name]["_sourceCount"]=0; companies[name]["_aggregateLabel"]="제공 항목 합산"
                companies[name]["_sourceCount"]=1
                continue
            row=companies[name]; row["_sourceCount"]+=1
            for field in NUMERIC[kind]:
                try: row[field]=str(float(row.get(field,0) or 0)+float(item.get(field,0) or 0))
                except ValueError: pass
        return sorted(companies.values(),key=lambda r:r.get("fncoNm", ""))
    def api(self,q):
        kind=q.get("kind",[""])[0]; key=q.get("key",[""])[0].strip(); title=q.get("title",[""])[0].strip(); bas=q.get("basYm",[""])[0].strip()
        if kind not in ENDPOINTS or not key: return self.send_json(400,{"error":"조회 유형과 공공데이터포털 인증키를 입력하세요."})
        params={"numOfRows":"100","resultType":"xml","serviceKey":unquote(key)}
        if title: params["title"]=title
        if bas: params["basYm"]=bas
        try:
            result=self.all_pages(kind,params); fallback=False
            if result["header"].get("resultCode","00")!="00":
                return self.send_json(400,{"error":"공공 API가 요청을 거부했습니다.","detail":f"{result['header'].get('resultCode','')} {result['header'].get('resultMsg','')}".strip()})
            if not result["items"] and title:
                params.pop("title",None); result=self.all_pages(kind,params); fallback=True
            if result["header"].get("resultCode","00")!="00":
                return self.send_json(400,{"error":"공공 API가 요청을 거부했습니다.","detail":f"{result['header'].get('resultCode','')} {result['header'].get('resultMsg','')}".strip()})
            raw_count=len(result["items"]); result["items"]=self.aggregate(kind,result["items"]); result["rawCount"]=raw_count; result["titleFallbackUsed"]=fallback
            self.send_json(200,result)
        except HTTPError as e:
            raw=e.read().decode("utf-8",errors="replace")[:500]
            self.send_json(e.code,{"error":f"공공 API HTTP 오류 ({e.code})","detail":raw})
        except (URLError,TimeoutError) as e: self.send_json(502,{"error":"공공 API에 연결하지 못했습니다. 재시도 후에도 실패했습니다.","detail":str(e)})
        except ET.ParseError as e: self.send_json(502,{"error":"공공 API XML 응답을 해석하지 못했습니다.","detail":str(e)})
    def log_message(self,fmt,*args): sys.stdout.write("%s - %s\n"%(self.log_date_time_string(),fmt%args))

if __name__=="__main__":
    port=int(os.environ.get("CARD_DASHBOARD_PORT","8788")); print(f"대시보드: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()
