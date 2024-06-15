#!/usr/bin/env python
#
# Hi There!
#
# You may be wondering what this giant blob of binary data here is, you might
# even be worried that we're up to something nefarious (good for you for being
# paranoid!). This is a base85 encoding of a zip file, this zip file contains
# an entire copy of pip (version 24.0).
#
# Pip is a thing that installs packages, pip itself is a package that someone
# might want to install, especially if they're looking to run this get-pip.py
# script. Pip has a lot of code to deal with the security of installing
# packages, various edge cases on various platforms, and other such sort of
# "tribal knowledge" that has been encoded in its code base. Because of this
# we basically include an entire copy of pip inside this blob. We do this
# because the alternatives are attempt to implement a "minipip" that probably
# doesn't do things correctly and has weird edge cases, or compress pip itself
# down into a single file.
#
# If you're wondering how this is created, it is generated using
# `scripts/generate.py` in https://github.com/pypa/get-pip.

import sys

this_python = sys.version_info[:2]
min_version = (3, 7)
if this_python < min_version:
    message_parts = [
        "This script does not work on Python {}.{}".format(*this_python),
        "The minimum supported Python version is {}.{}.".format(*min_version),
        "Please use https://bootstrap.pypa.io/pip/{}.{}/get-pip.py instead.".format(*this_python),
    ]
    print("ERROR: " + " ".join(message_parts))
    sys.exit(1)


import os.path
import pkgutil
import shutil
import tempfile
import argparse
import importlib
from base64 import b85decode


def include_setuptools(args):
    """
    Install setuptools only if absent and not excluded.
    """
    cli = not args.no_setuptools
    env = not os.environ.get("PIP_NO_SETUPTOOLS")
    absent = not importlib.util.find_spec("setuptools")
    return cli and env and absent


def include_wheel(args):
    """
    Install wheel only if absent and not excluded.
    """
    cli = not args.no_wheel
    env = not os.environ.get("PIP_NO_WHEEL")
    absent = not importlib.util.find_spec("wheel")
    return cli and env and absent


def determine_pip_install_arguments():
    pre_parser = argparse.ArgumentParser()
    pre_parser.add_argument("--no-setuptools", action="store_true")
    pre_parser.add_argument("--no-wheel", action="store_true")
    pre, args = pre_parser.parse_known_args()

    args.append("pip")

    if include_setuptools(pre):
        args.append("setuptools")

    if include_wheel(pre):
        args.append("wheel")

    return ["install", "--upgrade", "--force-reinstall"] + args


def monkeypatch_for_cert(tmpdir):
    """Patches `pip install` to provide default certificate with the lowest priority.

    This ensures that the bundled certificates are used unless the user specifies a
    custom cert via any of pip's option passing mechanisms (config, env-var, CLI).

    A monkeypatch is the easiest way to achieve this, without messing too much with
    the rest of pip's internals.
    """
    from pip._internal.commands.install import InstallCommand

    # We want to be using the internal certificates.
    cert_path = os.path.join(tmpdir, "cacert.pem")
    with open(cert_path, "wb") as cert:
        cert.write(pkgutil.get_data("pip._vendor.certifi", "cacert.pem"))

    install_parse_args = InstallCommand.parse_args

    def cert_parse_args(self, args):
        if not self.parser.get_default_values().cert:
            # There are no user provided cert -- force use of bundled cert
            self.parser.defaults["cert"] = cert_path  # calculated above
        return install_parse_args(self, args)

    InstallCommand.parse_args = cert_parse_args


def bootstrap(tmpdir):
    monkeypatch_for_cert(tmpdir)

    # Execute the included pip and use it to install the latest pip and
    # setuptools from PyPI
    from pip._internal.cli.main import main as pip_entry_point
    args = determine_pip_install_arguments()
    sys.exit(pip_entry_point(args))


def main():
    tmpdir = None
    try:
        # Create a temporary working directory
        tmpdir = tempfile.mkdtemp()

        # Unpack the zipfile into the temporary directory
        pip_zip = os.path.join(tmpdir, "pip.zip")
        with open(pip_zip, "wb") as fp:
            fp.write(b85decode(DATA.replace(b"\n", b"")))

        # Add the zipfile to sys.path so that we can import it
        sys.path.insert(0, pip_zip)

        # Run the bootstrap
        bootstrap(tmpdir=tmpdir)
    finally:
        # Clean up our temporary working directory
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


