**Português (BR)** | [English (US)](/docs/CONTRIBUTING-en-US.md)

# Contribuindo
O Querido Diário possui um [Guia para Contribuição](https://docs.queridodiario.ok.org.br/pt-br/latest/contribuindo/guia-de-contribuicao.html#contribuindo) principal que é relevante para todos os seus repositórios. Este guia traz informações gerais sobre como interagir com o projeto, o código de conduta que você adere ao contribuir, a lista de repositórios do ecossistema e as primeiras ações que você pode tomar. Recomendamos sua leitura antes de continuar.

Já leu? Então vamos às informações específicas deste repositório:
- [Arquitetura](#arquitetura)
- [Como configurar o ambiente de desenvolvimento](#como-configurar-o-ambiente-de-desenvolvimento)
    - [Em Linux](#em-linux)
- [Testes](#testes)

## Arquitetura
![arquitetura](/docs/images/arquitetura.png)

 Abaixo, uma breve descrição de seus componentes: 
| **Tipo**  | **Nome**                                           | **Descrição**                                                                                      | **Dependências**                    |
|-----------|----------------------------------------------------|----------------------------------------------------------------------------------------------------|-------------------------------------|
| Aplicação | [`api`](/api)                                      | Configuração e criação de endpoints da API.                                                        | _serviços e recursos_               |
| Aplicação | [`main`](/main)                                    | Configuração e execução da API.                                                                    | _api, serviços, módulos e recursos_ |
| Serviço   | [`cities`](/cities)                                | Consultas ao banco do [Censo de Diários Municipais](https://censo.ok.org.br).                      | Banco de dados do Censo             |
| Serviço   | [`companies`](/companies)                          | Consultas ao banco de dados de CNPJ.                                                               | database                            |
| Serviço   | [`gazettes`](/gazettes)                            | Consultas ao índice de busca textual principal do QD.                                              | index                               |
| Serviço   | [`suggestions`](/suggestions)                      | Envio de emails de sugestão.                                                                       | Mailjet                             |
| Serviço   | [`themed_excerpts`](/themed_excerpts)              | Consultas ao índices de busca textual temáticos do QD.                                             | index                               |
| Módulo    | [`database`](/database)                            | Classe de interação com bancos de dados Postgres.                                                  | Postgres                            |
| Módulo    | [`config`](/config)                                | Configuração de variáveis de ambiente.                                                             |                                     |
| Módulo    | [`index`](/index)                                  | Classe de interação com índices Opensearch.                                                        | Opensearch                          |
| Recurso   | Postgres                                           | Banco de dados de CNPJ. Contém informações sobre empresas e sócios cadastrados na Receita Federal. |                                     |
| Recurso   | Banco de dados do [Censo](https://censo.ok.org.br) | Banco de dados de municípios. Contém metadados municipais.                                         |                                     |
| Recurso   | Opensearch                                         | Índices de busca textual.                                                                          |                                     |
| Recurso   | Mailjet                                            | Serviço de envio de email.                                                                         |                                     |

## Como configurar o ambiente de desenvolvimento

### Em Linux

A API é construída e executada em contêineres [`podman`](https://podman.io/). Para conhecer mais sobre o `podman`, veja esta [postagem da Red Hat](https://www.redhat.com/pt-br/topics/containers/what-is-podman) ou navegue nos [tutoriais](https://docs.podman.io/en/latest/Tutorials.html) de sua documentação. E é desenvolvida em [Python](https://docs.python.org/3/) (3.6+) utilizando as bibliotecas [FastAPI](https://fastapi.tiangolo.com/) e [Pydantic](https://docs.pydantic.dev/), assim como outras bibliotecas que permitem interação com os recursos da tabela acima. 

1. Instale o [`podman`](https://podman.io/) em sua máquina. Ele existe em quase todos os repositórios de pacotes de distribuição Linux. Consulte a [documentação do podman](https://podman.io/getting-started/installation.html) para entender como instalá-lo na distribuição que utiliza.

2. Abra um terminal no diretório do seu clone deste repositório

3. Construa a imagem do contêiner usado no desenvolvimento com o seguinte comando: 
```
make build
```

4. Pronto! Com isso, você terá uma imagem do contêiner que poderá executar a API localmente no processo de desenvolvimento.


## Testes
Este projeto foi desenvolvido com o paradigma TDD (Test Driven-Development). Isso significa que não há mudanças sem testes. Devemos sempre buscar ter uma cobertura de testes de todo código-fonte. Outra maneira de encarar os testes é o seguinte:

> “Escreva o teste que o força a escrever o código que você já sabe que quer escrever” 
> Por Robert C. Martin (a.k.a. Uncle Bob), tradução nossa.

Para executar os testes, faça o seguinte:

```bash
make test
```

ATENÇÃO: Não é necessário reiniciar a base de teste a cada vez que você quiser executar os testes. Uma vez que o banco de dados esteja em execução, você só precisa rodar o  `make retest` novamente. Se você remover o banco de dados com `make destroydatabse` ou reiniciar a máquina, você terá que iniciar o banco de dados novamente. 

Para checar a cobertura do código:

```bash
make coverage
```

# Mantendo
As pessoas mantenedoras devem seguir as diretrizes do [Guia para Mantenedoras](https://docs.queridodiario.ok.org.br/pt-br/latest/contribuindo/guia-de-contribuicao.html#mantendo) do Querido Diário.
