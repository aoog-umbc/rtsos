import subprocess


def test_exe():
    assert subprocess.run(['rtsos_GSFC_AC_LUT.exe'])
    assert subprocess.run(['rtsos_Aerosol_Phmx_Cal.exe'])
    assert subprocess.run(['rtsos_PACE_Simulator_DoubleK.exe'])
