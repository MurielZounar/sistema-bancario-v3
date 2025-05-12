from abc import ABC, abstractmethod
from datetime import datetime
import os

class Client:
    def __init__(self, address):
        self._address = address
        self._accounts = []
    
    @property
    def accounts(self):
        return self._accounts

    def add_account(self, account):
        self._accounts.append(account)

    def make_transaction(self, account, transaction):
        transaction.register(account)

class PersonalAccount(Client):
    def __init__(self, doc_id, name, birth_date, address):
        super().__init__(address)
        self._doc_id = doc_id
        self._name = name
        self._birth_date = birth_date

    @property
    def doc_id(self):
        return self._doc_id
    
    @property
    def name(self):
        return self._name
    
    def __str__(self):
        return f'{self._name}\n\t{self._birth_date}\n\t{self._address}\n\n'

class History:
    def __init__(self):
        self._transactions = []

    @property
    def transactions(self):
        return self._transactions

    def add_transaction(self, transaction):
        self._transactions.append(
            {
                'type': transaction.__class__.__name__,
                'value': transaction.value,
                'date': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            }
        )

class Account:
    def __init__(self, number: int, client: Client):
        self._balance = 0
        self._number = number
        self._agency = '001'
        self._client = client
        self._history = History()

    @classmethod
    def new_account(cls, number: int, client: Client):
        return cls(number, client)
    
    @property
    def balance(self) -> float:
        return self._balance

    @property
    def number(self):
        return self._number

    @property
    def agency(self):
        return self._agency

    @property
    def client(self):
        return self._client

    @property
    def history(self):
        return self._history

    def deposit(self, value) -> bool:
        if value > 0:
            self._balance += value
            print('\nDepósito realizado com sucesso!\n')
            return True
        else:
            print('\nValor inválido!\n')
        
        return False

    def withdraw(self, value) -> bool:
        balance = self._balance
        balance_exceeded = value > balance

        if balance_exceeded:
            print('\nFalha na aperação!\n\nNão há saldo suficiente para realizar esta operação.\n')
        elif value > 0:
            self._balance -= value 
            print('\nSaque realizado com sucesso!\n')
            return True
        else:
            print('\nFalha na aperação!\n\nValor inválido!\n')

        return False

class CurrentAccount(Account):
    def __init__(self, number, client, limit = 500, withdrawals_limit = 3):
        super().__init__(number, client)
        self._limit = limit
        self._withdrawals_limit = withdrawals_limit

    def withdraw(self, value):
        number_of_withdrawals = len([transaction for transaction in self.history.transactions if transaction['type'] == Withdraw.__name__])

        limit_exceeded = value > self._limit
        withdrawals_exceeded = number_of_withdrawals >= self._withdrawals_limit

        if limit_exceeded:
            print('\nOperação não permitida!\n\nO valor escede seu limite por saque.\n')
        elif withdrawals_exceeded:
            print('\nOperação não permitida!\n\nVocê atingiu a quantidade máxima de saques.\n')
        else:
            return super().withdraw(value)
        
        return False
    
    def __str__(self):
        return f'Agência: \t{self.agency}\n\tC/C:\t\t{self.number}\n\tTitular:\t{self.client.name}'
    
class Transaction(ABC):
    @property
    @abstractmethod
    def value(self):
        pass
    
    @abstractmethod
    def register(self, account):
        pass

class Deposit(Transaction):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value
    
    def register(self, account):
        transaction_ok = account.deposit(self.value)

        if transaction_ok:
            account.history.add_transaction(self)

class Withdraw(Transaction):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value
    
    def register(self, account):
        transaction_ok = account.withdraw(self.value)

        if transaction_ok:
            account.history.add_transaction(self)

def new_window(title=''):
    os.system('cls')
    WIDTH = 100
    BANK_NAME = f"{' Mu Bank '.center(WIDTH, '=')}\n"

    print(BANK_NAME)

    if title:
        print(title.upper().center(WIDTH))

def menu():
    new_window()
    menu = f'''[1] - Cadastrar Usuário
[2] - Cadastrar Conta Corrente
[3] - Depósito
[4] - Saque
[5] - Extrato
[6] - Listar Usuários
[7] - Listar Contas Correntes
[0] - Sair
    '''
    print(menu)
    
    option = int(input('Digite a opção desejada: '))
    
    return option

