import Demo, extdemo
with open('vals', 'w') as f:
    f.write("%s %s" % (Demo.value, extdemo.val))
