# ForkUpTool
## Ferramenta de customização de forks

Este repositório contém a implementação do protótipo da ferramenta ForkUpTool. Trata-se de uma ferramenta web escrita em Python com uso do framework Django.

Um vídeo ilustrativo de uso da ferramenta, bem como arquivos necessários para reprodução do exemplo apresentado no vídeo, estão disponíveis [aqui](example).


As demais pastas fazem parte da estrutura do projeto seguindo o padrão Django.

***

### Instruções para deploy em ambiente Linux (Ubuntu)

#### Crie um ambiente virtual com "virtualenv"
``` virtualenv -p python3 forkupenv ```

#### Ative o ambiente virtual 
``` cd forkupenv ```

``` source bin/activate ```

#### Navegue até a pasta onde o projeto foi clonado
``` cd ~/xxxx/forkuptool ```

#### Instale as dependências do projeto
``` pip install -r requirements.txt ```

#### Crie um usuário para acesso ao sistema (superuser)
``` python manage.py createsuperuser ```


### Subindo a aplicação 
Depois de ativar o ambiente virtual e entrar na pasta da aplicação, rode o seguinte comando:

``` python manage.py runserver ```

Abra seu navegador e acesse:

http://localhost:8000/