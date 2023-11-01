#can rust have debuginfo? Verify and fix! Likely issue in Makefile of itw.
%global debug_package %{nil}

# Version of java
%define javaver 1.8.0

# Alternatives priority
%define priority 18000
# jnlp prorocol gnome registry keys
%define gurlhandler   /desktop/gnome/url-handlers
%define jnlphandler   %{gurlhandler}/jnlp
%define jnlpshandler  %{gurlhandler}/jnlps

%define javadir     %{_jvmdir}/java-%{javaver}-openjdk
%define jredir      %{_jvmdir}/jre-%{javaver}-openjdk

%define binsuffix      .itweb

%define preffered_java  java-%{javaver}-openjdk

Name:		icedtea-web
Version:	1.8.4
Release:	4%{?dist}
Summary:	Additional Java components for OpenJDK - Java browser plug-in and Web Start implementation

Group:      Applications/Internet
License:    LGPLv2+ and GPLv2 with exceptions
URL:        http://icedtea.classpath.org/wiki/IcedTea-Web
Source0:    http://icedtea.classpath.org/download/source/%{name}-%{version}.tar.gz
Patch0:     patchOutDunce.patch
Patch1:     altjava.patch
Patch2:     fed2f5b-22402bb.patch

BuildRequires:  javapackages-tools
#for deprecated add_maven_depmap, see https://www.spinics.net/lists/fedora-devel/msg233211.html
BuildRequires:  javapackages-local
BuildRequires:  %{preffered_java}-devel
BuildRequires:  desktop-file-utils
BuildRequires:  glib2-devel
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:	cargo 
BuildRequires:  junit
BuildRequires:  hamcrest
BuildRequires:  libappstream-glib
# new in 1.5 to have  clean up for malformed XMLs
BuildRequires:  tagsoup
# to apply binary tests for CVEs
BuildRequires:      git

# For functionality and the OpenJDK dirs
Requires:      %{preffered_java}
Requires:      javapackages-tools
Recommends:    bash-completion
#maven fragments
Requires(post):      javapackages-tools
Requires(postun):      javapackages-tools

# When itw builds against it, it have to be also in runtime
Requires:      tagsoup

# Post requires alternatives to install tool alternatives.
Requires(post):   %{_sbindir}/alternatives
# jnlp protocols support
Requires(post):   GConf2
# Postun requires alternatives to uninstall tool alternatives.
Requires(postun): %{_sbindir}/alternatives
# jnlp protocols support
Requires(postun):   GConf2

# Standard JPackage plugin provides.
Provides: java-plugin = 1:%{javaver}
Provides: javaws      = 1:%{javaver}
Provides:   %{preffered_java}-javaws =  1:%{version}

Provides:   %{preffered_java}-plugin =  1:%{version}

%description
The IcedTea-Web project provides a an implementation of Java Web Start
(originally based on the Netx project) and a settings tool to
manage deployment settings for the aforementioned plugin and Web Start
implementations. 

%package javadoc
Summary:    API documentation for IcedTea-Web
Group:      Documentation
Requires:   %{name} = %{version}-%{release}
BuildArch:  noarch

%description javadoc
This package contains Javadocs for the IcedTea-Web project.


%package devel
Summary:    pure sources for debugging IcedTea-Web
Group:      devel
Requires:   %{name} = %{version}-%{release}
BuildArch:  noarch

%description devel
This package contains ziped sources of the IcedTea-Web project.

%package nativelaunchers
Summary:    native launchers of icedtea-web
Group:      Applications/Internet
Requires:   %{name} = %{version}-%{release}

%description nativelaunchers
This package contains native launchers for faster starup

%prep
%setup -q -n  IcedTea-Web-%{name}-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
autoreconf -vfi
CXXFLAGS="$RPM_OPT_FLAGS $RPM_LD_FLAGS" \
%configure \
    --with-pkgversion=fedora-%{release}-%{_arch} \
    --docdir=%{_datadir}/javadoc/%{name} \
    --with-jdk-home=%{javadir} \
    --with-jre-home=%{jredir} \
    --libdir=%{_libdir} \
    --program-suffix=%{binsuffix} \
    --disable-native-plugin \
    --with-itw-libs=DISTRIBUTION \
    --with-modularjdk-file=%{_sysconfdir}/java/%{name}    \
    --enable-shell-launchers \
    --prefix=%{_prefix}

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# icedteaweb-completion is currently not handled by make nor make install
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/
mv completion/policyeditor.bash $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/
mv completion/javaws.bash $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/
mv completion/itweb-settings.bash $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/

