import numpy as np
import math
def input_writer(filestrbase,irh,iaerosol):
    fileinput='input_'+filestrbase
    f = open(fileinput, 'w')
    
    f.write("%d" % iaerosol+ '      #IAEROSOL=1,20. 1-10 is Shettle and Fenn, 11-20  Ahmad model \n')
    f.write("%d" % irh+ '       #Relative Humidity IRH=1,5, RH=[0.50,0.70,0.80,0.90,0.95] \n')
    f.write("%d" % wv_seg_flag+ '       #wv_seg_flag, 0: all; 1: seg1+3only; 2: seg2only; 3 seg1+2+3; 4: seg4only \n')
    f.write("%s" % aux_dir +'    #aux_dir \n')
    f.write("%s" % 'output_' + filestrbase+'\n')
    f.close

def input_writer_water_clouds(filestrbase,irh,iaerosol):
    fileinput='input_'+filestrbase
    f = open(fileinput, 'w')
    
    f.write("%d" % iaerosol+ '      #IAEROSOL=-98 Water Clouds \n')
    f.write("%f" % Reff_Cloud + '       #Effective Radius \n')
    f.write("%f" % Veff_Cloud + '       #Effective Variance \n')
    f.write("%d" % wv_seg_flag+ '       #wv_seg_flag, 0: all; 1: seg1+3only; 2: seg2only; 3 seg1+2+3; 4: seg4only \n')
    f.write("%s" % aux_dir +'    #aux_dir \n')
    f.write("%s" % 'output_' + filestrbase+'\n')
    f.close

def input_writer_monomodal(filestrbase,irh,iaerosol):
    fileinput='input_'+filestrbase
    f = open(fileinput, 'w')
    
    f.write("%d" % iaerosol+ '      #IAEROSOL=-96 mono-modal  \n')
    f.write("%f" % Reff_Cloud + '       #Effective Radius \n')
    f.write("%f" % Veff_Cloud + '       #Effective Variance \n')
    f.write("%f" % Mr_Cloud + '       #Real Refractive Index  \n')
    f.write("%f" % Mi_Cloud + '       #Imaginary Refractive Index \n')
    f.write("%d" % wv_seg_flag+ '       #wv_seg_flag, 0: all; 1: seg1+3only; 2: seg2only; 3 seg1+2+3; 4: seg4only \n')
    f.write("%s" % aux_dir +'    #aux_dir \n')
    f.write("%s" % 'output_' + filestrbase+'\n')
    f.close


def input_writer_flexible_nmode2(filestrbase,irh,iaerosol,rf1,rf2,rf3,fmfrac,cmsfracs,mixing_flag,nmode):
    fileinput='input_'+filestrbase
    f = open(fileinput, 'w')

    f.write("%d" % iaerosol+ '      #IAEROSOL= -99  for  flexible \n')
    f.write("%d" % nmode+ '     #number of modes flag bi-modal=2, tri-modal=3 \n')
    f.write("%f" % fmfrac+ '        # fine mode fraction: by volume \n')
    f.write("%f" % cmsfracs+ '       #spherical fraction in coarse mode: by volume \n')
    f.write("%f" % rf1+ '       #rf1 dust like  contribution in fine mode: by volume \n')
    f.write("%f" % rf2+ '       #rf2 water soluable contribution in fine mode: by volume\n')
    f.write("%f" % rf3+ '       #rf3 brown carbon contribution in fine mode:by volume \n')
    f.write("%d" % mixing_flag+ '       #Mixing of fine mode aerosols external = 2, internal = 1, internal with zia = 0 \n')
    f.write("%d" % ivar+ '      # dust variance select 1-5 from 1.2, 1.5, 2. , 2.5, 3. (data base) \n')
    f.write("%d" % ireff+ '     # dust effective radius select 1-15 from 0.2, 0.4, 0.6, 0.8, 1. , 1.2, 1.4, 1.6, 1.8,2.,2.2, 2.4, 2.6,2.8, 3.\n')
    f.write("%f" % rh+ '        # realative humidity < 1.0 \n')
    f.write("%f" % r0f+ '       # dry radius fine mode spherical - internal mixing by volume \n')
    f.write("%f" % r0c+ '       # dry radius coarse mode spherical (sea salt) by volume \n') 
    f.write("%f" % sigf+ '      # standard deviation fine mode \n')
    f.write("%f" % sigc+ '      # standard deviation coarse mode \n')
    f.write("%f" % r0_dl+ '     # dry radius dust like (fine mode) by volume  \n')
    f.write("%f" % r0_ws+ '     # dry radius water soluable (fine mode) by volume \n')
    f.write("%f" % r0_bc+ '     # dry radius brown carbon (fine mode) volume \n')
    f.write("%f" % r0_s+ '      # dry radius soot (fine mode) volume \n')
    f.write("%f" % r0_ss+ '     # dry radius sea salt (coarse mode) volume \n')
    f.write("%d" % wv_seg_flag+ '       #wv_seg_flag, 0: all; 1: seg1+3only; 2: seg2only; 3 seg1+2+3; 4: seg4only \n')
    f.write("%s" % aux_dir +'    #aux_dir \n')
    f.write("%s" % 'output_flexible_' + filestrbase+'\n')
    f.close

