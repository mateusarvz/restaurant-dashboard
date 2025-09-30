import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import random
from datetime import datetime, timedelta
import gspread.utils


scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
client = gspread.authorize(creds)
sheet = client.open("DF-Pedidos").sheet1
dados = sheet.get_all_records()
df = pd.DataFrame(dados)

entradas = {
    "Tartar de Salmão": 35,
    "Carpaccio de Wagyu": 50,
    "Ceviche de Lagosta": 45,
    "Foie Gras Grelhado": 60,
    "Vieiras ao Molho Trufado": 55,
    "Salada de Aspargos": 28,
    "Bolinho de Siri": 30,
    "Bruschetta de Burrata": 25,
    "Sopa Cremosa de Lagosta": 40,
    "Ostras Frescas": 50
}

pratos = {
    "Filé Mignon ao Molho": 120,
    "Ravioli de Lagosta": 110,
    "Salmão Grelhado Especial": 95,
    "Risoto de Trufas Negras": 130,
    "Cordeiro Assado ao Alecrim": 140,
    "Peito de Pato Confit": 125,
    "Bacalhau à Portuguesa": 115,
    "Linguado ao Molho Limão": 105,
    "Frango Recheado com Brie": 90,
    "Tagliatelle ao Molho Funghi": 100,
    "Camarões ao Alho e Óleo": 95,
    "Medalhão de Porco Especial": 110,
    "Penne ao Molho Pesto": 85,
    "Costela Assada Lentamente": 135,
    "Polvo Grelhado com Ervas": 120,
    "Peixe do Dia Grelhado": 100,
    "Espaguete ao Molho Carbonara": 95,
    "Curry de Camarão Especial": 105,
    "Filé de Linguado Trufado": 125,
    "Frutos do Mar ao Vapor": 130,
    "Risoto de Camarão Rosa": 115,
    "Tournedor de Filé Mignon": 140,
    "Salmão ao Molho Mostarda": 100,
    "Cordeiro ao Vinho Tinto": 135,
    "Robalo ao Molho Champagne": 120,
    "Lasanha de Berinjela Gourmet": 90,
    "Bacalhau ao Molho Cremoso": 110,
    "Peito de Frango Trufado": 95,
    "Risoto de Cogumelos Frescos": 105,
    "Espetinhos de Camarão Grelhado": 115
}

sobremesas = {
    "Mousse de Chocolate Belga": 45,
    "Tartelette de Frutas Vermelhas": 40,
    "Panna Cotta de Baunilha": 38,
    "Cheesecake de Framboesa": 42,
    "Petit Gateau com Sorvete": 50,
    "Creme Brulée Tradicional": 45,
    "Sorvete Artesanal Variado": 35,
    "Tiramisu Clássico Italiano": 48,
    "Brownie de Chocolate Amargo": 40,
    "Coulant de Chocolate Branco": 50,
    "Pudim de Leite Cremoso": 38,
    "Gelatina de Champanhe": 35,
    "Panqueca de Maçã Caramelizada": 42,
    "Profiteroles com Chocolate": 45,
    "Macaron Sortido Francês": 48
}

bebidas = {
    "Vinho Tinto Cabernet": 80,
    "Vinho Branco Chardonnay": 75,
    "Espumante Brut": 90,
    "Champagne Dom Pérignon": 500,
    "Cerveja Artesanal": 35,
    "Suco de Laranja Natural": 20,
    "Água Mineral Com Gás": 15,
    "Água Mineral Sem Gás": 12,
    "Coquetel Margarita": 50,
    "Coquetel Mojito": 55,
    "Café Expresso": 18,
    "Café com Leite": 20,
    "Capuccino Gourmet": 25,
    "Chá de Camomila": 18,
    "Chá Verde Premium": 22,
    "Suco Detox Verde": 25,
    "Smoothie de Frutas Vermelhas": 30,
    "Suco de Abacaxi com Hortelã": 28,
    "Whisky Single Malt": 120,
    "Vodka Premium": 100,
    "Gin Tônica Especial": 90,
    "Rum Escuro": 85,
    "Tequila Silver": 95,
    "Licor de Café": 60,
    "Licor de Amêndoas": 55
}



ultima_linha = sheet.get_all_values()[-1]
ultimo_id = int(ultima_linha[0])

todas_linhas = sheet.get_all_values()
linhas_validas = [linha for linha in todas_linhas if linha[1].strip() != ""]

