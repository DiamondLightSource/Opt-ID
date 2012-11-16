C	------------------
	PROGRAM MEAS_FIELD
C       ------------------
	PARAMETER(NX=10,NY=10)
        LOGICAL exists
	COMMON/CALC1/NP,NSTEP,NSTP,DZ,NPOLMAX,ZMIN,PERIOD
	COMMON/CALC2/CONST,OMEGA0,GAM,TWOC
	COMMON/FLD/BX(0:49999),BY(0:49999)
	COMMON/TRJ/X(0:49999),Y(0:49999),X1(0:49999),Y1(0:49999)
	COMMON/PHS/ PH(0:49999),PH2(0:49999)
	COMMON/SPC/SPEC(0:20000),SPEC2(20000),SSPEC(20000)
	COMMON/SPC2/SPE1(0:20000),SPE2(0:20000),SPE3(0:20000),
     $	SPE4(0:20000),SPE5(0:20000)
	COMMON/ZPOS/ PZ(0:49999)
	COMMON/MFLD/BMX(0:49999),BMY(0:49999)
	COMMON PHASE(0:49999)
	COMMON/DHP/ANGX,ANGY
	DIMENSION ZERO(401),PEAKX(401),PEAKY(401),BCX(401),BCY(401)
	DIMENSION XX(400),YY(400)
	DIMENSION R1(499),R2(499),S1(499),S2(499),SMAX1(499),PMAX(499)
	DIMENSION PPZ(401),PPH(401)
	DIMENSION FP(-200:200,-200:200),FPS(2*NX+1,2*NY+1)
	DIMENSION THX(401),THY(401), Y2A(401,401)
	DIMENSION CAK(9),CBK(9)
	DIMENSION EPS(0:20000),COEFF(20000),PR(401)
	DIMENSION BBX(0:49999),BBY(0:49999),Y2(49999)
	CHARACTER*1 IANS3
C
	TWOPI=2.0*ACOS(-1.0)
C
	OPEN(UNIT=5,FILE='mf.inp',STATUS='OLD')
	READ (5,*)NP,PERIOD,EG,CUR
	READ (5,*)NSKIP
	READ (5,*)NN
C
C	Other Input parameters
C
	NPOLMAX=2*NP+1
C
C	Constants
C
	PI=ACOS(-1.0)
	C=2.997924E10
	TWOC=2.0*C
	EC=4.803242E-10
	EM=9.109534E-28
	GAM=EG/0.5110034E-3
	CONST=EC/EM/C/C/GAM
	HT=1.054588E-27
	EVTOERG=1.602E-12
C
C	HP probe angles
C
	ANGX=0.0
	ANGY=0.0
C
	CALL MFIELD(BXPEAK,BYPEAK,bckx,bcky)
C
	CALL INTERPOLATE(NN)
C
	CALL TRAJECT(0.0,0.0,C1,C2,C3,C4,C5,CC5,C6)
C
	IPOL=1
C
	ICORR=0
	FIXFC=0
	FIYFC=0

	IF (ICORR.EQ.1) THEN
C
C	Impose agreement with field integrals measured 
C	with S.W. or F.C. by adding a field offset
C
	ZLEN=2*ABS(ZMIN)	
	DBX=(FIXFC/10-C3)/ZLEN
	DBY=(FIYFC/10-C1)/ZLEN
	DO JJ=0,NSTEP
	BX(JJ)=BX(JJ)+DBX	
	BY(JJ)=BY(JJ)+DBY	
	END DO
C
	ENDIF
C
	IF (ICORR.EQ.2) THEN
C
C	Correct for planar effect imposing agreement with 
C	field integrals measured with S.W. or F.C.
C
C	Compute integrals
C
	CCX=0.0
	CCY=0.0
	DO JJ=1,NSTEP
	DELTAZ=PZ(JJ)-PZ(JJ-1)
	CCX=CCX+(BX(JJ)**2)*DELTAZ
	CCY=CCY+(BY(JJ)**2)*DELTAZ
	END DO
C
	dbxmax=0
	dbymax=0
	DO JJ=0,NSTEP
	CX=(FIXFC/10-C3)/CCY
	CY=(FIYFC/10-C1)/CCX
	DBX=CX*BY(JJ)**2
	DBY=CY*BX(JJ)**2
	if (abs(dbx).gt.dbxmax)dbxmax=abs(dbx)
	if (abs(dby).gt.dbymax)dbymax=abs(dby)
	BX(JJ)=BX(JJ)+DBX	
	BY(JJ)=BY(JJ)+DBY	
	END DO
C
c	write(6,*)'max deltab =',dbxmax,dbymax

	ENDIF
C
	CALL TRAJECT(0.0,0.0,C1INI,C2INI,C3INI,C4INI,DUM1,DUM2,DUM3)
c
	IANS3='N'
55      FORMAT(A1)
	IF (IANS3.EQ.'K'.OR.IANS3.EQ.'k') THEN
	CALL TRAJECT(0.0,0.0,C1,C2,C3,C4,DUM1,DUM2,DUM3)
	AL=(PZ(NSTEP-NSTP)-PZ(NSTP))*10/1E3
        T2X=(C4*10*10+C3*10*ZMIN*10)/1E6
        T2Y=(C2*10*10+C1*10*ZMIN*10)/1E6
	FIX1=-(C3*10/1E3)/2-T2X/AL
	FIY1=-(C1*10/1E3)/2-T2Y/AL
	FIX2=-(C3*10/1E3)/2+T2X/AL
	FIY2=-(C1*10/1E3)/2+T2Y/AL
	BX(NSTP)=BX(NSTP)+FIX1/(DZ*10)*1E3
	BY(NSTP)=BY(NSTP)+FIY1/(DZ*10)*1E3
	BX(NSTEP-NSTP)=BX(NSTEP-NSTP)+FIX2/(DZ*10)*1E3
	BY(NSTEP-NSTP)=BY(NSTEP-NSTP)+FIY2/(DZ*10)*1E3
	CALL TRAJECT(0.0,0.0,C1,C2,C3,C4,C5,CC5,C6)
	ENDIF
c
	IF (IANS3.EQ.'C'.OR.IANS3.EQ.'c') THEN
	CALL TRAJECT(0.0,0.0,C1,C2,C3,C4,DUM1,DUM2,DUM3)
	I1=NSTEP/2-NP*NSTP/2
	I4=NSTEP/2+NP*NSTP/2
	I2=I1+INT(30/DZ)
	I3=I4-INT(30/DZ)
	II1=INT((I1+I2)/2)
	II2=INT((I3+I4)/2)
	AL=(PZ(II2)-PZ(II1))*10/1E3
        T2X=(C4*100+C3*10*ZMIN*10)/1E6
        T2Y=(C2*100+C1*10*ZMIN*10)/1E6
	FIX1=-(C3*10/1E3)/2-T2X/AL
	FIY1=-(C1*10/1E3)/2-T2Y/AL
	FIX2=-(C3*10/1E3)/2+T2X/AL
	FIY2=-(C1*10/1E3)/2+T2Y/AL
	DO I=I1,I2
	BX(I)=BX(I)+FIX1/300*1E3
	BY(I)=BY(I)+FIY1/300*1E3
	END DO
	DO I=I3,I4
	BX(I)=BX(I)+FIX2/300*1E3
	BY(I)=BY(I)+FIY2/300*1E3
	END DO
	CALL TRAJECT(0.0,0.0,C1,C2,C3,C4,C5,CC5,C6)
	ENDIF
C
	IFUZZ=0
	IQUAD=1
	if (iquad.ne.1.and.iquad.ne.2) then
c	write(6,*)'*** Error in IQUAD input value ***'
	stop
	endif
	READ (5,*)IORD1,IORD2,NPOINTS
	FSX=0.0
	FSY=0.0
	FSX1=0.0
	FSY1=0.0
	FSIGE=1.0
	THPINX=250E-6
	THPINY=250E-6
	THPINX0=0
	THPINY0=0.0
 	DIST=10
	if (dist.eq.0.0) then 
	fsx=0.0
	fsy=0.0
	dist=1.0
	endif
	ENANG=0.0
	EFUND=0.0
	close(5)
C
C	Compute Average Peak Vertical Field and rms field error
C
	NDATAY=NPOLMAX-NSKIP
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2
	BYAV=0.0
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2
	BYAV=BYAV+ABS(BY(IZP))
	END DO
	BYAV=BYAV/NDATAY
c
	S=0.0
	SS=0.0
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2
	ERRY1=ABS(BY(IZP))-BYAV
	S=S+ERRY1
	SS=SS+ERRY1*ERRY1
	END DO
	arg=(SS/NDATAY-S/NDATAY*S/NDATAY)	
	if (arg.gt.0.0) then
	SBPY=SQRT(SS/NDATAY-S/NDATAY*S/NDATAY)	
	else
	sbpy=0.0
	endif
C
	IF (IPOL.EQ.1) THEN
	NDATAX=NPOLMAX-NSKIP+1
	IOFF=-NSTP/4
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2+1
	ELSE
	NDATAX=NPOLMAX-NSKIP
	IOFF=0
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2
	ENDIF
C
	BXAV=0.0
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2+IOFF
	BXAV=BXAV+ABS(BX(IZP))
	END DO
	BXAV=BXAV/NDATAX
c
	S=0.0
	SS=0.0
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2-NSTP/4
	ERRX1=ABS(BX(IZP))-BXAV
	S=S+ERRX1
	SS=SS+ERRX1*ERRX1
	END DO
	arg=(SS/NDATAX-S/NDATAX*S/NDATAX)	
	if (arg.gt.0.0) then
	SBPX=SQRT(SS/NDATAX-S/NDATAX*S/NDATAX)	
	else
	sbpx=0.0
	endif
