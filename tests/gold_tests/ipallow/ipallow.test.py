Test.Summary = '''
Testing IP Allow functionality.
'''

Test.SkipUnless(Condition.HasProgram("curl","Curl need to be installed on system for this test to work"))
Test.testName = "Missing IP Allow file check."

# For this test there is no need to distinguish between requests and responses. It's fine to have the same for all.
#server = Test.MakeOriginServer("server")
#request_header = {"headers": "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n", "body": ""}
#response_header = {"headers": "HTTP/1.1 200 OK\r\n", "body": ""}
#server.addResponse("sessionfile.log", request_header, response_header)

ts = Test.MakeATSProcess("ts")

# Easier to just disable this.
ts.Disk.records_config.update({
    'proxy.config.url_remap.remap_required' : 0,
    })

'''
ts.Disk.ip_allow_config.AddLine({
    'src_ip=0.0.0.0-255.255.255.255                    action=ip_deny  method=PUSH|PURGE|DELETE',
    'src_ip=::-ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff action=ip_deny  method=PUSH|PURGE|DELETE'
    })
'''

# No ip_allow.config -> all connections allowed.
# Not implemented yet because it's broken. Need to fix this and then do the test.

# Check an empty ip_allow.config
ts.Disk.ip_allow_config.WriteOn('')

tr=Test.AddTestRun()
tr.Processes.Default.Command='curl -sS --proxy 127.0.0.1:{0} "http://www.example.com" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=52
tr.Processes.Default.Streams.stderr="gold/deny.gold"
tr.Processes.Default.StartBefore(Test.Processes.ts)

'''
ts.Disk.remap_config.AddLine(
    'map http://www.example.com http://127.0.0.1:{0}'.format(server.Variables.Port)
)
ts.Disk.remap_config.AddLine(
    'map http://www.example.com:8080 http://127.0.0.1:{0}'.format(server.Variables.Port)
)
'''

