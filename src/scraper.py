from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

print(ChromeDriverManager().install())
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Ejecutar en modo headless
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-notifications')

    # Configurar el servicio y asegurarse de usar el ejecutable correcto
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def get_player_data(player_id, driver):
    """Obtiene los datos de un jugador usando Selenium"""
    url = f"https://resultadosffcv.isquad.es/jugador_ficha.php?id_jugador={player_id}"
    
    try:
        print(f"\nAccediendo a URL del jugador: {url}")
        driver.get(url)
        
        # Esperar a que cargue el contenido principal
        time.sleep(2)  # Espera para que el popup aparezca
        
        # Intentar cerrar el popup si existe
        try:
            popup = driver.find_element(By.CLASS_NAME, "block")
            if popup.is_displayed():
                # Hacer clic en algún lugar fuera del popup
                body = driver.find_element(By.TAG_NAME, "body")
                body.click()
        except:
            pass  # Si no hay popup, continuamos
        
        # Esperar a que el contenido real esté disponible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "playerName"))
        )
        
        # Obtener el HTML después de manejar el popup
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Obtener nombre del jugador
        player_name_elem = soup.find('h1', id='playerName')
        player_name = player_name_elem.text.strip() if player_name_elem else "Nombre no encontrado"
        print(f"Nombre encontrado: {player_name}")
        
        # Inicializar diccionario con el nombre
        player_data = {'Nombre': player_name}
        
        # Obtener estadísticas
        for div in soup.find_all('div', class_='bloque_general_sidebar_ficha_jugador'):
            section = div.find('section')
            if section and section.find('h3') and 'Estadísticas' in section.find('h3').text:
                labels = section.find_all('div', class_='label_ficha')
                values = section.find_all('div', class_='enlace_sidebar info')
                
                print("\nEstadísticas encontradas:")
                for label, value in zip(labels, values):
                    label_text = label.text.strip()
                    # Limpiar etiquetas de tarjetas
                    if 'tarjetas_plantilla' in label.get('class', []):
                        if 'Amarillas' in label_text:
                            label_text = 'Tarjetas Amarillas'
                        elif 'Rojas' in label_text:
                            label_text = 'Tarjetas Rojas'
                    
                    value_text = value.text.strip()
                    player_data[label_text] = value_text
                    print(f"{label_text}: {value_text}")
        
        return player_data
            
    except Exception as e:
        print(f"Error procesando jugador {player_id}: {e}")
        return None

def get_team_player_ids(team_url, driver):
    """Obtiene los IDs de los jugadores del equipo"""
    try:
        print(f"Accediendo a URL del equipo: {team_url}")
        driver.get(team_url)
        
        # Esperar a que cargue la página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )
        
        # Parsear el HTML
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Encontrar los enlaces de los jugadores
        player_links = soup.find_all('a', href=lambda x: x and 'jugador_ficha.php' in x)
        player_ids = []
        
        for link in player_links:
            href = link.get('href')
            if 'id_jugador=' in href:
                player_id = href.split('id_jugador=')[1].split('&')[0]
                player_ids.append(player_id)
                print(f"ID de jugador encontrado: {player_id}")
        
        return player_ids
    
    except Exception as e:
        print(f"Error obteniendo IDs de jugadores: {e}")
        return []

def main():
    # URL del equipo
    team_url = "https://resultadosffcv.isquad.es/equipo_plantilla.php?id_temp=20&id_modalidad=33327&id_competicion=903498407&id_equipo=20477&torneo_equipo=903498408&id_torneo=903498408"
    
    driver = setup_driver()
    try:
        # Obtener IDs de jugadores
        print("Obteniendo IDs de jugadores...")
        player_ids = get_team_player_ids(team_url, driver)
        
        # Obtener datos de cada jugador
        all_players_data = []
        for player_id in player_ids:
            player_data = get_player_data(player_id, driver)
            if player_data:
                all_players_data.append(player_data)
            time.sleep(1)  # Espera entre peticiones
        
        # Crear DataFrame y guardar en CSV
        if all_players_data:
            df = pd.DataFrame(all_players_data)
            output_file = 'data/player_statistics.csv'
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"\nDatos guardados en {output_file}")
            print("\nDatos recopilados:")
            print(df)
        else:
            print("No se recopilaron datos")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()