c
c	Harmonic Analysis of the vertical field component
c
c	J1=NSKIP/2+1
c	J2=NPOLMAX-NSKIP/2
c	open(unit=20,file='field.dat',status='new')
c	iz1=nstep/2-np*nstp/2+(j1-1)*nstp/2
c	iz2=nstep/2-np*nstp/2+(j2-1)*nstp/2
c	akz=twopi/period	
c	sumcak=0.0
c	sumcbk=0.0
c	do k=1,9
c	cak(k)=0.0
c	cbk(k)=0.0
c	do izp=iz1,iz2
c	terma=cos(akz*pz(izp)*k)*by(izp)*2.0/(iz2-iz1)
c	termb=sin(akz*pz(izp)*k)*by(izp)*2.0/(iz2-iz1)
c	if (izp.eq.iz1.or.izp.eq.iz2) then
c	terma=terma/2
c	termb=termb/2
c	endif
c	cak(k)=cak(k)+terma
c	cbk(k)=cbk(k)+termb
c	end do
c	sumcak=sumcak+cak(k)
c	sumcbk=sumcbk+cbk(k)
c	end do
c	close(20)
C
	BX0=BXAV
	BY0=BYAV
c	write(6,*)'BXmax=',BXPEAK
c	write(6,*)'BYmax=',BYPEAK
c
	AKX=-EC*PERIOD/2.0/PI/EM/C/C*ABS(BX0)
	AKY=-EC*PERIOD/2.0/PI/EM/C/C*ABS(BY0)
	OMEGA0=4.0*PI*C*GAM*GAM/(1.0+(AKX*AKX+AKY*AKY)/2.0)/PERIOD
c	WRITE (6,*)'E1 (eV) from average field =',OMEGA0*HT/EVTOERG
C
C	Compute Average Trajectory Angles
C
	NDATAY=NPOLMAX-NSKIP
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2
	X1AV=0.0
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2
	X1AV=X1AV+X1(IZP)
	END DO
	X1AV=X1AV/NDATAY
c
	IF (IPOL.EQ.1) THEN
	NDATAX=NPOLMAX-NSKIP+1
	IOFF=-NSTP/4
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2+1
	ELSE
	NDATAX=NPOLMAX-NSKIP
	IOFF=0
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2
	ENDIF
	Y1AV=0.0
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2+IOFF
	Y1AV=Y1AV+Y1(IZP)
	END DO
	Y1AV=Y1AV/NDATAX
C
C	Compute path length
C	
	PATH1=0.0
	PATH2=0.0
	DO I=1,NSTEP
	PATH1=PATH1+(X1(I)*X1(I))/2*DZ*10
	PATH2=PATH2+(X1(I)*X1(I)+X1(I-1)*X1(I-1))/2/2*DZ*10
	END DO		
C
C       Compute fundamental energy
C
	NPOLMAX=4*NP+1
	J1=NSKIP+1
	J2=NPOLMAX-NSKIP
	NDATA=NPOLMAX-2*NSKIP
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	JJ=J-NSKIP
	XX(JJ)=IZP
	YY(JJ)=PH2(IZP)
	END DO
	CALL FIT(XX,YY,NDATA,SIG,0,A,B,SIGA,SIGB,CHI2)
	OMEGA0=TWOPI/B/NSTP
c	WRITE(6,*)'E1 (eV) from linear fit of phase =',
c     $	OMEGA0*HT/EVTOERG
C
C	Assume fundamental is at EFUND
C
	IF (EFUND.NE.0.0) OMEGA0=EFUND*EVTOERG/HT
C
C       Compute rms phase error at V-poles
C
	NVPOLMAX=2*NP+1
	NDATAY=NVPOLMAX-NSKIP
	JY1=NSKIP/2+1
	JY2=NVPOLMAX-NSKIP/2
	DO J=JY1,JY2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2
	JJ=J-NSKIP/2
	XX(JJ)=IZP
	YY(JJ)=PH(IZP)
	END DO
	CALL FIT(XX,YY,NDATAY,SIG,0,A,B,SIGA,SIGB,CHI2)
c
	DO J=JY1,JY2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2
	PHFIT=A+B*IZP
	PH(IZP)=PH(IZP)-PHFIT
	END DO
C
	PHERRV=0.0
	DO J=JY1,JY2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2
	PHERRV=PHERRV+PH(IZP)*OMEGA0*PH(IZP)*OMEGA0
	END DO
	PHERRV=SQRT(PHERRV/NDATAY)*360/TWOPI
c
c	OPEN(UNIT=4,FILE='pherr_v.dat',STATUS='NEW')
c	DO J=J1,J2
c	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
c	P=PH(IZP)*OMEGA0*360/TWOPI
c	WRITE(4,440)PZ(IZP)*10,P
c440	FORMAT(2(1X,F10.2),1X,I3)
c	END DO
c	CLOSE(4)
C
C       Compute rms phase error at all poles
C
	CALL TRAJECT(0.0,0.0,dum1,dum2,dum3,dum4,dum5,dum6,dum7)
c
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	JJ=J-NSKIP
	XX(JJ)=IZP
	YY(JJ)=PH(IZP)
	END DO
	CALL FIT(XX,YY,NDATA,SIG,0,A,B,SIGA,SIGB,CHI2)
C
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	PHFIT=A+B*IZP
	PH(IZP)=PH(IZP)-PHFIT
	END DO
C
	PHERR1=0.0
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	PHERR1=PHERR1+PH(IZP)*OMEGA0*PH(IZP)*OMEGA0
	END DO
	PHERR1=SQRT(PHERR1/NDATA)*360/TWOPI
C
	OPEN(UNIT=4,FILE='pherr.dat',STATUS='NEW')
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	P=PH(IZP)*OMEGA0*360/TWOPI
	WRITE(4,446)PZ(IZP)*10,P
446	FORMAT(2(1X,F10.2),1X,I3)
	END DO
	CLOSE(4)
C
C	Angle-corrected Phase Error (all poles)
C
	CALL TRAJECT(X1AV,Y1AV,C1,C2,C3,C4,C5,CC5,C6)
c
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	JJ=J-NSKIP
	XX(JJ)=IZP
	YY(JJ)=PH(IZP)
	END DO
	CALL FIT(XX,YY,NDATA,SIG,0,A,B,SIGA,SIGB,CHI2)
C
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	PHFIT=A+B*IZP
	PH(IZP)=PH(IZP)-PHFIT
	END DO
C
	PHERR2=0.0
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	PHERR2=PHERR2+PH(IZP)*OMEGA0*PH(IZP)*OMEGA0
	END DO
	PHERR2=SQRT(PHERR2/NDATA)*360/TWOPI
C
        OPEN(UNIT=1,FILE='traj.dat',STATUS='NEW')
	DO I=0,NSTEP,NN+1
	P=PH2(I)*OMEGA0/TWOPI
	WRITE(1,100)PZ(I)*10,X(I)*10,Y(I)*10,P,X1(I)*1E3,Y1(I)*1E3
	END DO
        CLOSE(1)
C
C	Compute real peaks positions, peak field values, and average period
C
	NPOLMAX=2*NP+1
C
c	open(unit=1,file='peak_y.dat',status='new')
	NDATAY=NPOLMAX-NSKIP
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2
	DO J=J1,J2
	IZP1=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2-1
	IZP2=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2
	IZP3=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2+1
	B1=BY(IZP1)
	B2=BY(IZP2)
	B3=BY(IZP3)
	A0=B2
	A1=(B3-B1)/2/DZ
	A2=(B3+B1-2*B2)/2/DZ/DZ
	IF (A2.NE.0.0) THEN
	ZMAX=-A1/2/A2
	PEAKY(J)=PZ(IZP2)+ZMAX
	ELSE
	ZMAX=0.0
	PEAKY(J)=0.0
	ENDIF
	BCY(J)=A0+A1*ZMAX+A2*ZMAX*ZMAX
c	write(1,*)peaky(j)*10,bcy(j)
	END DO	
	AVPER1Y=0.0
	DO J=J1+1,J2
	AVPER1Y=AVPER1Y+PEAKY(J)-PEAKY(J-1)
	END DO
	AVPER1Y=AVPER1Y/(NDATAY-1)*2
c	close(1)
C
c	open(unit=1,file='peak_x.dat',status='new')
	IF (IPOL.EQ.1) THEN
	NDATAX=NPOLMAX-NSKIP+1
	IOFF=-NSTP/4
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2+1
	ELSE
	NDATAX=NPOLMAX-NSKIP
	IOFF=0
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2
	ENDIF
	DO J=J1,J2
	IZP1=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2-1+IOFF
	IZP2=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2+IOFF
	IZP3=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2+1+IOFF
	B1=BX(IZP1)
	B2=BX(IZP2)
	B3=BX(IZP3)
	A0=B2
	A1=(B3-B1)/2/DZ
	A2=(B3+B1-2*B2)/2/DZ/DZ
	IF (A2.NE.0.0) THEN
	ZMAX=-A1/2/A2
	PEAKX(J)=PZ(IZP2)+ZMAX
	ELSE
	ZMAX=0.0
	PEAKX(J)=0.0
	ENDIF
	BCX(J)=A0+A1*ZMAX+A2*ZMAX*ZMAX
c	write(1,*)peakx(j)*10,bcx(j)
	END DO	
	AVPER1X=0.0
	DO J=J1+1,J2
	AVPER1X=AVPER1X+PEAKX(J)-PEAKX(J-1)
	END DO
	AVPER1X=AVPER1X/(NDATAX-1)*2
