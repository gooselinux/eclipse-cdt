%global debug_package %{nil}

Epoch: 1

%define run_tests               0
%define ship_tests              0
%define major                   6
%define minor                   0       
%define majmin                  %{major}.%{minor}
%define micro                   2
%define eclipse_base            %{_libdir}/eclipse
%define build_id		201002161416


# All arches line up except i386 -> x86
%ifarch %{ix86}
%define eclipse_arch    x86
%else
%define eclipse_arch   %{_arch}
%endif

Summary:        Eclipse C/C++ Development Tools (CDT) plugin
Name:           eclipse-cdt
Version:        %{majmin}.%{micro}
Release:        3%{?dist}
License:        EPL and CPL
Group:          Development/Tools
URL:            http://www.eclipse.org/cdt
Requires:       eclipse-platform


# The following tarball was generated using the included fetch-cdt.sh
# script.  Note that the optional c99 and upc parsers plus the optional
# xlc support features have been removed.

Source0: %{name}-fetched-src-v%{build_id}.tar.bz2
Source4: fetch-cdt.sh

Source1: %{name}-fetched-src-autotools-R0_5_1.tar.gz
Source14: make-autotools-tarball.sh

Source2: %{name}-fetched-src-libhover-R0_5_1.tar.gz
Source15: make-libhover-tarball.sh

## The following tarball was generated thusly:
##
## mkdir temp && cd temp
## cvs -d:pserver:anonymous@dev.eclipse.org:/cvsroot/tools export -r CPPUnit_20061102 \
##   org.eclipse.cdt-cppunit/org.eclipse.cdt.cppunit \
##   org.eclipse.cdt-cppunit/org.eclipse.cdt.cppunit-feature
## cd org.eclipse.cdt-cppunit
## tar -czvf eclipse-cdt-cppunit-20061102.tar.gz org.eclipse.cdt.cppunit*
#
#Source2: %{name}-cppunit-20061102.tar.gz

# Script to run the tests in Xvnc
Source5: %{name}-runtests.sh

# Libhover docs to place locally
Source6: glibc-2.7-2.libhover
Source7: libstdc++-v3.libhover

# Autotools docs to place locally
Source8: acmacros-2.13.xml
Source9: acmacros-2.59.xml
Source10: acmacros-2.61.xml
Source11: ammacros-1.4-p6.xml
Source12: ammacros-1.9.5.xml
Source13: ammacros-1.9.6.xml

## Patch to cppunit code to support double-clicking on file names, classes, and
## member names in the Hierarchy and Failure views such that the appropriate
## file will be opened and the appropriate line will be selected.
#Patch8: %{name}-cppunit-ui.patch
## Patch to upgrade version number for cppunit feature.
#Patch9: %{name}-cppunit-feature.patch
## Patch to fix default paths used by cppunit wizards to find header files and
## libraries.
#Patch10: %{name}-cppunit-default-location.patch
## Patch to cppunit code to remove references to deprecated class which has
## been removed in CDT 4.0.
#Patch11: %{name}-cppunit-env-tab.patch

# Remove include of stropts.h in openpty.c as it is no longer included 
# in glibc-headers package
# https://bugs.eclipse.org/bugs/show_bug.cgi?id=272373
Patch12: %{name}-openpty.patch

# Add XML -> HTML generation after running tests
Patch13: %{name}-testaggregation.patch

# Following is a patch to supply libhover docs directory from the libhover
# plugin and not require html to access them.
Patch14: %{name}-libhover-local.patch

# Patches for ppc64
# https://bugs.eclipse.org/bugs/show_bug.cgi?id=272380

# Add LDFLAGS to Makefile for .so
# https://bugs.eclipse.org/bugs/show_bug.cgi?id=272364
Patch16: %{name}-ppc64-add_ldflags.patch

# Add define of _XOPEN_SOURCE so that ptsname header is included
# https://bugs.eclipse.org/bugs/show_bug.cgi?id=272370
Patch17: %{name}-ppc64-add_xopen_source-include.patch

# Following is a patch to autotools to supply macro hover docs locally
# in the plugin.
Patch19: %{name}-autotools-local.patch

# Disable mylyn bridge compiling. Should be removed when CDT 7.0 is out.
Patch20: %{name}-disable-mylyn.patch

# Add new setTargets interface to MakeTargetManager for use by Autotools.
# This can be removed for CDT 7.0.
Patch21: %{name}-maketargets.patch

BuildRequires: eclipse-pde
BuildRequires: eclipse-rse >= 3.0
BuildRequires:  java-devel >= 1.4.2
BuildRequires: lpg-java-compat
%if %{run_tests}
BuildRequires:  vnc-server
BuildRequires:  w3m
%endif

Requires:       gdb make gcc-c++ autoconf automake libtool
Requires:       eclipse-platform >= 1:3.5.0
Requires:	eclipse-rse >= 3.0

%if 0%{?rhel} >= 6
ExclusiveArch: i686 x86_64
%else
ExclusiveArch: %{ix86} x86_64 ppc ia64 ppc64
%endif
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

%description
Eclipse features and plugins that are useful for C and C++ development.

%package parsers
Summary:        Eclipse C/C++ Development Tools (CDT) SDK plugin
Group:          Text Editors/Integrated Development Environments (IDE)
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       lpg-java-compat

%description parsers
Optional language-variant parsers for the CDT.

%package sdk
Summary:        Eclipse C/C++ Development Tools (CDT) SDK plugin
Group:          Text Editors/Integrated Development Environments (IDE)
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description sdk
Source for Eclipse CDT for use within Eclipse.

%if %{ship_tests}
%package tests
Summary:        Test suite for Eclipse C/C++ Development Tools (CDT)
Group:          Text Editors/Integrated Development Environments (IDE)
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       vnc-server

