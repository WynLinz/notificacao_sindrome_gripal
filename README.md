
## Monitoramento de Síndrome Gripal

Projeto que consiste em uma aplicação desenvolvida com **Django Framework** para consumir e gerenciar dados da **API de Notificações de Síndrome Gripal**, integrada ao catálogo do Governo Federal (Conecta gov.br).

## Sobre a API

A API utilizada é responsável por fornecer dados brutos das notificações de casos suspeitos de síndrome gripal registrados no sistema **e-SUS Notifica**.

### Funcionalidades Integradas:

  * **Consulta de Dados:** Acesso aos registros de notificações por estado ou período.
  * **Transparência:** Ferramenta essencial para análise epidemiológica e monitoramento de saúde pública.
  * **Integração:** Os dados são provenientes da base oficial do Ministério da Saúde.

> [\!IMPORTANT]
> Para mais detalhes técnicos sobre os endpoints e autenticação, acesse a [documentação oficial no portal gov.br](https://www.gov.br/conecta/catalogo/apis/notificacoes-de-sindrome-gripal).

-----

  * **Backend:** [Django Framework](https://www.djangoproject.com/)
  * **Linguagem:** Python
  * **Consumo de API:** Requests / django-ninja / Django Rest Framework (opcional)

-----

## **Instalação e Configuração**

Siga os passos abaixo para configurar o ambiente e instalar as dependências necessárias contidas no arquivo `requirements.txt`.

## Linux (Ubuntu/Debian/Fedora ou Arch Linux)

1.  **Crie um ambiente virtual (recomendado):**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
    obs: se apenas "python" não funcionar, use python3
    

3.  **Instale as dependências:**

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

## Windows

1.  **Crie um ambiente virtual:**

    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```

2.  **Instale as dependências:**

    ```powershell
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

-----

Executar (launch):

Após instalar os requisitos, execute as migrações do banco de dados e inicie o servidor:

```bash
python manage.py migrate
python manage.py runserver
```

O projeto estará disponível em `http://127.0.0.1:8000`.

-----

📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](https://www.google.com/search?q=LICENSE) para mais detalhes.

-----

*Desenvolvido para fins de estudo e integração de dados governamentais.*

-----