c	close(1)
C
C	Compute Z-shift Corrected peak-field Values
C
c	NDATAY=NPOLMAX-NSKIP
c	J1=NSKIP/2+1
c	J2=NPOLMAX-NSKIP/2
c	DO J=J1,J2
c	IZP1=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2-1
c	IZP2=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2
c	IZP3=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2+1
c	B1=BY(IZP1)
c	B2=BY(IZP2)
c	B3=BY(IZP3)
c	A0=B2
c	A1=(B3-B1)/2/DZ
c	A2=(B3+B1-2*B2)/2/DZ/DZ
c	IF (A2.NE.0.0) THEN
c	ZMAX=-A1/2/A2
c	ELSE
c	ZMAX=0.0
c	ENDIF
c	PEAKY(J)=PZ(IZP2)+ZMAX
c	BCY(J)=A0+A1*ZMAX+A2*ZMAX*ZMAX
c	END DO	
C
c	NDATAX=NPOLMAX-NSKIP+1
c	J1=NSKIP/2+1
c	J2=NPOLMAX-NSKIP/2+1
c	DO J=J1,J2
c	IZP1=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2-1-NSTP/4
c	IZP2=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2-NSTP/4
c	IZP3=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2+1-NSTP/4
c	B1=BX(IZP1)
c	B2=BX(IZP2)
c	B3=BX(IZP3)
c	A0=B2
c	A1=(B3-B1)/2/DZ
c	A2=(B3+B1-2*B2)/2/DZ/DZ
c	IF (A2.NE.0.0) THEN
c	ZMAX=-A1/2/A2
c	ELSE
c	ZMAX=0.0
c	ENDIF
c	PEAKX(J)=PZ(IZP2)+ZMAX
c	BCX(J)=A0+A1*ZMAX+A2*ZMAX*ZMAX
c	END DO	
C
C	Compute Z-shift Corrected Average Peak Field and rms field errors
C
	NDATAY=NPOLMAX-NSKIP
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2
	BYAV2=0.0
	DO J=J1,J2
	BYAV2=BYAV2+ABS(BCY(J))
	END DO
	BYAV2=BYAV2/NDATAY
C
	S=0.0
	SS=0.0
	DO J=J1,J2
	ERRY1=ABS(BCY(J))-BYAV2
	S=S+ERRY1
	SS=SS+ERRY1*ERRY1
	END DO
	arg=(SS/NDATAY-S/NDATAY*S/NDATAY)	
	if (arg.gt.0.0) then
	SBPY2=SQRT(SS/NDATAY-S/NDATAY*S/NDATAY)	
	else
	sbpy2=0.0
	endif
C
	IF (IPOL.EQ.1) THEN
	NDATAX=NPOLMAX-NSKIP+1
	IOFF=-NSTP/4
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2+1
	ELSE
	NDATAX=NPOLMAX-NSKIP
	IOFF=0
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2
	ENDIF
	BXAV2=0.0
	DO J=J1,J2
	BXAV2=BXAV2+ABS(BCX(J))
	END DO
	BXAV2=BXAV2/NDATAX
C
	S=0.0
	SS=0.0
	DO J=J1,J2
	ERRX1=ABS(BCX(J))-BXAV2
	S=S+ERRX1
	SS=SS+ERRX1*ERRX1
	END DO
	arg=(SS/NDATAX-S/NDATAX*S/NDATAX)	
	if (arg.gt.0.0) then
	SBPX2=SQRT(SS/NDATAX-S/NDATAX*S/NDATAX)	
	else
	sbpx2=0.0
	endif
C
C	Compute crossing points position and average period
C
	NDATAY=NPOLMAX-NSKIP
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2
	DO J=J1,J2
	IZP1=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2+NSTP/4-1
	IZP2=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2+NSTP/4+1
	B1=BY(IZP1)
	B2=BY(IZP2)
	IF (B1.NE.B2) THEN
	ZERO(J)=PZ(IZP1)-B1*2.0*DZ/(B2-B1)	
	ELSE
	ZERO(J)=PZ(IZP1)
	ENDIF
	END DO
	AVPER2=0.0
	DO J=J1+1,J2
	AVPER2=AVPER2+ZERO(J)-ZERO(J-1)
	END DO
	AVPER2=AVPER2/(NDATAY-1)*2
C
C	Compute average DZ
C
	NDATAY=NPOLMAX-NSKIP
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2
	DELTAZY=0.0
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2
	ZZ=ZMIN+DZ*IZP
	DELTAZY=DELTAZY+(PEAKY(J)-ZZ)
	END DO
	DELTAZY=DELTAZY/NDATAY
C
	IF (IPOL.EQ.1) THEN
	NDATAX=NPOLMAX-NSKIP+1
	IOFF=-NSTP/4
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2+1
	ELSE
	NDATAX=NPOLMAX-NSKIP
	IOFF=0
	J1=NSKIP/2+1
	J2=NPOLMAX-NSKIP/2
	ENDIF
	DELTAZX=0.0
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/2+IOFF
	ZZ=ZMIN+DZ*IZP
	DELTAZX=DELTAZX+(PEAKX(J)-ZZ)
	END DO
	DELTAZX=DELTAZX/NDATAX
C
	call traject(0.0,0.0,c1,c2,c3,c4,c5,cc5,c6)
C
	K1=-NP
	K2=+NP
	NFREQ=400
	WEIGHT=1.0
c
	THETAX=0.0
	THETAY=0.0
	DO J=0,NFREQ
	SPEC(J)=0.0
	SPE1(J)=0.0
	SPE2(J)=0.0
	SPE3(J)=0.0
	spe4(j)=0.0
	spe5(j)=0.0
	END DO
	CALL SPECTRUM(1,K1,K2,NFREQ,THETAX,THETAY,WEIGHT)
	SMAX=0.0
	DO I=0,NFREQ
	IF (SPEC(I).GT.SMAX) THEN
	IMAX=I
	SMAX=SPEC(I)
	ENDIF
	END DO
	XNOM=FLOAT(K1)+FLOAT(K2-K1)/FLOAT(NFREQ)*(IMAX)
	OMP=OMEGA0*(1.0+XNOM/NP)
	PMAX1=HT*OMP/EVTOERG
c	write(6,*)'zero emittance (i=1), zero angle'
c	write(6,*)'peak at ',pmax1,' eV'	
c	write(6,*)'S0 =',spec(imax)*omega0*omega0/4/pi/pi/c/c*4.56e7*cur
	al1=spe1(imax)/spec(imax)
	al2=spe2(imax)/spec(imax)
	al3=spe3(imax)/spec(imax)
c	write(6,*)'L1 =',al1
c	write(6,*)'L2 =',al2
c	write(6,*)'L3 =',al3
C
	THETAX=X1AV
	THETAY=Y1AV
	DO J=0,NFREQ
	SPEC(J)=0.0
	SPE1(J)=0.0
	SPE2(J)=0.0
	SPE3(J)=0.0
	spe4(j)=0.0
	spe5(j)=0.0
	END DO
	CALL SPECTRUM(1,K1,K2,NFREQ,THETAX,THETAY,WEIGHT)
	SMAX=0.0
	DO I=0,NFREQ
	IF (SPEC(I).GT.SMAX) THEN
	IMAX=I
	SMAX=SPEC(I)
	ENDIF
	END DO
	XNOM=FLOAT(K1)+FLOAT(K2-K1)/FLOAT(NFREQ)*(IMAX)
	OMP=OMEGA0*(1.0+XNOM/NP)
	PMAX1=HT*OMP/EVTOERG
c	write(6,*)'zero emittance (i=1), average trajectory angle'
c	write(6,*)'peak at ',pmax1,' eV'	
c	write(6,*)'S0 =',spec(imax)*omega0*omega0/4/pi/pi/c/c*4.56e7*cur
	al1=spe1(imax)/spec(imax)
	al2=spe2(imax)/spec(imax)
	al3=spe3(imax)/spec(imax)
c	write(6,*)'L1 =',al1
c	write(6,*)'L2 =',al2
c	write(6,*)'L3 =',al3
c
	NFREQ=400
	DO J=0,NFREQ
	SPEC(J)=0.0
	SPE1(J)=0.0
	SPE2(J)=0.0
	SPE3(J)=0.0
	spe4(j)=0.0
	spe5(j)=0.0
	END DO
	K1=(IORD1-1)*NP-NP/4
 	K2=(IORD1-1)*NP+NP/4
	CALL SPECTRUM(1,K1,K2,NFREQ,THETAX,THETAY,WEIGHT)
	SMAX=0.0
	DO I=0,NFREQ
	IF (SPEC(I).GT.SMAX) THEN
	IMAX=I
	SMAX=SPEC(I)
	ENDIF
	END DO
	XNOM=FLOAT(K1)+FLOAT(K2-K1)/FLOAT(NFREQ)*(IMAX)
	OMP=OMEGA0*(1.0+XNOM/NP)
	PMAX1=HT*OMP/EVTOERG
c	write(6,*)'zero emittance (i=iord1), average trajectory angle'
c	write(6,*)'peak at ',pmax1,' eV'	
c	write(6,*)'S0 =',
c    $	spec(imax)*omega0*omega0/4/pi/pi/c/c*4.56e7*cur
	al1=spe1(imax)/spec(imax)
	al2=spe2(imax)/spec(imax)
	al3=spe3(imax)/spec(imax)
