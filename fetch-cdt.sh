#!/bin/sh

CDTTAG=v201002161416
ECLIPSEBASE=$(rpm --eval %{_libdir})/eclipse

mkdir -p temp && cd temp
mkdir -p home
mkdir -p ws
rm -rf org.eclipse.cdt-releng
cvs -d:pserver:anonymous@dev.eclipse.org:/cvsroot/tools export -r $CDTTAG org.eclipse.cdt-releng/org.eclipse.cdt.releng
cd org.eclipse.cdt-releng/org.eclipse.cdt.releng/

# The build.xml doesn't fetch master or testing features so we must add this ourselves.
sed --in-place -e'91,91i\\t\t<ant antfile="build.xml" dir="${pde.build.scripts}" target="fetch">\n\t\t\t<property name="builder" value="${basedir}/master"/>\n\t\t</ant>' build.xml
sed --in-place -e'91,91i\\t\t<ant antfile="build.xml" dir="${pde.build.scripts}" target="fetch">\n\t\t\t<property name="builder" value="${basedir}/testing"/>\n\t\t</ant>' build.xml
sed --in-place -e'71,71i\\t\t<ant antfile="build.xml" dir="${pde.build.scripts}" target="preBuild">\n\t\t\t<property name="builder" value="${basedir}/master"/>\n\t\t</ant>' build.xml
sed --in-place -e'71,71i\\t\t<ant antfile="build.xml" dir="${pde.build.scripts}" target="preBuild">\n\t\t\t<property name="builder" value="${basedir}/testing"/>\n\t\t</ant>' build.xml

# Remove copying of binary jar in build.xml.  We remove this jar so this operation will fail.
sed --in-place -e "/copy file=\"\${buildDirectory}.*net\.sourceforge\.lpg/,/\/>/"d build.xml 

PDEBUILDVERSION=$(ls $ECLIPSEBASE/dropins/sdk/plugins | grep pde.build_ | sed 's/org.eclipse.pde.build_//')
java -cp /usr/lib/eclipse/startup.jar \
     -Duser.home=../../home \
-XX:CompileCommand="exclude,org/eclipse/core/internal/dtree/DataTreeNode,forwardDeltaWith" \
-XX:CompileCommand="exclude,org/eclipse/jdt/internal/compiler/lookup/ParameterizedMethodBinding,<init>" \
-XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/dom/parser/cpp/semantics/CPPTemplates,instantiateTemplate" \
-XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/pdom/dom/cpp/PDOMCPPLinkage,addBinding" \
     org.eclipse.core.launcher.Main             \
  -Dpde.build.scripts=$ECLIPSEBASE/dropins/sdk/eclipse/plugins/org.eclipse.pde.build_$PDEBUILDVERSION/scripts \
  -application org.eclipse.ant.core.antRunner \
  -buildfile build.xml -DbaseLocation=$ECLIPSEBASE \
  -Dpde.build.scripts=$ECLIPSEBASE/dropins/sdk/plugins/org.eclipse.pde.build_$PDEBUILDVERSION/scripts \
  -DcdtTag=$CDTTAG \
  -DdontUnzip=true fetch
#eclipse -nosplash -console

find . -name net.*.jar -exec rm {} \;

cd .. && tar jcf eclipse-cdt-fetched-src-$CDTTAG.tar.bz2 org.eclipse.cdt.releng
