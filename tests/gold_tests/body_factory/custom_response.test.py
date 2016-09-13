import os 

Test.Summary = '''
Tests for custom reponse body
'''

# this test currently fails and it should not

Test.SkipUnless(Condition.HasProgram("curl","Curl need to be installed on sytem for this test to work"))

ts=Test.MakeATSProcess("ts")
ts.Disk.records_config.update({
            'proxy.config.body_factory.enable_customizations': 3,  # enable domain specific body factory
        })
ts.Disk.remap_config.AddLine(
            'map / http://www.linkedin.com/ @action=deny'
        )


domain_directory = ['www.linkedin.com', '127.0.0.1', 'www.foobar.net']
body_factory_dir=ts.Variables.body_factory_template_dir
# for each domain
set=False
for directory_item in domain_directory:
    # write out a files with some content for Traffic server for given domain
    ts.Disk.File(os.path.join(body_factory_dir, directory_item, "access#denied")).\
        WriteOn("{0} 44 Not 89 found".format(directory_item))
    print(os.path.join(body_factory_dir, directory_item, ".body_factory_info"))
    ts.Disk.File(os.path.join(body_factory_dir, directory_item, ".body_factory_info")).\
        WriteOn("")
    # make a test run for a given domain
    tr=Test.AddTestRun("Test domain {0}".format(directory_item))
    if not set:
        #Start the ATS process for first test run
        tr.Processes.Default.StartBefore(Test.Processes.ts)
        set = True
        tr.StillRunningAfter = ts
    else:
        # test that ats is still running before and after
        tr.StillRunningBefore = ts
        tr.StillRunningAfter = ts
        
    tr.Processes.Default.Command="curl --proxy 127.0.0.1:{1} {0}".format(directory_item,ts.Variables.port)
    tr.Processes.Default.ReturnCode=0
    tr.Streams.All=Testers.ContainsExpression("{0} Not found".format(directory_item),"should contain custom data")
    
