# math-genealogy

Projeto final para MO412A - Algoritmos em Grafos

Este projeto realiza uma análise da genealogia matemática brasileira utilizando dados do Mathematics Genealogy Project (MGP). O código busca informações sobre matemáticos formados no Brasil, analisa suas relações de orientação (orientador-orientando) e gera estatísticas e visualizações sobre a estrutura do grafo de genealogia acadêmica.

#### Desenvolvido por:
- Lademir Júnior
- Pedro Pereira

## 📋 Requisitos

- Python 3.11 ou superior
- Poetry (gerenciador de dependências)
- Chave de API do Mathematics Genealogy Project

## 🚀 Configuração do Ambiente

### 1. Instalar o Poetry

Se você ainda não tem o Poetry instalado, siga as instruções em [python-poetry.org](https://python-poetry.org/docs/#installation).

### 2. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd math-genealogy
```

### 3. Instalar as dependências

```bash
poetry install
```

**Nota:** O projeto também utiliza a biblioteca `networkx`, que precisa ser adicionada manualmente caso não esteja instalada:

```bash
poetry add networkx
```

Ou, se preferir usar pip diretamente:

```bash
pip install networkx
```

### 4. Configurar as credenciais da API

1. Obtenha sua chave de API do Mathematics Genealogy Project em [mathgenealogy.org](https://www.mathgenealogy.org/).

2. Crie um arquivo `.credentials.txt` na raiz do projeto:

```bash
echo "sua-chave-api-aqui" > .credentials.txt
```

Ou edite manualmente o arquivo `.credentials.txt` e cole sua chave de API (uma única linha, sem aspas).

**Importante:** O arquivo `.credentials.txt` está no `.gitignore` e não será versionado. Mantenha suas credenciais seguras!

## ▶️ Como Executar

### Ativar o ambiente virtual do Poetry

```bash
poetry shell
```

### Executar o script principal

```bash
python src/main.py
```

Ou, se estiver usando Poetry:

```bash
poetry run python src/main.py
```

## 📊 O que o Script Faz

O script realiza as seguintes etapas:

1. **Busca IDs de matemáticos formados no Brasil** - Consulta a API do MGP para obter todos os IDs de matemáticos que se formaram no Brasil.

2. **Busca detalhes de cada matemático** - Oferece dois métodos de busca:
   - **Paralelo** (padrão): Múltiplas requisições simultâneas (rápido)
   - **Sequencial**: Uma requisição por vez (lento, mas seguro)

3. **Análise de orientadores** - Identifica os matemáticos que mais orientaram alunos no Brasil.

4. **Análise de universidades** - Lista as universidades brasileiras que mais formaram doutores.

5. **Análise de descendentes** - Identifica o matemático formado no Brasil com mais descendentes acadêmicos.

6. **Análise do grafo** - Analisa a estrutura do grafo de genealogia:
   - Vértices isolados
   - Componentes conexos
   - Identificação de componente gigante

## 💾 Arquivos Gerados

- **`cache_brazil_data.json`**: Cache com os dados coletados da API (permite reutilização sem novas requisições)
- **`matematicos_brasil.csv`**: Arquivo CSV com informações resumidas de cada matemático:
  - ID
  - Nome
  - Número de descendentes
  - Número de orientandos diretos

## 🔧 Estrutura do Projeto

```
math-genealogy/
├── src/
│   └── main.py              # Script principal
├── utils/
│   └── credentials.py       # Função para ler credenciais
├── notebook/
│   └── mathgenealogy.ipynb  # Notebook Jupyter (análises exploratórias)
├── graph/                   # Arquivos relacionados ao grafo
├── images/                  # Imagens geradas
├── pyproject.toml           # Configuração do Poetry
└── README.md                # Este arquivo
```

## 📝 Notas Importantes

- O script utiliza cache para evitar requisições desnecessárias à API. Se um cache existir, você será perguntado se deseja utilizá-lo.
- As requisições são feitas com rate limiting através de workers paralelos (padrão: 10 workers).
- O tempo de execução depende do método escolhido e da quantidade de dados a serem processados.

## 🐛 Solução de Problemas

### Erro ao ler credenciais
- Verifique se o arquivo `.credentials.txt` existe na raiz do projeto
- Confirme que a chave de API está em uma única linha, sem espaços extras

### Erro de dependências
- Execute `poetry install` novamente
- Certifique-se de que `networkx` está instalado: `poetry add networkx`

### Erro de conexão com a API
- Verifique sua conexão com a internet
- Confirme que sua chave de API é válida
- Verifique se o serviço da API está disponível

## 📄 Licença

Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
