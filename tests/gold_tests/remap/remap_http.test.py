import os
Test.Summary = '''
Test a basic remap of a http connection
'''
# need Curl
Test.SkipUnless(
    Condition.HasProgram("curl","Curl need to be installed on sytem for this test to work")
    )
Test.ContinueOnFail=True
# Define default ATS
ts=Test.MakeATSProcess("ts")
server=Test.MakeOriginServer("server")
server.Bob("LOOK AT ME.....................***************************************************************************")
request_header={"headers": "GET /mailservices/v1/newmailcount?appid=UnivHeader&wssid=EOFUrB24A12&callback=YUI.Env.JSONP.yui_3_18_0_6_1469730713762_2538 HTTP/1.1\r\nAccept: application/javascript, */*;q=0.8\r\nReferer: https://www.yahoo.com/\r\nAccept-Language: en-US\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko/20100101 Firefox/12.0\r\nUA-CPU: AMD64\r\nAccept-Encoding: gzip, deflate\r\nHost: mg.mail.yahoo.com\r\nDNT: 1\r\nConnection: Keep-Alive\r\n\r\n", "timestamp": "1469734314.778", "body": ""}

response_header={"headers": "HTTP/1.1 200 OK\r\nDate: Thu, 28 Jul 2016 19:31:54 GMT\r\nP3P: policyref=\"http://info.yahoo.com/w3c/p3p.xml\", CP=\"CAO DSP COR CUR ADM DEV TAI PSA PSD IVAi IVDi CONi TELo OTPi OUR DELi SAMi OTRi UNRi PUBi IND PHY ONL UNI PUR FIN COM NAV INT DEM CNT STA POL HEA PRE LOC GOV\"\r\ncache-control: private,max-age=0\r\ncontent-type: application/json\r\nVary: Accept-Encoding\r\nContent-Encoding: gzip\r\nAge: 0\r\nServer: ATS\r\nVia: http/1.1 r07.ycpi.gq1.yahoo.net (ApacheTrafficServer [cMsSf ]), https/1.1 r10.ycpi.sjb.yahoo.net (ApacheTrafficServer [cMsSf ])\r\nX-Frame-Options: SAMEORIGIN\r\nTransfer-Encoding: chunked\r\nConnection: keep-alive\r\nY-Trace: BAEAQAAAAAAXHfT.N9dZjQAAAAAAAAAAYrB88BoByM8AAAAAAAAAAAAFOLcvu_S7AAU4ty._HXh2HAqZAAAAAA--\r\n\r\n", "timestamp": "1469734314.778", "body": "000005f%0D%0A"}

f=server.Disk.File(os.path.join(server.Variables.DataDir,"persia.json"),id="data1",typename="ats:tracelog")
f.addResponse("persia.json", "remap", request_header, response_header)
ts.Setup.CopyAs("../persia.json",server.Variables.DataDir)
ts.Disk.records_config.update({
        'proxy.config.diags.debug.enabled': 1,
        'proxy.config.diags.debug.tags': 'url.*',
    })

ts.Disk.remap_config.AddLine(
    'map http://www.example.com http://127.0.0.1:{0}'.format(server.Variables.Port)
)
ts.Disk.remap_config.AddLine(
    'map http://www.example.com:8080 http://127.0.0.1:{0}'.format(server.Variables.Port)
)

# call localhost straight
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl "http://127.0.0.1:{0}/" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
# time delay as proxy.config.http.wait_for_cache could be broken
tr.Processes.Default.StartBefore(server)
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Streams.All="gold/remap-404.gold"
tr.StillRunningAfter=server

# www.example.com host
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl --proxy 127.0.0.1:{0} "http://www.example.com/remap" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
tr.Processes.Default.Streams.All="gold/remap-200.gold"

# www.example.com:80 host
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl  --proxy 127.0.0.1:{0} "http://www.example.com:80/remap" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
tr.Processes.Default.Streams.All="gold/remap-200.gold"

# www.example.com:8080 host
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl  --proxy 127.0.0.1:{0} "http://www.example.com:8080/remap" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
tr.Processes.Default.Streams.All="gold/remap-200.gold"

# no rule for this
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl  --proxy 127.0.0.1:{0} "http://www.test.com/remap" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
tr.Processes.Default.Streams.All="gold/remap-404.gold"

# bad port
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl  --proxy 127.0.0.1:{0} "http://www.example.com:1234" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
tr.Processes.Default.Streams.All="gold/remap-404.gold"

     
