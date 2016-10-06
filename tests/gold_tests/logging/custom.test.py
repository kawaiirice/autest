import os

Test.Summary = '''
Test custom log file
'''
# need Curl
Test.SkipUnless(
    Condition.HasProgram("curl", "Curl need to be installed on sytem for this test to work")
    )

# Define default ATS
ts=Test.MakeATSProcess("ts")

# setup some config file for this server
ts.Disk.remap_config.AddLine(
            'map / http://www.linkedin.com/ @action=deny'
        )

ts.Disk.logging_config.AddLines(
            '''custom = format {
  Format = "%<hii> %<hiih>"
}

log.ascii {
  Format = custom,
  Filename = 'test_log_field'
}'''.split("\n")
        )
# at the end of the different test run a custom log file should exist
Test.Disk.File(os.path.join(ts.Variables.LOGDIR,'test_log_field.log'),exists=True,content='gold/custom.gold')

#first test is a miss for default
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl "http://127.0.0.1:{0}" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0
# time delay as proxy.config.http.wait_for_cache could be broken
tr.Processes.Default.StartBefore(Test.Processes.ts)
        
tr=Test.AddTestRun()
tr.Processes.Default.Command='curl "http://127.1.1.1:{0}" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0

tr=Test.AddTestRun()
tr.Processes.Default.Command='curl "http://127.2.2.2:{0}" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0

tr=Test.AddTestRun()
tr.Processes.Default.Command='curl "http://127.3.3.3:{0}" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0

tr=Test.AddTestRun()
tr.Processes.Default.Command='curl "http://127.3.0.1:{0}" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0

tr=Test.AddTestRun()
tr.Processes.Default.Command='curl "http://127.43.2.1:{0}" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0

tr=Test.AddTestRun()
tr.Processes.Default.Command='curl "http://127.213.213.132:{0}" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0

tr=Test.AddTestRun()
tr.Processes.Default.Command='curl "http://127.123.32.243:{0}" --verbose'.format(ts.Variables.port)
tr.Processes.Default.ReturnCode=0    

