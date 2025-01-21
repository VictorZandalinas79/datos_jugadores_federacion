import requests
from bs4 import BeautifulSoup

def test_scraper():
    # URL de prueba con un jugador específico
    url = "https://resultadosffcv.isquad.es/jugador_ficha.php?id_jugador=88317"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    }
    
    try:
        # Hacer la petición
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Guardar el HTML recibido
        with open('test_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar el nombre
        print("\nBuscando nombre del jugador...")
        print("Todos los h1 encontrados:")
        for h1 in soup.find_all('h1'):
            print(f"H1: {h1}")
            print(f"Atributos: {h1.attrs}")
        
        # Buscar las estadísticas
        print("\nBuscando estadísticas...")
        print("Todos los divs con clase bloque_general_sidebar_ficha_jugador:")
        for div in soup.find_all('div', class_='bloque_general_sidebar_ficha_jugador'):
            print(f"\nDiv encontrado:")
            print(div.prettify())
            
            # Buscar sección de estadísticas dentro del div
            section = div.find('section')
            if section:
                print("\nSección encontrada dentro del div:")
                print(section.prettify())
                
                # Buscar las estadísticas
                labels = section.find_all('div', class_='label_ficha')
                values = section.find_all('div', class_='enlace_sidebar info')
                
                print("\nEstadísticas encontradas:")
                for label, value in zip(labels, values):
                    print(f"{label.text.strip()}: {value.text.strip()}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_scraper()