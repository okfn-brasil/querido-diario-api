# Documentação da Estrutura de Testes

Este documento descreve a organização dos testes e as boas práticas seguidas neste projeto.

## Organização dos Testes

Os testes estão organizados em módulos focados para melhorar a manutenibilidade e reduzir duplicação de código:

### Testes do URL Builder

A funcionalidade do URL builder foi dividida em módulos de teste focados:

- **`test_url_builder_base.py`**: Classe base com setUp/tearDown comum para testes de URL
- **`test_url_builder_relative_paths.py`**: Testes para manipulação de caminhos relativos (novo formato de dados)
- **`test_url_builder_replacement.py`**: Testes para transformação/substituição de URLs (migração de dados legados)
- **`test_url_builder_gazette.py`**: Testes para integração de URLs com objetos de diário
- **`test_url_builder_themed_excerpt.py`**: Testes para integração de URLs com objetos de excertos temáticos

### Módulos Auxiliares

- **`test_helpers.py`**: Mocks reutilizáveis e funções auxiliares para testes de API
  - Implementações mock de todas as interfaces
  - Funções factory para criar mocks configurados
  - `create_default_mocks()` para configuração rápida de testes

### Arquivos de Teste Principais

- **`test_api.py`**: Testes dos endpoints da API
- **`test_suggestion_service.py`**: Testes do serviço de sugestões
- **`test_config.py`**: Testes de configuração

## Boas Práticas Implementadas

### 1. DRY (Don't Repeat Yourself - Não se Repita)

- **Classes base**: `BaseUrlBuilderTest` fornece setUp/tearDown comum
- **Funções auxiliares**: Funções reutilizáveis em `test_helpers.py` evitam duplicação
- **Métodos factory**: `_build_message_data()`, `_create_gazette_hit()`, etc.

### 2. setUp e tearDown

Todas as classes de teste usam adequadamente os métodos `setUp()` e `tearDown()`:

```python
class MeuTeste(unittest.TestCase):
    def setUp(self):
        # Inicializa fixtures comuns do teste
        self.mock_client = MagicMock()
        
    def tearDown(self):
        # Limpa recursos se necessário
        pass
```

### 3. Nomes Descritivos de Testes

Métodos de teste seguem o padrão: `test_<o_que>_<cenario>_<esperado>`

Exemplos:
- `test_relative_path_with_endpoint_builds_full_url`
- `test_gazette_object_url_transformation`
- `test_replace_flag_case_insensitive`

### 4. Organização dos Testes

- **Um conceito por arquivo de teste**: Cada arquivo testa um componente ou funcionalidade específica
- **Agrupamento lógico**: Testes relacionados estão na mesma classe
- **Separação clara**: Testes unitários vs testes de integração

### 5. Usando subTest para Testes Paramétricos

Ao testar múltiplos cenários similares:

```python
for flag_value in ["TrUe", "TRUE", "True", "tRuE"]:
    with self.subTest(flag_value=flag_value):
        # Código do teste aqui
```

### 6. Métodos Auxiliares

Métodos auxiliares internos começam com `_` para distinguir dos testes:

```python
def _create_gazette_hit(self, url, txt_url=None):
    """Helper para criar um objeto de hit de diário"""
    # Implementação
```

### 7. Gerenciamento de Mocks

- Mocks são criados no `setUp()` para garantir isolamento
- Use `MagicMock` para mocking flexível
- Configure valores de retorno explicitamente para clareza

## Executando os Testes

```bash
# Executar todos os testes
make test

# Executar testes sem recriar serviços
make retest

# Executar com cobertura
make coverage

# Executar em shell de teste para depuração
make test-shell
```

## Métricas dos Testes

- Total de testes: 76 testes
- Tempo de execução: ~0.18 segundos
- Todos os testes passando (1 falha esperada)
- Código formatado com Black

## Adicionando Novos Testes

Ao adicionar novos testes:

1. **Use classes base existentes** se estiver testando funcionalidade de URL
2. **Use test_helpers** para criar mocks
3. **Siga as convenções de nomenclatura** para facilitar descoberta
4. **Adicione setUp/tearDown** se você tiver configuração comum
5. **Use subTest** para cenários paramétricos
6. **Documente cenários complexos** com docstrings

## Exemplo: Adicionando um Novo Teste de URL

```python
from tests.test_url_builder_base import BaseUrlBuilderTest
from utils import build_file_url

class TestMinhaNovaFuncionalidade(BaseUrlBuilderTest):
    """Testes para minha nova funcionalidade"""
    
    def test_meu_cenario(self):
        """Testa que minha funcionalidade funciona como esperado"""
        self.set_env(QUERIDO_DIARIO_FILES_ENDPOINT="example.com")
        result = build_file_url("path/to/file.pdf")
        self.assert_url_equals(result, "https://example.com/path/to/file.pdf")
```

## Notas de Migração

A estrutura de testes foi refatorada em 2026-01-13 para:
- Reduzir duplicação de código de ~1800 linhas com muita repetição
- Melhorar a manutenibilidade organizando em módulos focados
- Seguir boas práticas do unittest com setUp/tearDown
- Criar funções auxiliares e classes base reutilizáveis

Arquivos de teste anteriores eram:
- `test_url_builder.py` (206 linhas) → dividido em 4 módulos focados
- `test_gazette_file_url_builder.py` (319 linhas) → mesclado em `test_url_builder_gazette.py`
- `test_themed_excerpt_file_url_builder.py` (257 linhas) → mesclado em `test_url_builder_themed_excerpt.py`

## Benefícios da Refatoração

### Antes
- ❌ Muita duplicação de código (especialmente `with patch.dict`)
- ❌ Pouco uso de setUp/tearDown (apenas 7 ocorrências)
- ❌ Código repetitivo para configuração de ambiente
- ❌ Arquivos grandes e difíceis de navegar

### Depois
- ✅ Classes base reutilizáveis com setUp/tearDown adequado
- ✅ Helpers centralizados para criação de mocks
- ✅ Testes organizados por funcionalidade
- ✅ Código mais limpo e manutenível
- ✅ Mais fácil adicionar novos testes
- ✅ Uso de subTest para testes paramétricos

## Estrutura de Diretórios

```
tests/
├── README.md                                # Esta documentação
├── __init__.py
├── test_helpers.py                          # Mocks e helpers reutilizáveis
├── test_url_builder_base.py                 # Classe base para testes de URL
├── test_url_builder_relative_paths.py       # Testes de caminhos relativos
├── test_url_builder_replacement.py          # Testes de substituição de URL
├── test_url_builder_gazette.py              # Testes de URL com diários
├── test_url_builder_themed_excerpt.py       # Testes de URL com excertos
├── test_api.py                              # Testes dos endpoints da API
├── test_suggestion_service.py               # Testes do serviço de sugestões
└── test_config.py                           # Testes de configuração
```

## Contribuindo

Ao contribuir com novos testes:

1. Mantenha a estrutura organizada
2. Reutilize helpers e classes base existentes
3. Escreva testes claros e bem documentados
4. Execute `make retest` antes de fazer commit
5. Certifique-se de que o Black formatou seu código
6. Adicione documentação para cenários complexos
