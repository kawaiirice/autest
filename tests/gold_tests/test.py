from __future__ import absolute_import, division, print_function
import difflib



def _do_action_replace(data,text):

    if data == "{}":
        print("NTxt:", text)
        return text
    # more options when we need them
    #elif data == "range":
        # pass

    return None

def _do_action_add(data,text):
        
    if data.strip() == "{}":
        print("NTxt:", text)
        return ''

    return None

def test(val,gold):

    # get the attribute file context
    
    val_content = open(val).read()
    gf_content = open(gold).read()
    
    if True:
        val_content = val_content.replace("\r\n", "\n")
        gf_content = gf_content.replace("\r\n", "\n")

    # make seqerncer differ
    seq = difflib.SequenceMatcher(None,val_content,gf_content,autojunk=False)
    #seq = difflib.SequenceMatcher(None,gf_content,val_content)
    #do we have a match
    if seq.ratio() == 1.0:
        #The says ratio everything matched
        print("Match")
        return
    # if we are here we don't have a match at the moment.  At this point we
    # process difference to see if they
    # match and special code we have and do replacements of values and diff
    # again to see if we have a match
    #get diffs
    results = seq.get_opcodes()
    newtext = ''
    sub=False # true is we are doign a {} and have not had non-white space to replace    
    for tag, i1, i2, j1, j2 in results:
        # technically we can see that we might have a real diff
        # but we continue as this allow certain values to be replaced
        # helping to make the
        # finial diff string more readable
        print("\n-----",tag)
        print("gold:\n'{0}'".format(gf_content[j1:j2]))
        print("val :\n'{0}'".format(val_content[i1:i2]))
        
        print("---------------------------")
        data = gf_content[j1:j2].strip()
        if data.strip() == '{}' or (data == '' and sub==True):
            sub=True
            data='{}'
            if tag != 'insert':
                tag = "replace"
        else:
            sub=False
        print("sub :'{0}'".format(sub))
        if tag == "replace" :
            tmp = _do_action_replace(data,val_content[i1:i2])
            if tmp:
                newtext+=tmp
                continue

        if tag == "insert" :
            tmp = _do_action_add(data,val_content[i1:i2])
            if tmp is not None:
                newtext+=tmp
                continue
        
        newtext+=gf_content[j1:j2]

    print("new text:\n",newtext)
    #reset the sequence test
    seq.set_seq2(newtext)
    if seq.ratio() == 1.0:
        #The says ratio everything matched
        print("WE HAVE A MATCH !!!!!!!!!!!!!!")
        return
    # this makes a nice string value..
    diff = difflib.Differ()
    
    tmp_result = "\n".join(diff.compare(val_content.splitlines(),
                                            newtext.splitlines()))
    tmp_result = "\n".join(diff.compare(newtext.splitlines(),
                                            val_content.splitlines()))
    
    print("File differences\nGold File : {0}\nData File : {1}\n{2}".format(gold,
                        val,
                        tmp_result))



test("_sandbox/cache-generation-disjoint/_tmp_cache-generation-disjoint_0-general_Default/stream.all.txt",
    "cache/gold/miss_default-1.gold")