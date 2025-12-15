import sys
from pathlib import Path
from tqdm import tqdm
import requests
import pandas as pd
from collections import Counter, defaultdict
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
from functools import lru_cache

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.credentials import read_api_key

API_KEY = read_api_key()
BASE = "https://mathgenealogy.org:8000/api/v2/MGP"
HEADER = {"x-access-token": API_KEY}

# Configurações de otimização
MAX_WORKERS = 10  # Número de requisições paralelas
CACHE_FILE = "cache_brazil_data.json"

def save_cache(data, filename=CACHE_FILE):
    """Salva dados em cache"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"   Cache salvo: {filename}")

def load_cache(filename=CACHE_FILE):
    """Carrega dados do cache"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def get_mathematician_ids_by_country(country_name):
    """Busca IDs de matemáticos formados em um país"""
    url = f"{BASE}/search?country={country_name}"
    response = requests.get(url, headers=HEADER)
    response.raise_for_status()
    ids = response.json()
    
    if not ids:
        return []
    
    if isinstance(ids[0], list):
        return [id_list[0] for id_list in ids if id_list]
    else:
        return ids

def get_mathematician_details(mgp_id):
    """Busca detalhes de um matemático pelo ID"""
    url = f"{BASE}/acad?id={mgp_id}"
    response = requests.get(url, headers=HEADER)
    response.raise_for_status()
    return response.json()

def get_mathematician_range(start, stop, step=1):
    """Busca matemáticos usando o endpoint de range (mais eficiente)"""
    url = f"{BASE}/acad/range?start={start}&stop={stop}&step={step}"
    response = requests.get(url, headers=HEADER)
    response.raise_for_status()
    return response.json()

def fetch_mathematician_parallel(mgp_id):
    """Função auxiliar para busca paralela"""
    try:
        return get_mathematician_details(mgp_id)
    except Exception as e:
        print(f"\n   Erro ao buscar ID {mgp_id}: {e}")
        return None

def fetch_all_mathematicians_parallel(ids, max_workers=MAX_WORKERS):
    """Busca detalhes de múltiplos matemáticos em paralelo"""
    mathematicians_data = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(fetch_mathematician_parallel, mgp_id): mgp_id 
                        for mgp_id in ids}
        
        for future in tqdm(as_completed(future_to_id), total=len(ids), desc="   Processando"):
            result = future.result()
            if result:
                mathematicians_data.append(result)
    
    return mathematicians_data

def extract_advisor_info(academic_data):
    """Extrai informações dos orientadores"""
    advisors = []
    if 'MGP_academic' in academic_data:
        student_data = academic_data['MGP_academic'].get('student_data', {})
        degrees = student_data.get('degrees', [])
        for degree in degrees:
            advised_by = degree.get('advised by', {})
            for advisor_id, advisor_name in advised_by.items():
                advisors.append((advisor_id, advisor_name))
    return advisors

def extract_advisees_info(academic_data):
    """Extrai informações dos orientandos"""
    advisees = []
    if 'MGP_academic' in academic_data:
        student_data = academic_data['MGP_academic'].get('student_data', {})
        descendants = student_data.get('descendants', {})
        advisees_dict = descendants.get('advisees', {})
        for advisee_id, advisee_name in advisees_dict.items():
            advisees.append((advisee_id, advisee_name))
    return advisees

def extract_school_info(academic_data):
    """Extrai informações da escola"""
    schools = []
    if 'MGP_academic' in academic_data:
        student_data = academic_data['MGP_academic'].get('student_data', {})
        degrees = student_data.get('degrees', [])
        for degree in degrees:
            degree_schools = degree.get('schools', [])
            schools.extend(degree_schools)
    return schools

