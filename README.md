# querido-diario-api

______________________________________

_[Click here](docs/languages/en-US/README.md) to read this article in english._
______________________________________

Seja bem-vinda(o) ao projeto Querido Diário API! O objetivo deste repositório é manter o código-fonte da API que disponibiliza os diários oficiais raspados pelo [Querido Diário](https://github.com/okfn-brasil/querido-diario). 

## Requisitos

Todo o projeto é construído e executado em contêineres e é compatível apenas com ambientes Linux (por enquanto). Como executamos tudo dentro de contêineres, você só precisa instalar o [`podman`](https://podman.io/) para rodar localmente em sua máquina. Se você não está familiarizado com o `podman`, você pode pensá-lo como um `docker` /` docker-compose` mais “leve”. Ele existe em quase todos os repositórios de pacotes de distribuição Linux. Por favor, consulte a  [documentação do podman](https://podman.io/getting-started/installation.html) para entender como instalá-lo em seus ambientes. Se tiver alguma dificuldade com o podman, fale com a gente! 

## Instalação

Para poder executar e testar suas alterações no projeto, primeiro você precisa construir a imagem do contêiner usado no desenvolvimento. Para isso, use o seguinte comando: 

```
make build
```

Com isso, você terá uma imagem do contêiner que poderá executar a API localmente no processo de desenvolvimento. 

## Executando

Para executar a API localmente em sua máquina, use o seguinte comando:

```
make run
```

Esse comando vai iniciar todos os contêineres necessários para executar a API. Ou seja, ele inicializa o banco de dados e o contêiner da API. Se tudo correr bem, você poderá fazer consultas à API em `localhost:8080/gazettes/<City IBGE Code>`

ATENÇÃO: Quando você precisar reiniciar a API, apenas interrompa o processo da API e execute o `make rerun` novamente. Não é necessário reiniciar o banco de dados.

Você pode checar toda a documentação interativa da API em  `localhost:8080/docs`. Nessa página, você pode fazer requisições à API diretamente. Mas, para vê-la funcionar, você precisa inserir dados no banco de dados. Há outro comando, `make apisql`, que abre o `psql` e conecta ao banco de dados. Assim, você pode inserir dados usando alguns `INSERT INTO ...` para testar a API  ;)

### Usando o endpoint de ‘sugestões’

O endpoint de sugestões no Querido Diário é uma forma de coletar feedback dos usuários e usa o serviço do Mailjet para enviar e-mails. É necessário criar um token de acesso em [Mailjet](www.mailjet.com) para executar a aplicação e enviar e-mails (salve em `config/current.env`).

## Testes

Este projeto foi desenvolvido com o paradigma TDD (Test Driven-Development). Isso significa que não há mudanças sem testes. Devemos sempre buscar ter uma cobertura de 100% do código-fonte. Outra maneira de encarar os testes é o seguinte:

> “Escreva o teste que o força a escrever o código que você já sabe que quer escrever” 
> Por Robert C. Martin (a.k.a. Uncle Bob), tradução nossa.

Para executar os testes, faça o seguinte:

```bash
make test
```

ATENÇÃO: Não é necessário reiniciar a base de teste a cada vez que você quiser executar os testes. Uma vez que o banco de dados esteja em execução, você só precisa rodar o  `make retest` novamente. Claro que, se você remover o banco de dados com `make destroydatabse` ou reiniciar a máquina, você terá que iniciar o banco de dados novamente. 

Para checar a cobertura do código:

```bash
make coverage
```

