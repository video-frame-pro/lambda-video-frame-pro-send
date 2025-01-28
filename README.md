<p align="center">
  <img src="https://i.ibb.co/zs1zcs3/Video-Frame.png" width="30%" />
</p>


---
Este repositório contém a implementação da **lógica de envio de e-mails** do sistema **Video Frame Pro**, responsável por notificar os usuários sobre o status do processamento de vídeos. 

---

## Função

A função Lambda envia e-mails baseados no status do processamento:

1. **Sucesso**: Um e-mail contendo o link para download do vídeo processado.
   <div align="left">
      <img src="img_sucess.png" alt="E-mail de sucesso" width="400">
   </div>

2. **Erro**: Um e-mail notificando que ocorreu um problema no processamento.
   <div align="left">
      <img src="img_error.png" alt="E-mail de erro" width="400">
   </div>


## Tecnologias

<p>
  <img src="https://img.shields.io/badge/AWS-232F3E?logo=amazonaws&logoColor=white" alt="AWS" />
  <img src="https://img.shields.io/badge/AWS_Lambda-4B5A2F?logo=aws-lambda&logoColor=white" alt="AWS Lambda" />
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Brevo-007DB8?logoColor=white" alt="Brevo" />
  <img src="https://img.shields.io/badge/GitHub-ACTION-2088FF?logo=github-actions&logoColor=white" alt="GitHub Actions" />
</p>

## Estrutura do Repositório

```
/src
├── send
│   ├── lambda_function.py        # Lógica de envio de e-mails
│   ├── requirements.txt          # Dependências do Python
│   ├── __init__.py               # Inicialização do pacote
/tests
├── send
│   ├── test_send.py              # Testes unitários para a função de envio de e-mails
│   ├── requirements.txt          # Dependências do Python para testes
│   ├── __init__.py               # Inicialização do pacote para testes
/infra
├── main.tf                       # Definição dos recursos AWS com Terraform
├── outputs.tf                    # Outputs das funções e recursos Terraform
├── variables.tf                  # Definições de variáveis Terraform
├── terraform.tfvars              # Arquivo com variáveis de ambiente
```

## Como Funciona

1. **E-mail de Sucesso**:
   - Enviado quando o processamento do vídeo é concluído com sucesso.
   - Contém o link para download do vídeo processado.

2. **E-mail de Erro**:
   - Enviado quando ocorre uma falha durante o processamento do vídeo.
   - Notifica o usuário sobre o problema e oferece suporte.

## Passos para Configuração

### 1. Pré-Requisitos

Certifique-se de ter as credenciais da AWS configuradas corretamente, além de ter o **AWS CLI** e o **Terraform** instalados.

### 2. Deploy da Infraestrutura

1. Configure as variáveis no arquivo `terraform.tfvars`:
    - **brevo_token_ssm**: Nome do parâmetro no SSM que armazena a chave da API Brevo.

2. Execute o **Terraform** para provisionar os recursos na AWS:

```bash
cd infra
terraform init
terraform apply -auto-approve
```

Isso criará:
- A função **Lambda** para envio de e-mails.
- O **IAM Role** para concessão de permissões à Lambda.

### 3. Configuração da API Brevo

- Gere uma chave de API no **Brevo** (antigo SendinBlue).
- Armazene essa chave como um parâmetro seguro no AWS Systems Manager Parameter Store.

## Testes

Para testar o envio de e-mails:

1. **E-mail de Sucesso**:
   - Faça uma requisição POST para a função Lambda com o seguinte payload:

```json
{
   "body": {
      "email": "user@example.com",
      "processingLink": "https://example.com/download.zip",
      "error": false
   }
}
```
ou
```json
{
   "body": {
      "email": "user@example.com",
      "processingLink": "https://example.com/download.zip"
   }
}
````
2. **E-mail de Erro**:
   - Faça uma requisição POST para a função Lambda com o seguinte payload:

```json
{
   "body": {
      "email": "user@example.com",
      "error": true
   }
}
```

### Testes Unitários

1. Rode o bloco para instalar as dependências de testes, executar os testes e gerar o relatório de cobertura:

```sh
find tests -name 'requirements.txt' -exec pip install -r {} +
pip install coverage coverage-badge
coverage run -m unittest discover -s tests -p '*_test.py'
coverage report -m
coverage html  
```

## Licença

Este projeto está licenciado sob a **MIT License**. Consulte o arquivo LICENSE para mais detalhes.

---

Desenvolvido com ❤️ pela equipe Video Frame Pro.