if linhas_validas:
    ultima_linha = linhas_validas[-1]
    data_str = ultima_linha[1]
    try:
        ultima_data = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        ultima_data = datetime.strptime(data_str, "%d/%m/%Y %H:%M:%S")


def gerar_proxima_data(base):
    
    pesos_dia_escolhido = [0.1, 0.1, 0.1, 0.3, 0.3, 1, 1]
    peso_atual_dia_escolhido = pesos_dia_escolhido[base.weekday()]

    escolha_dia_por_peso = random.choices(
        ["mesmo_dia", "proximo_dia"],
        weights=[peso_atual_dia_escolhido, 0.1],
        k=1
    )[0]

    if escolha_dia_por_peso == "proximo_dia":
        nova_data = base + timedelta(days=1)
        nova_data = nova_data.replace(hour=18, minute=0, second=0)
    else:
        nova_data = base
    
    if nova_data.hour >= 22 and nova_data.minute >= 30:
        nova_data = nova_data.replace(hour=18, minute=0, second=0) + timedelta(days=1)

    hora_min = max(18, nova_data.hour)

    horas_possiveis = list(range(hora_min, 23))
    pesos_horas = [3] + [1] * (len(horas_possiveis) - 1)
    hora_sorteada = random.choices(horas_possiveis, weights=pesos_horas, k=1)[0]

    if hora_sorteada == nova_data.hour:
        if nova_data.minute < 59:
            minuto_sorteado = random.randint(nova_data.minute, 59)
        else:
            hora_sorteada = min(hora_sorteada + 1, 22)  # limita até 22h
            minuto_sorteado = random.randint(0, 59)
    else:
        minuto_sorteado = random.randint(0, 59)

    return nova_data.replace(hour=hora_sorteada, minute=minuto_sorteado, second=0)

def gerar_pedido(num_pedido, inicio):
    while True:
        numeros_pedidos = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        pesos_pedidos = [75, 50, 100, 20, 2, 1, 0.5, 0.2, 0.1, 0.01]
        k_pedidos = random.choices(numeros_pedidos, weights=pesos_pedidos, k=1)[0]

        selected_entradas = random.choices(list(entradas.keys()), k=random.randint(0, min(k_pedidos, len(entradas))))
        selected_pratos = random.choices(list(pratos.keys()), k=random.randint(0, min(k_pedidos, len(pratos))))
        selected_sobremesas = random.choices(list(sobremesas.keys()), k=random.randint(0, min(k_pedidos, len(sobremesas))))
        selected_bebidas = random.choices(list(bebidas.keys()), k=random.randint(0, min(k_pedidos, len(bebidas))))

        if selected_entradas or selected_pratos or selected_sobremesas or selected_bebidas:
            break
    data_hora = gerar_proxima_data(inicio)
    total = sum(entradas.get(e, 0) for e in selected_entradas)
    total += sum(pratos.get(p, 0) for p in selected_pratos)
    total += sum(sobremesas.get(s, 0) for s in selected_sobremesas)
    total += sum(bebidas.get(b, 0) for b in selected_bebidas)


    return {
        "Pedido": num_pedido,
        "DataHora": data_hora.strftime("%Y-%m-%d %H:%M:%S"),
        "Entradas": ", ".join(selected_entradas) if selected_entradas else "Nenhuma",
        "Pratos": ", ".join(selected_pratos) if selected_pratos else "Nenhuma",
        "Sobremesas": ", ".join(selected_sobremesas) if selected_sobremesas else "Nenhuma",
        "Bebidas": ", ".join(selected_bebidas) if selected_bebidas else "Nenhuma",
        "Valor Total": total
    }, data_hora

if st.button("Gerar Pedidos"):
    data_base = ultima_data
    pedidos_para_inserir = []

    for i in range(12873):
        pedido, data_base = gerar_pedido(ultimo_id + i + 1, data_base)
        pedidos_para_inserir.append(list(pedido.values()))

    primeira_linha = len(sheet.get_all_values()) + 1
    ultima_linha = primeira_linha + len(pedidos_para_inserir) - 1
    num_colunas = len(pedidos_para_inserir[0])

    cell_range = f"A{primeira_linha}:{chr(64 + num_colunas)}{ultima_linha}"
    sheet.update(cell_range, pedidos_para_inserir)