%description tests
Test suite for Eclipse C/C++ Development Tools (CDT).
%endif

%prep
%setup -q -c 

pushd "org.eclipse.cdt.releng"

# Following patches a C file to remove reference to stropts.h which is
# not needed and is missing in latest glibc
pushd results/plugins/org.eclipse.cdt.core.linux/library
%patch12 -p0
popd
pushd results/plugins
%patch13
popd
pushd results/plugins/org.eclipse.cdt.make.core
%patch21 -p0
popd
#pushd results/plugins/org.eclipse.cdt.core.tests
#rm parser/org/eclipse/cdt/core/parser/tests/scanner/LexerTests.java
#%patch14
#popd

# Only build the sdk
offset=0; 
for line in $(grep -no "value=.*platform" build.xml); do
  linenum=$(echo "$line" | cut -d : -f 1)
  sed --in-place -e "$(expr $linenum - 1 - $offset ),$(expr $linenum + 1 - $offset)d" build.xml 
  offset=$(expr $offset + 3) 
done
# Only build for the platform on which we're building
sed --in-place -e "s:linux.gtk.x86/:linux.gtk.%{eclipse_arch}/:g" build.xml
pushd sdk
sed --in-place -e "74,82d" build.properties
sed --in-place -e "s:configs=\\\:configs=linux,gtk,%{eclipse_arch}:" build.properties
popd
pushd master
sed --in-place -e "81,89d" build.properties
sed --in-place -e "s:configs= \\\:configs=linux,gtk,%{eclipse_arch}:" build.properties
popd
pushd platform
sed --in-place -e "74,82d" build.properties
sed --in-place -e "s:configs=.*\\\:configs=linux,gtk,%{eclipse_arch}:" build.properties
popd

# build.xml assumes we build all configs, but we only build one so update 
# build.xml directory reference to be accurate.
sed --in-place -e "s:linux.gtk.x86/:linux.gtk.%{eclipse_arch}/:g" build.xml

popd

## Autotools stuff
mkdir autotools
pushd autotools
tar -xzf %{SOURCE1}
%patch19 -p0
pushd org.eclipse.linuxtools.cdt.autotools.core
mkdir macros
pushd macros
cp %{SOURCE8} .
cp %{SOURCE9} .
cp %{SOURCE10} .
cp %{SOURCE11} .
cp %{SOURCE12} .
cp %{SOURCE13} .
popd
popd
popd

## Libhover stuff
mkdir libhover
pushd libhover
tar -xzf %{SOURCE2}
# newlib libhover is an optional feature...remove it from CDT base
rm -rf org.eclipse.linuxtools.cdt.libhover.newlib
rm -rf org.eclipse.linuxtools.cdt.libhover.newlib-feature
%patch14 -p0
pushd org.eclipse.linuxtools.cdt.libhover
mkdir libhoverdocs
pushd libhoverdocs
cp %{SOURCE6} .
cp %{SOURCE7} .
popd
popd
popd

## Cppunit stuff
#
#mkdir cppunit
#pushd cppunit
#tar -xzf %{SOURCE2}
#%patch8 -p0
#%patch9 -p0
#%patch10 -p0
#%patch11 -p0
#popd

# Upstream CVS includes random .so files.  Let's remove them now.
# We actually remove the entire "os" directory since otherwise
# we wind up with some empty directories that we don't want.
#rm -r org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.linux/os

mv org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.tests/resources/testlib/x86/so.g/libtestlib_g.so \
  org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.tests/resources/testlib/x86/so.g/libtestlib_g.BAK
find -name \*.so | xargs rm -rf
mv org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.tests/resources/testlib/x86/so.g/libtestlib_g.BAK \
  org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.tests/resources/testlib/x86/so.g/libtestlib_g.so

%ifarch ppc64
pushd org.eclipse.cdt.releng/results/plugins
echo "fragmentName.linux.%{eclipse_arch} = C/C++ Development Tools Core for Linux (%{eclipse_arch})" \
  >> org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core/plugin.properties
cp -rp org.eclipse.cdt.core.linux.{x86,%{eclipse_arch}}
cd org.eclipse.cdt.core.linux.%{eclipse_arch}
sed -i "s/x86/%{eclipse_arch}/" META-INF/MANIFEST.MF
mv os/linux/{x86,%{eclipse_arch}}
cd ../org.eclipse.cdt.core.linux
%patch16 -p0
%patch17 -p0
popd
%endif

#remove mylyn plugins (part of mylyn srpm now)
rm -fr results/plugins/org.eclipse.cdt.mylyn*
%patch20

%build
export JAVA_HOME=%{java_home}
export PATH=%{java_bin}:/usr/bin:$PATH

# See comments in the script to understand this.
/bin/sh -x %{eclipse_base}/buildscripts/copy-platform SDK \
  %{eclipse_base} xmlrpc codec httpclient lang rse
ln -s %{_javadir}/lpgjavaruntime-1.1.0.jar SDK/plugins/net.sourceforge.lpg.lpgjavaruntime_1.1.0.jar
SDK=$(cd SDK >/dev/null && pwd)

# Eclipse may try to write to the home directory.
mkdir home
homedir=$(cd home > /dev/null && pwd)

pushd org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.linux/library
make JAVA_HOME="%{java_home}" ARCH=%{eclipse_arch} CC='gcc -D_GNU_SOURCE'
popd

PDEBUILDVERSION=$(ls %{eclipse_base}/dropins/sdk/plugins \
  | grep org.eclipse.pde.build_ | \
  sed 's/org.eclipse.pde.build_//')
