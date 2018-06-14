# installation
CDATE=20180601

pip3.6 install mecab-python3
GITDIR=./wikiextractor
if [ -e "$GITDIR" ]; then
    echo "Dir $GITDIR exists."
else
    git clone https://github.com/attardi/wikiextractor.git
fi
cd wikiextractor
mkdir extracted2

# download, preprocess and make data
TARGETURL=https://dumps.wikimedia.org/jawiki/$CDATE/jawiki-$CDATE-pages-articles.xml.bz2
TARGETFILE=jawiki-$CDATE-pages-articles.xml.bz2

if [ -e "$TARGETFILE" ]; then
    echo "File $TARGETFILE exists."
else
    curl $TARGETURL >$TARGETFILE
fi

if [ -e "./extracted2" ]; then
    echo "extracted2 directory is."
else
    python3 WikiExtractor.py --json -b 20M -o extracted2 -q $TARGETFILE
fi

cd ..
python3 ExtractCorpus.py wikiextractor/extracted2 ja.text8.$CDATE.100MB

