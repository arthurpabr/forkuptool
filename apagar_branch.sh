#!/bin/bash
branch=$1
echo "Apagando branch $branch - início"
caminho_repositorio="/home/arthur/dev_ifsuldeminas/suap"
cd $caminho_repositorio
git branch -D $branch
echo "Apagando branch $branch - fim"