PDEDIR=%{eclipse_base}/dropins/sdk/plugins/org.eclipse.pde.build_$PDEBUILDVERSION
# Call eclipse headless to process CDT releng build scripts
pushd org.eclipse.cdt.releng 
java -cp $SDK/startup.jar \
     -Duser.home=$homedir                        \
     -DbuildId=%{build_id} \
     -DbranchVersion=%{version} \
     -DforceContextQualifier=%{build_id} \
     -XX:CompileCommand="exclude,org/eclipse/core/internal/dtree/DataTreeNode,forwardDeltaWith" \
     -XX:CompileCommand="exclude,org/eclipse/jdt/internal/compiler/lookup/ParameterizedMethodBinding,<init>" \
     -XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/dom/parser/cpp/semantics/CPPTemplates,instantiateTemplate" \
     -XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/pdom/dom/cpp/PDOMCPPLinkage,addBinding" \
     org.eclipse.core.launcher.Main             \
    -application org.eclipse.ant.core.antRunner \
    -DbuildId=%{build_id} \
    -DbranchVersion=%{version} \
    -DforceContextQualifier=%{build_id} \
    -DjavacFailOnError=true \
    -DdontUnzip=true \
    -DbaseLocation=$SDK \
    -Dpde.build.scripts=$PDEDIR/scripts \
    -DdontFetchAnything=true \
    -DskipFetch=true \
     zips
popd

## Autotools has dependencies on CDT so we must add these to the SDK directory
unzip -o org.eclipse.cdt.releng/results/I.%{build_id}/cdt-master-%{version}-%{build_id}.zip -d $SDK

## Autotools build
pushd autotools
java -cp $SDK/startup.jar \
     -Duser.home=$homedir                        \
     -XX:CompileCommand="exclude,org/eclipse/core/internal/dtree/DataTreeNode,forwardDeltaWith" \
     -XX:CompileCommand="exclude,org/eclipse/jdt/internal/compiler/lookup/ParameterizedMethodBinding,<init>" \
     -XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/dom/parser/cpp/semantics/CPPTemplates,instantiateTemplate" \
     -XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/pdom/dom/cpp/PDOMCPPLinkage,addBinding" \
     org.eclipse.core.launcher.Main             \
     -application org.eclipse.ant.core.antRunner \
     -DjavacSource=1.5 \
     -DjavacTarget=1.5 \
     -Duser.home=$homedir                        \
     -Dtype=feature                                    \
     -Did=org.eclipse.linuxtools.cdt.autotools \
     -DsourceDirectory=$(pwd)                          \
     -DbaseLocation=$SDK                               \
     -Dbuilder=$PDEDIR/templates/package-build  \
     -f $PDEDIR/scripts/build.xml 
popd

## Libhover build
pushd libhover
java -cp $SDK/startup.jar \
     -Duser.home=$homedir                        \
     -XX:CompileCommand="exclude,org/eclipse/core/internal/dtree/DataTreeNode,forwardDeltaWith" \
     -XX:CompileCommand="exclude,org/eclipse/jdt/internal/compiler/lookup/ParameterizedMethodBinding,<init>" \
     -XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/dom/parser/cpp/semantics/CPPTemplates,instantiateTemplate" \
     -XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/pdom/dom/cpp/PDOMCPPLinkage,addBinding" \
     org.eclipse.core.launcher.Main             \
     -application org.eclipse.ant.core.antRunner \
     -Duser.home=$homedir                        \
     -Dtype=feature                                    \
     -Did=org.eclipse.linuxtools.cdt.libhover  \
     -DsourceDirectory=$(pwd)                          \
     -DbaseLocation=$SDK                               \
     -Dbuilder=$PDEDIR/templates/package-build  \
     -f $PDEDIR/scripts/build.xml 
popd

## Cppunit build
#pushd cppunit
#java -cp $SDK/startup.jar \
#     -Duser.home=$homedir                        \
#     org.eclipse.core.launcher.Main             \
#     -application org.eclipse.ant.core.antRunner       \
#     -Dtype=feature                                    \
#     -Did=org.eclipse.cdt.cppunit                      \
#     -DsourceDirectory=$(pwd)                          \
#     -DbaseLocation=$SDK                               \
#     -Dbuilder=$PDEDIR/templates/package-build  \
#     -f $PDEDIR/scripts/build.xml
#popd

%install
rm -rf ${RPM_BUILD_ROOT}

# Eclipse may try to write to the home directory.
mkdir -p home
homedir=$(cd home > /dev/null && pwd)

LAUNCHERJAR=$(ls %{eclipse_base}/plugins \
  | grep org.eclipse.equinox.launcher_)
LAUNCHER=%{eclipse_base}/plugins/$LAUNCHERJAR

installDir=${RPM_BUILD_ROOT}/%{eclipse_base}/dropins/cdt
parsersInstallDir=${installDir}-parsers
sdkInstallDir=${installDir}-sdk
install -d -m755 $installDir
install -d -m755 $parsersInstallDir
install -d -m755 $sdkInstallDir

unzip -q -o org.eclipse.cdt.releng/results/I.%{build_id}/cdt-master-%{version}-%{build_id}.zip \
-d $installDir/eclipse

rm $installDir/eclipse/site.xml
rm $installDir/eclipse/pack.properties

