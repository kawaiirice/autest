Test.Summary = '''
Test that Trafficserver starts with default configurations.
'''

Test.SkipUnless(Condition.HasProgram("curl","Curl need to be installed on sytem for this test to work"))

p=Test.MakeATSProcess("ts",select_ports=False)
t = Test.AddTestRun("Test traffic server started properly")
t.StillRunningAfter = Test.Processes.ts

p = t.Processes.Default
p.Command = "curl http://127.0.0.1:8080"
p.ReturnCode = 0
p.StartBefore(Test.Processes.ts, ready = When.PortOpen(8080))