DATA = b"""
P)h>@6aWAK2ml36Ls(GPCgAn}003hF000jF003}la4%n9X>MtBUtcb8c|B0UO2j}6z0X&KUUXrd5m`_
R3SI<3)PuKWDYI?b2HKe+NnQH)PIu{sK*;0e<?&jMBj}tcbU<T@tnf*qTlh{&G5Eols`^8gyi^suK=H
7%_k}U0!4^hO;ns5}<(0o*&iA5xIAr!$47h>2SD>J!fm}sV{PrY}+lK{4&R6jE^8qmoGmPkiLK_(-K{
(EkDBTFeQ-C@Ki35VvOi9I>v*3HC`lg}FduUKS4YCD6gkCjC>0C$JPe)tF(WN<gmo*)UOepSg_xxm6X
Xn{2kz|IgR(E#NENL+)&nae9)~u=%`;?F`Rv2~Sa0SoFY|KAUO9KQH0000800mA%Sa0{Q*SrA$09FG4
01p5F0B~t=FJE76VQFq(UoLQYT~bSL+b|5i`&SU@!Oq~iIS)&L9d|8u8wNv=>6nNu38Ea&`}HFgyJ@G
B9{e8sD4K$g2|O2c-|@;t@dR%;`5Qu6f^i+#IYx8|79X$VF3?d#n|xfMkA8wQAoLVDffU76;J#O)CYU
tTKs|(rtOUt}xq0efX64y=-}wYe4gv+Rewsv@!47DzwFn{pMIm#X%sAFClIW>99{f@Za2e3a^UYte1H
%y3G<XNkQ|9}&5xy4m@b>HUTlK2Lp_T}m3nsgC)$#bX09kug6MU#nM~&r24-0~c2yu2!TgU+z6-O~;x
-O@YkJ|0dA=sY-F^F})aITrzTyS?O7N5T~%P_vE*{#XPt(tDzVC+>eZ42i!91eGvPx8>ysJFuZiRYzl
Cqu4no3L)R_c2M{&P)haML0zYtRpKw0?HZ~t=E9}0<93*a^reKp2wsiXosq<ZDnF1d&EGAaqKtH_neS
PAHxCm8ml!jzxyu~m0X`+&pMkth|PEP|9MZ~c>Fv#$q{3!PIV@d3Fa6TvSqmUyJeY&DcVg-E}?LbjUB
1cn%!C6%kRp-;$05^P^$8se4pYUP)h>@6aWAK2ml36Ls)(XC6&+u005)~000#L003}la4%n9aA|NYa&
>NQWpZC%E^v8$RKafBFbuu>D>(Ns8*sg%9WWqRh5<#2_0nWXdKkJwP;9!<W=pOlXEBQY`$#)Z+Mt^bi
6oPckB`p|!*H_2tnmoAm6<PF@N4BDGj$85fLhfF{84nLK|-#I0xfC}s5i<QUC}-bf+eREszjiFEi24H
I#8aD33x-%uCYkS()aL{$s3B!q<-&VMQK%Stf#b%l7ZB_GdM3j_BFyV41yE*@a`vc)i!9IGMb21we)J
GO66O~)|mYUhneSRRpUDJS?kwyJl_YGm@-lj40T$^;FqRW#G$aJA`IWuY2601AIopk8!?}JzrCJM7BG
hBB7skF5Cl0E0}tW6jduHZ1aJbrt#JhEK^uz!(6WSRHH2xH{xV8OT}BLrv9JM>cgQASRWPM=z*f32cc
b%r_zXvEMm@4r4q?$c5^J(mKI(3Hg|D>g=Lxw%nv$Wmo4RYi?)7<khREV$qbxoDGJblFi7L^n<O@VzF
MEEAXPmqWIpQ4evHD%i(qFOWYw{KtO@`~N0gc<w?g9#wq#u%@Rt>udNh0m#wx6=aN-9l2Z_Ro?XWMA9
H4R6bM>&GY$FuXGn|A-aRI9X-8F?LTJ9uy={rXDj9PL|)#-&tcJp|{<vi*-DgW2^=ET*^f%gI8_r_&{
wXcrj`|3dKlBSg&e&r0bW%v62d!OoGQ*wgx<XVQ=TYZq1_HJo=B?8kxvgsU-&9F|1_MN^hsAOYq%zA>
7%UfKur-Qgc*<wY(Wvf<qrLh?>HdS!&2r5PvKKj7lj;6b<a!0Eu|?pTxif!4tv)E)BMNtp>m#|ekt4j
DT_oIx_OH%T5Txb;+NMvKmp{|Fng{JXM3Ft!jdrrw2Me+dyL5MD~nZx5M?Vn~!z+L2>~pw9(=_ax0;p
K|=}I~N9>@lyH~{Y}(~nJ`9IW&E;$EIpwS`SH>=)ZAZCO9KQH0000800mA%Sk1@4HNXG>03HDV01N;C
0B~t=FK~G-ba`-PWF?NVPQ@?`MfZNi-B_Ob4-5=!Z$M%;t!XVKc9b}U{5?(?Egj!;iWEo#VY8e`cO+3
psdiM#D?U$24DrcGE{QX%^A1rwho7bo%%^4nEOe11`ih5ds}r~C4-D(by*bnzy~VhcmspFPs+92he4i
Km495?R6(6IB9*bzqWO6Z``e?dj4>$ei>cuLo8^bh>J0qwmAsn45g@9MQ{TAMQ=}M~B1K+Woqz5;+g_
LK&{q3XhT~awQHE!$j2T)4`1QY-O00;mDPD5BBwV5F}0RR940ssIR0001RX>c!JX>N37a&BR4FJE72Z
fSI1UoLQYby2}e#Xt<a?^lH9r3Kwy1oeR)Jw5c|P2{n!P20eBcS%yEe{WiSiU;?y!!S%Hlb-Vgx)e$S
&{Q%j97yyMo{LgWAv)Kul0wBFDJimXepZTd)*oXYoVx%@q$?iGtEyp|Md5_dh8VFk)MrKrY1tUi4BuK
mpdJh&SGC!EjMR=WhEgyI1U-+*Jxtjwr`*jE#k+Nu|2xz<*P-bGr7G|sd#KKPysm4#it^iA4fpVr6V`
C`V5xQQz}{}Rdl|{L5-5y<{BEf&GvwGoo0H^-AT3i-0Ua&a6c!L`BCcyP_Q;r8%dy#!dbfc`vj|;BUo
oIV4OZSI2qKKCMfOcIkdE`ow|Q#HQbJ>GHzYEnG&k3GxBeV(`~SO#$E3WJZ0zrCK6ovXzoIbe%;|^RD
yrQlP)h>@6aWAK2ml36Ls$$Rh+|s}0009h000^Q003}la4%nJZggdGZeeUMVs&Y3WM5@&b}n#v)mlq)
<G2yN>sMeohb0q|`#7akqa^dt?6@-VxMn<?Y^hXSiiAdtDUu72wzV$*_jES^5+Et>Y$})4!4knnqaR;
C0NC@qmt9fjY+c<JqOOj-YFQ_F&i1ung{;f8E$WKpohYi$Oy-4b*$!vG<HGa2#iBSiwP;ycfBuYP`mv
VgSCh7fve=nNS+u<Wed?)Ne&61Sv{~#$ePmf(mOR6iCDR1&Ma~7!Ul&=cXxdZ5`?uF3&G;_OZmwape~
%&?f}gI|$*Z^PSO2)U{2^o)Ef?vo<RN<p8inkAgNvnQ$Ubs-yzUx&hs;9use)Gv#k47!IJxCjUW+*6q
Am7?S>f&g@=d845GqB>#Df3Q6@sIQd$~UhV^2-J<wBwx^sFD%;~<lHktF+~<VnI(iNi@*XXHPNcTs`r
plO_yMJ&NY6)-dN>xNf}9-NzF`1KP$^EPP!BjDgrJ#>Qi4>CJ|YIBT^yiN18O>I6o-=|&KCVYURVq*=
=@#@;5l(Fn~ji@s&d)czIER$jQ{M42on<Otpj}>@+4PMFGTAV_Lui<TSQ&hPGyzgBwEf)+vGt7aU-)k
pwa11>5OI)eZH#E3dVDP}pm5HJl)P6@}ev(w_5nLK977MTt12g4a<EKj|TM@DyeFrT1tHSAqpu2&wt%
mW2=x|`GL>0X4M8*6RW(N$^N!eE`wqv}M97l1btW3d>$(7*y;$BUo#X-BGO%h-7avxG?59?pn6<4JAL
5dg&Kr8%mUr3Olfj4hbSaf(rc!A*oJih0_IwZyl*#s`1T~U$eR(ftMGf_0Hbg2N4NF{+xn@>~sXf@9Y
%Es0xhUlsaGerW<^+`|ASE&i<?+4z3`7r2MTZ5ipH26;0)u}x|yz+aVb*)M?Fb=#}d*CeVga9y?rwF-
YmO|t#i0SpA00c{wg!P=1VtjydsIqe<TYxxDcT-CR({LHe)5O$@pxB5`-?HvR#<hz;^Y{wBeLHmokhh
==+;TqvccR!zPQXo7x0*p*NHnk?4E}$nG`Xugs4j=Jfy{z)WPRj-6Q!ZnTm=uPQ{)_U{S`;RqA|NbbE
U1tGfO3y@(xUxR%jx6&vFXZ@)Y-!8sp$9Ur87&Z0y%E-pib4b<XvB_6_qA^f9@FizJDglh+3w0rDgv6
(m@|bWlqL2q+m8a1JUIHI+MN$dwGAWCw0LDXsB6M!U^5B(h!CvON%DRbzmqpRM%j2j5tk*AIS1({@#Q
n-(RajTrdAI0mzVNx}OqEDA7Snc!&)(Au4>(dXZPs}1yl3?#v~;+U4juRsa0%IZDZ68t4y{J^q@RHiN
388ir)H`2wkAYmC0Lvc=ZU&S}3A{$DU{Lk6<-?ADC;+-Hq#HBg0y8<Gvqe@~kw3yh&v}|cxGPcND9f&
toeOF;59t(`_0~#SD@5lp!yZX9CBU4-hI_(vyB^XNtm;sZq9fyE`kOft8=J((qG!4$#ZQ}qTWDXLxHq
0LY=NQ;AdJ~27DTPw@pwtX<+sq&P%uh|B)f4v6ens$+EUj{OOe<6fe(O#VG_f)b+Dzvtm5QK*G?IG8*
?KZlMEc6Sa*MK$wRq(e=J@5Oi+8V+_2rLXk+R-lh$TwGe0424lL7jokf^FcCbgPNzo()Y!r~j6Lg*WN
{--V~-v~!TAw$X_2%PC?XdFjF`<{v^sAnGHw@fj=7|Mxsy0Xb7b*PkI(D&OBnJH~&$;j6vJqjT>wvs&
eOQ7~$JH)qX*&#jyD`uwx#gxl)UrjR=IGCAXWQ(D<w`Q1OOXX+mRVUl}2>C{3%(k|}KLS`u06dEu04>
%A03AF+iLJqH4rPNX0{GI5dO^V8Y$iSvTjvw~*gyDIL-Q$Act~gYS(i;Sh2Mi8r0=pEnICA6H&|UqR6
P-<K5E_l@w`DScdnKzGe)Oc2ZMJ2PF_J-ge14}x^^G^#Ty`syNZ3|3b$`!O2qEc_%S=W7&<O+$dmv-r
jFR3eg_#cRa0=AIH7vR-T;PRhmec9(Qb^C8zD1NE<){PJegUG0($JUL_a6GLxrDYtj%&ep{D{sgjBV7
>jx7WJEK0>nEFaQE@w5Tx|QZRexq|0T&%TL*6-<pdJS8u*=6P{z%1#gDkytECGsZ*3ude|<vC~P&Fsq
b(q4Wtb#@xW(wPE>AvV-DGSY;@R0X3nhV(>$832BS2C~XS23};4)N~sPQ~3<)o~ay$EpMO2D2eHwp6A
m!4ysJrJc}r(+Z^HsbsxL&ixD{W;#`CV@g7SV6c7vPEBhg2M%<NK3)}?)yA|NLaX#M*=nR(Lay$?KA3
Zp%u*@zI54r=v&Qe!z<nvTrzIt)}7OV2rPuFkXUtYfd^l|;+<HhxQ7$b^-#p8emlRumiX=jnT%oB&mX
s}W14wMLIP3$^YR|=}3h9Z_tS+u4hk-Q143f0i=(}bLx`nLm_Wvs5r({U1im|}q>Ub10TRa^);;SBlM
piAa`=ba@y$Gz8Pw8rDOd(t?%r<T$I&M=YRX9*r1F8edT4IcAtUPAU*-)Ec#w_A4tbVe4vOFCk`vl-i
`lA3S^*@(v5R4A~bgQ*dt_;nBygA0$+AGHS>HhPX6@t*N@Q#XFU+%z`az1MX9M$g4QvtM|ye|F&6O=2
HNj68vd70|Al6Ig0l2g|4<E8J0!53j<0pS>N#gY2Ystn7QNfpT~gF-Xq)5<2?v0m;(rXnnmq;gG}cQp
i4eK*F&WmzEYQ-1?nmgHvpQ`rl^OxM{Ej8^0?QKi2^&-%Shr=y243D%EP{{cfFH;q}Dcl$y>1&m7G9<
2-IZA)Y~r1bn6T9Aka(1EZjmb^h(^DN{k7v48Qep;GdD$az`OmM6v$btzepx?k9WLf_rOi~Cl<E*de3
?PHbM$6zi~OC7bHpvo!gTiA)`!12V6JUgUSA&<0;;CLm$WW%#!Uu0^fnL@8T7#~w{gXg`H*kYK`o*5s
8*Rj@v`wt%R!wl&?2J;0Ta0425eDacRWmc$AO#UkHtY+6?7DB7Wv^AX*6s1Ax`Smn@u}3)XoF@f?B??
JV29EG?C3BS#noEo`y7r-&7$mLO-g_|GJg!y`HoM1ZlQN&jzKr*8GS{}lDH;&qOf*9Z%twmCjudtz9M
6W-LBv__nyf$;_a|b8CaQwD7<qH??|-hB>{U%iNkVs{?9+#Le;Xf*T1$n-%R>g&>pqpkhtfqC7yw%5L
c=QYZpL(y{y?M-29i`J>X1?0ZS=4IH2lP)9_#H)G1X@stI;9PX1vDGciDZjI-#K3i4n*C$^u<D-p)H(
I=)dBA2qR0TNppnn+Lb`QFaeUOAXxIH%bF{j84$-&oHdJsK0}7ZIK;0v|ahoS3NB>UKtpHNACN7Vq|H
K;{Hc;q~i1VsLVaMI^k(me`(`d(NfWU<7wNBT3auQiqCjL74@M!rKswtla4v`3#G6(=Sg+8G{fl*TC+
%9fkoy5$Kv4ZHPoFW7L4_NkC*MY{2jmLr5~{8!$sul^~+B`xR6F0nnOS@y0tn7Ec|L`m|!jxb!iShac
h){6P<ll<;gsbQlXkF)de86DGEEW%QPG<5=_O@yQN8*JaY;aMIQU}h-)l(Q$qjldkKmic{4j4njCuih
^-dTLi$Dtu*HM7tPp-s(Pt*lZiUG?cyXL`qC`t*3k+kn4~Nki7ik-8yr=*L2GY&9+wHVrqxK^qDs-Af
{@rprtyrTKBAOo2tO#b|IpV<3T5ejET{t0%Y0d~%Wl`OrTm}&EmEhRZibqHn5uFzjkF8~A<a?-PYw>M
GC&7sc4*v#gO&TF7FvqX0)5mL;5cl<6f|=851fDbj(0Oy5F!;I9vGZFTfHE>swm3sJextRs^ReYQ@~3
W^@%Y6{t}d>UkJm3QU%z<w{&JnXT7S5P29|EU{9xFf_vh2*UrYSGcQIUEKVaH^^yqk56S&Ha{*hxE!z
lbTzOwpwgq9n&FEU&0J@*RTzMRqmOgU(2R{DEN;Mip4JcZ-v);DXH_4{UgyXKDvg8shk1@sqD-Owp_M
4Kr}N_4-5_#MyuUDs>){|dk31a3n9M>}Y7704hIEBs%OFVXgo-4u(ofW7=>-Ci7<lGf$<T8LV}KK{Q@
O9KQH0000800mA%Sb3BpWef}e0D>q002TlM0B~t=FJEbHbY*gGVQepBVPj}zE^v9>T5XTp#u5ImU$Iq
SgeqiSVmNLqKt&zr9J}yK5IgXP!+}_dD`|Zcm*J8pD@Ff%pP5~fOOd)<nx+jZ7_zu8v-3XBEN?oUK9l
R660c=0w`#BQYBHTpClkFdOj(JYw7X2Nn#YgU<jwEQY_~e!Hjl<mHl^8%LRPdx_~GyH=q9RTf#uEk)B
HFW-{^HU7q7I%_uHb<CYRa7lhH+-+^Re^Wn9Shjij^UN^WgK;l13>h0ZHg7Nx>>lFPm7kKC%#g6Lfo>
q=)W$+gT)uGcctKPe^`GQ)(yV5~l^6*JrJdzs&2Px@h}RQ6nFinosJ+?!NoHcoY^)>TrMSwr9(9{Hin
?%0*-{H9s|3cv4IdLTxcwanGnVirBF)V@f-QL9!wJ9bP76VWtglN+6<_B<8H(rSY|AgK(=H<^%^s8TE
&cZs*Edc|W=!YWRZ*<|we`<LIoe3ShB-P<?Go2RcYv3_bwjSVrm9Q<*Ts*Om<9l`9niqZvp&y}spxxm
-;Og#K6{a8!{KJel1RaKX{kQkJ!ObNS_j~+c1W`iLjLEcs#WAb*|VR0s%6{q#Suu%%C5GJ`%N4tDq*6
=K=3Rz01#V(`id^#7?#dJ0oDz|m15^2|3^U4|1E8X!vfMR!gWMh@DVWeov>!-6>yi=c2y;Zh~poqyjl
hz83$ySo5kYWYV<Qgu@^AAN)np>SJ3!kO%O})i5MmDAtsjQ@6YmwX736ok7|9iKCOui8Bv9&a&BCS;T
%~Nr6uG__mhrM-`B#~9wW*$-iTdesvCie`pGV1~cp2h9HSvv*x6`UkDRYyjEV`F1-oLF1P8nsj1Mmjp
~wk-SG>HL6Scv<4+*&88vWj*txkOfB&Gfvruyy&{)9-@D%$d9p!G($h29$ATfZ7Z=-Ewdku&Q&T7y4r
Q@w3?&OXX1kr2bqI_5nGijc#sk@7Zm*%sx6*yN?m$O!r|uP0E?RZ^Qzeyko!n1l<FaEB$NH{{VQ;^mh
`N_q2BH&ZQp`POe3rj!3fQq7jH_r<s9G9lX==5x0WT?S(%#THP*WVeZZE}A{76RDVU!wSd$d_3CWK=N
kjgh?KZt}t2l5e+=aGmd$Jdw-A;!yoh^E2U-fBSQ(9?821nX@)kMXy<?I~cX}EgY5+0=y8uw+s&gxW!
RY$lww3i>@mL%a`=lJDo5m}-&bU+BMur`HquB5Z<;YyJaQ(;p$sCDkQs&$rf`r2$%304GW`hZNT3RF0
%v&LDxIKnh}dpd>?FBZ9}h>Ihse5Gi0S?Aa>Kk*Ca6fR>iwdUZpVmZtnQJ_~k)74Q>ZH@y1yQ(Ve;^J
ZpiRx91#TUh~kQXQ)7uwod*^56t`pc7{hh0rit2!IxbTG&%XSRBw2fO_^<=c+kOD81-BFJ%gvMpTVrj
YzR%Y=(MR$Ci#@IGPnUT3ll=vlR{OVSH6HIiXPnHfeVa$h}}!<3bykNUJjp@H92rji*Ls0z$Q(0}M2y
V{COA@ws|HH*ayb5OUmt!EeOjkcFJh%Z!K%I%?pbQYvKLE@4aYl$zUiy-1DsNjFgu<Evoo}I~XIqI0_
s4Ga;Anq{<_1}`y!m-KcB*t>CJf;Y!WmuH;_8*8bN>VPlv9H!#vk;%Xm7qt51=OCu>m+LO*Oe3PYVqi
L?!~-%w0PV-JYGEM9-b_&uRCddS!Ys%dV|PA;Z?&*Gw+~f;;^T~mtFnjG6YZ@lp$<MkPuxR1KX4wPl_
Nc=nCl=@n)9T2(x34Za*P<>8=8Ssm|eWKA5EBdJ5M`h-^e(vygaK#=&1iKWF1dM6J5!e8!CZu^puRVh
HrwswH%NYK4YRGQp6y(Q@A+MEZm%vCZ=wrTF2|P})^cVvx&1gBh6>sS!GFO!abKWZXch^s+2X*`ycGT
+{<HU8W73B+z;2B28z+D5YBjj74x;r3q!;h4UaZMSh9*Di9xvYbi5OI{{H;C?;7D8BKknnlpC@;z071
ejf$`E&=6y0T0i(pK3hPeWz)TdlUw}5r5A*?CYx~f}LxfgSVR+?2wND+h=G${<B~;0H6N__X@<~NNu-
&?MqC>>5q`v>u|BmkAgrH0|bVQz9$GzYl#uQU`2u&%$(1;z~h0+I69cjBixS91I=Z|+)%Eriy$o#nVq
gs?b|_=0F!4&vWQ}^j7=0XIJWI8$hq)vbm+9mAe^Sgtm)DlT6w)+VTc+q$5RJSO<qaBDasEWSuUggM8
Cf5yp%Fvo$DWK6^qMw8;khDhgXP|Q}Yx0IP$W_r|3vmBXtLtNoNfRYakW&d=Y;U$1zPpL~u(>DqieuE
S=#PMRa8yNDYcb{Ur^PJeIPyYu>3+dWAs`b%}aSIAf(StWv~k8ff1)cFq^6r{m!EJstZ83v$@$_0GYU
10ZIjK6a_`2yQASXaDi0s$T(och@gdK{<ZMp6|Vw4CfmYZbF9}e4Y>6t*B2MUAUu$e*BLiH2M9c-3}K
J_6SNV%uC+cJ9eyA_S3?dV!s^TUPa-8&PL7^pfi7C=6>@PP~Nk23um%BAk0a5ugYV8fIiNpm+mSm>dv
0^R=Rt&(aW?UNlFDeuT^itftwR0@NqF8C;qTJ2gC*kxQnYeRjYa%4QA;xeYr(rN3k1ba`C{WXZ(kFMK
PU@Z%&PJ{q9~?9F+<RD3E(Wh$6PsXb~vCuyr4x#?40w1(qD0&w4H%enR<&D`xjrISJvE+{Q-KkCNF?y
`PD%IZ1LQ3mRJ2uU^P<y}MA=`hHAwt{TgN8sMS9#!c8`8|6P$pOQW0m_Gaep61)Q`Z?v!1}UKv=pG3n
nV$*gC0#vqINNrodODP+qTsqV>LuEa|A78%)?v5H0$3t|Zl_o-L~*Bcu2Qc{#d%RzpQHF5a=vahr3C!
w-)kPvBfK$0$4RWc*<SW9wfn9>7u(C;Eq8qR-HXfD$%hx0m#>m%PoKTG>>F^KnH3PiG1>Dwlhj=gw@U
(R4v=M^G1m3TrSE0lX3(Cbzod*2FtHWgc8QfSnJ-Ky>S2hm>^Fxz(QU_c_t0PDF6V<H*}lP`%ND+jZP
vS`N%ztt@hv628j4z8;tg^=PtBkg&IK3Z^u0i@(;TH6yWS<bPgx2i0XwY(G2NRd^e$jLX`DG2u8ee{K
2;H4n4vB#r**Y?_~+>`m5vs^%jUfj6^`>2=^)D-#DA_PX;(&l94T@u&$%E?2W2XHU}tBF%ebiL3k@6b
d`28CGmZP7?*TuQvKV9=hS!6v!X1Ycgs34SkGXJsPpH>#%rbLu(r-(-R+}2ZjA+9H(j@dh4<NasQ+;J
;RWdd1jnFv*>q_nNadUmWF*Wr84%S-cFWe60m$v#XUa_2eWs<n$-P|G#8t$|ESoC(^X|n&7y|J%A0}j
vLG4)P!to^Dp1L^K{=I^4BAWOMW4sPUvVUN^%$nNBz-fdk-5&k=T^%4S(ld)iL+yRotLLpQC3(d7#yQ
+G9<|eFL(cH-Y{M{HbV@r&*7IWJj=2{>LbQuh8Tp!Lf4$}5B#7KcfUSj7|rOd)NvYzqK4oLBBcYYE?{
rW%>Er+c@sP5(YexR@LW&bfmK7ng_?tE6vdX5};QK$UK?U)BD@vqa*NqiE*{}&QJmzg~gnKpH=xBq4<
6sh%Ip-)QNkVAboWtybG(3t@aafLhTSCP4B=XJg@iw^RP)E8g+L#)<Siu*ycUy8@>gkmAhJD}EYhpe8
NI!oEKbo?onYG3QR=qF4SpKJX;(B+$~s14wkX69Cvhf>o^kLp~TABg`8uvKpX9BZr(fB*KIw+ns=*r{
FpSZjEuf5V)Q?7HjiZUI1b@#Pm^J$X#QfIPOP+sacKt)I}J5YWv`&pByu$Sr;DV=Vei-#QD?A4m)h^n
fmSdp9u6@w{Q&a!mGtjUAfAzf9jKU`I)R6D3ylR`6|xI|l(-*3Rqrb@w@UV5002p&vB2+Dhc=AYcm+I
O7`h=`?wMO?PK{cFDj5<4b2_St4fEU0C+%RK|rc|FP6*YxFNrO9KQH0000800mA%Shx=DdDIX90Jb&&
03HAU0B~t=FJEbHbY*gGVQepBZ*FF3XLWL6bZKvHE^v9xTWxRK$PxaoU$MvF5D6zUO<NQ_0cz_zJ2~S
VJFt`76^6j0#g)Z|A_*>KM>X8v-e+ca$z77NeL+9e2x5ucot^i$9S1@1W09}Yn{5@>X_1RfoX0nEBlB
7)S#QhH=(5;IQOjzR=0#TA>}I0_k;fZ365>#ayDF_~nTs?RO9muXX(m;OMYnObrB$Ekw}_Q0mT6qeMB
JtITErU2f%q(USagOjfUvnvbGss~Un(H6WW2`aLrA+O482O@ye2G!O7ojcio2ppL?YF)N&)6Z+^uB=)
YsCWW@*HU2aKF3<Fpb>I(k(Vn^6!1qfxpki>fwT%D7Upvd^+&8E4XdE0q1Dc4|ZbM7=BNVDtDe-%Z6)
x~!+-1PqL?GdUHfslxX&dG}#g;_G=yD8<=SeAt$Nt>Khu8AfT2O?VZ`FH6bGl!ZJ7*+O`dJFcptn)aW
+fjE9Fwpnsk)IZ46B2Hv79ZiPL+16>+91)jgl2&T(x)8!D<JvC&<>c(>{Flr9%b_|q4sUK`eTpaG?cN
=mR4wgtnX7FjBVaVe=j~=Rx`^*Io$pyhV(v*S?7kK+#N`^0)^VPUeopfQ8;lUf0eugqLe<q|H2U%U?9
IvB=!e70<Fmte$5<B-c4?jlB3)TRh0K)HZ|K}$bbR(HqV<>2$=kE@i{m5Ocq=Of831;$mRSkydLceQA
3x(jC5n}=n2K~28XH$K9O)%<rdEsl<K^+iJlKL7zym!WiLT31F4I-I<P~pE&wn^Pod-8raUExR)#Xmr
awC386Ul2XPd*&a1C`cNzrXsFR`oW{7UDR+O{*ej+xNhNw0R)&TfKqh_5S32WEl14<n-7si#{D*@KV@
U<t%qWe<H($DJUr6`KRNHi<6_{==|d7_yW{2)uE<iYQ7QO_A_B`KjS>-BON{Zba;Al6rG+Q9!2M8r~h
mKx*&Yu1aLIUSQW9nQOj`@k*A3wXat0IcK+dbCf>!nYbhWBb}9wi<QEawH5|^i#?wONMYV~u^xu-a3_
*Y^Oyo*L%?pM*rvGNFapK@_^n1oUga>*Tf0o8Ol6olk3u0R(Z{jKe+gNW@v8|R;jHScaqGI1WAumR-7
{Z)?!TRn%(<H29nZ-+}d_+2V5KMR_)S6eRI<9I(&UYLf;HAc?1MBLKvjqvZ$g`a&E4c#WvI3S3ekk5h
A#hZ=_U|K2eUd5!0J(wOBQT~zKKaBed|AvaIzbqKl{JMGUfLic$<0Mzt3sFpM&srUv+rlQ6G<TzZwB}
37!Z<zf*BkGM;{we;0Q=Yp$I$>tKhw?)^VxCuGoq@gc$6BU`gsPwPA(#gww-IU<cX6$=_QDljc(ur`X
YV(PNK-Nta=vDzmg6gZ`;_Ju&QqRz{wuh&afOnRygouE>K;TRs{_YIMz3y$3A2YH%!62p7H%|5c><m_
AKK$NNph3Tj2KNE9X}gycOeRC+KbKWKDmG2&nD5;_>?dZ!^|hNL{{m;RXyAcMXycaMSSks-g75Gpyya
qypDGHn(xdVS{|(&Khj2Mzr~Ba_R!$1t&cp`#tX7`E&o&<Op$Ip1|pvmx0{J4?xT&BRrg)r;;r@_ty?
=jgOcnA!ROy<285SYLk|7xfd^OuFPGi``fjYBhLY6}N~y3f3k#yszMW$eiNk5*9!S0ofq~qAz};W>QI
p^kJPUp^?HO1lC%?`?Syx-=DxMBO$5bKa~h<zDUU)8CC#qv&(c0#52X`s=BBohh3em_OjFzi4cIbK(=
`Te}@fP%Z)Fwrv)yuaR#re*nnbSE<F}-ZVHp4qpu5`L?2w&WRI{%Q&vFk7AkfN?8q8(A!D^8ZfZf$Q5
#`^4sep;8Q3C;>sZqdV1%qf@Jg4+JdBVvCG5SCnWc3UAqUS^Q>-pB;?N9;7f4()<dhLbgISZ!vOii-i
dE#2y%c?Dy|~(z9F7{ulTq^yX4*g`%*d0|ZpOTQW1>SR;?F!^zSjqPtC-%m3=T?=CPo!VZtZagLaix_
7DxaH8R+}{Ll6?j<GK%zVIsn6|FDV6F(NN=*ABXqNpGkBr2R&`4=wA#S^Lpn&>}o<k#BkXLi`|?F@>@
_N>F4e>MCA-CTeuCgvU4FM57>F7I`N`I>A=6Uf|&ZhQiNObh7Wof^^~Dqs-KA@JkD3wfRmm^|Qie*Fy
&pt>GRX{E;z0?e*B9_YYrr=%z@J7t5q&!;`dA$X&G7L}Fn}8n6qP9aU(mYrT|14;VC?gp&f=%&$e4b-
;}w<B4l%IcG+WV)^#tz;I59z%^wp)}|)}JgSRGCdghI>KcF0CU=I+3yyx;^>RpMce_q+)>75*b7@hf^
{#Cz7`j~wDWR<DuHHKy1NL_&b@m3URl20X_gJ5(9}~ieJV9$Db+zlb5gn;DH;7m*dm@+BVK<&!{bA9j
s9dg#6GVzH>~0335rQoX5yCgB<(q96xO&AJJ;+19pP@vSqJl_Z3ZVu&5#)RjIdY<uS)OqppaJIb*gay
@!CLcxV3S;{ojt)<21dq23n14f`k=w1;H^Y_wf>eHDBZ{vx=27LZm4{qx{kX>`bR(MR#<pCd8SNTdak
gmCrK0)19E&J+M<Tp3gl2Y!YIWCQI!gY)i%=wi?9U?^&gNMZ^~@f0T!GU2#d=#Q4=&lJmy+6)*hMYOj
Z7}wy!zfFN+Pre-i3))Pve9yF8vS8}>!Wm5UFe-@WDiL*NKo?Gg4=%XCHpA9i!^*l-%*4<#+0=$|2DE
lblWTF19CYP^D*Uktj9=Ix5$PDN>(N{<=6m$R51j{E8QQr5AlEv1KL(@_e;C1Q<%Z_~G7i#50q2Br_T
j#Xriwk_0&j~M-!#c`7K7LNwjLF{9X9wToDe>X&5`Mh4Rk%0xaLG13>#MS2rINLZo_5|Xn-ZtN-e8UR
&k=8$7-@e|}{7=*nLZqWilKU7lpPBJKZO{J)+CQMi{nYvq#b)a;?<=_}z<cc#eQoWe*nM-*O<KKG+{K
zG4KN9NtDj$G&`<CNd3A>DK=-;$e7H)J`Rhd}-lI$eFvM%_!Ba4~-rj^k4^+=pd~oW=O}yjOW>X@Cid
VI+SY3h!iSa#$O-Y{c8HUe~x{cpq+Vqpi>}mhu1R>biBMJ2-UTb6DR+Z#r|6l{8s~wyLa^A3?H9u**R
6F>#(pYJ)K=3%B8_i*wuZnT-OO@(`tPtNSREsOEoE^a)GcrgvDzKKYmS0eDC|`8#{m9sMrtq1alZN^v
*q2I_bjhda!eX4ac{APcNlHe2nf5X&`r#zLC}nPC8{7pGQsY&Bt)oMH#CYW&V3M!%OEx9~BKt`g{ro=
rTLp)?F}h;ODv_Y}<qD(~$8ZBh^vzI1yk}}3P*yVFhrQ<dLjNz`SLrQOPgKPgN1D#e3#a2Utbu!!JY5
YGL46;*mrq<Jab09;q@`ORX@3vKgh4AHqsNJacY-3PS;neTRG<0cmDJ!{)s)wS6Wy<QNE(*>qpYAXRl
RG8Z`1LXV!yKY4E#{E8}?N?k3@QVxpQQJq*PeLG}spw<yLoGjC0iBLUCD42__YfRNyKHoc^&8a?M-nu
CykL>H~QQwI?2Yr?R&p(W_o=>7KMqfZN#fl?KAXF?dt!=uM82^_v6#o3@0@-Ok+uNlN1ji?2GJ39mKb
zPf5|`4(4yn7u~sI2Tv&bBVmow^_Cr^s!nu`<=ea&uPiG^hExip0h}{tp0sN4xB~^TxRDU6h=T0Thx3
2ldcdUmO=SX4H`}RL-WB_+djQbFrwwWZYZNUS?SwlnyIi>ZncdvW9<E{vCZFfS66sBX$y-h(gxMsGz<
%Zulo7XpnLMVx)zUb=AD(pQNwpWjXc?Bz5G_a6yv7P_pO@Pz&f?Z^n0%KLzjhVzLlfi+fFvj$kAEjR#
*dpTXX7XDNEfPFm2YhlvC6pNP2s`CTnBOVO%1rCgV=dH0fG1<E6`?h6lPey7I4FJ6+0I*R$Ws>bg*J9
K3P75;1oQ?+$N|@ZT5^Jr1U#%Z@$#qdV=o+AeKPG467Y^x0;z(8{Lf<R?AtXOjT%!K`&43+=c`--kAJ
T|z~PYRd)&JL&sWGauASp+}t-#&fyf@anN)7N>{X+O;++UE=Axy`-R4(KVYT@YS+P@nl<zCBE0Pxn$C
ynij+EF5XSa|E-Ixy)6ozrALL1uQ)VSw$*jFmU){l=nJ;^)|#f8ws#DSngh<Jn+^Anix}G7n9yGIQU+
`kr|bM_L<{-TvS51W=1GVmRu3y6;j?eYZxFeklh-!2PTW*27RJ1D;$RZ{F;DSU9!dItpqHq*a4Dr&*L
A68uU_3Ch1y=zkkzYlSH`c(w0wo!d@I$fKY#z1KRqW29-90b&WS;nD)RX%FcTB1xeB}QQ1>8~>lnTa!
CN_3=k5>lXRf(4kOvQN$J6zvvi;|?>95~^J)8LOIsZR-(&mRRNWLPMa;JH2?U+=*JT)%N8+~dV*?`OI
dbMDNgJw1%r|yn9*xc;26ua@I3&lffYCX1T|FXZF?Z3z1%}*uvXZA#8ynM$)IB7pu94&@?!ymTZn(yO
Hu|*E6oebp>Eu?KrnsROC0w{UkKoRt<ydHM7IxsMXbugGiLX91PhAw5zX9s022JCZ+flXtTqM&A|CtT
f&w2|^Vo|*b?aL~-Ry7o+`5!+Src9DOz<7vvH_f^gulA+q(SH*yoV?zxh^(-(F3Wrson853IdPs;9ZI
^MxAYk9{2cf}07*3LPL)DvbV~_)lEz_dJ@~c137It)QD6Qp{rbpYG{~XR;cd0~3ZA5F@0^-+Sf1PP9#
XrQj<yy~pkp9)OY4@0`!fH>|))7N@D9o3}KM9kzMklo&ykhQ6#B}Yd9gL_st4Q<(q&8U?iEF5#?yOb`
9H<4twn#&Jl&-|96%-l<8uN@W03Z{s(gZP^_R_#HyUw~Qvdl@JuXmk-ITSxZaJSt0#1<Y3H2ZY5Qkg-
X9a($ZdrVcC#XFsj&^nsw3c=ZzJZ^Li_U@45s2cI<rpTeNsH3pd>}%lQ(ELVO5t0irCnB=#88z^m5|{
6ePfus!U2)rtu<K?6ShB5kDFM1x+njmZ$^>T6pH;KA0hVgTcZya70v^-ZSF`V(K5Wm_TJ6u*4ixbE)x
w=eDP?s)EVh3=U`j*Nwc(7iOOVd~+VI2br-QIFfJf7+-RTBa^8T$t_W)YeNi{o5+z9FTgFUEp?~Ta>^
e~?LHxop9tL&uE9G~Q!yU2s&a$Qe25Ad8`cpSgg^WLDyEFYAj9<&~SM=uuM-A|W&doO`p_&mIQ)!FLY
ydy7vYV*R6OnkAYqBJ)UhsxlmG7g$Y&~SulBl4h~D}lX35uL))$(#o7&l;!w$mr0_5!;c}e}hA#gDGk
}Q>@YO9|LTbK7O%idk^zYqoH%f;>x$Z6H<LmZv8(kTXUO&l>(Z)V<*U6Ve-8d-85u7zd`gnM)dYxoc-
~+7iSaK4nCSO{@%<{xA64Resy*5dhr!eyMO!DZ4B6^&aA5j14RT+TUnJN{h>+t&UKn2!TxgZV)^katK
l`aA=LxzmJAVf<IUWt|91`!Usu7sJ|g1j-Y5#~pI$tS@4NFk-&7BiVDw*5O9KQH0000800mA%SU7x9@
TD6708(5402=@R0B~t=FJEbHbY*gGVQepDcw=R7bZKvHb1ras-8|cJ<2IJ>{tAS>TP-CLdoq_)%DYaD
)2&Xs(igAoPA27eX^Mm-#uTX`NV_#ERc-Az%+~(K{=@!BzGTk@0Kto7b&{7^SJIM5;Nalk;M@Vv^Cll
6xhj)9Q=(Eb7UiPItN9|YO0f!~yKpZ3qob=uqQo+ft5k|N?=P>!+jm!@EY_mTMY3GwMJZ-Qz7%1$E*D
8Q7Y_-3irZDP@`EHRWs!yHEi^yMSF#98=?j7h|H%(48I?G4E~Zk03#TxW0r@OUQ!z_YsSMn5A&*ow)d
)hHcm&TXH4+LiPh*kgrHJK9X0gbr`O-h~Jn!g8V;kk!ESayuLdn8;R>}`$noP};G>^hm*1zU+n49^z3
d@Dlwy^EgS{)JU2~4}p^HdocMT;=WMq&;WUQO2{=(Cbx$&JhP3JIrMUj1-B37)^2JpcCW?KdOwB8ke8
I4hBKc`*{N69vED(Yl4{NW9PB%Mk-2lHbG3^TIFWUn{9f<-^*^8jlNpJc2K31uHLmdM44r2a2dXHESZ
C^Usm_!s9Chlf|+CU{zY~0JRK@yJ}@1Nfm{wU8CY6SUSLWShQJ_Ajd}n{;2mNRJaPJeeeo?*KeCdeT@
qerbqSr27CHTS%z^~hNk`3p^`6v(nT_@aHhNZ0hRH8c%VvTRo(rJe<HDyLM~+nGeI7bg*Y+H<j-aKnw
|}UAPbi=2!=;TM^BEPh|4IP&GIxxmV0s(%b5rg72L^bI1M7eY@m(>;5HQFuf!C%jEPdnvMMt80E(B<V
o-ShejSegcJtX_%%8(g|H*@GGQ_QiyX0-2Nf?pfuL?O!J_NYQU@|daJRqPj5^>lyF2@K*y&2I9%^=5?
HR$Q5{K3!&Nq)c}^#j5i;W6H@#EBvTW)VznM6ZVY4*!TLPK2Tdz{;}oO5*}6fy@}dAOkf#a*5K@f^i&
){9YEbG=Dhpl6jUF(i@7;`r6w;XWoz5h9|W3diqntq5o5!WCKLdSF1EB2fz>cLoiLl?C#{MsN@h=J4!
>P#Cfus6h&SPtVGt+2f1~%kYWmJj*KTHw(?1u>8>x55JpvH5?LVTOAX^R<DMuf!xC3V0rE=3wlgfyEH
8j>5|o)aicQoBh0jzZfsH~EgqRYcm{wV|5cv#wIf+KtLuMqn0d`rg%@7O^+T~TjC=j@%R0@Q*^2H<sI
P^lmc0kZomVktUb(={bek2=hqA(L-szCE(QCh{4poMXqurxGsd<1YnSCpt7o<X+|*<Fh9SUfC1%!sg%
218Ij$n&ID2sN0Y9!z5iV*vnU2#^QR19*6yN|!M39|(^X!eY?_#A6VkN>>&4AYlY*QLO;84`b9zay+e
)6!`1bH!EeBR!^Qb3_qh?3R^QNgP`U`CDYl+{`$23dIt=8ES_q)ckK~Az^&dxSY&{Uck>iBj(KdmIU^
etbB%i*+M=|m8*1Vh>45v1_U%pGL@$N|somCTjLQYvY<XaFT+c_FcaVlfxZ5`|5={8BmM~AmBvTdeO9
&i;224#NTz7bOpTsiuZ3mEMjTTLC#IFiAR*C8>EKyS75(>|D@`fY5E)F0R*Ji9wyau?s(Fw7GZyy}BM
r<h&+pcfGWu;2A$*BDp+kc{&)3BY7ECyrZNArb?QH@NqjoDl$hLf7FHSe%&FUb;UytnHQE$sJZ6U$N1
#C~sqL54t$3?I&$3YK{=^zCk&dH=eh=0QM0Hwb*AvA4%!)1346D{tuTSTOVofPsyOy@2VCo$W^2Y0y~
EeZvjBR#Q9fNehopiY+W_tF@-JZmWOww$x<TE%mS7mX`dwt^M8G+OC9dZGS`SW?OIgRsEnzQjp<+*3i
3!VZVWbe>oek$8BS_mI1C+d+b0=QIDPAW{o}E>CQf|!jw!D;jJa=duPwA6A9kQ%)8z&oGqAcX?(M>Ft
*pvZjQyZ^R#9vc;&Sqc@Atq1to-@m>;SrNrF5}*G<XuM4YqMBNauePV>NswO}Drc^_uhA<}l6E8p~Rj
a};4lg$BZY<C)%?LU_@N4+hg_IkR1Jj{th=9~ZhZ=jy=`r9)qjrKqP{Xchf82%=cGe*j9GP$4s>wkX!
`+t1(aWjOc2hFf)Z2y`$|LO(xu3^s|w3MFMKe6tlctS3ozn0rQZ^sK4P-FYHw3;)90KME&Xge|Jl?=N
<_jNvKU7H}g)ZV$Gb~TqkW$+JJ1|lR9emx6UuPXkv8Vo!0JeWv_&(nhZCG(8d;Ihyp5zH@~WM`ISw>-
`T-G?*pHQB%$3uf!-pu=fYR^URB>!{!f`<KrtT2>Y0$?ftlzmXYw8A2NO6+NBE?diI#Iymx?5aX&~7p
m^;0tMs$*MP0EU4Y*tN<oYB^?8y1B%|_cblG%ZM-95}cRkoem|#@(VIecITCcdfU*^jcZGUk~&fi$A!
K+-}j=-lbVLh9VDT;>!-TGbU5Dk$fV>h<&$8Ptr>F)LTknDGSIx?}|I;7O(sE#?@U@K!$&b;Tq=-N$*
;Gx)Xq;H_X54SD0HWnuOYTcdZk!Nk9yhyJQx#~VllekSyj1T)iW?h*}!INv3A~%BL%NWyU(rHsDi!r>
q7Ppq-;QFlnCd^@T2DRnu**E|osZ=FxP{B?CgMh$Vz!2dyzXyYhXqBw|7FlWonF!-uN-54K=i*PFe<^
053J_*2%Mj)a>SQIOWR^t4wZ7-zH*~fe5$(5SU}rHtj$w7L-;7}~k{+r&`v>CQ9Rx#uL%G>y<C)i_KJ
fa6XTAM@z@NBYZ*=&5m)v$aF^q75aOZ}?4beYU!h18hI(>0^b?Twf<eh)}&G_u?%Xgj|tW(K61C*p*5
*ycx)+2_G6L8@QKr>k?jBzf)do~S8W|))#iXSmx7Yx`DQ5CnhFX8FiynLBgSxmFJy(Q%(!+6NTKH-Qq
(m5pEo2~^3Cm0EqJFYN*RC3%E7DuPemf;%XGI7Q2WI=LFXDG-6Rjp{^A(6uvCJdHIJMH1Dy_qgWBAm#
6&z|!f)8lv*7U5FEKW!2=pAt*A+qOnR8IIpDjNG96R1y;qJIJ`fqyr2T1C@3$#L(|WmW(1q6(kjYv_n
=7UKF@;e!HZGDejE;JQ44aJrFwbgA*$@5wWR^!b<VdBeAl%-9Zi%9RSDFY$4s~{Ya$Aog}#TvOvzjC^
+RaX%n_%Pcx64j7@inTZhGwi)nku&H@@U5}$1yQ%uRiwehq98g%SFCqW^`V@x*)n@3YZCom<YabY=Sc
Ape^hH{Fe7pAGHk4j4Ex43=Z66lG0h$p93Vi3R)sef%#Yq=$3udPNeBMjU>&zI9AqnYfS*5imw<qQ`O
wBks3oG-#eQ#d3_hsYj8->{gg>*Mj~H^c7Yf!-p7WhpicZ%gaFse3}lEy#+w1fD3|%u&6PMo{frqlOG
_@ByY}5DD0D%qSq36o61O5NM*Plc26$?c_!k%F1(0$g})E7>T(t=Q-IDMOA@Xx6s<b8CkKE28TyB(q~
@-hkeJ}<TM4H8n5->GJZr2kthPgNmQ$GnU7(c)Ef>YRcI9}YF!3RU=jnriANX%PoWw5$gr>nP*uQY5X
2)9_cDx2^mhSksD~(4WDlv01g0o?anyf|loP;C6;ab2;k=OdNnR<kD_<nV!9zV&lvLr~<SwR3RN~T+f
mH8GceJ;%e8`JCa7#0IxyRLeb#--)Ky@>o(MRb->Jco}+|hQt_qcMx$t0O#if+nDOR+{<dh%%I$yH2e
fM^2Z=WlWc0oa~n??s|&L7uoZnBLZ*Z&JBxkNPuxD0ibvL|P4K2zpQ7ny)R@pn?7F1~8h|a&t_#Fu`q
wvtcn;BhYDJ5^4q-CDo{@R}0SJao_M}Mh$E_19f}}JHL^r2i3iXAE}O%P6gHk?6`2>FQiOSR-$&^Cna
@z+-s8EW9-ooIPWu<4c4ki2D=ZO)0ROtAi2mLg496zb02nQQB<pP=mM<i)$sU?>7xBTYkxXR$<Zv`j!
JA=1``J?*>3w7bIs~mnx1&Nv4FNuc@%V*N)u1h!)}q0wY%p#p(Jfioz-4PxsPHfQOnv0v-KB_*HXHsU
#ljeXlttuAV3gURj&w92ltWIVngle!0h6jb{~}$5h%A>#7J=PUh*lzHDwTrENR1iEa%W*8zVQRU|fNh
^hD0*C*T<oCL>a5nKc3({Y}^%?$-$D_E+#{x^-A!YRxbbs+nmPz{vXh(th71l4+3<G;k4qG+z*0ctfA
9R|pzk;b+UM(68w8BiXW@H@>hY^TwjOrSL<8Wi~as+v84#))r-MYSbx}i$1I6Aq2XqC(y{=4tqnrm(^
4US6F3tBTu7lXxMcTlm!3=Czgd$jA2Kdsct-$AHYF~$EYF4Yz6$HiW+SR1>kf=MY5_TQf)B6KtYtpAf
A%U$rf-GP=F?satr~i<fIyuo1Hd5GHZ11uP4zhV7ki{DzQ2)Ly;VECb*67?Ms8T;dH}V2-(NI9dJ$OV
8&^=>kaJjfs5&ID;VS4%;4tw+0Boc*G-{*rV-X2Py@=Y)(s>s7>OURspQukuQl3mPmM=!Sg=b0nDD%i
GP^PH!5*#{VzwTvS2kIS3Uqr#L5f+Grt987HSW3uv+l?{8_P%g!+RzK*;uz-!MdhZihp%<a98|NyH!O
pM_(5fldH0wjW`n8_rRC~C;*CO^+Yf|Xg^KmlFd|#D(;%uuvMbdLtv^3>O5_kp@xQNhMMmmt@Ss%P}m
BVDm<Z0bI5I1<#XZ*d%h&8HP|B=cZ<Ph>PLef&n@gRi^N|h-?YCPaPU^`5ApH-**gg$?IRn^n}A-bu$
UT1$?W#9Ku6uo37o+?K+W@Q2c*q5Xa?-fG={r2L`y*G=564=c?kVu-2%JJqF!cUmsxWeR=#uIcAq)<r
b^3X1;n+@g{is*V=>2=1nR9^U_5X})qrU9W3lK?>wK4y#DVBzI<0W+*#SNDdarM4VBrc6YG^~BI)On_
H{TE5*S+c2!GvYKL}>KER50biom`)!;c^;>0tB-3^CFf-txS+OQK~e?D#&L+ghwngbH2mz<e-%c$=39
>98to`ObCGa3rrOBGyztpIs4N*UJp1_NHxk0TpEQDY<M(a8SVmQ#A=uIZHN0B>yAeaT(Z_j51cOe(4G
FU%cc96ls-?1!?EfXxDniugaV27$j=;|mr~qi`9n6I=Q+9l3#k~_<LEv_tpzJ~EKbpzD1~A^rgl#9pY
Q@^n65!x&t^#kI|RI#nKP#d%lp@2kme5<EtU+0*a1XbT__Jel2qB#66TM=El`!R#33yx5D6Ht&Q?i=5
<*W#v3s`QBw;KiRv43bQ96+S-SbNegO4?V0!Z*R&?c7PJD?o$#VMA>-vI!lw|VyxSB4IR5;I0wLPh^X
B;TPLG99LAln$EVZ=A7?{IAk*t!3saM^_@Dq!lQ~wPOU^LuHh(0f}iVgpU&(gj_Ss>U6y`b~j6~IOe1
hN^6GLLt~D<vdMuNOo}rpbpeXf!VPeQW+Nx9@|1#177iX1ia7ap4_rqXI2jh;pqkSUj)(DA$A0hgE=^
RAnj`g4Q!`U*jzo4m5#!J6jYS)|Ushq*l(!XHU0{V2$ey5R8Y@y^u`119ua{rjP((EtB?Q*S(@81e$!
bL5Z#=7!WOVexHL*C^RuhSr1bM;n%AIj^?(WgG#Ul3nuCcUSd)g3BnERp{CmlHlc3V{`1zTXR;!F#v@
)WivEM{O{qSJ5(M*WdXzphb-KXie$GZ#vE4Tjr~O(Pj25lO%OG2<UBn;Wn?Lp{FY-SudML|S`gDGywB
MjQy7!)o@A(OMD;{%6&4DhsujxHgChFow2T4Fe`z6kTN`w2kzuEtu~jh3dhHG!Cq~aAN=@z#qc;;Dt_
=>6q0RjX^MFOgRZ=_hOf56vZHL4-!N+3T#a30|c<M7CD2%LAWv~S59V;HZbhn-?^K+wrepJ2jH~2VvS
@fB2;7Llodu6iJFq0#^)hibIAcr*yNS;>`1h$qy*0l^twK8=H&Hs+T?wa{=?Ap^It?$j4d8Nd)7}|Xt
H+cy2?@XqSDj^>LVT!NLTzlLaa>6npEz#<kAjMlUQiqo$2p)%=8sc4v(g3XlRX#u_=if>)GRRUXI1l1
hKs{NmJCu0oZ)m<U3!yGATaT(_li;j?YyCM1z<i2?^`zXdK{cf)>w1mgXT+AuOUrau07DIJTx`5yoJi
#Id%#O?iSM>u!xFDmsZ;s<v_0u8{X6^1|hcw2&_bXEW?<<1G68VTWEWal(u+8u4*JlAj3xC25FuL{;V
()MjgdbIjS=+MSI(iX_Al{GnwbE9#r+i+NsxsT5%2T}5g=1v8CaSDN%jLJwg3t7J;1SDHi^eIJ@NfKA
v?r9a_8u6n6@$0RB3j0l|R{5r@|c_LoqF%T(A3b3NV%HxyJb)vE7@N`w8$F0{%pPYVq`rW&Wv#Uw)>h
$tet!vC0oHTQTj)rNUbUEXs2cBF*vc11}-IZKmL>n6l+v-SHij7;)l$4n%*XfoOfLp#G3oOhU0f9R2;
Xq=aL7xoObxJIfU_GOJl^8d?cdX_?oSG~<YS;06x|tT4N1bL43H?L`j7g^z(UWM2LWKeZApaEo;%gs}
#bBTXo_4KPN!$Yh=F~L{pHk`{c&S2}?0346;V_q_JuB&xeS%`j8xc3OgS_UO@nP}%W($%5IqhV#J>G0
RpYvCPUTR{gSldz=H92$C*)wj0$5AHlwZqr1O<cVJVp7YLy8MXbJZT$>B$4L`R19rlC4th4x~pscutV
3J?bIu+w435{prp=O=sQAC533Afq$N&H&{IR<&Pl^v8kVmp=phPyHp&EPi?JQV`AW7i2!b|w*|9XCzy
7*Gv$`D@lY!fLEj4n!cuCpwLXx6-D3Vh0(RkFK{VpdLf0lVIpq6M<aWP+`%&+ZQnkD<=jwQQ#HMyLK^
V8?wo_;gA6ffS<JuGidub#gW@J=98!t<9G@7~bwi^;#eKf9Q`nY_KabQkUA+3SffwC<#JtyVEPRxXXq
(vAdp4!G;Nkqf9c2Ym4k#ot4M)erJRxI}Nkg{BKwF>O~!N`m~03&}_ntZZdYBQ5Wo%wPJCDOtK)LB_{
)T?(H8chYO9&6NAjqsv0Po5OUm1%3*GIwGqnOy?k0%f*sd47LComt^1OWLYV0ME#lpX!!wv%<*QH9+j
^S9Yb&0maexZ*E}!ls|eVj;vj*l)CvuTtarX#Gssv2`?c{mB2Te>pbjz&4s^SZjq6OpG>Gyg5G7H0)^
elUZ+Cjp_Pceb>s~}%KJJA1E1U6lgpA`$Pk^Oi8yp`WHHb}bbVs!afB&a1z~+x)dFVeKP3QiBp!odvf
B55{4*jPW*f+oh`VR-39r{nx#dl(dGonxcOqB(BF`yrHIS#IZNB11jw)5H+*-Mxd=u}oRd`uu>#YenM
TmOqO04SK@DZct3$wmSLpam^N2blx}hGW4=r9h<unS*7XbnAs`S`+3f7{qXJZIQn*moW`Iro1<Fa*#S
{Z-q%SabP@K0yMIWr0UXL-a<Ygv{Zvu%%2Yl;`Ic*RNWK(AIv=S-16Wi!!$a>9B#!%Zap_UU{LFWs?!
b~CaOni^V7!40*8=32sf5(uxZ<A?yg<d&OP*$rk$_BJ<W81?x7`WE9z8Nzef=$S1mWqxu-EhHY$q1)C
tB${j76}5o_<B<0WHn^YUx?njES@_k?7P*7tQ?EjsF)5z#45^vAePxp7jG#PvtjsX7OsFxnj1ThOLFh
>V^5<Ba#~{>xo-BF;8)uT1l4ijP*W_SZ@d8&mKZbE+i8FU^-TU9Lx;%~xzm>H5+`<F&@oVYo