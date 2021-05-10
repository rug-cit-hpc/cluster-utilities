#!/bin/bash

CLEANUPFILE=$1
SOFTWARE=/apps
TRASH="/apps/trash/`date +'%Y-%m-%d'`"
ARCHS="generic sandybridge haswell skylake"

#modules=`grep -v -P "\t" /software/lmod/lmodadmin.txt | grep "/" | sed 's/:$//'`

if [ ! -f "$CLEANUPFILE" ];
then
  echo "Please specify a valid file with modules to be cleaned. This file should have one module (NAME/VERSION) per line."
  exit 1
fi

for module in `cat $CLEANUPFILE`
do
  for arch in $ARCHS
  do
    echo "# $module - $arch"
  
    swname=`echo $module | cut -d '/' -f 1`
    version=`echo $module | cut -d '/' -f 2`
    swdir="$SOFTWARE/$arch/software/$swname/$version"
  
    if [ -d "$swdir" ];
    then
      echo "mkdir -p $TRASH/$arch/software/$swname"
      echo "mv $swdir $TRASH/$arch/software/$swname"
    else
      echo "# Error: installation directory of $module for $arch cannot be found!"
    fi
  
    # The modulefile can either be written in TCL (no file extension), or in LUA (.lua extension), or both.
    if [ -f "$SOFTWARE/$arch/modules/all/$swname/$version" ];
    then
        if [ -f "$SOFTWARE/$arch/modules/all/$swname/$version.lua" ];
        then
            modulefile="$SOFTWARE/$arch/modules/all/$swname/$version $SOFTWARE/$arch/modules/all/$swname/$version.lua"
        else
            modulefile="$SOFTWARE/$arch/modules/all/$swname/$version"
        fi
    else
       	if [ -f "$SOFTWARE/$arch/modules/all/$swname/$version.lua" ];
       	then
       	    modulefile="$SOFTWARE/$arch/modules/all/$swname/$version.lua"
       	else
            modulefile=""
       	fi
    fi

    if [ ! -z "$modulefile" ];
    then
      # Remove the modulefile in "modules/all" and the symlink in "modules/<category>".
      echo "mkdir -p $TRASH/$arch/modules/all/$swname"
      echo "mv $modulefile $TRASH/$arch/modules/all/$swname"
      modulefilelink=`echo $modulefile | sed "s/all/\*/"`
      modulefilelink=`ls -1 $modulefilelink | grep -v "/modules/all/"`
      if [ -f "$modulefilelink" ];
      then
        echo "rm $modulefilelink"
      fi
    else
      echo "# Warning: modulefile of $module for $arch cannot be found!"
    fi
    echo '# -----------'
  done
done

# Find broken symlinks in module dir
# echo "Broken symlinks:"
# find $SOFTWARE/modules -xtype l
