import abc


class InvalidCNPJException(Exception):
    """Exception for when an invalid CNPJ is detected"""


class CompaniesDatabaseInterface(abc.ABC):
    """
    Interface to access data from Receita Federal do Brasil.
    """

    @abc.abstractmethod
    def get_company(self, cnpj: str = ""):
        """
        Get information about a company by its CNPJ.
        """

    @abc.abstractmethod
    def get_partners(self, cnpj: str = ""):
        """
        Get information about the partners of a company by the company's CNPJ.
        """


class CompaniesAccessInterface(abc.ABC):
    """
    Rules to interact with companies.
    """

    @abc.abstractmethod
    def get_company(self, cnpj: str = ""):
        """
        Method to get information about a company.
        """

    @abc.abstractmethod
    def get_partners(self, cnpj: str = ""):
        """
        Method to get information about the partners of a company.
        """


class CompaniesAccess(CompaniesAccessInterface):
    _database_gateway = None

    def __init__(self, database_gateway=None):
        self._database_gateway = database_gateway

    def get_company(self, cnpj: str = ""):
        cnpj_info = self._database_gateway.get_company(cnpj)
        return vars(cnpj_info) if cnpj_info is not None else None

    def get_partners(self, cnpj: str = ""):
        total_partners, partners = self._database_gateway.get_partners(cnpj)
        return (total_partners, [vars(partner) for partner in partners])


class Company:
    """
    Item to represent a company in memory inside the module
    """

    def __init__(
        self,
        cnpj_basico,
        cnpj_ordem,
        cnpj_dv,
        cnpj_completo,
        cnpj_completo_apenas_numeros,
        identificador_matriz_filial,
        nome_fantasia,
        situacao_cadastral,
        data_situacao_cadastral,
        motivo_situacao_cadastral,
        nome_cidade_exterior,
        data_inicio_atividade,
        cnae_fiscal_secundario,
        tipo_logradouro,
        logradouro,
        numero,
        complemento,
        bairro,
        cep,
        uf,
        ddd_telefone_1,
        ddd_telefone_2,
        ddd_telefone_fax,
        correio_eletronico,
        situacao_especial,
        data_situacao_especial,
        pais,
        municipio,
        razao_social,
        natureza_juridica,
        qualificacao_do_responsavel,
        capital_social,
        porte,
        ente_federativo_responsavel,
        opcao_pelo_simples,
        data_opcao_pelo_simples,
        data_exclusao_pelo_simples,
        opcao_pelo_mei,
        data_opcao_pelo_mei,
        data_exclusao_pelo_mei,
        cnae,
    ):
        self.cnpj_basico = cnpj_basico
        self.cnpj_ordem = cnpj_ordem
        self.cnpj_dv = cnpj_dv
        self.cnpj_completo = cnpj_completo
        self.cnpj_completo_apenas_numeros = cnpj_completo_apenas_numeros
        self.identificador_matriz_filial = identificador_matriz_filial
        self.nome_fantasia = nome_fantasia
        self.situacao_cadastral = situacao_cadastral
        self.data_situacao_cadastral = data_situacao_cadastral
        self.motivo_situacao_cadastral = motivo_situacao_cadastral
        self.nome_cidade_exterior = nome_cidade_exterior
        self.data_inicio_atividade = data_inicio_atividade
        self.cnae_fiscal_secundario = cnae_fiscal_secundario
        self.tipo_logradouro = tipo_logradouro
        self.logradouro = logradouro
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cep = cep
        self.uf = uf
        self.ddd_telefone_1 = ddd_telefone_1
        self.ddd_telefone_2 = ddd_telefone_2
        self.ddd_telefone_fax = ddd_telefone_fax
        self.correio_eletronico = correio_eletronico
        self.situacao_especial = situacao_especial
        self.data_situacao_especial = data_situacao_especial
        self.pais = pais
        self.municipio = municipio
        self.razao_social = razao_social
        self.natureza_juridica = natureza_juridica
        self.qualificacao_do_responsavel = qualificacao_do_responsavel
        self.capital_social = capital_social
        self.porte = porte
        self.ente_federativo_responsavel = ente_federativo_responsavel
        self.opcao_pelo_simples = opcao_pelo_simples
        self.data_opcao_pelo_simples = data_opcao_pelo_simples
        self.data_exclusao_pelo_simples = data_exclusao_pelo_simples
        self.opcao_pelo_mei = opcao_pelo_mei
        self.data_opcao_pelo_mei = data_opcao_pelo_mei
        self.data_exclusao_pelo_mei = data_exclusao_pelo_mei
        self.cnae = cnae

    def __hash__(self):
        return hash(self.cnpj_completo)

    def __eq__(self, other):
        return self.cnpj_completo == other.cnpj_completo

    def __repr__(self):
        return (
            f"Company({self.cnpj_completo}, {self.nome_fantasia}, {self.razao_social})"
        )


class Partner:
    """
    Item to represent a company in memory inside the module
    """

    def __init__(
        self,
        cnpj_basico,
        cnpj_ordem,
        cnpj_dv,
        cnpj_completo,
        cnpj_completo_apenas_numeros,
        identificador_socio,
        razao_social,
        cnpj_cpf_socio,
        qualificacao_socio,
        data_entrada_sociedade,
        pais_socio_estrangeiro,
        numero_cpf_representante_legal,
        nome_representante_legal,
        qualificacao_representante_legal,
        faixa_etaria,
    ):
        self.cnpj_basico = cnpj_basico
        self.cnpj_ordem = cnpj_ordem
        self.cnpj_dv = cnpj_dv
        self.cnpj_completo = cnpj_completo
        self.cnpj_completo_apenas_numeros = cnpj_completo_apenas_numeros
        self.identificador_socio = identificador_socio
        self.razao_social = razao_social
        self.cnpj_cpf_socio = cnpj_cpf_socio
        self.qualificacao_socio = qualificacao_socio
        self.data_entrada_sociedade = data_entrada_sociedade
        self.pais_socio_estrangeiro = pais_socio_estrangeiro
        self.numero_cpf_representante_legal = numero_cpf_representante_legal
        self.nome_representante_legal = nome_representante_legal
        self.qualificacao_representante_legal = qualificacao_representante_legal
        self.faixa_etaria = faixa_etaria

    def __hash__(self):
        return hash(self.cnpj_completo)

    def __eq__(self, other):
        return self.cnpj_completo == other.cnpj_completo

    def __repr__(self):
        return f"Partner({self.cnpj_completo}, {self.cnpj_cpf_socio}, {self.numero_cpf_representante_legal}, {self.razao_social})"


def create_companies_interface(database_gateway: CompaniesDatabaseInterface):
    if not isinstance(database_gateway, CompaniesDatabaseInterface):
        raise Exception(
            "Database gateway should implement the CompaniesDatabaseInterface interface"
        )
    return CompaniesAccess(database_gateway)