c	write(6,*)'L1 =',al1
c	write(6,*)'L2 =',al2
c	write(6,*)'L3 =',al3
C
C	Angular distribution at fixed frequency
C
c	IORD=1
c	OPEN(UNIT=11,FILE='ANGDIST_X.DAT',STATUS='NEW')
c	THETAY=0.0
c	THXMAX=AKY/GAM/2
c	thxmax=10.0/GAM
C
c	IF (ENANG.EQ.0.0) THEN
c	OM=OMP*IORD
c	EP=HT*OM/EVTOERG
c	ELSE
c	EP=ENANG
c	OM=EP/HT*EVTOERG
c	ENDIF
C
c	DO IX=0,320
c	THETAX=THXMAX/320*IX
c	CALL ANGDIST(IORD,OM,THETAX,THETAY,SP)
c	SP=SP*OMEGA0*OMEGA0/4/PI/PI/C/C*4.56E7*CUR
c	IF (IX.EQ.0) SSP=SP
c	GT=THETAX*GAM
c	WRITE(11,1234)GT,SP
c1234	FORMAT(10(1X,E10.5))
c	END DO
c	WRITE(11,1234)EP,SSP
c	CLOSE(11)
C
c	OPEN(UNIT=11,FILE='ANGDIST_Y.DAT',STATUS='NEW')
c	THETAX=0.0
C	THYMAX=MAX(AKX/GAM/2.0,1.0/GAM)
c	THYMAX=THXMAX
c	DO IY=0,320
c	THETAY=THYMAX/320*IY
c	CALL ANGDIST(IORD,OM,THETAX,THETAY,SP)
c	SP=SP*OMEGA0*OMEGA0/4/PI/PI/C/C*4.56E7*CUR
c	IF (IX.EQ.0) SSP=SP
c	GT=THETAY*GAM
c	WRITE(11,1234)GT,SP
c	END DO
c	CLOSE(11)
C
c	OPEN(UNIT=11,FILE='ANGDIST_XY.DAT',STATUS='NEW')
c	DO IY=0,320
c	THETAY=THYMAX/320*IY
c	THETAX=THETAY
c	CALL ANGDIST(IORD,OM,THETAX,THETAY,SP)
c	SP=SP*OMEGA0*OMEGA0/4/PI/PI/C/C*4.56E7*CUR
c	IF (IX.EQ.0) SSP=SP
c	GT=GAM*SQRT(THETAX**2+THETAY**2)
c	WRITE(11,1234)GT,SP
c	END DO
c	CLOSE(11)
C
	THETAX=THPINX0
	THETAY=THPINY0
C
	if (iord1.ne.0.and.iord2.ne.0) then
	DO IORD=IORD1,IORD2,2
	DO J=0,NFREQ
	SPEC(J)=0.0
	SPE1(J)=0.0
	SPE2(J)=0.0
	SPE3(J)=0.0
	spe4(j)=0.0
	spe5(j)=0.0
	END DO
	CALL SPECTRUM(IORD,K1,K2,NFREQ,THETAX,THETAY,WEIGHT)
C
	SMAX=0.0
	DO I=0,NFREQ
	IF (SPEC(I).GT.SMAX) THEN
	IMAX=I
	SMAX=SPEC(I)
	ENDIF
	END DO
C
	IF (IMAX.EQ.0) IMAX=1
	IF (IMAX.EQ.NFREQ) IMAX=NFREQ-1
	SS1=SPEC(IMAX-1)
	SS2=SPEC(IMAX)
	SS3=SPEC(IMAX+1)
	A0=SS2
	A1=(SS3-SS1)/2
	A2=(SS3+SS1-2*SS2)/2
	XV=-A1/2/A2
	YV=A0+A1*XV+A2*XV*XV
	SMAX=YV
C
	SMAX1(IORD)=SMAX
	XNOM=FLOAT(K1)+FLOAT(K2-K1)/FLOAT(NFREQ)*(IMAX+XV)
	OMP=OMEGA0*(IORD+XNOM/NP)
	PMAX(IORD)=HT*OMP/EVTOERG
C
	END DO
	endif
C
	if (npoints.ne.0) then
	IORD=1
	K1=(IORD1-1)*NP-NP/4
 	K2=(IORD2-1)*NP+NP/4
	if (iord1.eq.0) k1=-np
	NFREQ=NPOINTS
C
	DO J=0,NFREQ
	SPEC(J)=0.0
	SPE1(J)=0.0
	SPE2(J)=0.0
	SPE3(J)=0.0
	spe4(j)=0.0
	spe5(j)=0.0
	END DO
	CALL SPECTRUM(IORD,K1,K2,NFREQ,THETAX,THETAY,WEIGHT)
C
	IF (IFUZZ.NE.0) THEN
C
	DO J=0,NFREQ
	SPEC(J)=0.0
	SPE1(J)=0.0
	SPE2(J)=0.0
	SPE3(J)=0.0
	spe4(j)=0.0
	spe5(j)=0.0
	END DO
C
C	Emittance
C
c	ELETTRA NATURAL BEAM SIZE AND DIVERGENCE (scaling with E)
c
	SIGX=0.237E-3/2.0*EG*fsx
	SIGY=0.013E-3/2.0*EG*fsy
	SIGX1=0.029E-3/2.0*EG*fsx1
	SIGY1=0.0052E-3/2.0*EG*fsy1
C
	SIGU2=SIGX*SIGX/DIST/DIST+SIGX1*SIGX1
	SIGV2=SIGY*SIGY/DIST/DIST+SIGY1*SIGY1
	SIGU=SQRT(SIGU2)
	SIGV=SQRT(SIGV2)
C
C	Pinhole
C
	THETAX0=THPINX0
	THETAY0=THPINY0
C
	NX2=2*NX+1
	NY2=2*NY+1
C
	CALL FUZZY(THPINX,THPINY,SIGU,SIGV,NX,NY,FP,XMAX,YMAX)
	DTX=XMAX/NX
	DTY=YMAX/NY
C
	DO IX=-NX,NX
	THX(IX+NX+1)=DTX*IX+THETAX0
	END DO
	DO IY=-NY,NY
	THY(IY+NY+1)=DTY*IY+THETAY0
	END DO
	DO IX=-NX,NX
	DO IY=-NY,NY
	FPS(IX+NX+1,IY+NY+1)=FP(IX,IY)	
	END DO
	END DO
C
c	CALL SPLIE2(THX,THY,FPS,NX2,NY2,Y2A)
C
C	UNIFORM THETA GRID
C
	IF (IQUAD.EQ.1) THEN
	IXMIN=-NX
	IYMIN=-NY
	ENDIF
	IF (IQUAD.EQ.2) THEN
	IXMIN=0
	IYMIN=0
	ENDIF
	IXMAX=NX
	IYMAX=NY
	DO IX=IXMIN,IXMAX
	THETAX=THX(IX+NX+1)
c	WRITE(6,67)IX,NX
	DO IY=IYMIN,IYMAX
	THETAY=THY(IY+NY+1)
c	CALL SPLIN2(THX,THY,FPS,Y2A,NX2,NY2,THETAX,THETAY,FF)
c
	IF (THPINX.EQ.0.0.AND.THPINY.EQ.0.0) THEN
	WEIGHT=FP(IX,IY)*DTX*DTY
c	on-axis flux density
	ELSE
	WEIGHT=FP(IX,IY)*DTX*DTY*1E6
C	flux through the pinhole
	ENDIF
	IF 
     *	(IX.EQ.IXMIN.OR.IX.EQ.IXMAX.OR.IY.EQ.IYMIN.OR.IY.EQ.IYMAX)
     *	WEIGHT=WEIGHT/2
C
	IF (IQUAD.EQ.2) WEIGHT=4*WEIGHT
c
c	write(9,*)GAM*thetax,GAM*thetay,fp(ix,iy),FF
C
	CALL SPECTRUM(IORD,K1,K2,NFREQ,THETAX,THETAY,WEIGHT)
C
	END DO
	END DO
C
	ENDIF
C
	SMAX=0.0
	DO I=0,NFREQ
	IF (SPEC(I).GT.SMAX) THEN
	IMAX=I
	SMAX=SPEC(I)
	ENDIF
	END DO
C
	IF (IMAX.EQ.0) IMAX=1
	IF (IMAX.EQ.NFREQ) IMAX=NFREQ-1
	SS1=SPEC(IMAX-1)
	SS2=SPEC(IMAX)
	SS3=SPEC(IMAX+1)
	A0=SS2
	A1=(SS3-SS1)/2
	A2=(SS3+SS1-2*SS2)/2
	XV=-A1/2/A2
	YV=A0+A1*XV+A2*XV*XV
	SMAX=YV
	XNOM=FLOAT(K1)+FLOAT(K2-K1)/FLOAT(NFREQ)*(IMAX+XV)
	OMP=OMEGA0*(1+XNOM/NP)
	EPSP=HT*OMP/EVTOERG
c	write(6,*)'pinhole spectrum'
	yyy=smax*omega0*omega0/4/pi/pi/c/c*4.56e7*cur
c	write(6,*)'peak value=',yyy,' at ',epsp,' eV'	
C
C	Convolution for energy spread
C
C	SIGE= Relative Energy spread (scaling as EG)
C
	SIGE=8E-4*(EG/2.0)*FSIGE
C
	DV=FLOAT(K2-K1)/NFREQ/IORD/NP/2
	IF(DV.GT.(0.2*SIGE)) DV=0.2*SIGE
	NV=(6.0*SIGE/DV)+1.5
	IF(NV.GT.201) STOP
C
	DO J=1,NV
	V=-3.0+((J-1)*DV/SIGE)
	PR(J)=EXP(-V*V/2.0)/(2.506628*SIGE)
	END DO
C
C	Zero Padding
C
	NFREQ2=NFREQ+2*NV
	DO J=1,NV
	SSPEC(J)=0.0
	END DO
	DO J=NV+1,NV+NFREQ
	SSPEC(J)=SPEC(J-NV)
	END DO
	DO J=NV+NFREQ+1,NFREQ2
	SSPEC(J)=0.0
	END DO
C
	DO J=1,NFREQ2
	JJ=J-NV
	XNOM=FLOAT(K1)+FLOAT(K2-K1)/FLOAT(NFREQ)*JJ
	OM=OMEGA0*(1.0+XNOM/NP)
	EPS(J)=HT*OM/EVTOERG
	END DO
C
	CALL SPLINE(EPS,SSPEC,NFREQ2,1.0E30,1.0E30,COEFF)
C
	DO J=1,NFREQ2
	SUM=0.0
	DO JJ=1,NV
	V=(-3.0*SIGE)+((JJ-1)*DV)
	EPS1=EPS(J)/(1+V)/(1+V)
	CALL SPLINT(EPS,SSPEC,COEFF,NFREQ2,EPS1,S)
	SUM=SUM+S*PR(JJ)
	END DO
	SPEC2(J)=SUM*DV
	END DO

	OPEN(UNIT=4,FILE='spec.dat',STATUS='NEW')
