# 🏭🖊️ BluePen Backend (ERP & E-commerce API)

API RESTful desenvolvida com **Django** e **Django REST Framework (DRF)** para gerir integralmente uma fábrica de canetas e a sua loja online. O sistema unifica os processos de venda (E-commerce) com a gestão fabril (ERP), automatizando o controlo de stock, produção, compras e fluxo de caixa.

## 🚀 Funcionalidades Principais

O projeto está dividido em dois módulos principais: **Loja** (Frontend/Cliente) e **Fábrica** (Backoffice/Operacional).

### 🛒 Módulo Loja (E-commerce)
-   **Gestão de Produtos:** Catálogo com cálculo automático de stock disponível.
-   **Pedidos de Venda:** Criação e gestão de pedidos de clientes com validação de stock em tempo real.
-   **Gestão de Utilizadores:** Autenticação (Token/JWT), perfis de utilizador e gestão de múltiplos endereços.
-   **Logística:** Atualização de status de entrega (com simulação automática de entrega via *timer*).

### 🏭 Módulo Fábrica (ERP)
-   **Engenharia de Produto:** Definição de **Ficha Técnica** (`ComposicaoProduto`) para cada caneta (ex: 1 Caneta = 1 Tubo + 1 Ponta + 1 Mola + 0.005L Tinta).
-   **Planeamento e Produção (PCP):**
    -   Gestão de **Ordens de Produção**.
    -   Alocação de Máquinas e Funcionários.
    -   **Controlo de Qualidade (CQ):** Aprovação ou rejeição de lotes produzidos.
-   **Gestão de Stock e Insumos:**
    -   Controlo de Matéria-prima (Insumos) e Fornecedores.
    -   **Pedidos de Compra:** Reposição de insumos.
    -   Movimentações de Stock (Entradas e Saídas) auditáveis.
-   **Financeiro Automatizado:**
    -   **Fluxo de Caixa:** Lançamentos automáticos baseados em eventos do sistema (Venda = Entrada, Compra de Insumo = Saída).
    -   **Custos de Armazenamento:** Rotina automática (`Command`) para calcular depreciação/custo de stock diário.

## 🤖 Automações Inteligentes (Signals & Commands)

Este backend possui uma lógica de negócios avançada implementada via Django Signals e Management Commands:

1.  **Baixa Automática de Insumos:** Quando o Controlo de Qualidade aprova uma Ordem de Produção, o sistema consome automaticamente a matéria-prima necessária baseada na Ficha Técnica e dá entrada no produto acabado.
2.  **Integração Financeira:**
    -   Ao receber um Pedido de Compra de insumos, o sistema gera uma **Saída** no Fluxo de Caixa.
    -   Ao entregar um Pedido de Venda, o sistema gera uma **Entrada** no Fluxo de Caixa.
3.  **Custo Diário:** Um comando personalizado calcula diariamente 2% de custo sobre o valor do stock parado e regista no financeiro.

## 🛠️ Tecnologias Utilizadas

-   **Linguagem:** Python 3.12+
-   **Framework:** Django 5.2 & Django REST Framework
-   **Base de Dados:** SQLite (Desenvolvimento) / PostgreSQL (Produção recomendada)
-   **Autenticação:** Token Authentication & SimpleJWT
-   **Media:** Cloudinary (para armazenamento de imagens dos produtos e avatares)
-   **Outros:** `django-environ`, `corsheaders`, `whitenoise`.

## 📦 Como Executar o Projeto

### Pré-requisitos
-   Python instalado.
-   Git instalado.

### Passo a Passo

1.  **Clonar o repositório:**
    ```bash
    git clone [https://github.com/Vencce/BluePen-Back.git](https://github.com/Vencce/BluePen-Back.git)
    cd BluePen-Back
    ```

2.  **Criar e ativar o ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Instalar dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar Variáveis de Ambiente:**
    Crie um ficheiro `.env` na raiz do projeto (baseado no exemplo abaixo):
    ```env
    DEBUG=True
    SECRET_KEY=sua_chave_secreta_aqui
    DATABASE_URL=sqlite:///db.sqlite3
    CLOUDINARY_URL=cloudinary://sua_url_cloudinary
    ```

5.  **Executar Migrações:**
    ```bash
    python manage.py migrate
    ```

6.  **Criar Superutilizador (Admin):**
    Você pode usar o comando padrão ou o comando personalizado incluído:
    ```bash
    python manage.py createsuperuser
    # OU via variáveis de ambiente (SUPERUSER_USERNAME, etc)
    python manage.py create_default_admin
    ```

7.  **Iniciar o Servidor:**
    ```bash
    python manage.py runserver
    ```

O sistema estará disponível em `http://127.0.0.1:8000`.

## ⚙️ Rotinas Administrativas

Para processar os custos diários de stock (ideal para rodar via CRON):
```bash
python manage.py processar_custos