# Move javaws man page to a more specific name
mv $RPM_BUILD_ROOT/%{_mandir}/man1/javaws.1 $RPM_BUILD_ROOT/%{_mandir}/man1/javaws.itweb.1

# Install desktop files.
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/{applications,pixmaps}

# patch desktops to use the legacy sh laucnhers
sed "s/.itweb /.itweb.sh /" -i javaws.desktop  #there is javaws... %u
sed "s/.itweb$/.itweb.sh/" -i itweb-settings.desktop
sed "s/.itweb$/.itweb.sh/" -i policyeditor.desktop

desktop-file-install --vendor ''\
  --dir $RPM_BUILD_ROOT%{_datadir}/applications javaws.desktop
desktop-file-install --vendor ''\
  --dir $RPM_BUILD_ROOT%{_datadir}/applications itweb-settings.desktop
desktop-file-install --vendor ''\
  --dir $RPM_BUILD_ROOT%{_datadir}/applications policyeditor.desktop

# install MetaInfo file for firefox
DESTDIR=%{buildroot} appstream-util install metadata/%{name}.metainfo.xml
# install MetaInfo file for javaws
DESTDIR=%{buildroot} appstream-util install metadata/%{name}-javaws.appdata.xml

# maven fragments generation
mkdir -p $RPM_BUILD_ROOT%{_javadir}
pushd $RPM_BUILD_ROOT%{_javadir}
ln -s ../%{name}/javaws.jar ../%{name}/netx.jar # backward copatinlity needed?
ln -s ../%{name}/javaws.jar %{name}.jar
ln -s ../%{name}/plugin.jar %{name}-plugin.jar
popd
mkdir -p $RPM_BUILD_ROOT/%{_mavenpomdir}
cp  metadata/%{name}.pom  $RPM_BUILD_ROOT/%{_mavenpomdir}/%{name}.pom
cp metadata/%{name}-plugin.pom  $RPM_BUILD_ROOT/%{_mavenpomdir}/%{name}-plugin.pom

%add_maven_depmap %{name}.pom %{name}.jar
%add_maven_depmap %{name}-plugin.pom %{name}-plugin.jar

cp  netx.build/lib/src.zip  $RPM_BUILD_ROOT%{_datadir}/%{name}/netx.src.zip # backward copatinlity needed?
cp  netx.build/lib/src.zip  $RPM_BUILD_ROOT%{_datadir}/%{name}/javaws.src.zip
cp liveconnect/lib/src.zip  $RPM_BUILD_ROOT%{_datadir}/%{name}/plugin.src.zip

%find_lang %{name} --all-name --with-man

%check
#make check
#appstream-util validate $RPM_BUILD_ROOT/%{_datadir}/appdata/*.xml || :

%post nativelaunchers
PRIORITY=%{priority}
let PRIORITY=PRIORITY-1
alternatives \
  --install %{_bindir}/javaws				javaws.%{_arch}		%{_prefix}/bin/javaws%{binsuffix} $PRIORITY  --family %{preffered_java}.%{_arch} \
  --slave   %{_bindir}/itweb-settings			itweb-settings		%{_prefix}/bin/itweb-settings%{binsuffix} \
  --slave   %{_bindir}/policyeditor			policyeditor		%{_prefix}/bin/policyeditor%{binsuffix} \
  --slave   %{_bindir}/ControlPanel			ControlPanel		%{_prefix}/bin/itweb-settings%{binsuffix} \
  --slave   %{_mandir}/man1/javaws.1.gz			javaws.1.gz		%{_mandir}/man1/javaws%{binsuffix}.1.gz \
  --slave   %{_mandir}/man1/ControlPanel.1.gz		ControlPanel.1.gz	%{_mandir}/man1/itweb-settings.1.gz
