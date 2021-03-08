import sys
import numpy                      as np
import nkUtilities.load__config   as lcf
import nkUtilities.cMapTri        as cmt
import nkUtilities.configSettings as cfs


# ========================================================= #
# ===  convert__sf7.py                                  === #
# ========================================================= #

def convert__sf7():

    # ------------------------------------------------- #
    # --- [1] load config & sf7 file                --- #
    # ------------------------------------------------- #

    import nkUtilities.load__constants as lcn
    cnfFile = "dat/parameter.conf"
    const   = lcn.load__constants( inpFile=cnfFile )
    
    with open( const["sf7File"], "r" ) as f:
        lines = f.readlines()

    # ------------------------------------------------- #
    # --- [2] search for the data start line        --- #
    # ------------------------------------------------- #

    if ( const["flag__auto_in7"] ):
        LI, LJ, LK = int( const["in7_auto_LI"] ), 1, int( const["in7_auto_LK"] )
    else:
        LI, LJ, LK = int( const["in7_xMinMaxNum"][2] ), 1, int( const["in7_zMinMaxNum"][2] )
    nLine      = LI*LJ*LK
    searchline = "Magnetic fields for a rectangular area with corners at:"
    offset     = 7
    DataStart  = None
    for iL,line in enumerate(lines):
        if ( line.strip() == searchline ):
            DataStart = iL + offset
            break
    if ( DataStart is None ):
        sys.exit( "[convert__sf7.py] cannot find searchline in {0}".format( const["sf7File"] ) )
        
    # ------------------------------------------------- #
    # --- [3] fetch Data from outsf7.txt            --- #
    # ------------------------------------------------- #
    
    # -- [3-1] load file contents                   --  #
    with open( const["sf7File"], "r" ) as f:
        Data = np.loadtxt( f, skiprows=DataStart, max_rows=nLine )
    wData = np.zeros( (Data.shape[0],6) )
        
    # -- [3-2] unit conversion                      --  #
    wData[:,0] = Data[:,0] * 1.e-3 #  R    :: (mm)   -> (m)
    wData[:,1] = Data[:,1] * 1.e-3 #  Z    :: (mm)   -> (m)
    wData[:,2] = Data[:,2] * 1.e-4 #  Br   :: (G)    -> (T)
    wData[:,3] = Data[:,3] * 1.e-4 #  Bz   :: (G)    -> (T)
    wData[:,4] = Data[:,6] * 1.e-2 # dBzdr :: (G/cm) -> (T/m)
    wData[:,5] = Data[:,7] * 1.e-2 # dBrdz :: (G/cm) -> (T/m)
    
    # ------------------------------------------------- #
    # --- [4] save as a pointData                   --- #
    # ------------------------------------------------- #

    # index  = np.lexsort( ( wData[:,0], wData[:,1] ) )
    # wData  = wData[index]
    wData_ = np.reshape( wData, (LK,1,LI,6) )
    
    import nkUtilities.save__pointFile as spf
    names = ["R","Z","Br","Bz","dBzdr","dBrdz"]
    spf.save__pointFile( outFile=const["poiFile"], Data=wData_, names=names )


    # ------------------------------------------------- #
    # --- [5] convert into field-type pointFile     --- #
    # ------------------------------------------------- #
    #
    #  x => r direction
    #  y => t direction
    #
    #  -- [5-1] BField    -- #
    xp_, yp_, zp_  = 0, 1, 2
    bx_, by_, bz_  = 3, 4, 5
    
    pData          = np.zeros( (wData.shape[0],6) )
    pData[:,xp_]   = wData[:,0]
    pData[:,yp_]   = 0.0
    pData[:,zp_]   = wData[:,1]
    pData[:,bx_]   = wData[:,2]
    pData[:,by_]   = 0.0
    pData[:,bz_]   = wData[:,3]

    index          = np.lexsort( ( pData[:,xp_], pData[:,yp_], pData[:,zp_]) )
    pData          = pData[index]
    pData          = np.reshape( pData, (LK,LJ,LI,6) )
    
    import nkUtilities.save__pointFile as spf
    names = ["xp","yp","zp","Bx","By","Bz"]
    spf.save__pointFile( outFile=const["bfieldFile"], Data=pData, names=names )

    

# ========================================================= #
# ===  display__sf7                                     === #
# ========================================================= #
def display__sf7():

    x_ , y_ , z_  = 0, 1, 2
    bx_, by_, bz_ = 3, 4, 5
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    import nkUtilities.load__constants as lcn
    cnfFile = "dat/parameter.conf"
    const   = lcn.load__constants( inpFile=cnfFile )

    config  = lcf.load__config()
    datFile =   const["bfieldFile"]
    pngFile = "png/bfield_{0}.png"

    # ------------------------------------------------- #
    # --- [2] Fetch Data                            --- #
    # ------------------------------------------------- #
    import nkUtilities.load__pointFile as lpf
    Data  = lpf.load__pointFile( inpFile=datFile, returnType="point" )
    
    # ------------------------------------------------- #
    # --- [3] config Settings                       --- #
    # ------------------------------------------------- #
    cfs.configSettings( configType="cMap_def", config=config )
    config["FigSize"]           = (8,3)
    config["cmp_position"]      = [0.16,0.12,0.97,0.88]
    config["xTitle"]            = "Z (m)"
    config["yTitle"]            = "R (m)"
    config["xMajor_Nticks"]     = 8
    config["yMajor_Nticks"]     = 3
    config["cmp_xAutoRange"]    = True
    config["cmp_yAutoRange"]    = True
    config["cmp_xRange"]        = [-5.0,+5.0]
    config["cmp_yRange"]        = [-5.0,+5.0]
    config["vec_AutoScale"]     = True
    config["vec_AutoRange"]     = True
    config["vec_AutoScaleRef"]  = 200.0
    config["vec_nvec_x"]        = 24
    config["vec_nvec_y"]        = 6
    config["vec_interpolation"] = "nearest"

    # ------------------------------------------------- #
    # --- [4] plot Figure                           --- #
    # ------------------------------------------------- #
    cmt.cMapTri( xAxis=Data[:,z_], yAxis=Data[:,x_], cMap=Data[:,bz_], \
                 pngFile=pngFile.format( "Bz" ), config=config )
    cmt.cMapTri( xAxis=Data[:,z_], yAxis=Data[:,x_], cMap=Data[:,bx_], \
                 pngFile=pngFile.format( "Br" ), config=config )

    absB = np.sqrt( Data[:,bz_]**2 + Data[:,bx_]**2 )
    fig  = cmt.cMapTri( pngFile=pngFile.format( "Bv" ), config=config )
    fig.add__cMap   ( xAxis=Data[:,z_], yAxis=Data[:,x_], cMap=absB )
    fig.add__vector ( xAxis=Data[:,z_], yAxis=Data[:,x_], \
                      uvec=Data[:,bz_], vvec=Data[:,bx_], color="blue" )
    fig.save__figure()
    

# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):
    convert__sf7()
    display__sf7()
