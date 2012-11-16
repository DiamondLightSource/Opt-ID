C
C	Create an initial configuration file (setmag.inp)
C
	DIMENSION N(4)
	CHARACTER*2 DIRLAB
	CHARACTER*5 TYPLAB
	CHARACTER*1 ORLAB
C
	NP=90
C
	NB=4*NP+1
C
	OPEN(UNIT=1,FILE='setmag.inp',STATUS='NEW')
	open(unit=2,file='I13iV.sim',status='old')
	open(unit=3,file='I13iH.sim',status='old')
	open(unit=4,file='I13iVE.sim',status='old')
	open(unit=5,file='I13iHEA.sim',status='old')
C
	DO ITYPE=1,4
	N(ITYPE)=0
	END DO
C
	DO IQ=1,2
	DO IPOS=1,NB
C	
	IOR=INT(RAND(0)*2.0+1)
	IF (IOR.EQ.2) IOR=-1
C
	ITYPE=2
	IF (MOD(IPOS,2).EQ.0) ITYPE=1	
	IF (IPOS.EQ.1) ITYPE=4
	IF (IPOS.EQ.NB) ITYPE=4
	IF (IPOS.EQ.2.OR.IPOS.EQ.(NB-1)) ITYPE=3
C
	IF (MOD(IPOS,4).EQ.0) IDIR=-1
	IF (MOD(IPOS+2,4).EQ.0) IDIR=+1
C
	IF (MOD(IPOS+1,4).EQ.0) THEN
	IDIR=1
	IF (IQ.EQ.2) IDIR=-IDIR
	ENDIF
	IF (MOD(IPOS-1,4).EQ.0) THEN
	IDIR=-1
	IF (IQ.EQ.2) IDIR=-IDIR
	ENDIF
C
	if (itype.eq.1) read(2,*) dum
	n(itype)=dum
	if (itype.eq.2) read(3,*) dum
	n(itype)=dum
	if (itype.eq.3) read(4,*) dum
	n(itype)=dum
	if (itype.eq.4) read(5,*) dum
	n(itype)=dum
C
	IF (ITYPE.EQ.1) TYPLAB='Vfull'
	IF (ITYPE.EQ.2) TYPLAB='Hfull'
	IF (ITYPE.EQ.3) TYPLAB='Vhalf'
	IF (ITYPE.EQ.4) TYPLAB='Dhalf'
C
	IF (IOR.EQ.1) ORLAB='N'
	IF (IOR.EQ.-1) ORLAB='R'
C
	IF ((ITYPE.EQ.1.OR.ITYPE.EQ.3).AND.IDIR.EQ.1) DIRLAB='UP'
	IF ((ITYPE.EQ.1.OR.ITYPE.EQ.3).AND.IDIR.EQ.-1) DIRLAB='DW'
	IF ((ITYPE.EQ.2.OR.ITYPE.EQ.4).AND.IDIR.EQ.1) DIRLAB='RG'
	IF ((ITYPE.EQ.2.OR.ITYPE.EQ.4).AND.IDIR.EQ.-1) DIRLAB='LF'
C
	WRITE(1,111)IQ,IPOS,ITYPE,IDIR,IOR,N(ITYPE),TYPLAB,DIRLAB,ORLAB
	END DO
	WRITE(1,*)
	END DO
	CLOSE(1)
	CLOSE(2)
	CLOSE(3)
	CLOSE(4)
	CLOSE(5)
C
111	FORMAT(6(2X,I3),6X,A5,2X,A2,2X,A1)
C
	END
