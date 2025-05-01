import requests
import json

def test_cadastro():
    # Dados de teste
    dados_fan = {
        "nome": "Teste da Silva",
        "email": "teste@exemplo.com",
        "endereco": "Rua de Teste, 123",
        "cpf": "123.456.789-00",
        "atividades": ["Streaming", "Cosplay"],
        "interesses": ["CS:GO", "LoL"],
        "eventos": ["CBLOL 2023"],
        "compras": ["Camiseta FURIA"]
    }

    # Enviar requisição POST para o endpoint
    response = requests.post("http://localhost:8000/cadastro", json=dados_fan)

    # Verificar resposta
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")

    # Verificar se foi cadastrado corretamente
    assert response.status_code == 200
    assert "id" in response.json()
    assert "mensagem" in response.json()
    assert response.json()["mensagem"] == "Cadastro realizado com sucesso!"

    return response.json()["id"]

if __name__ == "__main__":
    fan_id = test_cadastro()
    print(f"Fã cadastrado com ID: {fan_id}")