C
	p=0.0
	estep=eps(nfreq/2)-eps(nfreq/2-1)
	gmax=0.0
	DO JJ=1,NFREQ
	J=JJ+NV-1	
	XNOM=FLOAT(K1)+FLOAT(K2-K1)/FLOAT(NFREQ)*J
	OM=OMEGA0*(1.0+XNOM/NP)
	XXX=(OM-IORD1*OMEGA0)/OM
	YY2=SPEC(JJ)*OMEGA0*OMEGA0/4/PI/PI/C/C*4.56E7*CUR
	YY3=SPEC2(J)*OMEGA0*OMEGA0/4/PI/PI/C/C*4.56E7*CUR
	f1=spec(jj-1)*omega0*omega0/4/pi/pi/c/c*4.56e7*cur
	f2=spec(jj)*omega0*omega0/4/pi/pi/c/c*4.56e7*cur
	g=(f2-f1)/estep
	if (g.gt.gmax) then
	gmax=g
	jjmax=jj
	endif
	WRITE(4,120)XXX,SPEC(JJ),EPS(J),YY2,YY3,g
	p=p+yy2*estep
	AS1=SPE1(JJ)*OMEGA0*OMEGA0/4/PI/PI/C/C*4.56E7*CUR
	AS2=SPE2(JJ)*OMEGA0*OMEGA0/4/PI/PI/C/C*4.56E7*CUR
	AS3=SPE3(JJ)*OMEGA0*OMEGA0/4/PI/PI/C/C*4.56E7*CUR
	as4=spe4(jj)*omega0*omega0/4/pi/pi/c/c*4.56e7*cur
	as5=spe5(jj)*omega0*omega0/4/pi/pi/c/c*4.56e7*cur
c	WRITE(44,120)EPS(J),AS1,AS2,AS3,as4,as5
	END DO
	f=p
	evtojou=1.602189e-19
	p=p*1000*evtojou
C
	CLOSE(4)
	endif
c
	xnom=float(k1)+float(k2-k1)/float(nfreq)*jjmax
	omp=omega0*(1+xnom/np)
	epsp=ht*omp/evtoerg
	alam=1240/epsp
c	write(6,*)'max gain=',gmax,' at ',alam,' nm'
C	
c	OPEN(UNIT=1,FILE='bxy.cor',STATUS='NEW')
c	DO I=0,NSTEP,NN+1
c	WRITE(1,*)BX(I),BY(I),PZ(I)*10
c	END DO
c	CLOSE(1)
C
C	CORRECT FOR MEASURED DELTA_Z BY INTERPOLATION
C	(only if average deltaz is smaller than 1 mm)
C
	IF (ABS(DELTAZY).LT.1) THEN
	CALL SPLINE(PZ,BY,NSTEP,1.0E30,1.0E30,Y2)
	DO I=1,NSTEP
	ZZY=PZ(I)+DELTAZY
	CALL SPLINT(PZ,BY,Y2,NSTEP,ZZY,B)
	BBY(I)=B
	END DO
	DO i=1,nstep
	by(i)=bby(i)
	END DO
	ENDIF
C
	IF (ABS(DELTAZX).LT.1) THEN
	CALL SPLINE(PZ,BX,NSTEP,1.0E30,1.0E30,Y2)
	DO I=1,NSTEP
	ZZX=PZ(I)+DELTAZX
	CALL SPLINT(PZ,BX,Y2,NSTEP,ZZX,B)
	BBX(I)=B
	END DO
	DO i=1,nstep
	bx(i)=bbx(i)
	END DO
	ENDIF
C
C       Re-compute rms phase error
C
	CALL TRAJECT(0.0,0.0,DUM1,DUM2,DUM3,DUM4,DUM5,DUM6,DUM7)
c
	NPOLMAX=4*NP+1
	J1=NSKIP+1
	J2=NPOLMAX-NSKIP
	NDATA=NPOLMAX-2*NSKIP
c
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	JJ=J-NSKIP
	XX(JJ)=IZP
	YY(JJ)=PH(IZP)
	END DO
	CALL FIT(XX,YY,NDATA,SIG,0,A,B,SIGA,SIGB,CHI2)
C
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	PHFIT=A+B*IZP
	PH(IZP)=PH(IZP)-PHFIT
	END DO
C
	PHERR3=0.0
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	PHERR3=PHERR3+PH(IZP)*OMEGA0*PH(IZP)*OMEGA0
	END DO
	PHERR3=SQRT(PHERR3/NDATA)*360/TWOPI
C
C	Angle-corrected Phase Error
C
	CALL TRAJECT(X1AV,Y1AV,DUM1,DUM2,DUM3,DUM4,DUM5,DUM6,DUM7)
c
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	JJ=J-NSKIP
	XX(JJ)=IZP
	YY(JJ)=PH(IZP)
	END DO
	CALL FIT(XX,YY,NDATA,SIG,0,A,B,SIGA,SIGB,CHI2)
C
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	PHFIT=A+B*IZP
	PH(IZP)=PH(IZP)-PHFIT
	END DO
C
	PHERR4=0.0
	DO J=J1,J2
	IZP=NSTEP/2-NP*NSTP/2+(J-1)*NSTP/4
	PHERR4=PHERR4+PH(IZP)*OMEGA0*PH(IZP)*OMEGA0
	END DO
	PHERR4=SQRT(PHERR4/NDATA)*360/TWOPI
c
c	OPEN(UNIT=7,FILE='BXY.SHF',STATUS='NEW')
c	DO I=0,NSTEP,NN+1
c	WRITE(7,*)BBX(I),BBY(I),PZ(I)*10.0
c	END DO
c	CLOSE(7)
C
c	WRITE(6,*)
c	WRITE(6,*) '******************************************'
c	WRITE(6,91)NP,PERIOD,EG,GAM,CUR
c	WRITE(6,92)NSKIP,NN
c	WRITE(6,93)IFUZZ,SIGX*1E3,SIGY*1E3,SIGX1*1E3,SIGY1*1E3
c	WRITE(6,*)SIGU*1E3,SIGV*1E3
c	WRITE(6,*)' background fields [G] =',bckx,bcky
c	IF (ICORR.EQ.1.OR.IANS.EQ.2) THEN
c	WRITE(6,*)' First integrals calibrated on SW measurements'
c	ENDIF
c	IF (IANS3.EQ.'K'.OR.IANS3.EQ.'k') THEN
c	WRITE(6,*)'Applied Localized Kick Correction'
c	WRITE(6,*)'DELTA IX_IY_START [G m] =',FIX1,FIY1
c	WRITE(6,*)'DELTA IX_IY_END   [G m] =',FIX2,FIY2
c	open(unit=22,file='kicks.dat',status='new')
c	write(22,*)fix1,fiy1,fix2,fiy2
c	close(22)
c	write(6,*)'Field integrals before correction'
c	WRITE(6,*)'I1X [G*m]   =',C3INI*10.0/1e3
c	WRITE(6,*)'I1Y [G*m]   =',C1INI*10.0/1e3
c        WRITE(6,*)'I2,X,0 [G*m^2] =',(C4INI+C3INI*ZMIN)*1E-4
c	WRITE(6,*)'I2,Y,0 [G*m^2] =',(C2INI+C1INI*ZMIN)*1E-4
c        WRITE(6,*)'I2,X,0 [micron] =',(C4INI+C3INI*ZMIN)*const*1e4
c	WRITE(6,*)'I2,Y,0 [micron] =',-(C2INI+C1INI*ZMIN)*const*1e4
c	ENDIF
c	IF (IANS3.EQ.'C'.OR.IANS3.EQ.'c') THEN
c	WRITE(6,*)'Applied Coils (length=30 cm) Correction'
c	WRITE(6,*)'DELTA IX_IY_START [G m] =',FIX1,FIY1
c	WRITE(6,*)'DELTA IX_IY_END   [G m] =',FIX2,FIY2
c	open(unit=22,file='kicks.dat',status='new')
c	write(22,*)fix1,fiy1,fix2,fiy2
c	close(22)
c	write(6,*)'Field integrals before correction'
c	WRITE(6,*)'I1X [G*m]   =',C3INI*10.0/1e3
c	WRITE(6,*)'I1Y [G*m]   =',C1INI*10.0/1e3
c        WRITE(6,*)'I2,X,0 [G*m^2] =',(C4INI+C3INI*ZMIN)*1E-4
c	WRITE(6,*)'I2,Y,0 [G*m^2] =',(C2INI+C1INI*ZMIN)*1E-4
c        WRITE(6,*)'I2,X,0 [micron] =',(C4INI+C3INI*ZMIN)*const*1e4
c	WRITE(6,*)'I2,Y,0 [micron] =',-(C2INI+C1INI*ZMIN)*const*1e4
c	ENDIF
c	WRITE(6,*) '******************************************'
c66	FORMAT(1X,I3,4X,1PE8.2,3(4X,0PF8.2))
c	WRITE(6,*)'Av. peak BX    [G] =',BXAV
c	WRITE(6,*)'Av. peak BY    [G] =',BYAV
c	WRITE(6,90)'Deflection Par. Kx =',AKX
c	WRITE(6,90)'Deflection Par. Ky =',AKY
c	WRITE(6,90)'Sigma_BX  [G]  =',SBPX
c	WRITE(6,90)'Sigma_BY  [G]  =',SBPY
c	BAV=SQRT(BXAV*BXAV+BYAV*BYAV)
c	WRITE(6,90)'Sigma_BX  [%]  =',SBPX/BAV*100
c	WRITE(6,90)'Sigma_BY  [%]  =',SBPY/BAV*100
c	WRITE(6,*)
c	WRITE(6,90)'Phase Error (V-POLES)       [deg] =',PHERRV
c	WRITE(6,90)'Phase Error (ALL POLES)     [deg] =',PHERR1
c	WRITE(6,94)'Angles (hor/vert)                 =',X1AV*1E6,
c    $	Y1AV*1E6
c	WRITE(6,90)'Angle corrected Phase Error [deg] =',PHERR2
cc	WRITE(6,*)
c	WRITE(6,90)'Average DZ (mm)_Bx          =',deltazx*10
c	WRITE(6,90)'Average DZ (mm)_By          =',deltazy*10
c	WRITE(6,90)'Corrected BX0  [G]          =',BXAV2
c	WRITE(6,90)'Corrected BY0  [G]          =',BYAV2
c	BAV2=SQRT(BXAV2*BXAV2+BYAV2*BYAV2)
c	WRITE(6,90)'Corrected Sigma_BX [G]      =',SBPX2
c	WRITE(6,90)'Corrected Sigma_BX [%]      =',SBPX2/BAV2*100
c	WRITE(6,90)'Corrected Sigma_BY [G]      =',SBPY2
c	WRITE(6,90)'Corrected Sigma_BY [%]      =',SBPY2/BAV2*100
c	WRITE(6,*)
c	WRITE(6,90)'Phase Error (ALL POLES)     [deg] =',PHERR3
c	WRITE(6,90)'Angle corrected Phase Error [deg] =',PHERR4
c	WRITE(6,*)
c	WRITE(6,*)'I1X [G*m]   =',C3*10.0/1e3
c	WRITE(6,*)'I1Y [G*m]   =',C1*10.0/1e3
c        WRITE(6,*)'I2,X,0 [G*m^2] =',(C4+C3*ZMIN)*1E-4
cc	WRITE(6,*)'I2,Y,0 [G*m^2] =',(C2+C1*ZMIN)*1E-4
c        WRITE(6,*)'I2,X,0 [micron] =',(C4+C3*ZMIN)*const*1e4
c	WRITE(6,*)'I2,Y,0 [micron] =',-(C2+C1*ZMIN)*const*1e4
C	WRITE(6,*)'INTEGRAL BX*BX DZ (G^2 mm) =',CC5*10
C	WRITE(6,*)'INTEGRAL BY*BY DZ (G^2 mm) =',C5*10
c	bxeff=sqrt((2*cc5*10)/(np*period*10))
c	byeff=sqrt((2*c5*10)/(np*period*10))
c	ptot=633*eg*eg*(bxeff*bxeff+byeff*byeff)/1e8*np*period/100*cur
c	write(6,*)'power (W) =',ptot
c	write(6,*)'flux within computed spectal range  =',f,
c c    $	' [phot/s or phot/s/mrad^2]'
c	write(6,*)'power within computed spectal range =',p,
c     $	' [W or W/mrad^2]'
c	write(6,*)'--> Effective Bx field (G)    =',bxeff
c	write(6,*)'--> Effective By field (G)    =',byeff
C	WRITE(6,*)'INTEGRAL BX*BY DZ (G^2 mm) =',C6*10
c	WRITE(6,*)'Average period from Bx peaks =',AVPER1X
c	WRITE(6,*)'Average period from By peaks =',AVPER1Y
c	WRITE(6,*)'Average period from By c.pts =',AVPER2
C	write(6,*)'--- Fourier Coefficients ---'
C	do k=1,9
C	write(6,666)k,cak(k),cak(k)/cak(1)*100
C	end do
C	write(6,667)sumcak
c	WRITE(6,*) '******************************************'
C	WRITE(6,*)
	STOP