%post
PRIORITY=%{priority}
alternatives \
  --install %{_bindir}/javaws				javaws.%{_arch}		%{_prefix}/bin/javaws%{binsuffix}.sh $PRIORITY  --family %{preffered_java}.%{_arch} \
  --slave   %{_bindir}/itweb-settings			itweb-settings		%{_prefix}/bin/itweb-settings%{binsuffix}.sh \
  --slave   %{_bindir}/policyeditor			policyeditor		%{_prefix}/bin/policyeditor%{binsuffix}.sh \
  --slave   %{_bindir}/ControlPanel			ControlPanel		%{_prefix}/bin/itweb-settings%{binsuffix}.sh \
  --slave   %{_mandir}/man1/javaws.1.gz			javaws.1.gz		%{_mandir}/man1/javaws%{binsuffix}.1.gz \
  --slave   %{_mandir}/man1/ControlPanel.1.gz		ControlPanel.1.gz	%{_mandir}/man1/itweb-settings.1.gz

gconftool-2 -s  %{jnlphandler}/command  '%{_bindir}/javaws %s' --type String &> /dev/null || :
gconftool-2 -s  %{jnlphandler}/enabled  --type Boolean true &> /dev/null || :
gconftool-2 -s %{jnlpshandler}/command '%{_bindir}/javaws %s' --type String &> /dev/null || :
gconftool-2 -s %{jnlpshandler}/enabled --type Boolean true &> /dev/null || :

%posttrans
update-desktop-database &> /dev/null || :
exit 0

%postun nativelaunchers
if [ $1 -eq 0 ]
then
  alternatives --remove javaws.%{_arch} %{_prefix}/bin/javaws%{binsuffix}
fi
exit 0

%postun
update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ]
then
  alternatives --remove javaws.%{_arch} %{_prefix}/bin/javaws%{binsuffix}.sh
  gconftool-2 -u  %{jnlphandler}/command &> /dev/null || :
  gconftool-2 -u  %{jnlphandler}/enabled &> /dev/null || :
  gconftool-2 -u %{jnlpshandler}/command &> /dev/null || :
  gconftool-2 -u %{jnlpshandler}/enabled &> /dev/null || :
fi
exit 0

%files nativelaunchers
%{_prefix}/bin/javaws.itweb
%{_prefix}/bin/itweb-settings.itweb
%{_prefix}/bin/policyeditor.itweb
%license COPYING