# Unpack all existing feature jars
for x in $installDir/eclipse/features/*.jar; do
  dirname=`echo $x | sed -e 's:\\(.*\\)\\.jar:\\1:g'`
  mkdir -p $dirname
  unzip -q $x -d $dirname
  rm $x
done 

# Autotools install
pushd autotools
unzip -qq -d $installDir build/rpmBuild/org.eclipse.linuxtools.cdt.autotools.zip
popd

# Libhover install
pushd libhover
unzip -qq -d $installDir build/rpmBuild/org.eclipse.linuxtools.cdt.libhover.zip
popd

# Move upc, xlc, and lrparser plugins/features to parsers install area.
mkdir -p $parsersInstallDir/eclipse/features $parsersInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*xlc* $parsersInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*xlc* $parsersInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*lrparser* $parsersInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*lrparser* $parsersInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*upc* $parsersInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*upc* $parsersInstallDir/eclipse/plugins
pushd $parsersInstallDir/eclipse/plugins
ln -s ../../../../../../share/java/lpgjavaruntime.jar net.sourceforge.lpg.lpgjavaruntime_1.1.0.jar
popd

mkdir -p $sdkInstallDir/eclipse/features $sdkInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*source* $sdkInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*source* $sdkInstallDir/eclipse/plugins
mv $installDir/eclipse/plugins/org.eclipse.cdt.doc.isv_* $sdkInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*sdk* $sdkInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*sdk* $sdkInstallDir/eclipse/plugins

rm -rf $installDir/eclipse/features/org.eclipse.cdt.master_*
rm -rf $installDir/eclipse/plugins/org.eclipse.ant.optional.junit_*
rm -rf $installDir/eclipse/plugins/org.eclipse.test_*
rm -rf $installDir/eclipse/plugins/net.sourceforge.*

## Cppunit install
#pushd cppunit
#unzip -qq -d $RPM_BUILD_ROOT%{eclipse_base}/dropins/cdt build/rpmBuild/org.eclipse.cdt.cppunit.zip
#popd

# Generate p2 metadata for CDT
pushd $installDir/eclipse
java -jar $LAUNCHER \
-application \
org.eclipse.equinox.p2.metadata.generator.EclipseGenerator \
-metadataRepository file:`pwd`/repo \
-artifactRepository file:`pwd`/repo \
-source `pwd` \
-root "Eclipse CDT" \
-rootVersion %{version} \
-flavor tooling \
-publishArtifacts \
-append \
-artifactRepositoryName "CDT" \
-metadataRepositoryName "CDT" \
-vmargs \
-Duser.home=$homedir

rm -rf repo
popd

# Generate p2 metadata for CDT Parsers
pushd $parsersInstallDir/eclipse
java -jar $LAUNCHER \
-application \
org.eclipse.equinox.p2.metadata.generator.EclipseGenerator \
-metadataRepository file:`pwd`/repo \
-artifactRepository file:`pwd`/repo \
-source `pwd` \
-root "CDT Parsers" \
-rootVersion %{version} \
-flavor tooling \
-publishArtifacts \
-append \
-artifactRepositoryName "CDT Parsers" \
-metadataRepositoryName "CDT Parsers" \
-vmargs \
-Duser.home=$homedir

rm -rf repo
popd

# Generate p2 metadata for CDT SDK
pushd $sdkInstallDir/eclipse
java -jar $LAUNCHER \
-application \
org.eclipse.equinox.p2.metadata.generator.EclipseGenerator \
-metadataRepository file:`pwd`/repo \
-artifactRepository file:`pwd`/repo \
-source `pwd` \
-root "Eclipse CDT SDK" \
-rootVersion %{version} \
-flavor tooling \
-publishArtifacts \
-append \
-artifactRepositoryName "CDT SDK" \
-metadataRepositoryName "CDT SDK" \
-vmargs \
-Duser.home=$homedir

rm -rf repo
popd

mkdir -p ${installDir}-tests/plugins
mkdir -p ${installDir}-tests/features
mv ${installDir}/eclipse/plugins/*test* \
  ${installDir}-tests/plugins
mv ${installDir}/eclipse/features/*test* \
  ${installDir}-tests/features
for x in ${installDir}-tests/plugins/*.jar; do
  dirname=`echo $x | sed -e 's:\\(.*\\)\\.jar:\\1:g'`
  mkdir -p $dirname
  unzip -q $x -d $dirname
  rm $x
done 
cp -p %{SOURCE5} ${installDir}-tests/runtests
chmod 755 ${installDir}-tests/runtests
%if ! %{ship_tests}
%if ! %{run_tests}
rm -rf ${installDir}-tests
%endif
%endif

%if %{run_tests}
%check
installDir=${RPM_BUILD_ROOT}/%{eclipse_base}/dropins/cdt
# Copy the SDK to simulate real system
rm -rf SDK.fortests
cp -rpL %{eclipse_base} SDK.fortests
# Remove any CDT or CDT tests we may have currently installed
rm -rf SDK.fortests/dropins/cdt*
cp -rpL $installDir SDK.fortests/dropins
# The libhover plugin offers lots of completions but these cause issues
# with some of the tests which expect only a few completions.  We should
# update the tests or something ...
rm -rf SDK.fortests/dropins/cdt/eclipse/plugins/org.eclipse.linuxtools.libhover.*
cp -rpL ${installDir}-tests SDK.fortests/dropins
# FIXME:  I'd like to simulate real life with something like this ...
#chown -R root:root SDK.fortests
SDK.fortests/dropins/cdt-tests/runtests -e $(pwd)/SDK.fortests
w3m -cols 120 -dump results-*/html/org.eclipse.cdt.testing.html
%if ! %{ship_tests}
rm -rf ${installDir}-tests
%endif
%endif

%clean 
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-,root,root)
%{eclipse_base}/dropins/cdt

%files sdk
%defattr(-,root,root)
%{eclipse_base}/dropins/cdt-sdk

%files parsers
%defattr(-,root,root)
%{eclipse_base}/dropins/cdt-parsers

%if %{ship_tests}
%files tests
%defattr(-,root,root)
%{eclipse_base}/dropins/cdt-tests
%endif

%changelog
* Tue May 18 2010 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.2-3
- Resolves: #592386
- Rebase Autotools/Libhover to Linux tools R0.5.1.
- Remove addbuilder patch which is already part of R0_5_1.
- Remove libhover template patch which is alread part of R0_5_1.

