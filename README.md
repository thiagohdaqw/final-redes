# Trabalho Final - Redes

## Alunos
|Matrícula | Aluno |
| -- | -- |
| 19/0012307  |  Eduardo Afonso |
| 19/0019085  |  Rafael Ramos |
| 19/0020377  |  Thiago Paiva |

## Uso

Instale as dependencias:<br>
`pip install -r requirements.txt`<br>
ou `pip install click`

Execute o servidor:<br>
```
$ python run_server.py --help
#Usage: run_server.py [OPTIONS]
#
#Options:
#  -i, --ip TEXT       Ip address of the server
#  -p, --port INTEGER  Port of the server
#  -m, --max INTEGER   Max connections of the server
#  --help              Show this message and exit.

$ python run_server.py -i 127.0.0.1 -p 7777 -m 10
# Aguardando em  ('127.0.0.1', 7777)
```

Execute o cliente:<br>
```
$ python run_client.py -i 127.0.0.1 -p 7777

# Ou pelo telnet

$ telnet 127.0.0.1 7777
```

Comandos no cliente:<br>
```
--CREATE <NomeCanal> <CapacidadeDeUsuarios> <NomeUsuario>  - Create Channel
--JOIN <NomeCanal> <NomeUsuario>  - Join Channel
--OUT - Exit Channel
--CHANNELS - List available channels
--LIST - List user in channel
--HELP - Show all commands description

```