def get_client_by_doc_id(doc_id, clients):
    filtered_clients = [client for client in clients if client.doc_id == doc_id]
    return filtered_clients[0] if filtered_clients else None

def get_client_account(client):
    if not client.accounts:
        print('\nO cliente não possui contas cadastradas!\n')
        return
    
    return client.accounts[0]

def get_client(clients):
    doc_id = input('CPF do cliente (apenas números): ')
    client = get_client_by_doc_id(doc_id, clients)

    if not client:
        print('\nCliente não encontrado!\nVerifique o CPF informado e tente novamente.\n')
        return None
    
    return client

def deposit(clients):
    new_window('DEPÓSITO')
    client = get_client(clients)
    if client:
        new_window('DEPÓSITO')
        value = float(input('Valor do depósito: R$'))
        transaction = Deposit(value)
        account = get_client_account(client)

        if not account:
            return

        client.make_transaction(account, transaction)
    
def withdraw(clients):
    new_window('SAQUE')
    client = get_client(clients)
    if client:
        new_window('SAQUE')
        value = float(input('Valor do saque: R$'))
        transaction = Withdraw(value)
        account = get_client_account(client)

        if not account:
            return

        client.make_transaction(account, transaction)

def extract(clients):
    new_window('EXTRATO')
    client = get_client(clients)
    if client:
        new_window('EXTRATO')
        account = get_client_account(client)
        if not account:
            return
        
        new_window('EXTRATO')
        transactions = account.history.transactions

        extract = ''
        if not transactions:
            extract = '\nNão foram realizadas movimentações.\n'
        else:
            for transaction in transactions:
                extract += f'\n{'Depósito' if transaction['type'] == 'Deposit' else 'Saque'}:\n\tR${transaction['value']:.2f}'

        print(extract)
        print(f'\nSaldo:\n\tR${account.balance:.2f}')
    
def create_account(account_number, clients, accounts):
    new_window('CADASTRAR CONTA')
    client = get_client(clients)
    if client:
        new_window('CADASTRAR CONTA')
        account = CurrentAccount.new_account(client=client, number=account_number)
        accounts.append(account)
        client.accounts.append(account)

        print('\nConta criada com sucesso!')

def list_accounts(accounts):
    new_window('LISTA DE CONTAS')

    for account in accounts:
        print('-' * 20)
        print(f'\t{str(account)}')

def create_client(clients):
    new_window('CADASTRAR CLIENTE')
    doc_id = input('CPF do cliente (apenas números): ')
    client = get_client_by_doc_id(doc_id, clients)
    if client:
        print('\nCliente já encontrado!\nVerifique o CPF informado e tente novamente.\n')
        return

    new_window('CADASTRAR CLIENTE')

    name = input('Nome: ')
    birth_date = input('Data Nascimento (dd/mm/aaa): ')
    doc_id = doc_id
    print('\nEndereço\n')
    address = f'{input('Logradouro: ')}, {input('Número: ')} - {input('Bairro: ')}, {input('Cidade: ')}/{input('UF: ')}'

    client = PersonalAccount(name=name, birth_date=birth_date, doc_id=doc_id, address=address)
    clients.append(client)
    print('\n === Cliente cadastrado com sucesso! ===')

def list_clients(clients):
    new_window('LISTA DE CONTAS')

    for client in clients:
        print('-' * 20)
        print(f'\t{str(client)}')

def main():
    OPTIONS = [0, 1, 2, 3, 4, 5, 6, 7]
    clients = []
    accounts = []

    while True:
        option = menu()

        if option in OPTIONS:
            if option == 1:
                create_client(clients)
            elif option == 2:
                number = len(accounts) + 1
                create_account(number, clients, accounts)
            elif option == 3:
                deposit(clients)
            elif option == 4:
                withdraw(clients)
            elif option == 5:
                extract(clients)
            elif option == 6:
                list_clients(clients)
            elif option == 7:
                list_accounts(accounts)
            else:
                os.system('cls')
                print('\nPrograma encerrado!')
                break

            input('Pressione ENTER para voltar ao menu principal.')
        else:
            print('\nOpção inválida!\n')
            input('Pressione ENTER para voltar ao menu principal.')

if __name__ == '__main__':
    main()