#!/bin/sh

function usage {
cat << _EOF_
usage: $0 [<options>]

Use PDE Build to build Eclipse features

Optional arguments:
   -h      Show this help message
   -e      Eclipse SDK location
   -g      Don't run the tests headless
   -d      Allow remote connection to test runs' JVM
_EOF_
}

debugTests=0
headless=1
while getopts “hgdbe:” OPTION
do
     case $OPTION in
         d)
             debugTests=1
             ;;
         e)
             eclipseHome=$OPTARG
             ;;
         g)
             headless=0
             ;;
         h)
             usage
             exit
             ;;
         ?)
             usage
             exit
             ;;
     esac
done

testSuite=org.eclipse.cdt.testing

if [ -z $eclipseHome ]; then
    eclipseHome=$(rpm --eval "%{_libdir}")/eclipse
fi

cdtTestPluginVersion=$(ls $eclipseHome/dropins/cdt-tests/plugins | \
  grep ${testSuite}_ | sed "s/${testSuite}_//")
testDriver=$eclipseHome/dropins/cdt-tests/plugins/${testSuite}_${cdtTestPluginVersion}/test.xml
properties=$(pwd)/cdt-tests.properties

libraryXml=$eclipseHome/dropins/sdk/plugins/org.eclipse.test/library.xml
results=$(pwd)/results-`date "+%Y%m%d%H%M%S"`
workspace=$(pwd)/workspace
datadir=$(pwd)/testDataDir
homedir=$(pwd)/home
testhome=$(pwd)/testhome
tmpresults=$(pwd)/tmpresults

os=linux
ws=gtk

if uname -m > /dev/null 2>&1; then
	arch=`uname -m`
else
	arch=`uname -p`
fi
# Massage arch for Eclipse-uname differences
case $arch in
	i[0-9]*86)
		arch=x86 ;;
	ia64)
		arch=ia64 ;;
	ppc)
		arch=ppc ;;
	ppc64)
		arch=ppc ;;
	x86_64)
		arch=x86_64 ;;
	*)
		echo "Unrecognized architecture:  $arch" 1>&2
		exit 1 ;;
esac
	echo >&2 "Architecture not specified.  Assuming host architecture: $arch"

setXvnc() {
	echo localhost > Xvnc.cfg
	# Pick a high display number.
	port=`expr '(' $RANDOM '*' 9 / 32767 ')' + 58` 
	$xvnc :$port -screen 1 1024x768x32 -auth Xvnc.cfg -localhost &
	Xvncpid=$!
	DISPLAY=`$HOST`:$port
}

rm $properties
rm -rf $workspace $datadir $homedir $tmpresults $testhome
mkdir -p $workspace $results $datadir $homedir $tmpresults $testhome

echo "data-dir=$datadir" >> $properties
echo "useEclipseExe=true" >> $properties
echo "junit-report-output=$results" >> $properties
echo "results=$results" >> $properties
echo "tmpresults=$tmpresults" >> $properties
echo "testhome=$testhome" >> $properties

echo "cdt-folder=$(pwd)/cdt_folder" >> $properties
echo "cdt-core-loc=$(pwd)/cdt_core_folder" >> $properties
echo "cdt-ui-loc=$(pwd)/cdt_ui_folder" >> $properties
echo "cdt-debug-ui-loc=$(pwd)/cdt_debug_ui_folder" >> $properties
echo "cdt-mbs-core-loc=$(pwd)/cdt_mbs_core_folder" >> $properties
echo "cdt-mbs-ui-loc=$(pwd)/cdt_mbs_ui_folder" >> $properties
if [ $debugTests -eq 1 ]; then
    echo "extraVMargs=-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=40000" >> $properties
fi

if [ $headless -eq 1 ]; then
# Try to find Xvnc
xvnc=
if [ -a /usr/bin/Xvnc ]
then
	xvnc=/usr/bin/Xvnc
	setXvnc
else
	if [ -a /usr/X11/bin/Xvnc ]
	then
		xvnc=/usr/X11/bin/Xvnc
		setXvnc
	else
		DISPLAY=`$HOST`:0.0
	fi
fi

export DISPLAY
fi

$eclipseHome/eclipse \
-Duser.home=$homedir \
-data $workspace \
-application org.eclipse.ant.core.antRunner \
-file $testDriver \
-Declipse-home=$eclipseHome \
-Dlibrary-file=$libraryXml \
-Darch=$arch \
-Dos=$os \
-Dws=$ws \
-propertyfile $properties \
-logger org.apache.tools.ant.DefaultLogger \
-vmargs \
-Duser.home=$homedir

# Clean up if we used Xvnc
if [ -e Xvnc.cfg ]
then
	kill $Xvncpid
	rm Xvnc.cfg
fi
