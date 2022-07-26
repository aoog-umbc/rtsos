OBJ=nrlib.o rttype_sos_rao_dg.o surface_glint.o Save_Ocean_Rad.o bfit.o rtsos_rao_dg.o bessel.o rtspecfunc.o deltafit.o main.o

#F90=pgf90
F90=gfortran
#F90=ifort
#FCFLAG= -g
#FCFLAG=-real-size 64 -O3
FCFLAG=-O3
#FCFLAG= -g -fbounds-check -ffpe-trap=invalid,zero,overflow -fbacktrace -finit-real=nan

#HDF5DIR = /usr/local/hdf5-1.8.13
#HDF5LIB=-I$(HDF5DIR)/include
#LIBSHDF= $(HDF5LIB) -L$(HDF5DIR)/lib/ -lhdf5 -lhdf5_fortran
LIBSHDF=

DIRCore=../src/core/
DIRMain=../src/main_program_monochromatic/

rtsos_rao_dg.exe: $(OBJ)
	$(F90) -o rtsos_rao_dg.exe $(FCFLAG) $(OBJ) $(LIBSHDF)
nrlib.o:$(DIRCore)/nrlib.f90
	$(F90) -c $(FCFLAG) $(DIRCore)/nrlib.f90
rttype_sos_rao_dg.o: $(DIRCore)/rttype_sos_rao_dg.f90
	$(F90) -c $(FCFLAG) $(DIRCore)/rttype_sos_rao_dg.f90
surface_glint.o: $(DIRCore)/surface_glint.f90
	$(F90) -c $(FCFLAG) $(DIRCore)/surface_glint.f90
Save_Ocean_Rad.o: $(DIRCore)/Save_Ocean_Rad.f90
	$(F90) -c $(FCFLAG) $(DIRCore)/Save_Ocean_Rad.f90
bessel.o:$(DIRCore)/bessel.f
	$(F90) -c $(FCFLAG) $(DIRCore)/bessel.f
rtspecfunc.o:$(DIRCore)/rtspecfunc.f90
	$(F90) -c $(FCFLAG) $(DIRCore)/rtspecfunc.f90
rtsos_rao_dg.o: $(DIRCore)/rtsos_rao_dg.f90
	$(F90) -c $(FCFLAG) $(LIBSHDF) $(DIRCore)/rtsos_rao_dg.f90
bfit.o: $(DIRCore)/bfit.f90
	$(F90) -c $(FCFLAG) $(DIRCore)/bfit.f90
deltafit.o: $(DIRCore)/deltafit.f90
	$(F90) -c $(FCFLAG) $(DIRCore)/deltafit.f90
main.o: $(DIRMain)/main.f90
	$(F90) -c $(FCFLAG) $(LIBSHDF) $(DIRMain)/main.f90

clean:;       rm -f *.o *.exe *.mod