* Thu May 13 2010 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.2-2
- Resolves: #591324
- Add requirement for libtool which is required by Autotools plugin.

* Fri Mar 19 2010 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.2-1
- Resolves: #566761
- Rebase CDT to Galileo SR2 (6.0.2).
- Rebase Autotools to Linux tools R0.5.
- Rebase Libhover to Linux tools R0.5.
- Move Autotools macros to org.eclipse.linuxtools.cdt.autotools.core.

* Fri Jan 15 2010 Jeff Johnston	<jjohnstn@redhat.com> 1:6.0.1-9
- Resolves: #546784
- Fix URLs for Autotools and Libhover which are fetched here.
- Make fetch scripts sources.

* Fri Dec 11 2009 Jeff Johnston	<jjohnstn@redhat.com> 1:6.0.1-7
- Resolves: #546784
- Rebase Autotools to Linux tools 0.4.0 release plus patches.
- Rebase Libhover to Linux tools 0.4.0 release.
- Remove Libhover patch which is already part of rebase.

* Fri Dec 11 2009 Andrew Overholt <overholt@redhat.com> 1:6.0.1-6.1
- Only build on x86 and x86_64 for RHEL 6.

* Wed Oct 28 2009 Alexander Kurtakov <akurtako@redhat.com> 1:6.0.1-6
- Disable mylyn bridge build, part of eclipse-mylyn srpm now.

* Tue Oct 27 2009 Alexander Kurtakov <akurtako@redhat.com> 1:6.0.1-5
- Sync build_id with upstream 6.0.1.

* Fri Oct 16 2009 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.1-4
- Rebase Autotools to 1.0.5.
- Add patch to move macro hover docs locally into Autotools plugin.

* Thu Oct 15 2009 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.1-3
- Include installed link for lpg java bundle in new cdt-parsers subpackage.

* Wed Oct 14 2009 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.1-2
- Ship new parsers sub-package which includes xlc, upc, and lrparser plug-ins.
- Require lpg-java-compat for build.

* Fri Oct 09 2009 Jeff Johnston  <jjohnstn@redhat.com> 1:6.0.1-1
- Rebase CDT to 6.0.1.

* Mon Oct 05 2009 Andrew Overholt <overholt@redhat.com> 1:6.0.0-11
- Build on ppc64

* Wed Sep 23 2009 Jeff Johnston <jjohnstn@redhat.com> 1:6.0.0-10
- Resolves #290247
- Upgrade libhover to 0.3.0.
- Add libhover patch to fix libstdc++ member resolution and
  to place libhover docs locally within libhover plugin.

* Wed Aug 12 2009 Andrew Overholt <overholt@redhat.com> 1:6.0.0-9
- Use launcher jar to run metadata generator instead of eclipse binary.

* Wed Aug 12 2009 Andrew Overholt <overholt@redhat.com> 1:6.0.0-8
- Remove shipping of content.xml.

* Wed Jul 29 2009 Jeff Johnston <jjohnstn@redhat.com> 1:6.0.0-7
- Resolves #514629

* Mon Jul 27 2009 Jeff Johnston <jjohnstn@redhat.com> 1:6.0.0-6
- Remove gcj_support.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:6.0.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 24 2009 Jeff Johnston <jjohnstn@redhat.com> 6.0.0-3
- Bump release number.
- Update Autotools to v200907241319 which has CDT 6.0 fixes.

* Wed Jun 17 2009 Jeff Johnston <jjohnstn@redhat.com> 6.0.0-1
- Rebase CDT to 6.0.0.
- Rebase Autotools to v200906171600 snapshot.
- Resolves #280504, #280505, #280506, #280509.

* Mon Jun 15 2009 Jeff Johnston <jjohnstn@redhat.com> 5.0.2-3
- Resolves #280117.

* Wed Apr 08 2009 Jeff Johnston <jjohnstn@redhat.com> 5.0.2-2
- Bump release.

* Tue Apr 07 2009 Jeff Johnston <jjohnstn@redhat.com> 5.0.2-1
- Rebase autotools to 1.0.3.
- Rebase CDT to v200903191301 (5.0.2).

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:5.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jan 16 2009 Jeff Johnston <jjohnstn@redhat.com> 5.0.1-2
- Rebase libhover to 0.1.1 and autotools to 1.0.2.
- Remove patch for 472731 which is already part of rebased autotools sources.

* Fri Nov 28 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.1-1
- Rebase to CDT 5.0.1.
- Fix bug in autotools project type detection.
- Resolve #472731

* Mon Nov 17 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-12
- Fix typo in autotools and libhover sources tarballs.
- Remove redundant patches which are already in new tarballs.

* Thu Nov 06 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-11
- Fix managed configurations dialog problem.
- Update libhover and autotools source tarballs to 20081106 snapshot.

* Thu Oct 16 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-10
- Change runtests section to remove new libhover plugin rather than old
  com.redhat.* autotools plugin.

* Thu Oct 16 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-9
- Fix org.eclipse.linuxtools.libhover.glibc plugin to add toc.xml to
  binary file list.

* Thu Oct 16 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-8
- Fix org.eclipse.linuxtools.libhover.feature to include
  org.eclipse.linuxtools.libhover.library_docs plugin.
- Add work-around patch for managed configurations dialog problem.

* Wed Oct 15 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-7
- Change to use new linuxtools version of autotools-1.0.1.
- Add build of libhover plugins again from linuxtools.

* Tue Sep 09 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-6
- Fix for NPE during alteration of Autotools configuration settings.
- Resolves #461647

* Thu Sep 04 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-5
- Fix for autotools plugin referencing invalid build nature.
- Resolves #461201

