#! /bin/bash
#
# $0 [url]

defdst=$PWD/save.dir

if [ $# -eq 1 ] ; then
  dst=$1
  shift 1
else
  dst=file://$defdst
fi

nom=test
autrenom=test2
src=init.dir
tst=test.dir

function sid()
{
  echo "# sid.py $@"
  ./sid.py "$@"
}

# arborescence minimale avec sous répertoire
mkdir $src
echo "fichier initial titi" >> $src/titi
echo "fichier initial toto" >> $src/toto
mkdir $src/subdir
echo "fichier initial subdir/titi" >> $src/subdir/titi
ln -s ./titi $src/lien

# création de la sauvegarde
sid create --pass foo $nom $src $dst "$@"
sid list
#sid ls -n $nom

# restorations
sid restore --pass foo $nom $tst
echo '# comparaison de la restoration'
diff -r $src $tst
rm -rf $tst

sid restore --pass foo $dst $tst
echo '# comparaison de la restoration'
diff -r $src $tst
rm -rf $tst

# modifications M D A
echo "titi modifié" >> $src/titi
echo "titi modifié 2" >> $src/subdir/titi
rm -f $src/toto
echo "fichier initial tata" > $src/tata

sid update --pass foo $nom

sid restore --pass foo -u $dst $tst
echo '# comparaison de la restoration'
diff -r $src $tst

# cleanup
rm -rf $src $tst $defdst