C	------------------------------------------------------
67	FORMAT(4X,4X,I3,' / ',I3)
70      FORMAT(1X,A25,F6.2,/)
72      FORMAT(1X,'A_',I1,' = ',F6.3,' +- ',F6.3)
80      FORMAT(/,1X,'B0 =',F8.4,4X,'K =',F8.4)
81      FORMAT(1X,'Final X =',F10.7,4X,'Final X1 =',F10.7)
82      FORMAT(1X,'Smax =',F12.8,4X,'iN D_omega/omega =',f8.4)
90      FORMAT(1X,A25,1X,F16.6)
91	FORMAT(1X,' NP = ',I3,12X,' PERIOD (cm) = ',F6.3,/,
     $	'  EG = ',F4.2,' (',F6.0,')',2X,' I (A) = ',F4.2)
92	FORMAT(1X,' NSKIP = ',I2,'  Int. points = ',I2)
93	FORMAT
     $	(1X,' IFUZZ = ',I1,' Sig_x,y (mm)     = ',F5.3,' , ',
     $	F5.3,/,10X,' Sig_x1,y1 (mrad) = ',F5.3,' , ',F5.3)
94      FORMAT(1X,A25,1X,F6.1,2X,F6.1)
100     FORMAT(1X,7(F12.6,1X))
110     FORMAT(1X,F12.6,1X,I3)
120     FORMAT(1X,7(E10.4,1X))
666	format(1x,i2,5x,f9.2,2x,'(',f5.1,'%)')
667	format(1x,'sumBk',1x,f9.2)
999     FORMAT(3(1X,F12.6))
C	------------------------------------------------------
	END
C
C	------------------------------------------
	SUBROUTINE MFIELD(BXPEAK,BYPEAK,BCKX,BCKY)
C	------------------------------------------
	COMMON/CALC1/NP,NSTEP,NSTP,DZ,NPOLMAX,ZMIN,PERIOD
	COMMON/MFLD/BMX(0:49999),BMY(0:49999)
	COMMON/FLD/BX(0:49999),BY(0:49999)
	COMMON/ZPOS/ PZ(0:49999)
	COMMON/DHP/ANGX,ANGY
	CHARACTER*1 IANS
C
C	Reads measured undulator field 
C
c        WRITE(*,*)'READING MEASURED FIELD DISTRIBUTION'
c        WRITE(*,*)'CORRENTING FOR PROBE ANGLES: ',ANGX,ANGY
	OPEN(UNIT=1,FILE='bxy.dat',STATUS='OLD')
	I=0
	BXPEAK=0.0
	BYPEAK=0.0
1       READ(1,*,END=2)B1,B2,Z
	IF (ABS(B1).GT.BXPEAK) BXPEAK=ABS(B1)
	IF (ABS(B2).GT.BYPEAK) BYPEAK=ABS(B2)
	IF (I.EQ.0) THEN
	ZMIN=Z
	ENDIF
	IF (I.EQ.1) THEN
	DZ=(Z-ZMIN)/10
c	WRITE(6,*)'DZ =',DZ
	ENDIF
 	BMX(I)=B1-B2*TAN(ANGX)
	BMY(I)=B2-B1*TAN(ANGY)
	PZ(I)=Z/10.0
	I=I+1
	GOTO 1
2       NSTEP=I-1
	ZMIN=ZMIN/10
	ANSTP=PERIOD/DZ
	IANS='Y'
	IF (IANS.EQ.'N'.OR.IANS.EQ.'n') STOP
	NSTP=INT(ANSTP+0.5)
	IANS='Y'
	IF (IANS.EQ.'N'.OR.IANS.EQ.'n') STOP
	DZ=PERIOD/NSTP
c	Write(6,*)'NSTEP=',NSTEP,' DZ=',DZ
	if (mod(i,2).eq.0) then
c	write (6,*)'*** error: even number of points in data file ***'
	stop
	endif
C
	CLOSE(1)
c
c	subtract background fields
c
	bckx=(bmx(0)+bmx(nstep))/2
	bcky=(bmy(0)+bmy(nstep))/2
c	do i=0,nstep
c	bmx(i)=bmx(i)-bckx
c	bmy(i)=bmy(i)-bcky
c	end do
C
C
	RETURN
66      FORMAT(1X,'NSTP =',F8.4,'    OK [Y/N] ?')
67      FORMAT(1X,'NSTP =',I4,'    OK [Y/N] ?')
68      FORMAT(A1)
	END
C
C	--------------------------
	SUBROUTINE INTERPOLATE(NN)
C	--------------------------
	COMMON/CALC1/NP,NSTEP,NSTP,DZ,NPOLMAX,ZMIN,PERIOD
	COMMON/MFLD/BMX(0:49999),BMY(0:49999)
	COMMON/FLD/BX(0:49999),BY(0:49999)
	COMMON/ZPOS/ PZ(0:49999)
	DIMENSION Y2(49999),PZZ(0:49999)
C
	IF (NN.EQ.0) THEN

	DO I=0,NSTEP
	BX(I)=BMX(I)
	BY(I)=BMY(I)
	END DO

	ELSE

	BX(0)=BMX(0)
	BY(0)=BMY(0)
	PZZ(0)=PZ(0)
	I=1
C
	CALL SPLINE(PZ,BMX,NSTEP,1.0E30,1.0E30,Y2)
	DO I=1,NSTEP
	BX((NN+1)*I)=BMX(I)
	DO JJ=1,NN
	ZZ=PZ(I-1)+JJ*DZ/(NN+1)
	CALL SPLINT(PZ,BMX,Y2,NSTEP,ZZ,B)
	BX((NN+1)*(I-1)+JJ)=B
	END DO
	END DO
C
	CALL SPLINE(PZ,BMY,NSTEP,1.0E30,1.0E30,Y2)
	DO I=1,NSTEP
	BY((NN+1)*I)=BMY(I)
	PZZ((NN+1)*I)=PZ(I)
	DO JJ=1,NN
	ZZ=PZ(I-1)+JJ*DZ/(NN+1)
	CALL SPLINT(PZ,BMY,Y2,NSTEP,ZZ,B)
	BY((NN+1)*(I-1)+JJ)=B
	PZZ((NN+1)*(I-1)+JJ)=ZZ
	END DO
	END DO
