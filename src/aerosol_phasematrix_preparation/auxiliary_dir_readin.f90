MODULE auxiliary_dir_readin

CHARACTER*360 :: aux_dir='00000'

CONTAINS
SUBROUTINE aux_dir_readin
IF(aux_dir=='00000')THEN
  OPEN(UNIT=1,FILE='./auxiliary_directory',STATUS='OLD',ACTION='READ')
  READ(1,'(A)')aux_dir
  CLOSE(1)
ELSE
  RETURN
ENDIF
ENDSUBROUTINE

ENDMODULE auxiliary_dir_readin

