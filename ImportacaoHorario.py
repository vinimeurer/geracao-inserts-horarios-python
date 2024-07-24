import tkinter as tk
from tkinter import filedialog
import csv
import chardet
import io
import os
import re
import shutil
import sys


######################################## CLASSE DE HORÁRIO NORMAL  ##########################################

class HorarioNormal:
    
    def __init__(self):
        self.root = tk.Tk()
        self.caminho_arquivo = tk.StringVar()
        self.root.withdraw()

    def buscar_arquivo(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Selecione um Arquivo", filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")))
        if filename:
            caminho_arquivo.set(filename)

    def realiza_processos(self):
        arquivo_selecionado = caminho_arquivo.get()
        print("Caminho do arquivo selecionado:", arquivo_selecionado)
        
        self.obter_dados(arquivo_selecionado)

        self.primeiro_tratamento()
        
        self.segundo_tratamento() 
        
        self.terceiro_tratamento()
        
        self.quarto_tratamento()
        
        self.quinto_tratamento()
        
        self.gerar_inserts ()
        
        self.renomear_arquivo()

    ############################################# OBETEM OS DADOS## #############################################
    #                                                                                                           #
    #   - lê e realiza a formatação inicial do arquivo a partir do caminho especificado                         #
    #   - organiza as informações por linhas                                                                    #
    #                                                                                                           #
    #############################################################################################################

    def obter_dados(self, caminho_arquivo):
        dados_por_dia = {
            'Segunda-Feira': [],
            'Terça-Feira': [],
            'Quarta-Feira': [],
            'Quinta-Feira': [],
            'Sexta-Feira': [],
            'Sábado': [],
            'Domingo': []
        }

        # Detecta a codificação do arquivo automaticamente (setar utf 8 de forma direta não deu certo)
        with open(caminho_arquivo, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        # Lê o arquivo CSV com a codificação
        with io.open(caminho_arquivo, 'r', encoding=encoding) as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader) 
            
            for row in reader:
                if len(row) > 0:  # Verifica se a linha não está vazia
                    descricao = row[0]
                    for i, dia in enumerate(dados_por_dia.keys()): # Dados de segunda a domingo
                        dados_por_dia[dia].append({
                            'Descrição': descricao,
                            'Tipo': row[1],
                            'Crédito': row[2],
                            'Débito': row[3],
                            'E1': row[4 + i * 4],
                            'S1': row[5 + i * 4],
                            'E2': row[6 + i * 4],
                            'S2': row[7 + i * 4]
                        })

        # cria a pasta temporária caso ela não exista
        if not os.path.exists('arquivosimphorario'):
            os.makedirs('arquivosimphorario')

        # Escreve os dados formatados no arqiuivo e salva na pasta
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo1_dados_obtidos.txt')
        with io.open(nome_arquivo_saida, 'w', encoding='utf-8') as arquivo_saida:
            for dia, dados in dados_por_dia.items():
                arquivo_saida.write(f"\n{dia}:\n")
                for dado in dados:
                    arquivo_saida.write(f"Descrição: {dado['Descrição']}\n")
                    arquivo_saida.write(f"Tipo: {dado['Tipo']}\n")
                    arquivo_saida.write(f"Crédito: {dado['Crédito']}\n")
                    arquivo_saida.write(f"Débito: {dado['Débito']}\n")
                    arquivo_saida.write(f"E1: {dado['E1']}\n")
                    arquivo_saida.write(f"S1: {dado['S1']}\n")
                    arquivo_saida.write(f"E2: {dado['E2']}\n")
                    arquivo_saida.write(f"S2: {dado['S2']}\n")
                    arquivo_saida.write("\n") 

        print("Dados obtidos. Arquivo salvo em .\\" + nome_arquivo_saida)


    ########################################### PRIMEIRO TRATAMENTO #############################################
    #                                                                                                           #
    #   - realiza o tratamento inciial nos dados obtidos                                                        #
    #   - formata os horários no padrão E1-S1-E2-S2                                                             #
    #   - agrupa os horários pela descrição                                                                     #
    #                                                                                                           #
    #############################################################################################################

    def primeiro_tratamento (self):
            
        nome_arquivo_entrada = os.path.join('arquivosimphorario', 'Arquivo1_dados_obtidos.txt')

        with open(nome_arquivo_entrada, 'r', encoding='utf-8') as f:
            lines = f.readlines()


        # Variáveis
        current_day = None
        descricao = None
        tipo = None
        credito = None
        debito = None
        e1 = None
        s1 = None
        e2 = None
        s2 = None

        # Dicionário para armazenar as variaáveis de forma organziad
        dados_organizados = {}

        # Iterando pelas linhas do arquivo
        for line in lines:
            line = line.strip()
            if line.startswith('Descrição:'):
                descricao = line.split(': ')[1]
            elif line.startswith('Tipo:'):
                tipo = line.split(': ')[1]
            elif line.startswith('Crédito:'):
                credito = line.split(': ')[1]  if len(line.split(': ')) > 1 else ''
            elif line.startswith('Débito:'):
                debito = line.split(': ')[1] if len(line.split(': ')) > 1 else ''
            elif line.startswith('E1:'):
                e1 = line.split(': ')[1] if len(line.split(': ')) > 1 else ''
            elif line.startswith('S1:'):
                s1 = line.split(': ')[1] if len(line.split(': ')) > 1 else ''
            elif line.startswith('E2:'):
                e2 = line.split(': ')[1] if len(line.split(': ')) > 1 else ''
            elif line.startswith('S2:'):
                s2 = line.split(': ')[1] if len(line.split(': ')) > 1 else ''
                # Ao encontrar S2, significa que todas as informações para um dia foram lidas
                if current_day and descricao and tipo and credito and debito:
                    # Criando ou atualizando a entrada no dicionário de dados organizados
                    if descricao not in dados_organizados:
                        dados_organizados[descricao] = {
                            'tipo': tipo,
                            'credito': credito,
                            'debito': debito,
                            'dias': {}
                        }
                    dados_organizados[descricao]['dias'][current_day] = f"{e1}-{s1}-{e2}-{s2}"
                
            elif line in ['Segunda-Feira:', 'Terça-Feira:', 'Quarta-Feira:', 'Quinta-Feira:', 'Sexta-Feira:', 'Sábado:', 'Domingo:']:
                current_day = line.rstrip(':')
                # caso não haja informações para o dia fica vazio (para tratamentos posteriores)
                e1 = ''
                s1 = ''
                e2 = ''
                s2 = ''

        # Salva os dados tratados na pasta
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo2_dados_tratados.txt')

        with open(nome_arquivo_saida, 'w', encoding='utf-8') as output_file:
            # Escrevendo os resultados formatados no arquivo
            for descricao, dados in dados_organizados.items():
                output_file.write(f"Descrição: {descricao}\n")
                output_file.write(f"Tipo: {dados['tipo']}\n")
                for day, values in dados['dias'].items():
                    output_file.write(f"{day}: {values}\n")
                output_file.write(f"Débito: {dados['debito']}\n")
                output_file.write(f"Crédito: {dados['credito']}\n")
                output_file.write("\n")
                
        print("Primeiro tratamento realizado. Arquivo salvo em .\\" + nome_arquivo_saida) 
        
    ########################################### SEGUNDO TRATAMENTO ##############################################
    #                                                                                                           #
    #   - remove os dados de cabeçalho que também foram incluidos                                               #
    #   - adiciona uma linha para o id do horário (auto incrementável)                                          #
    #                                                                                                           #
    #############################################################################################################

    def segundo_tratamento(self):
        # Valida a existência do arquivo CSV com os ids do hoário
        caminho_arquivo_csv = os.path.join('arquivosimphorario', 'Arquivo4_horario.csv')

        # Se o arquivo já existir, realzia a leitura e pga o último id para determianr o ponto de partida
        if os.path.exists(caminho_arquivo_csv):
            with open(caminho_arquivo_csv, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                last_row = None
                for row in reader:
                    last_row = row
                if last_row:
                    last_id = int(last_row['idHorario'])
                    idHorario = last_id + 1
                else:
                    idHorario = 1
        else:
            # Se o arquivo não existir, começar o id em 1
            idHorario = 1

        # Salva os dados
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo2_dados_tratados.txt')

        with open(nome_arquivo_saida, 'r', encoding='utf-8') as f:
            content = f.readlines()

        content = content[11:]

        treated_data = []
        for line in content:
            line = line.strip()

            if line.startswith('Descrição:'):
                treated_data.append(f'Descrição: {line.split("Descrição: ")[-1]}\n')
                treated_data.append(f'idHorario: {idHorario}\n')
                idHorario += 1
            else:
                treated_data.append(line + '\n')

        with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
            f.writelines(treated_data)

        print("Segundo tratamento realizado. Arquivo salvo em .\\" + nome_arquivo_saida)
    
    
    ########################################### TERCEIRO TRATAMENTO #############################################
    #                                                                                                           #
    #   - formata os dados de acordo com as espeficiações do banco                                              #
    #   - converte horas para minutos para inserção                                                             #
    #   - realiza o tratamento de débitose crédidos que foram cadastrados vazios                                #
    #                                                                                                           #
    #############################################################################################################

    def terceiro_tratamento (self):
        
        def horas_para_minutos(hora):
            # Dividir a string da hora em horas e minutos
            horas, minutos = map(int, hora.split(':'))
            
            # Calcular o total de minutos
            total_minutos = horas * 60 + minutos
            
            return total_minutos

        # Abrir o arquivo de entrada 'dados_tratados.txt'
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo2_dados_tratados.txt')

        with open(nome_arquivo_saida, 'r', encoding='utf-8') as arquivo:
            saida = arquivo.read()

        # Dividir a saída em blocos separados
        blocos = saida.strip().split('\n\n')

        # Processar cada bloco
        blocos_preparados = []
        for bloco in blocos:
            linhas = bloco.strip().split('\n')
            
            # Iterar através das linhas do bloco
            linhas_modificadas = []
            for linha in linhas:
                if linha.startswith("Tipo: Normal"):
                    linha = "Tipo: 1"
                elif any(dia in linha for dia in ["Segunda-Feira:", "Terça-Feira:", "Quarta-Feira:", "Quinta-Feira:", "Sexta-Feira:", "Sábado:", "Domingo:"]):
                    # Dividir a linha em chave e valor
                    chave, valor = linha.split(': ')
                    
                    # Dividir o valor por '-' para processar cada slot de tempo
                    slots_tempo = valor.split('-')
                    
                    # Converter cada slot de tempo de HH:MM para minutos
                    slots_convertidos = [str(horas_para_minutos(slot)) for slot in slots_tempo if slot.strip() != '']
                    
                    # Juntar os slots convertidos com '-'
                    valor_convertido = '-'.join(slots_convertidos)
                    
                    # Reconstruir a linha
                    linha = f"{chave}: {valor_convertido}"
                elif linha.startswith("Débito:") or linha.startswith("Crédito:"):
                    # Verificar se há valor após ': '
                    if ': ' in linha:
                        chave, valor = linha.split(': ', 1)
                        
                        # Verificar se o valor está vazio
                        if valor.strip() == '':
                            valor = '-1'  # Definir como -1 se estiver vazio
                        else:
                            # Converter o valor de HH:MM para minutos
                            valor = str(horas_para_minutos(valor.strip()))
                        
                        # Reconstruir a linha
                        linha = f"{chave}: {valor}"
                    else:
                        # Se não houver valor após ': ', inserir '-1'
                        linha = f"{linha.strip()}: -1"
                
                # Adicionar linha modificada à lista
                linhas_modificadas.append(linha)
            
            # Juntar as linhas modificadas de volta ao formato de bloco
            bloco_modificado = '\n'.join(linhas_modificadas)
            
            # Adicionar bloco modificado aos blocos preparados
            blocos_preparados.append(bloco_modificado)

        # Escrever os blocos preparados no arquivo de saída 'dados_preparados.txt'
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo3_dados_preparados.txt')
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as arquivo:
            arquivo.write('\n\n'.join(blocos_preparados))

        print("Terceiro tratamento realizado. Arquivo salvo em .\\" + nome_arquivo_saida)


    ############################################ QUARTO TRATAMENTO ##############################################
    #                                                                                                           #
    #   - Gera o arquivo csv com id do horário e descrição (para ler e gerar inserts)                           #
    #                                                                                                           #
    #############################################################################################################

    def quarto_tratamento(self):

        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo2_dados_tratados.txt')

        with open(nome_arquivo_saida, 'r', encoding='utf-8') as arquivo:
            saida = arquivo.read()

        # Define padrões regex para idHorario e Descrição
        padrao_id_horario = re.compile(r"idHorario:\s*(\d+)")
        padrao_descricao = re.compile(r"Descrição:\s*(.*)")

        # Lê dados do arquivo
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo2_dados_tratados.txt')

        with open(nome_arquivo_saida, 'r', encoding='utf-8') as arquivo:
            saida = arquivo.read()

        # Inicializa listas para armazenar dados extraídos
        id_horarios = []
        descricoes = []

        # Divide os dados em blocos (separados por linhas em branco)
        blocos = saida.strip().split("\n\n")

        for bloco in blocos:
            match_id_horario = padrao_id_horario.search(bloco)
            match_descricao = padrao_descricao.search(bloco)
            
            if match_descricao and match_id_horario:
                id_horario = match_id_horario.group(1)
                descricao = match_descricao.group(1)
                
                id_horarios.append(id_horario)
                descricoes.append(descricao)

        # Prepara dados para escrita no CSV
        dados_para_csv = zip(id_horarios, descricoes)

        # Escreve no arquivo CSV
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo4_horario.csv')

        with open(nome_arquivo_saida, 'w', newline='', encoding='utf-8') as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv)
            escritor_csv.writerow(['idHorario', 'Descrição'])  # Escreve o cabeçalho
            escritor_csv.writerows(dados_para_csv)

        print("Quarto tratamento realizado. Arquivo salvo em .\\" + nome_arquivo_saida)
        

    ############################################ QUINTO TRATAMENTO ##############################################
    #                                                                                                           #
    #   - Gera o arquivo csv com entradas e saídas por dia da semana (já formatados de acordo com o banco)      #
    #                                                                                                           #
    #############################################################################################################

    def quinto_tratamento(self):
        # Lê o conteúdo do arquivo de entrada
        nome_arquivo_entrada = os.path.join('arquivosimphorario', 'Arquivo3_dados_preparados.txt')

        with open(nome_arquivo_entrada, 'r', encoding='utf-8') as arquivo:
            entrada = arquivo.read()

        # Divide o conteúdo em blocos baseados em 'Descrição:'
        blocks = re.split(r'Descrição:\s+', entrada)
        blocks = [block.strip() for block in blocks if block.strip()]

        # Inicializa variáveis
        id_periodos = 1
        csv_linhas = []
        header = ['"idPeriodos"', '"idHorario"', '"entrada"', '"saida"', '"toleranciaAntesEntrada"', '"toleranciaAposEntrada"', '"toleranciaAntesSaida"', '"toleranciaAposSaida"', '"domingo"', '"segunda"', '"terca"', '"quarta"', '"quinta"', '"sexta"', '"sabado"']

        # Processa cada bloco
        for block in blocks:
            lines = block.split('\n')
            
            id_horario = None
            horario_linhas = {}
            debito = None
            credito = None
            
            # Extrai as linhas
            for line in lines:
                if line.startswith('idHorario:'):
                    id_horario = line.split(': ')[1]
                elif line.startswith('Segunda-Feira:'):
                    horario_linhas['segunda'] = line.split(': ')[1].split('-')
                elif line.startswith('Terça-Feira:'):
                    horario_linhas['terca'] = line.split(': ')[1].split('-')
                elif line.startswith('Quarta-Feira:'):
                    horario_linhas['quarta'] = line.split(': ')[1].split('-')
                elif line.startswith('Quinta-Feira:'):
                    horario_linhas['quinta'] = line.split(': ')[1].split('-')
                elif line.startswith('Sexta-Feira:'):
                    horario_linhas['sexta'] = line.split(': ')[1].split('-')
                elif line.startswith('Sábado:'):
                    horario_linhas['sabado'] = line.split(': ')[1].split('-')
                elif line.startswith('Domingo:'):
                    horario_linhas['domingo'] = line.split(': ')[1].split('-')
                elif line.startswith('Débito:'):
                    debito = line.split(': ')[1]
                elif line.startswith('Crédito'):
                    credito = line.split(': ')[1]
            
            # Agora geramos as linhas para o CSV
            for day in ['domingo', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado']:
                if day in horario_linhas:
                    times = horario_linhas[day]
                    for i in range(0, len(times), 2):
                        if i + 1 < len(times):
                            entrada = times[i]
                            saida = times[i + 1]
                            
                            # Usa string vazia se debito ou credito for None
                            tolerancia_antes_entrada = credito if credito is not None else ''
                            tolerancia_apos_entrada = debito if debito is not None else ''
                            tolerancia_antes_saida = debito if debito is not None else ''
                            tolerancia_apos_saida = credito if credito is not None else ''
                            
                            csv_linha = f'"{id_periodos}","{id_horario}","{entrada}","{saida}","{tolerancia_antes_entrada}","{tolerancia_apos_entrada}","{tolerancia_antes_saida}","{tolerancia_apos_saida}","{day == "domingo"}","{day == "segunda"}","{day == "terca"}","{day == "quarta"}","{day == "quinta"}","{day == "sexta"}","{day == "sabado"}"'
                            csv_linhas.append(csv_linha)
                            id_periodos += 1

        # Escreve no arquivo CSV
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo5_periodos.csv')
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as csv_file:
            csv_file.write(','.join(header) + '\n')
            for linha in csv_linhas:
                csv_file.write(linha + '\n')

        print("Quinto tratamento realizado. Arquivo salvo em .\\" + nome_arquivo_saida)

    
    ############################################ GERAÇÃO DE INSERTS #############################################
    #                                                                                                           #
    #   - Gera o arquivo csv com entradas e saídas por dia da semana (já formatados de acordo com o banco)      #
    #                                                                                                           #
    #############################################################################################################

    def gerar_inserts(self):
        def converter_booleano(valor):
            if valor.lower() == 'true':
                return '1'
            elif valor.lower() == 'false':
                return '2'
            else:
                return valor

        def gerar_insercoes_horario(idHorario, descricao):
            return f"INSERT INTO horario (idHorario, descricao, idSituacaoCadastro) VALUES ({idHorario}, '{descricao}', 1);\n"

        def gerar_insercoes_cargahoraria(idHorario, descricao):
            return f"INSERT INTO cargaHoraria (idCargaHoraria, idTipoCargaHoraria, descricao, quantidade) VALUES ({idHorario}, 1, '{descricao}', 0);\n"

        def gerar_insercoes_periodos(idPeriodos, idHorario, entrada, saida, toleranciaAntesEntrada, toleranciaAposEntrada, toleranciaAntesSaida, toleranciaAposSaida, domingo, segunda, terca, quarta, quinta, sexta, sabado):
            return f"INSERT INTO periodos (idPeriodos, idHorario, entrada, saida, toleranciaAntesEntrada, toleranciaAposEntrada, toleranciaAntesSaida, toleranciaAposSaida, domingo, segunda, terca, quarta, quinta, sexta, sabado) VALUES ({idPeriodos}, {idHorario}, '{entrada}', '{saida}', {toleranciaAntesEntrada}, {toleranciaAposEntrada}, {toleranciaAntesSaida}, {toleranciaAposSaida}, {domingo}, {segunda}, {terca}, {quarta}, {quinta}, {sexta}, {sabado});\n"

        def gerar_insercoes_politica(idHorario):
            return f"INSERT INTO `politica` (`idPolitica`, `idCargaHoraria`, `descricao`, `idSituacaoCadastro`, `horaFechamentoMarcacao`, `tempoMinimoIntervalo`, `extraIntervalo`, `separaExtraIntervalo`, `extraFaltaParcial`, `destacarExecessoIntervalo`, `intervaloVariavel`, `gerarHorarioIntervalo`, `moverMarcEncIntervalor`, `gerarHorarioFolga`, `naoMostrarIntervalorMenor`, `idTipoTolerancia`, `toleranciaGeral`, `consideraIntegral`, `compensarExtraFalta`, `compensarExtraAtrasoSaida`, `sabadoCompensado`, `valorDSR`, `limiteDescontoDsr`, `faltaCompoeDSR`, `saidaAnteCompoeDebitoDSR`, `atrasoCompoeDebitoDSR`, `dsrDiaSemana`, `consideraFeriadoDiaDescDSR`, `inicioNoturno`, `fimNoturno`, `umaHoraEmNoturno`, `separarExtraNoturno`, `extraNoturnoEstendido`, `calcExtraTipoDia`, `addNoturnoFimHorario`, `addNoturnoEstendido`, `consideraNoturnoReduzido`, `interJornada`, `extraInterJornada`, `permiteAbonoOcorrenciaBH`, `enviarOcorrenciaBHManualmente`, `considerarFaltasParciaisComoAtraso`, `considerarHorasEmDebitoComoFalta`, `emCasoDeFaltaConsiderar`, `adNoturnoAntecipado`, `extraNoturnoAntecipado`, `faltaParcialComoSaida`, `separaExtraInterJornada`, `desconsiderarIntervaloMenor`, `plantao`) VALUES ({idHorario}, {idHorario}, 'Geral', 1, 0, 60, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1, 10, 0, 0, 0, 0, -1, -1, 0, 0, 0, -1, 0, 1320, 300, 3150, 0, 0, 0, 0, 0, 0, 660, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0);\n"

        def gerar_insercoes_politicahorario(idHorario):
            return f"INSERT INTO politicaHorario (idPoliticaHorario, idHorario, idPolitica) VALUES ({idHorario}, {idHorario}, {idHorario});\n"

        csv_file_horario = os.path.join('arquivosimphorario', 'Arquivo4_horario.csv')
        csv_file_periodos = os.path.join('arquivosimphorario', 'Arquivo5_periodos.csv')
        sql_file = 'insertsHorariosMigracao.txt'
        sql_statements = []

        # Process 'Arquivo4_horario.csv' for tables 'horario' and 'cargaHoraria'
        with open(csv_file_horario, mode='r', newline='', encoding='utf-8') as csvfile_horario:
            reader_horario = csv.DictReader(csvfile_horario)
            
            for row in reader_horario:
                idHorario = row['idHorario']
                descricao = row['Descrição']
                
                sql_horario = gerar_insercoes_horario(idHorario, descricao)
                sql_statements.append(sql_horario)
                
                sql_cargahoraria = gerar_insercoes_cargahoraria(idHorario, descricao)
                sql_statements.append(sql_cargahoraria)

        # Process 'Arquivo5_periodos.csv' for table 'periodos'
        with open(csv_file_periodos, 'r', encoding='utf-8') as arquivo_periodos:
            csv_reader_periodos = csv.reader(arquivo_periodos)
            headers_periodos = next(csv_reader_periodos)  # Read headers
            
            for row in csv_reader_periodos:
                row = [converter_booleano(valor) for valor in row]
                
                idPeriodos = row[0]
                idHorario = row[1]
                entrada = row[2]
                saida = row[3]
                toleranciaAntesEntrada = row[4]
                toleranciaAposEntrada = row[5]
                toleranciaAntesSaida = row[6]
                toleranciaAposSaida = row[7]
                domingo = row[8]
                segunda = row[9]
                terca = row[10]
                quarta = row[11]
                quinta = row[12]
                sexta = row[13]
                sabado = row[14]
                
                sql_periodos = gerar_insercoes_periodos(idPeriodos, idHorario, entrada, saida, toleranciaAntesEntrada, toleranciaAposEntrada, toleranciaAntesSaida, toleranciaAposSaida, domingo, segunda, terca, quarta, quinta, sexta, sabado)
                sql_statements.append(sql_periodos)

        # Generate 'politica' and 'politicaHorario' inserts
        with open(csv_file_horario, mode='r', newline='', encoding='utf-8') as csvfile_horario:
            reader_horario = csv.DictReader(csvfile_horario)
            for row in reader_horario:
                idHorario = row['idHorario']
                sql_politica = gerar_insercoes_politica(idHorario)
                sql_politicahorario = gerar_insercoes_politicahorario(idHorario)
                sql_statements.append(sql_politica)
                sql_statements.append(sql_politicahorario)

        # Write all inserts to file
        with open(sql_file, 'w', encoding='utf-8') as saida_sql:
            saida_sql.write('-- Inserts tabelas "horario", "cargaHoraria", "periodos", "politica" e "politicaHorario"\n\n')
            for stmt_sql in sql_statements:
                saida_sql.write(stmt_sql)

        print(f'Inserts para as tabelas "horario", "cargaHoraria", "periodos", "politica" e "politicaHorario" foram escritas em {sql_file}')

    ############################################# RENOMEIA ARQUIVO ##############################################
    #                                                                                                           #
    #   - Adiciona o texto "PROCESSADO" no nome do arquivo para evitar confusão de selecionar duplicados        #
    #                                                                                                           #
    #############################################################################################################

    def renomear_arquivo(self):
        arquivo_selecionado = caminho_arquivo.get()
        novo_nome = os.path.dirname(arquivo_selecionado) + "/PROCESSADO___" + os.path.basename(arquivo_selecionado)
        os.rename(arquivo_selecionado, novo_nome)
        caminho_arquivo.set(novo_nome)
        print(f"Arquivo renomeado para: {novo_nome}")
  
  
  
        
        
######################################### CLASSE DE CARGA DIÁRIA  ###########################################

class CargaDiaria:
    
    def __init__(self):
        self.root = tk.Tk()
        self.caminho_arquivo = tk.StringVar()
        self.root.withdraw()

    def buscar_arquivo(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Selecione um Arquivo", filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")))
        if filename:
            caminho_arquivo.set(filename)

    def realiza_processos(self):
        arquivo_selecionado = caminho_arquivo.get()
        print("Caminho do arquivo selecionado:", arquivo_selecionado)
        
        self.obter_dados(arquivo_selecionado)

        self.primeiro_tratamento()
        
        self.segundo_tratamento() 
        
        self.terceiro_tratamento()
        
        self.quarto_tratamento()
        
        self.quinto_tratamento()
        
        self.gerar_inserts ()
        
        self.renomear_arquivo()
        
    ############################################# OBETEM OS DADOS## #############################################
    #                                                                                                           #
    #   - lê e realiza a formatação inicial do arquivo a partir do caminho especificado                         #
    #   - organiza as informações por linhas                                                                    #
    #                                                                                                           #
    #############################################################################################################

    def obter_dados(self, caminho_arquivo):
        dados_por_dia = {
            'Segunda-Feira': [],
            'Terça-Feira': [],
            'Quarta-Feira': [],
            'Quinta-Feira': [],
            'Sexta-Feira': [],
            'Sábado': [],
            'Domingo': []
        }

        # Detecta a codificação do arquivo automaticamente (setar utf 8 de forma direta não deu certo)
        with open(caminho_arquivo, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        # Lê o arquivo CSV com a codificação
        with io.open(caminho_arquivo, 'r', encoding=encoding) as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader) 
            
            for row in reader:
                if len(row) > 0:  # Verifica se a linha não está vazia
                    descricao = row[0]
                    # Dados de segunda a domingo
                    for i, dia in enumerate(dados_por_dia.keys()):
                        dados_por_dia[dia].append({
                            'Descrição': descricao,
                            'Tipo': row[1],
                            'Segunda-Feira': row[2],
                            'Terça-Feira': row[3],
                            'Quarta-Feira': row[4],
                            'Quinta-Feira': row[5],
                            'Sexta-Feira': row[6],
                            'Sábado': row[7],
                            'Domingo': row[8]
                        })

        # cria a pasta temporária caso ela não exista
        if not os.path.exists('arquivosimphorario'):
            os.makedirs('arquivosimphorario')

        # Escreve os dados formatados no arqiuivo e salva na pasta
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo1_dados_obtidos.txt')
        with io.open(nome_arquivo_saida, 'w', encoding='utf-8') as arquivo_saida:
            for dia, dados in dados_por_dia.items():
                arquivo_saida.write(f"\n{dia}:\n")
                for dado in dados:
                    arquivo_saida.write(f"Descrição: {dado['Descrição']}\n")
                    arquivo_saida.write(f"Tipo: {dado['Tipo']}\n")
                    arquivo_saida.write(f"Segunda-Feira: {dado['Segunda-Feira']}\n")
                    arquivo_saida.write(f"Terça-Feira: {dado['Terça-Feira']}\n")
                    arquivo_saida.write(f"Quarta-Feira: {dado['Quarta-Feira']}\n")
                    arquivo_saida.write(f"Quinta-Feira: {dado['Quinta-Feira']}\n")
                    arquivo_saida.write(f"Sexta-Feira: {dado['Sexta-Feira']}\n")
                    arquivo_saida.write(f"Sábado: {dado['Sábado']}\n")
                    arquivo_saida.write(f"Domingo: {dado['Domingo']}\n")
                    arquivo_saida.write("\n") 

        print("Dados obtidos. Arquivo salvo em .\\" + nome_arquivo_saida)
        
    ########################################### PRIMEIRO TRATAMENTO #############################################
    #                                                                                                           #
    #   - realiza o tratamento inciial nos dados obtidos                                                        #
    #   - formata os horários no padrão E1-S1-E2-S2                                                             #
    #   - agrupa os horários pela descrição                                                                     #
    #                                                                                                           #
    #############################################################################################################

    def primeiro_tratamento (self):
            
        nome_arquivo_entrada = os.path.join('arquivosimphorario', 'Arquivo1_dados_obtidos.txt')

        with open(nome_arquivo_entrada, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Dicionário para armazenar as variaáveis de forma organziad
        dados_organizados = {}

        # Variáveis
        current_day = None
        descricao = None
        tipo = None
        schedule = {}

        # Iterando pelas linhas do arquivo
        for line in lines:
            line = line.strip()
            if line.startswith('Descrição:'):
                descricao = line.split(': ')[1]
            elif line.startswith('Tipo:'):
                tipo = line.split(': ')[1]
            elif line.startswith('Segunda-Feira:'):
                current_day = 'Segunda-Feira'
                schedule[current_day] = line.split(': ')[1] if len(line.split(': ')) > 1 else ''
            elif line.startswith('Terça-Feira:'):
                current_day = 'Terça-Feira'
                schedule[current_day] = line.split(': ')[1] if len(line.split(': ')) > 1 else ''
            elif line.startswith('Quarta-Feira:'):
                current_day = 'Quarta-Feira'
                schedule[current_day] = line.split(': ')[1] if len(line.split(': ')) > 1 else ''
            elif line.startswith('Quinta-Feira:'):
                current_day = 'Quinta-Feira'
                schedule[current_day] = line.split(': ')[1] if len(line.split(': ')) > 1 else ''
            elif line.startswith('Sexta-Feira:'):
                current_day = 'Sexta-Feira'
                schedule[current_day] = line.split(': ')[1] if len(line.split(': ')) > 1 else ''
            elif line.startswith('Sábado:'):
                current_day = 'Sábado'
                schedule[current_day] = line.split(': ')[1] if len(line.split(': ')) > 1 else ''
            elif line.startswith('Domingo:'):
                current_day = 'Domingo'
                schedule[current_day] = line.split(': ')[1] if len(line.split(': ')) > 1 else ''
                # Ao encontrar Domingo, armazenamos os dados completos
                if descricao and tipo:
                    if descricao not in dados_organizados:
                        dados_organizados[descricao] = {
                            'tipo': tipo,
                            'dias': {}
                        }
                    dados_organizados[descricao]['dias'] = schedule
                    descricao = None
                    tipo = None
                    schedule = {}

        # Salva os dados tratados na pasta
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo2_dados_tratados.txt')

        with open(nome_arquivo_saida, 'w', encoding='utf-8') as output_file:
            # Escrevendo os resultados formatados no arquivo
            for descricao, dados in dados_organizados.items():
                output_file.write(f"Descrição: {descricao}\n")
                output_file.write(f"Tipo: {dados['tipo']}\n")
                for day, values in dados['dias'].items():
                    output_file.write(f"{day}: {values}\n")
                output_file.write("\n")
                
        print("Primeiro tratamento realizado. Arquivo salvo em .\\" + nome_arquivo_saida)
        
        
    ########################################### SEGUNDO TRATAMENTO ##############################################
    #                                                                                                           #
    #   - remove os dados de cabeçalho que também foram incluidos                                               #
    #   - adiciona uma linha para o id do horário (auto incrementável)                                          #
    #                                                                                                           #
    #############################################################################################################

    def segundo_tratamento(self):
        # Valida a existência do arquivo CSV com os ids do hoário
        caminho_arquivo_csv = os.path.join('arquivosimphorario', 'Arquivo4_horario.csv')

        # Se o arquivo já existir, realzia a leitura e pga o último id para determianr o ponto de partida
        if os.path.exists(caminho_arquivo_csv):
            with open(caminho_arquivo_csv, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                last_row = None
                for row in reader:
                    last_row = row
                if last_row:
                    last_id = int(last_row['idHorario'])
                    idHorario = last_id + 1
                else:
                    idHorario = 1
        else:
            # Se o arquivo não existir, começar o id em 1
            idHorario = 1

        # Salva os dados
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo2_dados_tratados.txt')

        with open(nome_arquivo_saida, 'r', encoding='utf-8') as f:
            content = f.readlines()

        content = content[9:]

        treated_data = []
        for line in content:
            line = line.strip()

            if line.startswith('Descrição:'):
                treated_data.append(f'Descrição: {line.split("Descrição: ")[-1]}\n')
                treated_data.append(f'idHorario: {idHorario}\n')
                idHorario += 1
            else:
                treated_data.append(line + '\n')

        with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
            f.writelines(treated_data)

        print("Segundo tratamento realizado. Arquivo salvo em .\\" + nome_arquivo_saida)
        
        
        
    ########################################### TERCEIRO TRATAMENTO #############################################
    #                                                                                                           #
    #   - formata os dados de acordo com as espeficiações do banco                                              #
    #   - converte horas para minutos para inserção                                                             #
    #   - realiza o tratamento de débitose crédidos que foram cadastrados vazios                                #
    #                                                                                                           #
    #############################################################################################################

    def terceiro_tratamento(self):
        
        def horas_para_minutos(hora):
            horas, minutos = map(int, hora.split(':')) # Dividir a string da hora em horas e minutos
            total_minutos = horas * 60 + minutos # Calcular o total de minutos
            return total_minutos
        
        # Abrir o arquivo de entrada para leitura
        nome_arquivo_entrada = os.path.join('arquivosimphorario', 'Arquivo2_dados_tratados.txt')
        with open(nome_arquivo_entrada, 'r', encoding='utf-8') as arquivo:
            saida = arquivo.read()

        # Dividir a saída em blocos separados
        blocos = saida.strip().split('\n\n')

        # Processar cada bloco
        blocos_preparados = []
        for bloco in blocos:
            linhas = bloco.strip().split('\n')

            # Iterar através das linhas do bloco
            linhas_modificadas = []
            for linha in linhas:
                try:
                    chave, valor = linha.split(': ', 1)  # Limitar a divisão a apenas 1 split
                except ValueError:
                    # Handle lines that cannot be split into key: value format
                    linhas_modificadas.append(linha)
                    continue
                
                if chave == "Tipo" and valor == "Diária":
                    linha = "Tipo: 2"  # Alterar 'Tipo: Diária' para 'Tipo: 2'
                elif any(dia in linha for dia in ["Segunda-Feira:", "Terça-Feira:", "Quarta-Feira:", "Quinta-Feira:", "Sexta-Feira:", "Sábado:", "Domingo:"]):
                    # Dividir o valor por '-' para processar cada slot de tempo
                    slots_tempo = valor.split('-')
                    
                    # Converter cada slot de tempo de HH:MM para minutos
                    slots_convertidos = [str(horas_para_minutos(slot)) for slot in slots_tempo if slot.strip()]
                    
                    # Juntar os slots convertidos com '-'
                    valor_convertido = '-'.join(slots_convertidos)
                    
                    # Reconstruir a linha
                    linha = f"{chave}: {valor_convertido}"
                
                # Adicionar linha modificada à lista
                linhas_modificadas.append(linha)
            
            # Juntar as linhas modificadas de volta ao formato de bloco
            bloco_modificado = '\n'.join(linhas_modificadas)
            
            # Adicionar bloco modificado aos blocos preparados
            blocos_preparados.append(bloco_modificado)

        # Abrir o arquivo de saída para escrita
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo3_dados_preparados.txt')
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as arquivo:
            # Escrever os blocos preparados no arquivo de saída
            arquivo.write('\n\n'.join(blocos_preparados))

        print(f"Terceiro tratamento realizado. Arquivo salvo em {nome_arquivo_saida}")
        
        
    ############################################ QUARTO TRATAMENTO ##############################################
    #                                                                                                           #
    #   - Gera o arquivo csv com id do horário e descrição (para ler e gerar inserts)                           #
    #                                                                                                           #
    #############################################################################################################

    def quarto_tratamento(self):

        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo2_dados_tratados.txt')

        with open(nome_arquivo_saida, 'r', encoding='utf-8') as arquivo:
            saida = arquivo.read()

        # Define padrões regex para idHorario e Descrição
        padrao_id_horario = re.compile(r"idHorario:\s*(\d+)")
        padrao_descricao = re.compile(r"Descrição:\s*(.*)")

        # Lê dados do arquivo
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo2_dados_tratados.txt')

        with open(nome_arquivo_saida, 'r', encoding='utf-8') as arquivo:
            saida = arquivo.read()

        # Inicializa listas para armazenar dados extraídos
        id_horarios = []
        descricoes = []

        # Divide os dados em blocos (separados por linhas em branco)
        blocos = saida.strip().split("\n\n")

        for bloco in blocos:
            match_id_horario = padrao_id_horario.search(bloco)
            match_descricao = padrao_descricao.search(bloco)
            
            if match_descricao and match_id_horario:
                id_horario = match_id_horario.group(1)
                descricao = match_descricao.group(1)
                
                id_horarios.append(id_horario)
                descricoes.append(descricao)

        # Prepara dados para escrita no CSV
        dados_para_csv = zip(id_horarios, descricoes)

        # Escreve no arquivo CSV
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo4_horario.csv')

        with open(nome_arquivo_saida, 'w', newline='', encoding='utf-8') as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv)
            escritor_csv.writerow(['idHorario', 'Descrição'])  # Escreve o cabeçalho
            escritor_csv.writerows(dados_para_csv)

        print("Quarto tratamento realizado. Arquivo salvo em .\\" + nome_arquivo_saida)
        
    ############################################ QUINTO TRATAMENTO ##############################################
    #                                                                                                           #
    #   - Gera o arquivo csv com entradas e saídas por dia da semana (já formatados de acordo com o banco)      #
    #                                                                                                           #
    #############################################################################################################

    def quinto_tratamento(self):
        # Lê o conteúdo do arquivo de entrada
        nome_arquivo_entrada = os.path.join('arquivosimphorario', 'Arquivo3_dados_preparados.txt')

        with open(nome_arquivo_entrada, 'r', encoding='utf-8') as arquivo:
            entrada = arquivo.read()

        # Divide o conteúdo em blocos baseados em 'Descrição:'
        blocks = re.split(r'Descrição:\s+', entrada)
        blocks = [block.strip() for block in blocks if block.strip()]

        # Inicializa variáveis
        id_periodos = 1
        csv_linhas = []
        header = ['"idPeriodos"', '"idHorario"', '"quantidade"', '"domingo"', '"segunda"', '"terca"', '"quarta"', '"quinta"', '"sexta"', '"sabado"']

        # Processa cada bloco
        for block in blocks:
            lines = block.split('\n')
            
            id_horario = None
            horario_linhas = {'domingo': '', 'segunda': '', 'terca': '', 'quarta': '', 'quinta': '', 'sexta': '', 'sabado': ''}
            
            # Extrai as linhas
            for line in lines:
                if line.startswith('idHorario:'):
                    id_horario = line.split(': ')[1]
                elif line.startswith('Segunda-Feira:'):
                    try:
                        horario_linhas['segunda'] = line.split(': ')[1]
                    except IndexError:
                        pass
                elif line.startswith('Terça-Feira:'):
                    try:
                        horario_linhas['terca'] = line.split(': ')[1]
                    except IndexError:
                        pass
                elif line.startswith('Quarta-Feira:'):
                    try:
                        horario_linhas['quarta'] = line.split(': ')[1]
                    except IndexError:
                        pass
                elif line.startswith('Quinta-Feira:'):
                    try:
                        horario_linhas['quinta'] = line.split(': ')[1]
                    except IndexError:
                        pass
                elif line.startswith('Sexta-Feira:'):
                    try:
                        horario_linhas['sexta'] = line.split(': ')[1]
                    except IndexError:
                        pass
                elif line.startswith('Sábado:'):
                    try:
                        horario_linhas['sabado'] = line.split(': ')[1]
                    except IndexError:
                        pass
                elif line.startswith('Domingo:'):
                    try:
                        horario_linhas['domingo'] = line.split(': ')[1]
                    except IndexError:
                        pass
            
            # Agora geramos as linhas para o CSV
            for day in ['domingo', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado']:
                if horario_linhas[day].strip():  # Only process days with valid times
                    times = horario_linhas[day]
                    quantidade = times.split('-')[0]  # Assuming first time slot is quantity
                    csv_linha = f'"{id_periodos}","{id_horario}","{quantidade}","{day == "domingo"}","{day == "segunda"}","{day == "terca"}","{day == "quarta"}","{day == "quinta"}","{day == "sexta"}","{day == "sabado"}"'
                    csv_linhas.append(csv_linha)
                    id_periodos += 1

        # Escreve no arquivo CSV
        nome_arquivo_saida = os.path.join('arquivosimphorario', 'Arquivo5_periodos.csv')
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as csv_file:
            csv_file.write(','.join(header) + '\n')
            for linha in csv_linhas:
                csv_file.write(linha + '\n')

        print("Quinto tratamento realizado. Arquivo salvo em .\\" + nome_arquivo_saida)
        
        
        
    ############################################ GERAÇÃO DE INSERTS #############################################
    #                                                                                                           #
    #   - Gera o arquivo csv com entradas e saídas por dia da semana (já formatados de acordo com o banco)      #
    #                                                                                                           #
    #############################################################################################################

    def gerar_inserts(self):
        # Função para converter 'true'/'false' para '1'/'2'
        def converter_booleano(valor):
            if valor.lower() == 'true':
                return '1'
            elif valor.lower() == 'false':
                return '2'
            else:
                return valor

        # inserts tabela 'horario'
        def gerar_insercoes_horario(idHorario, descricao):
            return f"INSERT INTO horario (idHorario, descricao, idSituacaoCadastro) VALUES ({idHorario}, '{descricao}', 1);\n"

        # inserts tabela tabela 'cargaHoraria'
        def gerar_insercoes_cargahoraria(idHorario, descricao):
            return f"INSERT INTO cargaHoraria (idCargaHoraria, idTipoCargaHoraria, descricao, quantidade) VALUES ({idHorario}, 2, '{descricao}', 0);\n"

        # inserts tabela 'cargaHorario'
        def gerar_insercoes_cargahorario(idPeriodos, idHorario, quantidade, domingo, segunda, terca, quarta, quinta, sexta, sabado):
            return f"INSERT INTO cargaHorario (idCargaHorario, idHorario, quantidade, domingo, segunda, terca, quarta, quinta, sexta, sabado) VALUES ({idPeriodos}, {idHorario}, {quantidade}, {domingo}, {segunda}, {terca}, {quarta}, {quinta}, {sexta}, {sabado});\n"

        # inserts tabela 'politica'
        def gerar_insercoes_politica(idHorario):
            return f"INSERT INTO `politica` (`idPolitica`, `idCargaHoraria`, `descricao`, `idSituacaoCadastro`, `horaFechamentoMarcacao`, `tempoMinimoIntervalo`, `extraIntervalo`, `separaExtraIntervalo`, `extraFaltaParcial`, `destacarExecessoIntervalo`, `intervaloVariavel`, `gerarHorarioIntervalo`, `moverMarcEncIntervalor`, `gerarHorarioFolga`, `naoMostrarIntervalorMenor`, `idTipoTolerancia`, `toleranciaGeral`, `consideraIntegral`, `compensarExtraFalta`, `compensarExtraAtrasoSaida`, `sabadoCompensado`, `valorDSR`, `limiteDescontoDsr`, `faltaCompoeDSR`, `saidaAnteCompoeDebitoDSR`, `atrasoCompoeDebitoDSR`, `dsrDiaSemana`, `consideraFeriadoDiaDescDSR`, `inicioNoturno`, `fimNoturno`, `umaHoraEmNoturno`, `separarExtraNoturno`, `extraNoturnoEstendido`, `calcExtraTipoDia`, `addNoturnoFimHorario`, `addNoturnoEstendido`, `consideraNoturnoReduzido`, `interJornada`, `extraInterJornada`, `permiteAbonoOcorrenciaBH`, `enviarOcorrenciaBHManualmente`, `considerarFaltasParciaisComoAtraso`, `considerarHorasEmDebitoComoFalta`, `emCasoDeFaltaConsiderar`, `adNoturnoAntecipado`, `extraNoturnoAntecipado`, `faltaParcialComoSaida`, `separaExtraInterJornada`, `desconsiderarIntervaloMenor`, `plantao`) VALUES ({idHorario}, {idHorario}, 'Geral', 1, 0, 60, 0, 0, 0, 0, 0, 0, 0, 0, -1, 1, 10, 0, 0, 0, 0, -1, -1, 0, 0, 0, -1, 0, 1320, 300, 3150, 0, 0, 0, 0, 0, 0, 660, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0);\n"
        # inserts tabela 'politicaHorario'
        def gerar_insercoes_politicahorario(idHorario):
            return f"INSERT INTO politicaHorario (idPoliticaHorario, idHorario, idPolitica) VALUES ({idHorario}, {idHorario}, {idHorario});\n"

        # Arquivos CSV
        csv_file_horario = os.path.join('arquivosimphorario', 'Arquivo4_horario.csv')
        csv_file_periodos = os.path.join('arquivosimphorario', 'Arquivo5_periodos.csv')

        # Arquivo de saída para as inserções SQL combinadas
        sql_file = 'insertsHorariosMigracao.txt'
        
        # Lista para armazenar as declarações SQL
        sql_statements = []

        # Processar 'Arquivo4_horario.csv' para as tabelas 'horario' e 'cargaHoraria'
        with open(csv_file_horario, mode='r', newline='', encoding='utf-8') as csvfile_horario:
            reader_horario = csv.DictReader(csvfile_horario)
            
            for row in reader_horario:
                idHorario = row['idHorario']
                descricao = row['Descrição']
                
                # Gerar declarações de inserção SQL para a tabela 'horario'
                sql_horario = gerar_insercoes_horario(idHorario, descricao)
                sql_statements.append(sql_horario)
                
                # Gerar declarações de inserção SQL para a tabela 'cargaHoraria'
                sql_cargahoraria = gerar_insercoes_cargahoraria(idHorario, descricao)
                sql_statements.append(sql_cargahoraria)

        # Processar 'Arquivo5_periodos.csv' para a tabela 'cargaHorario'
        with open(csv_file_periodos, 'r', encoding='utf-8') as arquivo_periodos:
            csv_reader_periodos = csv.reader(arquivo_periodos)
            headers_periodos = next(csv_reader_periodos)  # Ler cabeçalhos
            
            for row in csv_reader_periodos:
                # Converter valores booleanos na linha
                row = [converter_booleano(valor) for valor in row]
                
                # Extrair valores da linha CSV
                idPeriodos = row[0]
                idHorario = row[1]
                quantidade = row[2]
                domingo = row[3]
                segunda = row[4]
                terca = row[5]
                quarta = row[6]
                quinta = row[7]
                sexta = row[8]
                sabado = row[9]
                
                # Gerar declarações de inserção SQL para a tabela 'cargaHorario'
                sql_cargahorario = gerar_insercoes_cargahorario(idPeriodos, idHorario, quantidade, domingo, segunda, terca, quarta, quinta, sexta, sabado)
                sql_statements.append(sql_cargahorario)

        # Processar 'Arquivo4_horario.csv' novamente para as tabelas 'politica' e 'politicaHorario'
        with open(csv_file_horario, mode='r', newline='', encoding='utf-8') as csvfile_horario:
            reader_horario = csv.DictReader(csvfile_horario)
            
            for row in reader_horario:
                idHorario = row['idHorario']
                
                # Gerar declarações de inserção SQL para a tabela 'politica'
                sql_politica = gerar_insercoes_politica(idHorario)
                sql_statements.append(sql_politica)
                
                # Gerar declarações de inserção SQL para a tabela 'politicaHorario'
                sql_politicahorario = gerar_insercoes_politicahorario(idHorario)
                sql_statements.append(sql_politicahorario)

        # Escrever todos os inserts
        mode = 'a' if os.path.exists(sql_file) else 'w'
        with open(sql_file, mode, encoding='utf-8') as saida_sql:
            if mode == 'w':
                saida_sql.write('-- Inserts tabelas "horario", "cargaHoraria", "cargaHorario", "politica" e "politicaHorario"\n\n')
            for stmt_sql in sql_statements:
                saida_sql.write(stmt_sql)

        print(f'Inserts para as tabelas "horario", "cargaHoraria", "cargaHorario", "politica" e "politicaHorario" foram escritas em {sql_file}')


    ############################################# RENOMEIA ARQUIVO ##############################################
    #                                                                                                           #
    #   - Adiciona o texto "PROCESSADO" no nome do arquivo para evitar confusão de selecionar duplicados        #
    #                                                                                                           #
    #############################################################################################################

    def renomear_arquivo(self):
        arquivo_selecionado = caminho_arquivo.get()
        novo_nome = os.path.dirname(arquivo_selecionado) + "/PROCESSADO___" + os.path.basename(arquivo_selecionado)
        os.rename(arquivo_selecionado, novo_nome)
        caminho_arquivo.set(novo_nome)
        print(f"Arquivo renomeado para: {novo_nome}")

    
################################# APAGA A PASTA TEMPORÁRIA E FINALIZA #######################################
#                                                                                                           #
#   - Apaga a pasta temporária com os arquivos de tratamenbto (exceto os inserts)                           #
#                                                                                                           #
#############################################################################################################

def apagar_pasta_temporaria():
    pasta_temporaria = 'arquivosimphorario'
    if os.path.exists(pasta_temporaria):
        shutil.rmtree(pasta_temporaria)
        print(f"Pasta temporária '{pasta_temporaria}' apagada.")
    else:
        print(f"A pasta temporária '{pasta_temporaria}' não existe.")       
    sys.exit()
        
        
        
        
def check_and_start():
    if os.path.exists("insertsHorariosMigracao.txt"):
        os.remove("insertsHorariosMigracao.txt")
        print("Arquivo 'insertsHorariosMigracao.txt' apagado.")
    else:
        print("Arquivo 'insertsHorariosMigracao.txt' não existe.")

    # Start the initial screen
    tela_inicial()


######################################## TELAS DE NAVEGAÇÃO TKINTER #########################################
#                                                                                                           #
#   - Apaga a pasta temporária com os arquivos de tratamenbto (exceto os inserts)                           #
#                                                                                                           #
#############################################################################################################

def on_window_close(window):
    window.destroy()
    sys.exit()

################################################ TELA INICIAL ###############################################

def tela_inicial():
    inicial = tk.Tk()
    inicial.title("Tela Inicial")
    
    texto_tipo = tk.Label(inicial, text="Selecione o tipo de horário que deseja importar")
    texto_tipo.pack(pady=10)

    botao_normal = tk.Button(inicial, text="Normal", command=lambda: [inicial.destroy(), tela_horario_normal()])
    botao_normal.pack(pady=10)

    botao_diaria = tk.Button(inicial, text="Diária", command=lambda: [inicial.destroy(), tela_carga_diaria()])
    botao_diaria.pack(pady=10)

    inicial.protocol("WM_DELETE_WINDOW", lambda: on_window_close(inicial))
    inicial.mainloop()
    
    

############################################ TELA HORÁRIO NORMAL ############################################
    
def tela_horario_normal():
    horario_normal = tk.Tk()
    horario_normal.title("IMPORTAÇÃO DE HORÁRIO NORMAL")
    classe_horario_normal = HorarioNormal()

    # Criando um StringVar para armazenar o caminho do arquivo
    global caminho_arquivo
    caminho_arquivo = tk.StringVar()

    rotulo = tk.Label(horario_normal, text="Arquivo Selecionado:")
    rotulo.pack(pady=10)

    entrada = tk.Entry(horario_normal, textvariable=caminho_arquivo, width=50)
    entrada.pack(padx=10, pady=5)

    botao_buscar = tk.Button(horario_normal, text="Procurar arquivo", command=classe_horario_normal.buscar_arquivo)
    botao_buscar.pack(pady=10)

    botao_iniciar_processamento = tk.Button(horario_normal, text="Iniciar Processamento", command=classe_horario_normal.realiza_processos)
    botao_iniciar_processamento.pack(pady=10)
    
    botao_finalizar = tk.Button(horario_normal, text="Finalizar Horário Normal", command=lambda: [horario_normal.destroy(), continua_importando()])
    botao_finalizar.pack(pady=10)
 
    horario_normal.protocol("WM_DELETE_WINDOW", lambda: on_window_close(horario_normal))
    horario_normal.mainloop()
    
############################################# TELA CARGA DIÁRIA #############################################
    
def tela_carga_diaria():
    carga_diaria = tk.Tk()
    carga_diaria.title("IMPORTAÇÃO DE CARGA DIÁRIA")
    classe_carga_diaria = CargaDiaria()

    # Criando um StringVar para armazenar o caminho do arquivo
    global caminho_arquivo
    caminho_arquivo = tk.StringVar()

    rotulo = tk.Label(carga_diaria, text="Arquivo Selecionado:")
    rotulo.pack(pady=10)

    entrada = tk.Entry(carga_diaria, textvariable=caminho_arquivo, width=50)
    entrada.pack(padx=10, pady=5)

    botao_buscar = tk.Button(carga_diaria, text="Procurar arquivo", command=classe_carga_diaria.buscar_arquivo)
    botao_buscar.pack(pady=10)

    botao_iniciar_processamento = tk.Button(carga_diaria, text="Iniciar Processamento", command=classe_carga_diaria.realiza_processos)
    botao_iniciar_processamento.pack(pady=10)
    
    botao_finalizar = tk.Button(carga_diaria, text="Finalizar Carga Diária", command=lambda: [carga_diaria.destroy(), continua_importando()])
    botao_finalizar.pack(pady=10)

    carga_diaria.protocol("WM_DELETE_WINDOW", lambda: on_window_close(carga_diaria))
    carga_diaria.mainloop()


############################################ TELA DE CONFIRMAÇÃO ############################################
    
def continua_importando():
    continuar = tk.Tk()
    
    texto_tipo = tk.Label(continuar, text="Deseja finalizar a aplicação?")
    texto_tipo.pack(pady=10)

    botao_finalizar = tk.Button(continuar, text="Sim", command= lambda: [apagar_pasta_temporaria(), continuar.destroy()])
    botao_finalizar.pack(pady=10)
    
    botao_normal = tk.Button(continuar, text="Não (continuar importando)", command=lambda: [continuar.destroy(), tela_inicial()])
    botao_normal.pack(pady=10)

    continuar.protocol("WM_DELETE_WINDOW", lambda: on_window_close(continuar))
    continuar.mainloop()
    
    print("\nPROCESSO FINALIZADO")

# Inicializando a tela inicial
check_and_start()