C
	NSTEP=(NN+1)*NSTEP
	NSTP=(NN+1)*NSTP
	DZ=DZ/(NN+1)

	DO I=0,NSTEP
	PZ(I)=PZZ(I)
	END DO

	ENDIF
C
	RETURN
	END
C
C	---------------------------------------------------
	SUBROUTINE TRAJECT(thetax,thetay,C1,C2,C3,C4,C5,CC5,C6)
C	---------------------------------------------------
	COMMON/CALC1/NP,NSTEP,NSTP,DZ,NPOLMAX,ZMIN,PERIOD
	COMMON/CALC2/CONST,OMEGA0,GAM,TWOC
	COMMON/FLD/BX(0:49999),BY(0:49999)
	COMMON/TRJ/X(0:49999),Y(0:49999),X1(0:49999),Y1(0:49999)
	COMMON/ZPOS/ PZ(0:49999)
	COMMON/PHS/ PH(0:49999),PH2(0:49999)
C
        XX1=0.0
        XX=0.0
	BA=BY(0)
        X1A=0.0
        X1(0)=X1A
c
        DO I=1,NSTEP
	DELTAZ=PZ(I)-PZ(I-1)
	BZ=BY(I)
        XX1=XX1-CONST*(BA+BZ)/2.0*DELTAZ
        X1Z=XX1
        XX=XX+(X1A+X1Z)/2.0*DELTAZ
        X(I)=XX
        X1(I)=XX1
        BA=BZ
        X1A=X1Z
        END DO
	XF=XX
	X1F=XX1
C
        YY1=0.0
        YY=0.0
	BA=BX(0)
        Y1A=0.0
	Y1(0)=Y1A
        DO I=1,NSTEP
	DELTAZ=PZ(I)-PZ(I-1)
	BZ=BX(I)
        YY1=YY1+CONST*(BA+BZ)/2.0*DELTAZ
        Y1Z=YY1
        YY=YY+(Y1A+Y1Z)/2.0*DELTAZ
        Y(I)=YY
        Y1(I)=YY1
        BA=BZ
        Y1A=Y1Z
        END DO
        YF=YY
	Y1F=YY1
C
	WX=0.0
        WXA=0.0
	WY=0.0
        WYA=0.0
	PH(0)=0.0
	DO I=1,NSTEP
	DELTAZ=PZ(I)-PZ(I-1)
	WXZ=(X1(I)-thetax)**2
	WYZ=(Y1(I)-thetay)**2
	WX=WX+(WXA+WXZ)/2*DELTAZ
	WY=WY+(WYA+WYZ)/2*DELTAZ
	PH(I)=(WX+WY)/TWOC
        PH2(I)=(I*DZ/GAM/GAM/TWOC+PH(I))
	WXA=WXZ
	WYA=WYZ
        END DO
C
C	Compute first and second field integrals
C
	C1=0.0
	C2=0.0
	C3=0.0
	C4=0.0
	C5=0.0
	CC5=0.0
	C6=0.0
	DO JJ=1,NSTEP
	DELTAZ=PZ(JJ)-PZ(JJ-1)
	C1=C1+(BY(JJ)+BY(JJ-1))/2*DELTAZ
	C3=C3+(BX(JJ)+BX(JJ-1))/2*DELTAZ
	C2=C2+C1*DELTAZ
        C4=C4+C3*DELTAZ
	C5=C5+BY(JJ)*BY(JJ)*DELTAZ
	CC5=CC5+BX(JJ)*BX(JJ)*DELTAZ
	C6=C6+BX(JJ)*BY(JJ)*DELTAZ
	END DO
C
	RETURN
	END
C
C	-------------------------------------------------------
        SUBROUTINE SPECTRUM(IORD,K1,K2,NFREQ,THETAX,THETAY,WGH)
C	-------------------------------------------------------
	COMMON/CALC1/NP,NSTEP,NSTP,DZ,NPOLMAX,ZMIN,PERIOD
	COMMON/CALC2/CONST,OMEGA0,GAM,TWOC
	COMMON/TRJ/X(0:49999),Y(0:49999),X1(0:49999),Y1(0:49999)
	COMMON/SPC/SPEC(0:20000),SPEC2(20000),SSPEC(20000)
	COMMON/SPC2/SPE1(0:20000),SPE2(0:20000),SPE3(0:20000),
     $	SPE4(0:20000),SPE5(0:20000)
C
	DIMENSION SA(0:49999),CA(0:49999)
	DIMENSION VX1(0:49999),VY1(0:49999)
	COMMON PHASE(0:49999)
C		
C	Write(6,*)'<Spectrum>',iord
c
        OMEGAI=IORD*OMEGA0
        AKREF=FLOAT(K1+K2)/2.0
        OMREF=OMEGAI*(1.0+AKREF/IORD/NP)
        SMAX=0.0
C		
	W=0
        WA=0
	VX1(0)=X1(0)-THETAX
	VY1(0)=Y1(0)-THETAY
	PHASE(0)=0.0
	DO I=1,NSTEP
	VX1(I)=X1(I)-THETAX
	VY1(I)=Y1(I)-THETAY
	WZ=VX1(I)**2+VY1(I)**2
	W=W+(WA+WZ)/2*DZ
        PHASE(I)=(I*DZ/GAM/GAM/TWOC+W/TWOC)
	WA=WZ
        END DO
C
        DO J=0,NFREQ
	XNOM=FLOAT(K1)+FLOAT(K2-K1)/FLOAT(NFREQ)*J
	OM=OMEGA0*(1.0+XNOM/NP)
C
	AX=0.0
	AY=0.0
	BX=0.0
	BY=0.0
        DO I=1,NSTEP
        CA(I)=COS(OM*PHASE(I))
        SA(I)=SIN(OM*PHASE(I))
	AX=AX+VX1(I)*CA(I)
	bx=bx+VX1(I)*SA(I)
	ay=ay+VY1(I)*CA(I)
	BY=BY+VY1(I)*SA(I)
        END DO
        AX=AX*DZ
        AY=AY*DZ
        BX=BX*DZ
        BY=BY*DZ
        S=(OM/OMEGA0)*(OM/OMEGA0)*(AX*AX+bx*bx+ay*ay+BY*BY)
        S1=(OM/OMEGA0)*(OM/OMEGA0)*(AX*AX+bx*bx-ay*ay-BY*BY)
        S2=(OM/OMEGA0)*(OM/OMEGA0)*2*(AX*ay+bx*BY)
        S3=(OM/OMEGA0)*(OM/OMEGA0)*2*(bx*ay-AX*BY)
        sx=(om/omega0)*(om/omega0)*(ax*ax+bx*bx)
        sy=(om/omega0)*(om/omega0)*(ay*ay+by*by)
c
        SPEC(J)=SPEC(J)+S*WGH
        SPE1(J)=SPE1(J)+S1*WGH
        SPE2(J)=SPE2(J)+S2*WGH
        SPE3(J)=SPE3(J)+S3*WGH
        spe4(j)=spe4(j)+sx*wgh
        spe5(j)=spe5(j)+sy*wgh
C
	END DO
	RETURN
	END
C
C     ----------------------------------------------------
      SUBROUTINE FIT(X,Y,NDATA,SIG,MWT,A,B,SIGA,SIGB,CHI2)
C     ----------------------------------------------------
      DIMENSION X(NDATA),Y(NDATA),SIG(NDATA)
      SX=0.
      SY=0.
      ST2=0.
      B=0.
      IF(MWT.NE.0) THEN
        SS=0.
        DO 11 I=1,NDATA
          WT=1./(SIG(I)**2)
          SS=SS+WT
          SX=SX+X(I)*WT
          SY=SY+Y(I)*WT
11      CONTINUE
      ELSE
        DO 12 I=1,NDATA
          SX=SX+X(I)
          SY=SY+Y(I)
12      CONTINUE
        SS=FLOAT(NDATA)
      ENDIF
      SXOSS=SX/SS
      IF(MWT.NE.0) THEN
        DO 13 I=1,NDATA
          T=(X(I)-SXOSS)/SIG(I)
          ST2=ST2+T*T
          B=B+T*Y(I)/SIG(I)
13      CONTINUE
      ELSE
        DO 14 I=1,NDATA
          T=X(I)-SXOSS
          ST2=ST2+T*T
          B=B+T*Y(I)
14      CONTINUE
      ENDIF
      B=B/ST2
      A=(SY-SX*B)/SS
      SIGA=SQRT((1.+SX*SX/(SS*ST2))/SS)
      SIGB=SQRT(1./ST2)
      CHI2=0.
      IF(MWT.EQ.0) THEN
        DO 15 I=1,NDATA
          CHI2=CHI2+(Y(I)-A-B*X(I))**2
15      CONTINUE
        Q=1.
        SIGDAT=SQRT(CHI2/(NDATA-2))
        SIGA=SIGA*SIGDAT
        SIGB=SIGB*SIGDAT
      ELSE
        DO 16 I=1,NDATA
          CHI2=CHI2+((Y(I)-A-B*X(I))/SIG(I))**2
16      CONTINUE
      ENDIF
      RETURN
      END
C
C	-------------------------------------------------------
	SUBROUTINE FUZZY(GTHETAX,GTHETAY,GSIGX1,GSIGY1,NX,NY,C,
     $	GTHXMAX,GTHYMAX)
C	-------------------------------------------------------
	DIMENSION C(-200:200,-200:200)
	PI=ACOS(-1.0)
	TWOPI=2.0*PI
c	write(6,*)'Computing Fuzzy Pinhole distribution..'
C
	if (gsigx1.eq.0.0.and.gsigy1.eq.0.0) then
c	write(6,*)'ZERO EMITTANCE + PINHOLE'
c
	gthxmax=gthetax
	gthymax=gthetay
c
	do ix=-nx,nx
	do iy=-ny,ny
	c(ix,iy)=1.0
	end do
	end do
	return