* Wed Aug 20 2008 Andrew Overholt <overholt@redhat.com> 5.0.0-4
- Add building and running of tests
- Remove LexerTests until 5.0.1
- Fix fetch script to use new location of PDE Build

* Mon Aug 11 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-3
- Fix build id to be 200806171202.

* Fri Aug 08 2008 Jeff Johnston <jjohnstn@redhat.com> 5.0.0-2
- Add autotools 1.0.0 which supports CDT 5.0.
- Use java -cp to build cdt and autotools instead of eclipse -nosplash.
- Replace fetched source with CDT_5_0_0 tagged sources.

* Wed Aug 06 2008 Andrew Overholt <overholt@redhat.com> 5.0.0-1
- Remove master and testing features
- Move files to dropins/cdt{,-mylyn,-sdk}/eclipse
- Generate p2 metadata

* Fri Aug 01 2008 Andrew Overholt <overholt@redhat.com> 5.0.0-1
- 5.0
- Add Mylyn sub-package
- Disable CPPUnit for now
- Disable autotools until a new snapshot is made that will build with 5.0

* Thu Jul 17 2008 Tom "spot" Callaway <tcallawa@redhat.com> 4.0.3-2
- fix license tag

* Fri Apr 04 2008 Jeff Johnston <jjohnstn@redhat.com> 4.0.3-1
- Rebase to CDT 4.0.3
- Patch openpty code to not reference stropts.h which is no longer shipped
- Update eclipse-cdt-no-tests.patch

* Mon Jan 28 2008 Jeff Johnston <jjohnstn@redhat.com> 4.0.1-4
- Update autotools to 0.9.6
- Includes generic shell script support for makefile generation on
  different platforms

* Wed Dec 05 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.1-3
- Resolves #412651, #412661, #385991 
- Rebase autotools to 0.9.5.3
- Adds glibc C library completion support.
- Fix clean by removal option.
- Add support for changes to configure/autogen command names.
- Add gcj checks for %%post and %%postun steps.

* Wed Oct 24 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.1-2
- Rebase autotools to 0.9.5.1
- Add autotools property tab for C/C++ build.
- Resolves #330701

* Thu Oct 04 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.1-1
- Use official CDT 4.0.1 source tarball
- Update autotools to 0.9.5
- Resolves #315811

* Tue Sep 25 2007 Andrew Overholt <overholt@redhat.com> 4.0.1-0.2.v200709241202cvs
- Fix moving of arch-specific plugins that haven't been updated to new
  version.

* Mon Sep 24 2007 Andrew Overholt <overholt@redhat.com> 4.0.1-0.1.v200709241202cvs
- 4.0.1 RC.
- Update autotools for Binaries fix.

* Thu Sep 13 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-7
- Resolves #288711
- Ensure that all features are unpacked.

* Mon Sep 10 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-6
- Resolves #274551, #253331, #254246, #254248
- Rebase Autotools to 0.9.3 

* Thu Aug 23 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-5
- Add eclipse-cvs-client dependency

* Fri Aug 17 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-4
- Fix release number in Autotools feature to be 0.9.2.

* Thu Aug 16 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-3
- Resolves #251412
- Rebase autotools to 0.9.2
- Add minimum java runtime requirement
- Add direct Autotools wizards
- Add autogen.sh options

* Fri Aug 10 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-2
- Add Epoch 1 back.

* Wed Aug 08 2007 Jeff Johnston <jjohnstn@redhat.com> 4.0.0-1
- Rebase to CDT 4.0.0
- Rebase Autotools to 0.9.1

* Mon Apr 16 2007 Jeff Johnston <jjohnstn@redhat.com> 3.1.2-3
- Add missing gif to org.eclipse.cdt.make.ui.
- Resolves: #236558

* Tue Feb 27 2007 Jeff Johnston <jjohnstn@redhat.com> 3.1.2-2
- Resolves: #229891, #230253, #205310, #229893
- Rebase autotools to 0.0.8.1 source.

* Wed Feb 21 2007 Jeff Johnston <jjohnstn@redhat.com> 3.1.2-1
- Rebase CDT to 3.1.2.
- Rebase autotools to 0.0.8 source.
- Replace subconsole patch with new build console patch.

* Mon Jan 29 2007 Jeff Johnston <jjohnstn@redhat.com> 3.1.1-8
- Resolves: #214624, #224644
- Rebase autotools to 0.0.7 source.

* Wed Jan 17 2007 Jeff Johnston <jjohnstn@redhat.com> 3.1.1-7
- Resolves: #222350
- Rebase autotools to 0.0.6.1 source.
- Add comments.
- Put arch-specific jars in library dir.

* Mon Dec 11 2006 Jeff Johnston <jjohnstn@redhat.com> 3.1.1-6
- Rebase autotools to 0.0.6 source.

* Wed Nov 15 2006 Jeff Johnston <jjohnstn@redhat.com> 3.1.1-5
- Add cppunit support.

* Mon Nov 06 2006 Andrew Overholt <overholt@redhat.com> 3.1.1-4
- Use the new location of copy-platform.

* Thu Oct 19 2006 Ben Konrath <bkonrath@redhat.com> 3.1.1-3
- Remove work-around for gcc bug # 20198.
- Do not include notice.html and epl-v10.html because these files are already
  included in the SDK.
- Put JNI libraries in %%{_libdir}/eclipse.
- Only build the CDT SDK.
- Fix build issue on non-x86 systems.
- Resolves: #208622

* Mon Oct 16 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.1-2
- Replace build patches with sed commands
- Resolves: #208622

* Mon Oct 16 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.1-2
- Fix build so only single platform is built at a time
- Bugzilla 208622

