#!/bin/bash
echo "Atualizando branches - início"
caminho_repositorio="/home/arthur/dev_ifsuldeminas/suap"
branch_origem=$1
branch_forkeado=$2
cd $caminho_repositorio
echo "Atualizando branch $branch_origem"
git checkout $branch_origem
git pull https://ifsuldeminas:w2c5mKtvAtvhdA3bhQSMS3vVQ9685W@gitlab.ifrn.edu.br/cosinf/suap.git
echo "Atualizando branch $branch_forkeado"
git checkout $branch_forkeado
git pull
echo "Atualizando branches - fim"
