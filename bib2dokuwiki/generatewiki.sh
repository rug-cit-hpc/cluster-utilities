#!/bin/bash

if [ $# -ne 3 ]; then
   echo "Specify the bibtex file with all the references, the starting year and ending year"
   exit -1
fi

bibfile=$1
startyear=$2
endyear=$3

cat header.wiki > references.wiki

for year in $( seq $endyear -1 $startyear); do
   bib2bib -c "year=$year" $bibfile > $year.bib
   bibtex2html -nofooter -noheader --no-abstract --no-keywords --nobibsource --nodoc -a $year.bib
   cat << EOF >> references.wiki

=== $year ===

<html>
EOF
   cat $year.html >> references.wiki
   printf "</html>\n" >> references.wiki
   rm $year.bib
   rm $year.html
done
