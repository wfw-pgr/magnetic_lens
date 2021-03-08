cd/d F:\\kent\\linac_design\\maglens\\run\\
start /w /min %SFDIR%automesh maglens
start /w /min %SFDIR%pandira  maglens
start /w /min %SFDIR%sf7 maglens.in7 maglens.t35
exit
