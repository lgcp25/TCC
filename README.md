# VAPOREON - Virtual Assistant for Pentest Operations, Research, Education, Orchestration, and Networks.

## Sobre o Projeto

O VAPOREON é uma plataforma educacional desenvolvida para auxiliar estudantes no aprendizado de Pentest através de uma interface gráfica simples, integração com ferramentas amplamente utilizadas no mercado e recursos de Inteligência Artificial para interpretação de resultados.

O sistema foi desenvolvido como Trabalho de Conclusão de Curso (TCC) e tem como objetivo reduzir a curva de aprendizado de iniciantes em Segurança da Informação.

---

## Funcionalidades

### Ferramentas Integradas

* Nmap (Mapeamento de Rede)
* Gobuster (Enumeração Web)
* Nikto (Análise de Servidores Web)
* SQLMap (Teste de SQL Injection)
* Netcat (Conectividade e Pós-Exploração)

### Recursos Educacionais

* Explicação automática dos resultados utilizando IA.
* Sugestão de próximos passos para continuidade do Pentest.
* Guias técnicos integrados em cada ferramenta.
* Relatórios automáticos em PDF.

### Ambiente de Laboratório

* DVWA (Damn Vulnerable Web Application) integrado.
* Execução isolada através de Docker.

---

# Requisitos

Antes de iniciar, certifique-se de possuir:

* Docker Desktop ou Docker Engine
* Docker Compose
* Python 3.11 ou superior
* Conexão com Internet (para recursos de IA)

---

# Instalação

## 1. Clonar o Projeto

```bash
git clone https://github.com/lgcp25/TCC.git
cd vaporeon
```

### 2. Instalar Dependências

Você pode instalar as dependências diretamente no sistema ou isolá-las em um ambiente virtual (recomendado para evitar conflitos):

* **Opção A: Instalação Direta (Mais rápida)**
  ```bash
  pip install -r requirements.txt
  ```

* **Opção B: Usando Ambiente Virtual (Recomendado)**
  * *Linux/macOS:* `python3 -m venv .venv && source .venv/bin/activate`
  * *Windows:* `python -m venv .venv && .venv\Scripts\activate`
  * Após ativar, rode: `pip install -r requirements.txt`

### 4. Configurar a Chave da IA
Os recursos de Inteligência Artificial utilizam a API da Groq. Para que funcionem, cada usuário precisa de uma chave de API própria (gratuita):

1. Acesse o site [Groq Console](https://groq.com) e faça login ou crie uma conta rápida.
2. Clique em **Developers**, depois em **Free API Keys**.
3. Clique em **Create API Key**, dê um nome para a chave e copie o código gerado (ele começa com `gsk_`).
4. Na raiz do projeto VAPOREON, crie um arquivo chamado `.env`.
5. Cole a sua chave dentro do arquivo seguindo o modelo abaixo:

```env
GROQ_API_KEY=gsk_SUA_CHAVE_AQUI
```

> **Nota:** Caso não possua uma chave Groq configurada no arquivo `.env`, as funções de explicação de resultados e próximos passos não funcionarão.


# Executando o Projeto

## 1. Iniciar Docker

Verifique se o Docker está em execução.

Teste:

```bash
docker ps
```

---

## 2. Subir os Containers

O VAPOREON iniciará automaticamente os containers necessários.

Caso necessário:

```bash
docker compose up -d
```

---

## 3. Executar a Aplicação

```bash
python main.py
```

ou

```bash
python3 main.py
```

---

# Verificando o Ambiente

Após abrir a aplicação:

Verifique se os serviços estão online:

* Docker
* DVWA
* IA

Os indicadores devem aparecer em verde.

---
Agora siga as instruções do formulário de avaliação:

[Formulário de avaliação](https://forms.gle/74Ud3zVJTc1XXg1J9)

---

# Autor

Luis Guilherme Cantanhêde de Paiva

Trabalho de Conclusão de Curso

Plataforma VAPOREON - Virtual Assistant for Pentest Operations, Research, Education, Orchestration, and Networks.
