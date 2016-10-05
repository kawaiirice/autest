Test.Summary = '''
Test a basic remap of a http connection
'''
# need Curl
Test.SkipUnless(
    Condition.HasProgram("curl","Curl need to be installed on sytem for this test to work")
    )

# Define default ATS
ts=Test.MakeATSProcess("ts")
server=Test.MakeOriginServer("server")

ts.Disk.records_config.update({
        'proxy.config.diags.debug.enabled': 1,
        'proxy.config.diags.debug.tags': 'url.*',
    })

ts.Disk.remap_config.AddLine(
    'map http://www.example.com http://127.0.0.1:{0}'.format(server.Variables.Port)
)
ts.Disk.remap.config.AddLine(
    'map http://www.example.com:8080 http://127.0.0.1:{0}'.format(server.Variable.Port)
)

"curl --proxy 127.0.0.1:{1} {0}"
# call localhost straight
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl "http://127.0.0.1:{0}/" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
# time delay as proxy.config.http.wait_for_cache could be broken
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Streams.All="gold/remap-404.gold"

# www.example.com host
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl --proxy 127.0.0.1:{1} "http://www.example.com" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
tr.Processes.Default.Streams.All="gold/remap-200.gold"

# www.example.com:80 host
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl  --proxy 127.0.0.1:{1} "http://www.example.com:80" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
tr.Processes.Default.Streams.All="gold/remap-200.gold"

# www.example.com:8080 host
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl  --proxy 127.0.0.1:{1} "http://www.example.com:8080" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
tr.Processes.Default.Streams.All="gold/remap-200.gold"

# no rule for this
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl  --proxy 127.0.0.1:{1} "http://www.test.com" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
tr.Processes.Default.Streams.All="gold/remap-404.gold"

# bad port
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl  --proxy 127.0.0.1:{1} "http://www.example.com:1234" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
tr.Processes.Default.Streams.All="gold/remap-404.gold"

     