* Thu Sep 28 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.1-1
- Rebase autotools to 0.0.5 source.
- Rebase CDT to 3.1.1 source.
- Bugzilla 206719, 206359, 206164

* Mon Sep 11 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-3
- Add hover help for defined symbols
- Fix bug with defined symbol calculation on file that compilation
  string cannot be fetched for

* Fri Sep 01 2006 Ben Konrath <bkonrath@redhat.com> 3.1.0-2
- Remove jpp in release.
- Require java-gcj-compat >= 1.0.64.

* Tue Aug 29 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_13fc
- Rebase autotools to 0.0.4 source.
- Use ScannerInfoProvider extension instead of DynamicScannerInfoProvider.
- Add sub-console support to CDT.

* Mon Aug 21 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_12fc
- Fix build special targets when project hasn't configured yet.
- Fix to fully reconfigure after configuration options change.
- Fix configuration problem whereby config.sub complains.
- Bugzilla 200000, 201270, 203440

* Tue Aug 08 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_11fc
- Fix Build Special Targets bug when importing a CVS project and
  using ManagedMake Project Wizard.
- Bugzilla 201269

* Mon Jul 31 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_10fc
- Fix bug with library hover help.

* Tue Jul 25 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_9fc
- Remove redundant runtime packages from sdk.

* Tue Jul 25 2006 Ben Konrath <bkonrath@redhat.com> 3.1.0-1jpp_8fc
- Add epoch to sdk requires.

* Mon Jul 24 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_8fc
- Update autotools sources.
- Rebuild.

* Mon Jul 24 2006 Ben Konrath <bkonrath@redhat.com> 3.1.0-1jpp_7fc
- Rebuld.

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> 3.1.0-1jpp_6fc
- Rebuilt

* Thu Jul 20 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_5fc
- Split into main package and sdk sub-package.

* Thu Jul 20 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_4fc
- Add Autotools plug-ins via additional source tarball.

* Wed Jul 19 2006 Igor Foox  <ifoox@redhat.com> 3.1.0-1jpp_3fc
- Rebuild.

* Wed Jul 12 2006 Jeff Johnston  <jjohnstn@redhat.com> 3.1.0-1jpp_2fc
- Add dynamic scannerinfo extension used by Autotools plug-in.

* Mon Jul 10 2006 Andrew Overholt <overholt@redhat.com> 3.1.0-1jpp_1fc
- 3.1.0.

* Thu Jun 08 2006 Andrew Overholt <overholt@redhat.com> 3.1.0-0jpp_0fc.3.1.0RC2 
- 3.1.0 RC2.
- Remove unused hover patch.
- Use newly-created versionless pde.build symlink.
- Remove no-sdkbuild patch.

* Mon Apr 03 2006 Andrew Overholt <overholt@redhat.com> 3.0.2-1jpp_3fc
- Add ia64.

* Tue Mar 07 2006 Andrew Overholt <overholt@redhat.com> 3.0.2-1jpp_2fc
- Bump release.

* Mon Feb 13 2006 Andrew Overholt <overholt@redhat.com> 3.0.2-1jpp_1fc
- 3.0.2.

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1:3.0.1-1jpp_8fc
- bump again for double-long bug on ppc(64)

