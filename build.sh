#sed 's/$/\r/' <../aitest.py> aitest.py
#sed 's/$/\r/' <../map.py> map.py
#sed 's/$/\r/' <../region.py> region.py

if [ -n $1 ]
then
    zip zips/$1.zip *.py
else
    zip zips/new.zip *.py
fi