def main():
    print("=" * 80)
    print("ANÁLISE DO MATHEMATICS GENEALOGY PROJECT - BRASIL")
    print("=" * 80)
    
    start_time = time.time()
    
    # Verificar se existe cache
    cached_data = load_cache()
    
    if cached_data:
        print("\n[CACHE] Cache encontrado! Deseja usar? (s/n): ", end="")
        use_cache = input().strip().lower()
        
        if use_cache == 's':
            print("   Usando dados do cache")
            brazil_ids = cached_data['ids']
            mathematicians_data = cached_data['data']
            print(f"   Carregados {len(brazil_ids)} IDs e {len(mathematicians_data)} registros")
            goto_analysis = True
        else:
            goto_analysis = False
    else:
        goto_analysis = False
    
    if not goto_analysis:
        # 1. Buscar todos os matemáticos formados no Brasil
        print("\n[1/6] Buscando IDs de matemáticos formados no Brasil...")
        brazil_ids = get_mathematician_ids_by_country("Brazil")
        print(f"   Encontrados {len(brazil_ids)} matemáticos formados no Brasil")
        
        # 2. Buscar detalhes de cada matemático
        print("\n[2/6] Buscando detalhes de cada matemático...")
        print("   Escolha o método:")
        print("   1. Paralelo (rápido, múltiplas requisições simultâneas)")
        print("   2. Sequencial (lento, mas seguro)")
        
        choice = input("   Opção (1/2) [padrão=1]: ").strip() or "1"
        
        if choice == "1":
            print(f"   Usando método PARALELO com {MAX_WORKERS} workers")
            mathematicians_data = fetch_all_mathematicians_parallel(brazil_ids, MAX_WORKERS)
        else:
            print("   Usando método SEQUENCIAL")
            mathematicians_data = []
            for mgp_id in tqdm(brazil_ids, desc="   Processando"):
                try:
                    data = get_mathematician_details(mgp_id)
                    mathematicians_data.append(data)
                except Exception as e:
                    print(f"\n   Erro ao buscar ID {mgp_id}: {e}")
        
        print("\n   Salvando cache para uso futuro...")
        save_cache({
            'ids': brazil_ids,
            'data': mathematicians_data,
            'timestamp': time.time()
        })
    
    elapsed = time.time() - start_time
    print(f"\n   Tempo decorrido: {elapsed:.2f} segundos")
    print(f"   Dados coletados: {len(mathematicians_data)} registros")
    
    # 3. Análise: Quais matemáticos orientaram mais alunos no Brasil?
    print("\n[3/6] Analisando orientadores com mais alunos...")
    advisor_count = Counter()
    advisor_names = {}
    
    for data in mathematicians_data:
        advisors = extract_advisor_info(data)
        for advisor_id, advisor_name in advisors:
            advisor_count[advisor_id] += 1
            advisor_names[advisor_id] = advisor_name
    
    print("\n   TOP 10 ORIENTADORES COM MAIS ALUNOS NO BRASIL:")
    print("   " + "-" * 70)
    for advisor_id, count in advisor_count.most_common(10):
        print(f"   {advisor_names.get(advisor_id, 'Nome desconhecido'):40s} - {count:3d} alunos")
    
    # 4. Análise: Quais universidades brasileiras formaram mais doutores?
    print("\n[4/6] Analisando universidades que mais formaram doutores...")
    school_count = Counter()
    
    for data in mathematicians_data:
        schools = extract_school_info(data)
        for school in schools:
            # Filtrar apenas escolas brasileiras
            if "Brazil" in school or "Brasil" in school:
                school_count[school] += 1
    
    print("\n   TOP 10 UNIVERSIDADES BRASILEIRAS:")
    print("   " + "-" * 70)
    for school, count in school_count.most_common(10):
        print(f"   {school:50s} - {count:3d} doutores")
    
    # 5. Análise: Matemático formado no Brasil com mais descendentes
    print("\n[5/6] Analisando matemáticos com mais descendentes...")
    max_descendants = 0
    top_mathematician = None
    
    for data in mathematicians_data:
        if 'MGP_academic' in data:
            academic = data['MGP_academic']
            student_data = academic.get('student_data', {})
            descendants = student_data.get('descendants', {})
            descendant_count = descendants.get('descendant_count', 0)
            
            if descendant_count > max_descendants:
                max_descendants = descendant_count
                top_mathematician = academic
    
    if top_mathematician:
        name = f"{top_mathematician.get('given_name', '')} {top_mathematician.get('family_name', '')}"
        print(f"\n   Matemático com mais descendentes: {name}")
        print(f"   Total de descendentes: {max_descendants}")
    
    # 6. Análise do grafo: vértices isolados e componente conexo
    print("\n[6/6] Analisando estrutura do grafo...")
    
    # Construir grafo
    G = nx.DiGraph()
    
    for data in mathematicians_data:
        if 'MGP_academic' in data:
            academic = data['MGP_academic']
            student_id = academic.get('ID')
            
            # Adicionar arestas (orientador -> orientando)
            advisors = extract_advisor_info(data)
            for advisor_id, _ in advisors:
                G.add_edge(advisor_id, student_id)
    
    # Converter para grafo não-direcionado para análise de componentes
    G_undirected = G.to_undirected()
    
    # Vértices isolados (sem orientador e sem orientandos)
    isolated_nodes = list(nx.isolates(G_undirected))
    print(f"\n   Doutores que não orientaram ninguém e não têm orientador registrado: {len(isolated_nodes)}")
    
    # Doutores sem orientandos (mas podem ter orientador)
    no_advisees = []
    for data in mathematicians_data:
        if 'MGP_academic' in data:
            academic = data['MGP_academic']
            student_id = academic.get('ID')
            student_data = academic.get('student_data', {})
            descendants = student_data.get('descendants', {})
            advisees = descendants.get('advisees', {})
            
            if not advisees or (isinstance(advisees, list) and len(advisees) == 1 and advisees[0] == ""):
                no_advisees.append(student_id)
    
    print(f"   Doutores que não orientaram ninguém: {len(no_advisees)}")
    
    # Componentes conexos
    if len(G_undirected) > 0:
        components = list(nx.connected_components(G_undirected))
        components_sorted = sorted(components, key=len, reverse=True)
        
        print(f"\n   Número de componentes conexos: {len(components)}")
        
        if components_sorted:
            largest_component = components_sorted[0]
            print(f"   Tamanho do maior componente: {len(largest_component)} vértices")
            print(f"   Percentual do grafo: {100 * len(largest_component) / len(G_undirected):.2f}%")
            
            # componente gigante se > 50% dos vértices
            if len(largest_component) / len(G_undirected) > 0.5:
                print("   SIM, é um componente gigante (> 50% dos vértices)")
            else:
                print("   NÃO é um componente gigante (< 50% dos vértices)")
            
            # distribuição dos top 5 componentes
            print("\n   TOP 5 MAIORES COMPONENTES:")
            for i, comp in enumerate(components_sorted[:5], 1):
                print(f"   {i}. {len(comp)} vértices ({100 * len(comp) / len(G_undirected):.2f}%)")
    else:
        print("\n   Grafo vazio - nenhum vértice encontrado")
    
    print("\n[SALVANDO] Exportando resultados...")
    
    df_data = []
    for data in mathematicians_data:
        if 'MGP_academic' in data:
            academic = data['MGP_academic']
            student_data = academic.get('student_data', {})
            descendants = student_data.get('descendants', {})
            
            df_data.append({
                'ID': academic.get('ID'),
                'Nome': f"{academic.get('given_name', '')} {academic.get('family_name', '')}",
                'Descendentes': descendants.get('descendant_count', 0),
                'Orientandos_Diretos': len(descendants.get('advisees', {}))
            })
    
    df = pd.DataFrame(df_data)
    df.to_csv('matematicos_brasil.csv', index=False)
    print("   Salvo: matematicos_brasil.csv")
    
    total_time = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"ANÁLISE CONCLUÍDA EM {total_time:.2f} SEGUNDOS!")
    print("=" * 80)

if __name__ == "__main__":
    main()