* Fri Feb 10 2006 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_7fc
- Use Epoch in Requires (rh#180915).
- Require >= 3.1.2 but < 3.1.3 to ensure we get 3.1.2.

* Thu Feb 09 2006 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_6fc
- Make it Require >= 3.1.2.

* Thu Feb 09 2006 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_5fc
- Build against SDK 3.1.2.

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1:3.0.1-1jpp_5fc
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 10 2006 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_4fc
- Rebuild against latest gcc.

* Fri Dec 30 2005 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_3fc
- Fix %%files section to not be x86-specific.

* Fri Dec 16 2005 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_2fc
- Build against gcc 4.1.

* Mon Nov 14 2005 Andrew Overholt <overholt@redhat.com> 3.0.1-1jpp_1fc
- 3.0.1.

* Fri Oct 21 2005 Andrew Overholt <overholt@redhat.com> 3.0.0_fc-2
- Rebuild against gcc 4.0.2

* Tue Aug 23 2005 Andrew Overholt <overholt@redhat.com> 3.0.0_fc-1
- Import new upstream version (3.0).

* Thu Jul 14 2005 Andrew Overholt <overholt@redhat.com> 3.0.0_fc-0.RC2.1
- Import new upstream version (3.0RC2).
- Use gbenson's new aot-compile-rpm and change requirements appropriately.
- Re-enable native compilation - let's see what happens.

* Wed Jun 22 2005 Andrew Overholt <overholt@redhat.com> 3.0.0_fc-0.M7.1
- Import new upstream version (3.0M7).
- Remove refactoring/build.properties patch (now unneeeded).

* Fri Jun 03 2005 Jeff Pound <jpound@redhat.com> 3.0.0_fc-0.M6.8
- Patch refactoring/build.properties to include plugin.properties.
- Temporarily move all *.so's to *.so.bak due to native compilation bug.
- Temporarily remove gcj .jar -> .so db population.

* Mon May 23 2005 Andrew Overholt <overholt@redhat.com> 3.0.0_fc-0.M6.7
- Bring in new I-build to enable jump to Eclipse 3.1M7 and fix some critical
  issues.

* Wed May 11 2005 Ben Konrath <bkonrath@redhat.com> 3.0.0_fc-0.M6.6
- Temporarily disable org.eclipse.cdt.managedbuilder.core_3.0.0/libmngbuildcore.jar.so.

* Wed Apr 27 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0_fc-0.M6.5
- Changed to find-and-aot-compile build usage
- Added "if gcj_support" toggle
- Fixed installing all arch fragments (now only installs one (correct) arch)
- Redid BuildRequires and Requires to remove old/unneeded dependencies
- Cleaned %%eclipse_arch declares.

* Thu Apr 21 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0_fc-0.M6.4
- Added Chris Moller's libhover patch

* Sat Apr 16 2005 Ben Konrath <bkonrath@redhat.com> 3.0.0_fc-0.M6.3
- Clean up spec file (remove references to old patches and rh docs).

* Fri Apr 15 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0_fc-0.M6.2
- Generated tarball from official final tagged M6 build

* Mon Apr 11 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0_fc-0.M6.1
- Fixed db path in java -cp
- Regenerated tarball from M6 canditate build
- Reworked patches for M6 canditate Build

* Thu Apr 07 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0_fc-0.M5.4
- Changed Requires eclipse-ui to eclipse-platform
- Added Requires java-1.4.2-gcj-compat >= 1.4.2.0-40jpp_14rh
- Added Requires gcc-java >= 4.0.0-0.35

* Mon Apr 04 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0_fc-0.M5.3
- Added eclipse-cdt-no-sdkbuild.patch to build for platform only (fc4 space crunch)

* Sun Apr 03 2005 Andrew Overholt <overholt@redhat.com> 3.0.0_fc-0.M5.2
- Make use of rebuild-gcj-db.
- Use system-wide classmap.db.

* Wed Mar 23 2005 Phil Muldoon <pmuldoon@redhat.com> 3.0.0-1
- Updated to upstream CDT 3.0.0 M5 sources
- Removed Source1 (rhdocs) for now
- Removed libhover patch until updated
- Added eclipse-cdt-platform-build-linux.patch
- Added eclipse-cdt-sdk-build-linux.patch
- Stopped tests build for now (Added eclipse-cdt-no-tests.patch)
- Added Requires gcc-java (bz# 151866)
- Added new central db logic

* Fri Mar 4 2005 Phil Muldoon <pmuldoon@redhat.com> 2.0.2-3
- Added x86_64 to ExclusiveArch

* Thu Mar 3 2005 Phil Muldoon <pmuldoon@redhat.com> 2.0.2-2
- Moved upstream sources back to 2.0.2
- Revered back to releng build
- Added native build sections to spec file

* Tue Jan 11 2005 Ben Konrath <bkonrath@redhat.com> 2.1.0-1
- add devel rpm and use the patched sources for it
- update sources to 2.1.0
- new build method that does not require pre-fetched sources

* Sun Nov 07 2004 Ben Konrath <bkonrath@redhat.com> 2.0.2-1
- Update sources to 2.0.2
- Change which files are unzipped in the install phase - this changed in 2.0.2
- Update Red Hat documentation sources
- Remove no-cvs-patch as it is no longer needed (no-cvs2-patch is still needed)
- Update ui-libhover-patch 
- Add how-to document for doc and source tarball generation
- Add fetch-tests-patch for tarball generation

* Mon Jul 26 2004 Jeremy Handcock <handcock@redhat.com> 2.0-11
- Update Red Hat documentation sources

* Fri Jul 23 2004 Tom Tromey <tromey@redhat.com> 2.0-10
- Set user.home on all java invocations

* Fri Jul 23 2004 Tom Tromey <tromey@redhat.com> 2.0-9
- Pass dontFetchAnything to the build

* Fri Jul 23 2004 Tom Tromey <tromey@redhat.com> 2.0-8
- Patch from Phil Muldoon to avoid cvs operations

* Fri Jul 23 2004 Jeremy Handcock <handcock@redhat.com> 2.0-7
- Don't build on ppc64
- Require eclipse-ui, not eclipse-platform

* Fri Jul 23 2004 Tom Tromey <tromey@redhat.com> 2.0-6
- Set user.home when building

* Wed Jul 21 2004 Tom Tromey <tromey@redhat.com> 2.0-5
- Make .so files executable

* Wed Jul 21 2004 Chris Moller <cmoller@redhat.com> 2.0-4
- Add texthover

* Tue Jul 20 2004 Jeremy Handcock <handcock@redhat.com> 2.0-4
- Update Red Hat documentation sources

* Fri Jul 16 2004 Tom Tromey <tromey@redhat.com> 2.0-3
- Make platform symlink tree before building

* Fri Jul 16 2004 Jeremy Handcock <handcock@redhat.com> 2.0-3
- Add Red Hat-specific documentation
- Use `name' macro in source and patch names
- Correct BuildRequires to eclipse-platform

* Tue Jul 13 2004 Jeremy Handcock <handcock@redhat.com> 2.0-2
- Don't require ant
- Prevent possible `build' section overload

* Mon Jul 12 2004 Tom Tromey <tromey@redhat.com> 2.0-2
- Document source fetching process
- Update to CDT 2.0 final
- Set -D_GNU_SOURCE when building

* Fri Jul  9 2004 Tom Tromey <tromey@redhat.com> 2.0-2
- Don't define prefix
- Don't require pango

* Fri Jul  9 2004 Jeremy Handcock <handcock@redhat.com> 2.0-2
- Update sources to include tests from upstream
- Add new build patch for CDT tests
- Build CDT tests, but don't install them

* Thu Jul  8 2004 Tom Tromey <tromey@redhat.com> 2.0-1
- Removed unused patch

* Thu Jul  8 2004 Jeremy Handcock <handcock@redhat.com> 2.0-1
- Revert previous patch; don't unset javacVerbose

* Thu Jul  8 2004 Jeremy Handcock <handcock@redhat.com> 2.0-1
- Unset javacVerbose

* Tue Jun 15 2004 Tom Tromey <tromey@redhat.com> 2.0-1
- Updated to 2.0 M8

* Mon Jan 19 2004 Tom Tromey <tromey@redhat.com> 1.2.1-1
- Initial version
