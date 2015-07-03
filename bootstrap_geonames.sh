aria2c -s 5 -x 5 http://download.geonames.org/export/zip/US.zip
mv US.zip zip_US.zip
unzip zip_US.zip
mv US.txt zip_US.txt
rm -rf readme.txt
aria2c -s 5 -x 5 http://download.geonames.org/export/dump/US.zip
unzip US.zip
rm -rf readme.txt
aria2c -s 5 -x 5 http://download.geonames.org/export/dump/allCountries.zip
unzip allCountries.zip
rm -rf readme.txt
aria2c -s 5 -x 5 http://download.geonames.org/export/dump/cities1000.zip
unzip cities1000.zip
rm readme.txt
pyenv local 3.4.3
python process_geonames_us.py
rm *.zip
rm *.txt