c
	else if (gthetax.eq.0.0.and.gthetay.eq.0.0) then
c
c	write(6,*)'NON-ZERO EMITTANCE , ON-AXIS'
	gthxmax=3*gsigx1
	gthymax=3*gsigy1
	fact=1.0/twopi/gsigx1/gsigy1	
	dgthx1=gthxmax/nx
	dgthy1=gthymax/ny
c
	SUM=0.0
	do ix=-nx,nx
	do iy=-ny,ny
	gthx1=dgthx1*ix
	gthy1=dgthy1*iy
	fx=exp(-gthx1*gthx1/2.0/gsigx1/gsigx1)
	fy=exp(-gthy1*gthy1/2.0/gsigy1/gsigy1)
	c(ix,iy)=fx*fy*fact
	SUM=SUM+C(IX,IY)*DGTHX1*DGTHY1
	end do
	end do
c
c	WRITE(6,*)'TOTAL PROBABILITY =',SUM
c
	return
c
	else
c
c	write(6,*)'NON-ZERO EMITTANCE + PINHOLE'
	GTHXMAX=GTHETAX+3*GSIGX1
	GTHYMAX=GTHETAY+3*GSIGY1
	FACT=1.0/TWOPI/GSIGX1/GSIGY1	
C
	DGTHX=GTHXMAX/NX
	DGTHY=GTHYMAX/NY
C
	DELX=MIN(GTHETAX,GSIGX1)/8
	DELY=MIN(GTHETAY,GSIGY1)/8
	NNX=INT(GTHXMAX/DELX)
	NNY=INT(GTHYMAX/DELY)
C
	DO IX=-NX,NX
	DO IY=-NY,NY
	C(IX,IY)=0.0
	END DO
	END DO
C
	DGTHX1=GTHXMAX/NNX
	DGTHY1=GTHYMAX/NNY
C
	SUM=0.0
	DO IX=-NX,NX
c	write(6,*)IX,'       /',NX
	DO IY=-NY,NY
	GTHX=DGTHX*IX
	GTHY=DGTHY*IY
C
	DO JX=-NNX,NNX
	GTHX1=DGTHX1*JX
	DO JY=-NNY,NNY
	GTHY1=DGTHY1*JY
	FX=EXP(-(GTHX1-GTHX)*(GTHX1-GTHX)/2.0/GSIGX1/GSIGX1)
	FY=EXP(-(GTHY1-GTHY)*(GTHY1-GTHY)/2.0/GSIGY1/GSIGY1)
C
	IF (ABS(GTHX1).LE.(GTHETAX).AND.ABS(GTHY1).LE.(GTHETAY)) THEN
	C(IX,IY)=C(IX,IY)+FX*FY*FACT
	ENDIF
C
	END DO
	END DO
C
	END DO	
	END DO	
C
	SUM=0
	DO IX=-NX,NX
	DO IY=-NY,NY
	C(IX,IY)=C(IX,IY)*DGTHX1*DGTHY1
C
	SUM=SUM+C(IX,IY)*DGTHX*DGTHY
	END DO
	END DO
c	WRITE(6,*)'NNX , NNY =',NNX,NNY
c	WRITE(6,*)'CENTRAL VALUE     =',C(0,0)
	SUM=SUM/2/GTHETAX/2/GTHETAY
c	WRITE(6,*)'TOTAL PROBABILITY =',SUM
C
	endif
c
	RETURN	
	END
c
C     -------------------------------------
      SUBROUTINE SPLIE2(X1A,X2A,YA,M,N,Y2A)
C     -------------------------------------
      PARAMETER (NN=401)
      DIMENSION X1A(M),X2A(N),YA(M,N),Y2A(M,N),YTMP(NN),Y2TMP(NN)
      DO 13 J=1,M
        DO 11 K=1,N
          YTMP(K)=YA(J,K)
11      CONTINUE
        CALL SPLINE(X2A,YTMP,N,1.E30,1.E30,Y2TMP)
        DO 12 K=1,N
          Y2A(J,K)=Y2TMP(K)
12      CONTINUE
13    CONTINUE
      RETURN
      END
c
C     ---------------------------------------------
      SUBROUTINE SPLIN2(X1A,X2A,YA,Y2A,M,N,X1,X2,Y)
C     ---------------------------------------------
      PARAMETER (NN=401)
      DIMENSION X1A(M),X2A(N),YA(M,N),Y2A(M,N),YTMP(NN),Y2TMP(NN),
     $YYTMP(NN)
      DO 12 J=1,M
        DO 11 K=1,N
          YTMP(K)=YA(J,K)
          Y2TMP(K)=Y2A(J,K)
11      CONTINUE
        CALL SPLINT(X2A,YTMP,Y2TMP,N,X2,YYTMP(J))
12    CONTINUE
      CALL SPLINE(X1A,YYTMP,M,1.E30,1.E30,Y2TMP)
      CALL SPLINT(X1A,YYTMP,Y2TMP,M,X1,Y)
      RETURN
      END
C
C     -----------------------------------
      SUBROUTINE SPLINE(X,Y,N,YP1,YPN,Y2)
C     -----------------------------------
      PARAMETER (NMAX=49999)
      DIMENSION X(N),Y(N),Y2(N),U(NMAX)
      IF (YP1.GT..99E30) THEN
        Y2(1)=0.
        U(1)=0.
      ELSE
        Y2(1)=-0.5
        U(1)=(3./(X(2)-X(1)))*((Y(2)-Y(1))/(X(2)-X(1))-YP1)
      ENDIF
      DO 11 I=2,N-1
        SIG=(X(I)-X(I-1))/(X(I+1)-X(I-1))
        P=SIG*Y2(I-1)+2.
        Y2(I)=(SIG-1.)/P
        U(I)=(6.*((Y(I+1)-Y(I))/(X(I+1)-X(I))-(Y(I)-Y(I-1))
     *      /(X(I)-X(I-1)))/(X(I+1)-X(I-1))-SIG*U(I-1))/P
11    CONTINUE
      IF (YPN.GT..99E30) THEN
        QN=0.
        UN=0.
      ELSE
        QN=0.5
        UN=(3./(X(N)-X(N-1)))*(YPN-(Y(N)-Y(N-1))/(X(N)-X(N-1)))
      ENDIF
      Y2(N)=(UN-QN*U(N-1))/(QN*Y2(N-1)+1.)
      DO 12 K=N-1,1,-1
        Y2(K)=Y2(K)*Y2(K+1)+U(K)
12    CONTINUE
      RETURN
      END
C
C     ----------------------------------
      SUBROUTINE SPLINT(XA,YA,Y2A,N,X,Y)
C     ----------------------------------
      DIMENSION XA(N),YA(N),Y2A(N)
      KLO=1
      KHI=N
1     IF (KHI-KLO.GT.1) THEN
        K=(KHI+KLO)/2
        IF(XA(K).GT.X)THEN
          KHI=K
        ELSE
          KLO=K
        ENDIF
      GOTO 1
      ENDIF
      H=XA(KHI)-XA(KLO)
      IF (H.EQ.0.) PAUSE 'Bad XA input.'
      A=(XA(KHI)-X)/H
      B=(X-XA(KLO))/H
      Y=A*YA(KLO)+B*YA(KHI)+
     *      ((A**3-A)*Y2A(KLO)+(B**3-B)*Y2A(KHI))*(H**2)/6.
      RETURN
      END
C
C	-------------------------------------------
        SUBROUTINE ANGDIST(IORD,OM,THETAX,THETAY,S)
C	-------------------------------------------
	COMMON/CALC1/NP,NSTEP,NSTP,DZ,NPOLMAX,ZMIN,PERIOD
	COMMON/CALC2/CONST,OMEGA0,GAM,TWOC
	COMMON/TRJ/X(0:49999),Y(0:49999),X1(0:49999),Y1(0:49999)
	COMMON/SPC/SPEC(0:20000),SPEC2(20000),SSPEC(20000)
	COMMON/SPC2/SPE1(0:20000),SPE2(0:20000),SPE3(0:20000),
     $	SPE4(0:20000),SPE5(0:20000)
C
	DIMENSION SA(0:49999),CA(0:49999)
	DIMENSION VX1(0:49999),VY1(0:49999)
	COMMON PHASE(0:49999)
C		
C	Write(6,*)'<Spectrum>',iord
C		
	W=0
        WA=0
	VX1(0)=X1(0)-THETAX
	VY1(0)=Y1(0)-THETAY
	PHASE(0)=0.0
	DO I=1,NSTEP
	VX1(I)=X1(I)-THETAX
	VY1(I)=Y1(I)-THETAY
	WZ=VX1(I)**2+VY1(I)**2
	W=W+(WA+WZ)/2*DZ
        PHASE(I)=(I*DZ/GAM/GAM/TWOC+W/TWOC)
	WA=WZ
        END DO
C
	AX=0.0
	AY=0.0
	BX=0.0
	BY=0.0
        DO I=1,NSTEP
        CA(I)=COS(OM*PHASE(I))
        SA(I)=SIN(OM*PHASE(I))
	AX=AX+VX1(I)*CA(I)
	AY=AY+VX1(I)*SA(I)
	BX=BX+VY1(I)*CA(I)
	BY=BY+VY1(I)*SA(I)
        END DO
        AX=AX*DZ
        AY=AY*DZ
        BX=BX*DZ
        BY=BY*DZ
        S=(OM/OMEGA0)*(OM/OMEGA0)*(AX*AX+AY*AY+BX*BX+BY*BY)
        S1=(OM/OMEGA0)*(OM/OMEGA0)*(AX*AX+AY*AY-BX*BX-BY*BY)
        S2=(OM/OMEGA0)*(OM/OMEGA0)*2*(AX*BX+AY*BY)
        S3=(OM/OMEGA0)*(OM/OMEGA0)*2*(AY*BX-AX*BY)
C
	RETURN
	END