%files -f .mfiles -f %{name}.lang
%{_sysconfdir}/bash_completion.d/*
%config(noreplace) %{_sysconfdir}/java/%{name}/itw-modularjdk.args
%{_prefix}/bin/javaws.itweb.sh
%{_prefix}/bin/itweb-settings.itweb.sh
%{_prefix}/bin/policyeditor.itweb.sh
%{_datadir}/applications/*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*.jar
%{_datadir}/%{name}/*.png
%{_datadir}/man/man1/*
%{_datadir}/pixmaps/*
%{_datadir}/appdata/*.xml
%doc NEWS README
%license COPYING

%files javadoc
%{_datadir}/javadoc/%{name}
%license COPYING

%files devel
%{_datadir}/%{name}/*.zip
%license COPYING

%changelog
* Mon Nov 30 2020 - Jiri Vanek <jvanek@redhat.com> -1.8.4-4
- added patch2, fed2f5b-22402bb.patch containing important fixes from future 1.8.5
- Resolves: rhbz#1900043

* Fri Nov 27 2020 - Jiri Vanek <jvanek@redhat.com> -1.8.4-2
- added native launchers, via separate subpackage, but efectively changed main package to arched one
- removed policyeditor man page, it was link to itself
- Resolves: rhbz#1900043

* Fri Nov 27 2020 - Jiri Vanek <jvanek@redhat.com> -1.8.4-1
- rebased to itw 1.8, ommiting native launchers
- Resolves: rhbz#1900043

* Fri Nov 20 2020 Jiri Vanek <jvanek@redhat.com> 1.7.1-18
- patched to use alt-java if available
- Added Patch6, altjava.patch
- Resolves: rhbz#1888633

* Thu Jul 18 2019 Jiri Vanek <jvanek@redhat.com> 1.7.1-16
- Added Patch5, testTuning.patch to make tests pass inclean envirnment
- Resolves: rhbz#1724958 

* Thu Jul 18 2019 Jiri Vanek <jvanek@redhat.com> 1.7.1-16
- added patch1, patch4 and patch11 to fix CVE-2019-10182
- added patch2 to fix CVE-2019-10181
- added patch3 and patch33 to fix CVE-2019-10185
- Resolves: rhbz#1724958 
- Resolves: rhbz#1725928 
- Resolves: rhbz#1724989 

* Fri Mar 22 2019 - Jiri Vanek <jvanek@redhat.com> -1.7.1-10
- added gating

* Mon Jul 16 2018 - Jiri Vanek <jvanek@redhat.com> -1.7.1-8
- removed rhino

* Thu May 24 2018 - Jiri Vanek <jvanek@redhat.com> -1.7.1-6
- removed clang

* Mon May 14 2018 - Jiri Vanek <jvanek@redhat.com> -1.7.1-6
- added an applied patch1, oracleForms.patch to make oracle forms working

* Fri Mar 02 2018 - Jiri Vanek <jvanek@redhat.com> -1.7.1-5
- added 1473-1480.patch
- added support for javafx-desc and so allwong run of pure-javafx only applications
- --nosecurity enhanced for possibility to skip invalid signatures
- enhanced to allow resources to be read also from j2se/java element (OmegaT)

* Tue Feb 20 2018 - Jiri Vanek <jvanek@redhat.com> -1.7.1-3
- added buildrequires on gcc/gcc-c++
- to follow new packaging guidelines which no longer automatically pulls gcc/c++ to build root

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Dec 18 2017 Jiri Vanek <jvanek@redhat.com> 1.7.1-1
* bump to 1.7.1

* Fri Nov 03 2017 Jiri Vanek <jvanek@redhat.com> 1.7-6
- javaws specific manpage renmed from -suffix to .suffix

* Wed Oct 18 2017 Jiri Vanek <jvanek@redhat.com> 1.7-5
- gathered various patches from usptream

* Wed Aug 23 2017 Jiri Vanek <jvanek@redhat.com> 1.7-4
- removed natie plugin, no longer can build (removed xullruner and gecko devel packages)
- added forgotten slaves of itweb-settings policyeditor
- Own %%{_datadir}/%%{name} dir
- Mark non-English man pages with %%lang
- Install COPYING as %%license
- last three by Ville Skytta <ville.skytta@iki.fi> via 1481270
- added BuildRequires:  javapackages-local to introduce deprecated add_maven_depmap macro

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jul 19 2017 Jiri Vanek <jvanek@redhat.com> 1.7-1
- updated to itw 1.7

* Wed Jul 19 2017 Jiri Vanek <jvanek@redhat.com> 1.7-0.5
- updated to RC7

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7-0.4.pre06
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Fri May 12 2017 Jiri Vanek <jvanek@redhat.com> 1.7-0.3.pre06
- updated to RC6
- split bash-copletion
- added sources (to align with upstream binary release)

* Tue May 02 2017 Jiri Vanek <jvanek@redhat.com> 1.7-0.3.pre05
- gconf calls silenced by "&> /dev/null || :"
- see rhbz1446932

* Fri Apr 28 2017 Jiri Vanek <jvanek@redhat.com> 1.7-0.2.pre05
- updated to rc5
- added support for jnlp://, jnlps:// and jnlp: protocols 

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.7-0.2.pre04
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 12 2017 Jiri Vanek <jvanek@redhat.com> 1.7-0.1.pre04
- updated to rc4
- fixed RHBZ#1412544

* Wed Jan 11 2017 Jiri Vanek <jvanek@redhat.com> 1.7-0.1.pre03
- updated ro RC3 of 1.7 

* Wed Jan 04 2017 Jiri Vanek <jvanek@redhat.com> 1.7-0.1.pre01
- updated ro RC1 of 1.7 
- added recommends on vash completion

* Wed Jul 13 2016 Jiri Vanek <jvanek@redhat.com> 1.6.2-3
- minor fix to javadir and jre dir

* Wed Jul 13 2016 Jiri Vanek <jvanek@redhat.com> 1.6.2-2
- added --family to make it part of javas alternatives alignment
- java-javaver-openjdk collected into preffered_java 

* Wed Feb 03 2016 Jiri Vanek <jvanek@redhat.com> 1.6.2-1
- updated to 1.6.2
- fixed also rhbz#1303437 - package owns /etc/bash_completion.d but it should not own it 

* Thu Jan 28 2016 Jiri Vanek <jvanek@redhat.com> 1.6.1-66
- moved to 1.6.2pre

* Tue Dec 22 2015 Jiri Vanek <jvanek@redhat.com> 1.6.1-5
- generated maven metadata

* Thu Nov 19 2015 Jiri Vanek <jvanek@redhat.com> 1.6.1-4
- installed also javaws metadata

* Wed Oct 14 2015 Jiri Vanek <jvanek@redhat.com> 1.6.1-3
- added and applied three patches scheduled for 1.6.2
- patch2 fileLogInitializationError-1.6.patch to prevent consequences 1268909
- patch1 donLogToFileBeforeFileLogsInitiate.patch
- patch0 javadocFixes.patch 

* Mon Sep 21 2015 Jiri Vanek <jvanek@redhat.com> 1.6.1-2
- added and applied patch0 javadocFixes.patch 

* Fri Sep 11 2015 Jiri Vanek <jvanek@redhat.com> 1.6.1-1
- updated to upstream release 1.6.1
- metadata xml files enhanced for javaws

* Mon Jun 22 2015 Omair Majid <omajid@redhat.com> - 1.6-5
- Comply with newer java packaging guidelines
- Require javapackages-tools in main package
- Don't require jpackage-utils in -javadoc subpackage, since subpackage
  requires the main package

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon May 04 2015 Jiri Vanek <jvanek@redhat.com> 1.6-3
- added depndence on hamcrest - no longer part of junit

* Wed Apr 29 2015 Jiri Vanek <jvanek@redhat.com> 1.6-2
- enabled check

* Tue Apr 28 2015 Jiri Vanek <jvanek@redhat.com> 1.6-1
- updated to limited audience final release

* Fri Apr 24 2015 Jiri Vanek <jvanek@redhat.com> 1.6-0.1.pre05
- updated to pre06
- handled "Add Tab Completion for icedtea-web" change
- this release contains numers, not yet upstreamed, but going to release features:
- summary: Fixed resource test to pass for CZ localization
- summary: Added Czech translation for 1.6.
- summary: Messages from TextsProvider moved to properties
- summary: various improvements to default set of properties
- summary: Added MultipleDeploymentPropertiesModifier improvement to testsuite

* Fri Apr 17 2015 Jiri Vanek <jvanek@redhat.com> 1.6-0.1.pre05
- updated to pre05

* Tue Apr 14 2015 Jiri Vanek <jvanek@redhat.com> 1.6-0.1.pre04
- updated to pre04

* Mon Mar 16 2015 Jiri Vanek <jvanek@redhat.com> 1.6-0.1.pre03
- updated to pre03
- removed cp javaws.png. Handled by upstream now

* Mon Dec 22 2014 Jiri Vanek <jvanek@redhat.com> 1.6-0.1.pre02
- updated to pre02
- upstreamed patch1, quoteDocsPaths.patch
- temprarily disabled unittests
- fixed nlp apps shortcut

* Mon Dec 22 2014 Jiri Vanek <jvanek@redhat.com> 1.6-0.1.pre01
- update future 1.6 alpha pre01
- added localised man pages
- removed link to icedtea-web man page (now provided by upstream)

* Thu Nov 27 2014 Jiri Vanek <jvanek@redhat.com> 1.5.2-0
- update to upstream 1.5.2

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.1-1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Aug 15 2014 Jiri Vanek <jvanek@redhat.com> 1.5.1-0
- update to upstream 1.5.1
- removed all patches (all upstreamed)

* Thu Aug 14 2014 Richard Hughes <richard@hughsie.com> - 1.5-4
- Add MetaInfo file to show an addon in GNOME Software.
- See http://icedtea.classpath.org/bugzilla/show_bug.cgi?id=1907 for upstream.

* Mon Jun 09 2014 Omair Majid <omajid@redhat.com> - 1.5-3
- Require junit instead of juni4
- Build against OpenJDK 7 explicitly

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Apr 07 2014 Jiri Vanek <jvanek@redhat.com> 1.5-2
- add not yet upstreamed DE localisation of 1.5
 - patch0 DElocalizationforIcedTea-Web1.5-0001.patch
- autoreconf gog  -vfi, see RH1077898
- ./configure changed to %%configure,see RH1077287

* Mon Apr 07 2014 Jiri Vanek <jvanek@redhat.com> 1.5-1
- updated to icedtea-web-1.5

* Mon Mar 10 2014 Jiri Vanek <jvanek@redhat.com> 1.5-0.8.pre05
- updated to pre05
 - based on revision 925

* Mon Mar 10 2014 Jiri Vanek <jvanek@redhat.com> 1.5-0.4.pre04
- updated to pre04
 - based on revision 917

* Wed Mar 05 2014 Jiri Vanek <jvanek@redhat.com> 1.5-0.3.pre03
- updated to pre03
 - based on revision 910:0a36108ce4b9

* Wed Feb 26 2014 Jiri Vanek <jvanek@redhat.com> 1.5-0.2.pre02
- added supported tagsoup dependence

* Wed Feb 26 2014 Jiri Vanek <jvanek@redhat.com> 1.5-0.1.pre02
- updated to  bleeding edge as tracker before 1.5 actual release
 - based on revision 899
- added policyeditor.desktop
- removed -std=c++11  flag

* Wed Feb 12 2014 Jiri Vanek <jvanek@redhat.com> 1.5-0.1.pre01
- updated to  bleeding edge as tracker before 1.5 actual release
- named by https://fedoraproject.org/wiki/Packaging:NamingGuidelines#Pre-Release_packages
 - see commented original source0 line and setup line reusing versions
- the source tarball is based on revision 892

* Tue Feb 04 2014 Jiri Vanek <jvanek@redhat.com> 1.4.2-0
- updated to 1.4.2
- removed upstreamed patches
- added std=c++11 flag to CXXFLAGS (thanx omajid!)
- removed autoreconf

* Tue Dec 17 2013 Jiri Vanek <jvanek@redhat.com> 1.4.1-1
- added and applied patch0, christmasSplash3.diff. Will be upstreamed
- Christmas release for Fedora !-)

* Tue Sep 17 2013 Jiri Vanek <jvanek@redhat.com> 1.4.1-0
- updated to 1.4.1
- add icedtea-web man page
- removed upstreamed  patch1 b25-appContextFix.patch
- removed upstreamed  patch2 rhino-pac-permissions.patch
- make check enabled again
- should be build for non-standart archs !-)
- removed unused multilib arches (yupii!)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 23 2013 Omair Majid <jvanek@redhat.com> 1.4.0-3
- Added upstream fix for RH982558

* Wed Jun 19 2013 Jiri Vanek <jvanek@redhat.com> 1.4.0-2
- added patch1 b25-appContextFix.patch to make it run with future openjdk

* Fri Jun 07 2013 Jiri Vanek <jvanek@redhat.com> 1.4-1
- Adapted to latest openjdk changes
- added build requires for autoconf and automake
- minor clean up
- Updated to 1.4
- See announcement for detail
 - http://mail.openjdk.java.net/pipermail/distro-pkg-dev/2013-May/023195.html
- commented out check - some junit4  incompatibility

* Wed Apr 17 2013 Jiri Vanek <jvanek@redhat.com> 1.3.2-0
- Updated to latest ustream release of 1.3 branch - 1.3.2
 - Security Updates
  - CVE-2013-1927, RH884705: fixed gifar vulnerability
  - CVE-2013-1926, RH916774: Class-loader incorrectly shared for applets with same relative-path.
 - Common
  - Added new option in itw-settings which allows users to set JVM arguments when plugin is initialized.
 - NetX
  - PR580: http://www.horaoficial.cl/ loads improperly
 - Plugin
   PR1260: IcedTea-Web should not rely on GTK
   PR1157: Applets can hang browser after fatal exception
- Removed upstreamed patch to remove GTK dependency
  - icedtea-web-pr1260-remove-gtk-dep.patch

* Wed Feb 20 2013 Ville Skyttä <ville.skytta@iki.fi> - 1.3.1-5
- Resolves: rhbz#875496
- Build with $RPM_LD_FLAGS and %%{_smp_mflags}.
- Run unit tests during build.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan 16 2013 Deepak Bhole <dbhole@redhat.com> 1.3.1-3
- Resolves: rhbz#889644, rhbz#895197
- Added patch to remove GTK dependency

* Thu Dec 20 2012 Jiri Vanek <jvanek@redhat.com> 1.3.1-2
- Moved to be  build with GTK3

* Wed Nov 07 2012 Deepak Bhole <dbhole@redhat.com> 1.3.1-1
- Resolves: RH869040/CVE-2012-4540

* Mon Sep 17 2012 Deepak Bhole <dbhole@redhat.com> 1.3-1
- Updated to 1.3
- Resolves: rhbz#720836: Epiphany fails to execute Java applets

* Tue Jul 31 2012 Deepak Bhole <dbhole@redhat.com> 1.2.1-1
- Updated to 1.2.1
- Resolves: RH840592/CVE-2012-3422
- Resolves: RH841345/CVE-2012-3423

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu May 03 2012 Deepak Bhole <dbhole@redhat.com> 1.2-4
- Resolves rhbz#814585
- Fixed java-plugin provides and added one for javaws

* Tue Apr 17 2012 Deepak Bhole <dbhole@redhat.com> 1.2-3
- Updated summary
- Fixed virtual provide

* Tue Mar 13 2012 Peter Robinson <pbrobinson@fedoraproject.org> - 1.2-2
- Enable building on ARM platforms

* Mon Mar 05 2012 Deepak Bhole <dbhole@redhat.com> 1.2-1
- Updated to 1.2

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Nov 25 2011 Deepak Bhole <dbhole@redhat.com> 1.1.4-3
- Resolves rhbz#757191
- Bumped min_openjdk_version to -60 (latest)

* Thu Nov 24 2011 Deepak Bhole <dbhole@redhat.com> 1.1.4-2
- Resolves: rhbz#742887. Do not own directories not created by the package.

* Tue Nov 08 2011 Deepak Bhole <dbhole@redhat.com> 1.1.4-1
- Updated to 1.1.4
- Added npapi-fix patch so that the plug-in compiles with xulrunner 8 

* Thu Sep 01 2011 Deepak Bhole <dbhole@redhat.com> 1.1.2-1
- Updated to 1.1.2
- Removed all patches (now upstream)
- Resolves: rhbz# 734890

* Tue Aug 23 2011 Deepak Bhole <dbhole@redhat.com> 1.1.1-3
- Added patch to allow install to jre dir
- Fixed requirement for java-1.7.0-openjdk

* Tue Aug 09 2011 Deepak Bhole <dbhole@redhat.com> 1.1.1-2
- Fixed file ownership so that debuginfo is not in main package

* Wed Aug 03 2011 Deepak Bhole <dbhole@redhat.com> 1.1.1-1
- Bump to 1.1.1
- Added patch for PR768 and PR769

* Wed Jul 20 2011 Deepak Bhole <dbhole@redhat.com> 1.0.4-1
- Bump to 1.0.4
- Fixed rhbz#718164: Home directory path disclosure to untrusted applications
- Fixed rhbz#718170: Java Web Start security warning dialog manipulation

* Mon Jun 13 2011 Deepak Bhole <dbhole@redhat.com> 1.0.3-1
- Update to 1.0.3
- Resolves: rhbz#691259 

* Mon Apr 04 2011 Deepak Bhole <dbhole@redhat.com> 1.0.2-2
- Fixed incorrect macro value for min_openjdk_version
- Use posttrans instead of post, so that upgrade from old plugin works

* Mon Apr 04 2011 Deepak Bhole <dbhole@redhat.com> 1.0.2-1
- Initial build
