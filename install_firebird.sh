#!/bin/bash
echo "Baixando e instalando Firebird Client..."

# Baixar a biblioteca Firebird Client (versão 3.0)
wget https://github.com/FirebirdSQL/firebird/releases/download/v3.0.10/Firebird-3.0.10.33601-0.amd64.tar.gz

# Extrair os arquivos
tar -xzf Firebird-3.0.10.33601-0.amd64.tar.gz

# Criar diretório para as bibliotecas
mkdir -p firebird_lib

# Mover a biblioteca necessária para o diretório do projeto
mv Firebird-3.0.10.33601-0.amd64/lib/libfbclient.so firebird_lib/

echo "Firebird Client instalado com sucesso!"