def input_writer_flexible_nmode3(filestrbase,irh,iaerosol,rf2,rf3,fmfrac,dustfrac,dsfrac,mixing_flag,nmode):
    fileinput='input_'+filestrbase
    f = open(fileinput, 'w')
    
    f.write("%d" % iaerosol+ '      #IAEROSOL= -99 for Flexible \n')
    f.write("%d" % nmode+ '     #number of modes flag bi-modal=2, tri-modal=3 \n')
    f.write("%f" % fmfrac+ '        # fine mode fraction: by volume \n')
    f.write("%f" % dustfrac+ ' #dust fraction \n')
    f.write("%f" % dsfrac+ ' #spherical fraction in dust mode\n')
    f.write("%f" % rf2+ '       #rf2 water soluable contribution in fine mode: by volume\n')
    f.write("%f" % rf3+ '       #rf3 brown carbon contribution in fine mode:by volume \n')
    f.write("%d" % mixing_flag+ '       #Mixing of fine mode aerosols external = 2, internal = 1, internal with zia = 0 \n')
    f.write("%d" % ivar+ '      # dust variance select 1-5 from 1.2, 1.5, 2. , 2.5, 3. (data base) \n')
    f.write("%d" % ireff+ '     # dust effective radius select 1-15 from 0.2, 0.4, 0.6, 0.8, 1. , 1.2, 1.4, 1.6, 1.8,2.,2.2, 2.4, 2.6,2.8, 3.\n')
    f.write("%f" % rh+ '        # realative humidity < 1.0 \n')
    f.write("%f" % r0f+ '       # dry radius fine mode spherical - internal mixing by volume \n')
    f.write("%f" % r0c+ '       # dry radius coarse mode spherical (sea salt) by volume \n')
    f.write("%f" % sigf+ '      # standard deviation fine mode \n')
    f.write("%f" % sigc+ '      # standard deviation coarse mode \n')
    f.write("%f" % r0_dl+ '     # dry radius dust like (fine mode) by volume  \n')
    f.write("%f" % r0_ws+ '     # dry radius water soluable (fine mode) by volume \n')
    f.write("%f" % r0_bc+ '     # dry radius brown carbon (fine mode) volume \n')
    f.write("%f" % r0_s+ '      # dry radius soot (fine mode) volume \n')
    f.write("%f" % r0_ss+ '     # dry radius sea salt (coarse mode) volume \n')
    f.write("%d" % wv_seg_flag+ '       #wv_seg_flag, 0: all; 1: seg1+3only; 2: seg2only; 3 seg1+2+3; 4: seg4only \n')
    f.write("%s" % aux_dir +'    #aux_dir \n')
    f.write("%s" % 'output_flexible_' + filestrbase+'\n')
    f.close

# aux_dir definition
aux_dir='/Users/pwzhai/Research/RT/SOS/SOS_Callable/Data/'

#Common parameters
wv_seg_flag=0

#iaerosol=-99 #=-99 for flexible composition

iaerosol=-96 #=-96 for mono-modal size distribution with mr and mi inputs
Reff_Cloud=0.2  #modal radius of cloud size distribution
Veff_Cloud=0.47  #ln(sigma) of cloud size distribution

#convert to effective radius and variance
Veff_Cloud=Veff_Cloud*Veff_Cloud
Reff_Cloud=Reff_Cloud*math.exp(2.5*Veff_Cloud)
Veff_Cloud=math.exp(Veff_Cloud)-1.0


Mr_Cloud=1.45
Mi_Cloud=0.0

    
irh=4 # VARIABLE only for iaerosl<21


#consider the below parameters for iaerosol=-99 (flexible model) 

nmode=2 #number of modes flag bi-modal=2, tri-modal=3
mixing_flag = 2# aerosol mixing flag (0:internal mixing based on Zia's data, 1:internal mixing, 2:external mixing)

#for nmode=2 rf1+rf2+rf3 has to be less than 1, soot =1-(rf1+rf2+rf3)
#for nmode=3 rf1=0, then soot = 1-(rf2+rf3)

