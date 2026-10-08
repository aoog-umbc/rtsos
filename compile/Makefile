# ===============================================================
#  RTSOS – Radiative Transfer model based on Successive Orders of Scattering
#  Copyright (C) 2025  Pengwang Zhai
#
#  Licensed under the Creative Commons Attribution–NonCommercial 4.0
#  International License (CC BY-NC 4.0).
#  You may use, modify, and share this code for research and
#  educational purposes with proper attribution.
#  Commercial use requires written permission from the author.
#
#  Full license: https://creativecommons.org/licenses/by-nc/4.0/
#  Contact: Pengwang Zhai  |  [pwzhai@gmail.com]
# ===============================================================

OBJ=mathlib.o rttype_sos_rao_dg.o emis_sea.o SnowBRDF.o RossLiBRDF.o surface_glint.o Save_Ocean_Rad.o bfit.o rtsos_rao_dg.o bessel.o rtspecfunc.o deltafit.o main.o

#F90=pgf90
F90=gfortran
#F90=ifort
#FCFLAG= -g  -llapack -lblas
#FCFLAG=-real-size 64 -O3  -llapack -lblas
#FCFLAG=-O3 -llapack -lblas
FCFLAG= -g  -llapack -lblas -fbounds-check -ffpe-trap=invalid,zero,overflow -fbacktrace -finit-real=nan

# Keep compiler module files and generated dependencies out of the source tree.
# gfortran needs -cpp when using -MMD for Fortran module dependencies.
MODDIR = .mod
DEPDIR = .dep
DEPFLAGS = -cpp -MMD -MF $(DEPDIR)/$(@:.o=.d) -J$(MODDIR) -I$(MODDIR)
DEPS = $(patsubst %.o,$(DEPDIR)/%.d,$(OBJ))

#HDF5DIR = /usr/local/hdf5-1.8.13
#HDF5LIB=-I$(HDF5DIR)/include
#LIBSHDF= $(HDF5LIB) -L$(HDF5DIR)/lib/ -lhdf5 -lhdf5_fortran
LIBSHDF=

DIRCore=../src/core/
DIRMain=../src/main_program_monochromatic/

rtsos_rao_dg.exe: $(OBJ)
	$(F90) -o rtsos_rao_dg.exe $(FCFLAG) $(OBJ) $(LIBSHDF)
mathlib.o:$(DIRCore)/mathlib.f90
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(DIRCore)/mathlib.f90
rttype_sos_rao_dg.o: $(DIRCore)/rttype_sos_rao_dg.f90
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(DIRCore)/rttype_sos_rao_dg.f90
emis_sea.o:$(DIRCore)/emis_sea.f90
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(DIRCore)/emis_sea.f90
SnowBRDF.o:$(DIRCore)/SnowBRDF.f90
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(DIRCore)/SnowBRDF.f90
RossLiBRDF.o:$(DIRCore)/RossLiBRDF.f90
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(DIRCore)/RossLiBRDF.f90
surface_glint.o: $(DIRCore)/surface_glint.f90
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(DIRCore)/surface_glint.f90
Save_Ocean_Rad.o: $(DIRCore)/Save_Ocean_Rad.f90
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(DIRCore)/Save_Ocean_Rad.f90
bessel.o:$(DIRCore)/bessel.f
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(DIRCore)/bessel.f
rtspecfunc.o:$(DIRCore)/rtspecfunc.f90
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(DIRCore)/rtspecfunc.f90
rtsos_rao_dg.o: $(DIRCore)/rtsos_rao_dg.f90
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(LIBSHDF) $(DIRCore)/rtsos_rao_dg.f90
bfit.o: $(DIRCore)/bfit.f90
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(DIRCore)/bfit.f90
deltafit.o: $(DIRCore)/deltafit.f90
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(DIRCore)/deltafit.f90
main.o: $(DIRMain)/main.f90
	$(F90) -c $(FCFLAG) $(DEPFLAGS) $(LIBSHDF) $(DIRMain)/main.f90

# Ensure module/dependency directories exist before any object compilation.
$(OBJ): | $(MODDIR) $(DEPDIR)

$(MODDIR) $(DEPDIR):
	mkdir -p $@

clean:
	rm -f *.o *.exe *.mod
	rm -rf $(MODDIR) $(DEPDIR)

# Read compiler-generated Fortran module dependencies when present.
-include $(DEPS)
