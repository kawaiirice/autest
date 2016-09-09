Test.Summary = "Test start up of Traffic server with generated ports of more than one servers at the same time"

Test.SkipUnless(Condition.HasProgram("curl",
                    "Curl needs to be installed on your system for this test to work"))

# set up some ATS processes
ts1 = Test.MakeATSProcess("ts1")
ts2 = Test.MakeATSProcess("ts2")

# setup a testrun
t = Test.AddTestRun("Talk to ts1")
t.StillRunningAfter = ts1
t.StillRunningAfter += ts2
p = t.Processes.Default
p.Command = "curl 127.0.0.1:{0}".format(ts1.Variables.port)
p.ReturnCode = 0
p.StartBefore(Test.Processes.ts1, ready = When.PortOpen(ts1.Variables.port))
p.StartBefore(Test.Processes.ts2, ready = When.PortOpen(ts2.Variables.port))

# setup a testrun
t = Test.AddTestRun("Talk to ts2")
t.StillRunningBefore = ts1
t.StillRunningBefore += ts2
t.StillRunningAfter = ts1
t.StillRunningAfter += ts2
p = t.Processes.Default
p.Command = "curl 127.0.0.1:{0}".format(ts2.Variables.port)
p.ReturnCode = 0