if nmode==2:
    rf1=0.0 #dust like (=0 for nmode =3)
    rf2=0.0#water soluable
    rf3=1.0 #BrC
    cmsfracs=0.2 # coarse mode spherical fraction (sea salt)
    fmfrac=1.0 #finemode fraction
    #!check
    if fmfrac==0.0:
        rf1=0
        rf2=0
        rf3=0
    
    r_soot=(1-(rf1+rf2+rf3))
    dust=1-cmsfracs
    if fmfrac==0:
        r_soot=0
        
    if fmfrac==1:
        cmsfracs=0
        dust=0


if nmode==3:
    rf2=0.0 #water soluable
    rf3=0.0 #BrC
    fmfrac=0.0#finemode fraction
    dustfrac=1.0 # dust fraction (dust and dust like : non-spherical and spherical)
    dsfrac=1.0 # spherical fraction in dust mode (dust like aerosols)
    #!check
    if dustfrac==0.0:
        dsfrac=0.0
    if fmfrac==0.0:
        rf2=0
        rf3=0
    r_soot=(1-(rf2+rf3))
    salt=1-(fmfrac+dustfrac)
    if fmfrac==0:
        r_soot=0
    if fmfrac==1:
        dustfrac=0
        dsfrac=0
        salt=0
    #for nmode=3 and dustfrac>0 and dsfrac>0 and mix_flag=0:  specify r0_dl for mixing flag=0
    #for nmode=3 coarse mode fraction = 1-(fmfrac+dustfrac)


#dust scattering properties from database
ivar=2 # from 1.2, 1.5, 2. , 2.5, 3. (variance)
ireff=15 # from 0.2, 0.4, 0.6, 0.8, 1. , 1.2, 1.4, 1.6, 1.8,2.,2.2, 2.4, 2.6,2.8, 3. (effective radius)

#hygroscopic growth
rh = 0.6 #relative humidity < 1.0

#Change only for fexible model adapted from Zia's (mix_flag =0)
r0f = 0.15 #0.1487 #dry radius fine mode spherical in micro m by volume 
r0c = 2.0194 # dry radius coarse mode spherical or sea slat in micro m by volume 
sigf = 0.806 # standard deviation fine mode
sigc = 0.672 # standard deviation oarse mode

#only change for flexible model (for mix_flag=1 and =2 when nmode=2 and for all the mixing flags when nmode=3)
r0_dl = 0.2 # dry radius dust like in micro m by volume

#only change for flexible model (mix_flag =1 and =2 for both nmode=2 and =3) 
r0_ws = 0.15 #f dry radius water soluable in micro m by volume 
r0_bc = 0.3 #f dry radius brown carbon in micro m by volume 
r0_s = 0.05 #f dry radius soot  in micro m by volume 
r0_ss = 2.0194 #c dry radius sea slat in micro m by volume



if iaerosol==-99 and nmode==2:
    filestrbase='nmode_%d'% nmode\
                +'_flgmixing_%d' % mixing_flag\
                +'_fmfrac_%05.3f' %  fmfrac\
                +'_csalt_%05.3f' % cmsfracs\
                +'_cdust_%05.3f' % dust\
                +'_fdustlike_%05.3f' % rf1\
                +'_fwatersol_%05.3f' % rf2\
                +'_fBrc_%05.3f' % rf3\
                +'_fsoot_%05.3f'% r_soot
    input_writer_flexible_nmode2(filestrbase,irh,iaerosol,rf1,rf2,rf3,fmfrac,cmsfracs,mixing_flag,nmode)

if iaerosol==-99 and nmode==3:
        filestrbase='nmode_%d'% nmode\
                   +'_flgmixing_%d' % mixing_flag\
                   +'_fmfrac_%05.3f' %  fmfrac\
                   +'_csalt_%05.3f'% salt\
                   +'_ddust_%05.3f'% dustfrac\
                   +'_ddustlike_%05.3f'% dsfrac\
                   +'_fwatersol_%05.3f' % rf2\
                   +'_fBrc_%05.3f' % rf3\
                   +'_fsoot_%05.3f'% r_soot
        input_writer_flexible_nmode3(filestrbase,irh,iaerosol,rf2,rf3,fmfrac,dustfrac,dsfrac,mixing_flag,nmode)
                                      
                                      
if iaerosol<=20 and iaerosol>0:
    filestrbase='IAEROSOL_%d' % iaerosol\
                        +'_IRH_%d' % irh
    input_writer(filestrbase,irh,iaerosol)


if iaerosol==-98 :
    filestrbase='WaterCloud_Reff_%f' %Reff_Cloud \
                        +'_Veff_%f' %Veff_Cloud
    input_writer_water_clouds(filestrbase,irh,iaerosol)

if iaerosol==-96 :
    filestrbase='MonoModal_Reff_%f' %Reff_Cloud \
                        +'_Veff_%f' %Veff_Cloud \
                        +'_mr_%f' %Mr_Cloud \
                        +'_mi_%f' %Mi_Cloud
    input_writer_monomodal(filestrbase,irh,iaerosol)
