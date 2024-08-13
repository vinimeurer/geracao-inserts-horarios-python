CREATE DATABASE testehorario;
USE testehorario;


-- Criação da tabela `horario`
CREATE TABLE horario (
    idHorario INT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    idSituacaoCadastro INT NOT NULL
);

-- Criação da tabela `cargaHoraria`
CREATE TABLE cargaHoraria (
    idCargaHoraria INT PRIMARY KEY,
    idTipoCargaHoraria INT NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    quantidade INT NOT NULL
);

-- Criação da tabela `periodos`
CREATE TABLE periodos (
    idPeriodos INT PRIMARY KEY,
    idHorario INT NOT NULL,
    entrada INT NOT NULL,
    saida INT NOT NULL,
    toleranciaAntesEntrada INT,
    toleranciaAposEntrada INT,
    toleranciaAntesSaida INT,
    toleranciaAposSaida INT,
    domingo INT,
    segunda INT,
    terca INT,
    quarta INT,
    quinta INT,
    sexta INT,
    sabado INT,
    FOREIGN KEY (idHorario) REFERENCES horario(idHorario)
);

-- Criação da tabela `politica`
CREATE TABLE politica (
    idPolitica INT PRIMARY KEY,
    idCargaHoraria INT NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    idSituacaoCadastro INT NOT NULL,
    horaFechamentoMarcacao INT,
    tempoMinimoIntervalo INT,
    extraIntervalo INT,
    separaExtraIntervalo INT,
    extraFaltaParcial INT,
    destacarExecessoIntervalo INT,
    intervaloVariavel INT,
    gerarHorarioIntervalo INT,
    moverMarcEncIntervalor INT,
    gerarHorarioFolga INT,
    naoMostrarIntervalorMenor INT,
    idTipoTolerancia INT,
    toleranciaGeral INT,
    consideraIntegral INT,
    compensarExtraFalta INT,
    compensarExtraAtrasoSaida INT,
    sabadoCompensado INT,
    valorDSR INT,
    limiteDescontoDsr INT,
    faltaCompoeDSR INT,
    saidaAnteCompoeDebitoDSR INT,
    atrasoCompoeDebitoDSR INT,
    dsrDiaSemana INT,
    consideraFeriadoDiaDescDSR INT,
    inicioNoturno INT,
    fimNoturno INT,
    umaHoraEmNoturno INT,
    separarExtraNoturno INT,
    extraNoturnoEstendido INT,
    calcExtraTipoDia INT,
    addNoturnoFimHorario INT,
    addNoturnoEstendido INT,
    consideraNoturnoReduzido INT,
    interJornada INT,
    extraInterJornada INT,
    permiteAbonoOcorrenciaBH INT,
    enviarOcorrenciaBHManualmente INT,
    considerarFaltasParciaisComoAtraso INT,
    considerarHorasEmDebitoComoFalta INT,
    emCasoDeFaltaConsiderar INT,
    adNoturnoAntecipado INT,
    extraNoturnoAntecipado INT,
    faltaParcialComoSaida INT,
    separaExtraInterJornada INT,
    desconsiderarIntervaloMenor INT,
    plantao INT,
    FOREIGN KEY (idCargaHoraria) REFERENCES cargaHoraria(idCargaHoraria)
);

-- Criação da tabela `politicaHorario`
CREATE TABLE politicaHorario (
    idPoliticaHorario INT PRIMARY KEY,
    idHorario INT NOT NULL,
    idPolitica INT NOT NULL,
    FOREIGN KEY (idHorario) REFERENCES horario(idHorario),
    FOREIGN KEY (idPolitica) REFERENCES politica(idPolitica)
);
