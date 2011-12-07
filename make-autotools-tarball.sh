#!/bin/sh
rel=R0_5_1
tag=`echo $rel | sed -e 's/\./_/g'`
echo $tag
mkdir -p temp && cd temp
rm -rf autotools
svn export svn://dev.eclipse.org/svnroot/technology/org.eclipse.linuxtools/autotools/tags/$tag autotools
cd autotools
pwd
rm -rf org.eclipse.linuxtools.cdt.autotools.tests
rm -rf org.eclipse.linuxtools.cdt.autotools.ui.tests
tar -czvf eclipse-cdt-fetched-src-autotools-$tag.tar.gz org.eclipse.linuxtools.cdt.autotools*

