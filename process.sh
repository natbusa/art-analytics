#!/bin/bash

#tar -zxf test_photos.tgz
#tar -zxf train_photos.tgz

rm -rf preview/ filelists/ sequencefiles/

mkdir filelists
(cd photos; find . -name '*.jpg' | split - -d -a4 -l10000 --additional-suffix= photos_group_ ; mv -f photos_group_* ../filelists) > /dev/null 2>&1

for f in $(ls filelists); do
  sed -i 's/\.\///' filelists/$f
done

mkdir preview
mkdir sequencefiles

for g in photos; do
  for f in $(cd filelists; ls ${g}_*); do
    echo processing $g $f
    for i in $(cat filelists/$f); do  python process_image.py $g/$i preview/ 150 150; done

    (cd preview; tar -czf ../sequencefiles/$f.tgz -T ../filelists/$f ) > /dev/null 2>&1
    java -jar tar-to-seq.jar sequencefiles/$f.tgz sequencefiles/$f.hsf > /dev/null 2>&1
    rm sequencefiles/$f.tgz
    rm sequencefiles/.*.crc
  done
done

#single sequencefile
(cd preview; find . -name "*.jpg" -print | tar -czf ../sequencefiles/photos.tgz --files-from - )
java -jar tar-to-seq.jar sequencefiles/photos.tgz sequencefiles/photos.hsf
rm sequencefiles/photos.tgz