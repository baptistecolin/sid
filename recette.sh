#! /bin/bash
#
# $0 [url]

if [ $# -eq 1 ] ; then
  dst=$1
  shift 1
ielse
  dst=file://$PWD/save.dir
fi

nom=test
src=init.dir
tst=test.dir

function sid()
{
  echo "# sid.py $@"
  ./sid.py "$@"
}

# arborescence minimale
mkdir $src
echo "fichier initial titi" >> $src/titi
echo "fichier initial toto" >> $src/toto

# création de la sauvegarde
rm $HOME/.sid/$nom
sid create --pass foo -n $nom -d $src -u $dst "$@"
sid list
sid ls -n $nom

# restorations
sid restore --pass foo -n $nom -d $tst
diff -r $src $tst
rm -rf $tst

sid restore --pass foo -u $dst -d $tst
diff -r $src $tst
rm -rf $tst

# modifications M D A
echo "titi modifié" >> $src/titi
rm -f $src/toto
echo "fichier initial tata" > $src/tata

sid update --pass foo -n $nom

sid restore --pass foo -u $dst -d $tst
diff -r $src $tst

# cleanup
rm -rf $src $dst $tst
