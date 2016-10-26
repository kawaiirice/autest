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
ts=Test.MakeATSProcess("ts",select_ports=False)
server=Test.MakeOriginServer("server")

testName = ""
request_header={"headers": "GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n", "timestamp": "1469733493.993", "body": ""}
#desired response form the origin server
response_header={"headers": "HTTP/1.1 200 OK\r\nServer: microserver\r\nConnection: close\r\n\r\n", "timestamp": "1469733493.993", "body": ""}
server.addResponse("sessionlog.json", request_header, response_header)

#add ssl materials like key, certificates for the server
ts.addSSLfile("ssl/server.pem")
ts.addSSLfile("ssl/server.key")

ts.Variables.ssl_port = 4443
ts.Disk.remap_config.AddLine(
    'map / http://127.0.0.1:{0}'.format(server.Variables.Port)
)
ts.Disk.ssl_multicert_config.AddLine(
    'dest_ip=127.0.0.1 ssl_cert_name=server.pem ssl_key_name=server.key'
)
ts.Disk.records_config.update({
        'proxy.config.diags.debug.enabled': 1,
        'proxy.config.diags.debug.tags': 'ssl',
        'proxy.config.ssl.server.cert.path': '{0}'.format(ts.Variables.SSLDir), 
        'proxy.config.ssl.server.private_key.path': '{0}'.format(ts.Variables.SSLDir),
        'proxy.config.ssl.number.threads': 0,
        'proxy.config.http.server_ports': '{0} {1}:proto=http2;http:ssl'.format(ts.Variables.port,ts.Variables.ssl_port),  # enable ssl port
        'proxy.config.ssl.client.verify.server':  0,
        'proxy.config.ssl.server.cipher_suite' : 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384:ECDHE-RSA-RC4-SHA:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:RC4-SHA:RC4-MD5:AES128-SHA:AES256-SHA:DES-CBC3-SHA!SRP:!DSS:!PSK:!aNULL:!eNULL:!SSLv2',
    })
ts.Setup.CopyAs('h2client.py',Test.RunDirectory)
# call localhost straight
tr=Test.AddTestRun()
tr.Processes.Default.Command='python3.5 h2client.py -p {0}'.format(ts.Variables.ssl_port)
tr.Processes.Default.ReturnCode=0
# time delay as proxy.config.http.wait_for_cache could be broken
tr.Processes.Default.StartBefore(server,ready=When.PortOpen(server.Variables.Port))
tr.Processes.Default.StartBefore(Test.Processes.ts, ready=When.PortOpen(ts.Variables.ssl_port))
tr.Processes.Default.Streams.stdout="gold/remap-200.gold"
tr.StillRunningAfter=server

     