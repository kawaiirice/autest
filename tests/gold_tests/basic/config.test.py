Test.Summary = "Test start up of Traffic server with configuration modification of starting port"

Test.SkipUnless(Condition.HasProgram("curl",
                    "Curl needs to be installed on your system for this test to work"))

ts1 = Test.MakeATSProcess("ts1",select_ports=False)
ts1.Setup.ts.CopyConfig('config/records_8090.config',"records.config")
t = Test.AddTestRun("Test traffic server started properly")
t.StillRunningAfter = ts1

p = t.Processes.Default
p.Command = "curl 127.0.0.1:8090"
p.ReturnCode = 0

p.StartBefore(Test.Processes.ts1, ready = When.PortOpen(8090))                    