import numpy as np

# ========================================================= #
# ===  make__am.py ( for poisson )                      === #
# ========================================================= #

def make__am():

    # ------------------------------------------------- #
    # --- [1] load parameters                       --- #
    # ------------------------------------------------- #

    import nkUtilities.load__constants as lcn
    cnfFile = "dat/parameter.conf"
    const = lcn.load__constants( inpFile=cnfFile )

    print()
    print( "[make__am.py] outFile :: {0} ".format( const["outFile"] ) )
    print()

    # ------------------------------------------------- #
    # --- [2] comment & settings                    --- #
    # ------------------------------------------------- #

    comment = \
        "### Magnetic Lens \n"\
        "### created by K.Nishida\n"\
        "###\n\n"

    generals = \
        "kprob=0                                ! superfish problem \n"\
        "icylin=1                               ! cylindrical coordinates \n"\
        "mode=0                                 ! magnetizm mode\n"\
        "conv={0}                               ! unit conversion ( e.g. cm => mm ) \n"\
        "dx={1}                                 ! mesh size \n"\
        "xreg={2}                               ! \n"\
        "yreg={3}                               ! \n"\
        "kreg={4}                               ! \n"\
        "lreg={5}                               ! \n"\
        "kmax={6}                               ! \n"\
        "lmax={7}                               ! \n"\
        .format( const["unit_conversion"], const["meshsize"], \
                 ",".join( [ str(f) for f in const["xreg"] ] ), \
                 ",".join( [ str(f) for f in const["yreg"] ] ), \
                 ",".join( [ str(f) for f in const["kreg"] ] ), \
                 ",".join( [ str(f) for f in const["lreg"] ] ), \
                 const["kmax"], const["lmax"] )

    boundaries = \
        "nbsup={0}                              ! boundary :: upper  ( 0:Neumann, 1:Dirichlet )\n"\
        "nbslo={1}                              !          :: lower  \n"\
        "nbsrt={2}                              !          :: right  \n"\
        "nbslf={3}                              !          :: left   \n"\
        .format( const["boundary_upper"], const["boundary_lower"], \
                 const["boundary_right"], const["boundary_left"] )
        
    
    settings   = "&reg {0}{1}&\n\n".format( generals, boundaries )

    # ------------------------------------------------- #
    # --- [3] magnetic lens geometry                --- #
    # ------------------------------------------------- #
    #
    # -- ltype_== 1 :: straight line.
    # -- ltype_== 2 :: circle.
    # -- ltype_, x_, y_, x0_, y0_ -- #
    #
    pts1       = [ [ 1, const["simBox_r1"], const["simBox_z1"], 0.0,  0.0 ],
                   [ 1, const["simBox_r2"], const["simBox_z1"], 0.0,  0.0 ],
                   [ 1, const["simBox_r2"], const["simBox_z2"], 0.0,  0.0 ],
                   [ 1, const["simBox_r1"], const["simBox_z2"], 0.0,  0.0 ],
                   [ 1, const["simBox_r1"], const["simBox_z1"], 0.0,  0.0 ]
    ]
    pts2       = [ [ 1, const["coil_r1"], const["coil_z1"], 0.0,  0.0 ],
                   [ 1, const["coil_r2"], const["coil_z1"], 0.0,  0.0 ],
                   [ 1, const["coil_r2"], const["coil_z2"], 0.0,  0.0 ],
                   [ 1, const["coil_r1"], const["coil_z2"], 0.0,  0.0 ],
                   [ 1, const["coil_r1"], const["coil_z1"], 0.0,  0.0 ]
    ]
    pts1       = np.array( pts1 )
    pts2       = np.array( pts2 )
    
    #
    ltype_, x_, y_, x0_, y0_  = 0, 1, 2, 3, 4 
    geometry   = ""
    for ik, pt in enumerate( pts1 ):
        if ( int( pt[ltype_] ) == 1 ):
            geometry += "$po x={0}, y={1} $\n".format( pt[x_], pt[y_] )
        if ( int( pt[ltype_] ) == 2 ):
            geometry += "$po nt=2, x={0}, y={1}, x0={2}, y0={3} $\n".format( pt[x_], pt[y_], pt[x0_], pt[y0_] )

    geometry  += "\n\n" + "&reg mat=1, cur={0}&\n\n\n".format( const["coil_current"] )

    for ik, pt in enumerate( pts2 ):
        if ( int( pt[ltype_] ) == 1 ):
            geometry += "$po x={0}, y={1} $\n".format( pt[x_], pt[y_] )
        if ( int( pt[ltype_] ) == 2 ):
            geometry += "$po nt=2, x={0}, y={1}, x0={2}, y0={3} $\n".format( pt[x_], pt[y_], pt[x0_], pt[y0_] )

    # ------------------------------------------------- #
    # --- [4] write in a file                       --- #
    # ------------------------------------------------- #

    with open( const["outFile"], "w" ) as f:
        f.write( comment  )
        f.write( settings )
        f.write( geometry )

    return()



# ========================================================= #
# ===  make in7 ( input file for sf7 )                  === #
# ========================================================= #

def make__in7():

    # -- execute this script to generate grided field -- #
    # -- sf7 : post processor for poisson-superfish   -- #
    # -- in7 : input file for sf7                     -- #

    # ------------------------------------------------- #
    # --- [1] load config file                      --- #
    # ------------------------------------------------- #

    import nkUtilities.load__constants as lcn
    cnfFile = "dat/parameter.conf"
    const   = lcn.load__constants( inpFile=cnfFile )

    if ( const["flag__auto_in7"] ):
        const["in7_xMinMaxNum"] = [const["beam_r1"],const["beam_r2"],const["in7_auto_LI"]]
        const["in7_zMinMaxNum"] = [const["beam_z1"],const["beam_z2"],const["in7_auto_LK"]]
    
    # ------------------------------------------------- #
    # --- [2] write in file                         --- #
    # ------------------------------------------------- #
    line1 = "rect noscreen\n"
    line2 = "{0} {1} {2} {3}\n".format( const["in7_xMinMaxNum"][0], const["in7_zMinMaxNum"][0], \
                                        const["in7_xMinMaxNum"][1], const["in7_zMinMaxNum"][1]  )
    line3 = "{0} {1}\n".format( int( const["in7_xMinMaxNum"][2]-1 ), \
                                int( const["in7_zMinMaxNum"][2]-1 ) )
    line4 = "end\n"
    # line3 :: number of space should be prescribed == Not number of nodes.

    text  = line1 + line2 + line3 + line4

    with open( const["in7File"], "w" ) as f:
        f.write( text )
    print( "[make__in7.py] outFile :: {0} ".format( const["in7File"] ) )
    print()


# ========================================================= #
# ===  make__batch File                                 === #
# ========================================================= #

def make__batch():

    import nkUtilities.load__constants as lcn
    cnsFIle = "dat/parameter.conf"
    const   = lcn.load__constants( inpFile=cnsFIle )

    line1   = "cd/d {0}\n".format( const["cur_dir"] )
    line2   = "start /w /min %SFDIR%automesh maglens\n"
    line3   = "start /w /min %SFDIR%pandira  maglens\n"
    line4   = "start /w /min %SFDIR%sf7 maglens.in7 maglens.t35\n"
    line5   = "exit\n"

    with open( const["batchFile"], "w" ) as f:
        f.write( line1 + line2 + line3 + line4 + line5 )
    print( "[make__batch.py] outFile :: {0} ".format( const["batchFile"] ) )
    print()
    

# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):
    make__am()
    make__in7()
    make__batch()
