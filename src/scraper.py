import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from utils.helpers import load_config, ensure_output_directory

class FootballScraper:
    def __init__(self):
        self.config = load_config()
        ensure_output_directory(self.config['output_dir'])
        
    def get_player_ids(self, team_url):
        """Extract player IDs from the team page"""
        try:
            response = requests.get(team_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            player_links = soup.find_all('a', href=lambda x: x and 'jugador_ficha.php' in x)
            
            player_ids = []
            for link in player_links:
                href = link.get('href')
                player_id = href.split('id_jugador=')[1].split('&')[0]
                player_ids.append(player_id)
                
            return player_ids
        
        except requests.RequestException as e:
            print(f"Error fetching team page: {e}")
            return []

    def get_player_data(self, player_id):
        """Scrape individual player data"""
        base_url = "https://resultadosffcv.isquad.es/jugador_ficha.php"
        url = f"{base_url}?id_jugador={player_id}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            player_name = soup.find('h1', id='playerName').text.strip()
            
            stats_header = soup.find('h3', string='Estadísticas')
            if stats_header:
                stats_table = stats_header.find_next('table')
                
                stats_data = {}
                if stats_table:
                    rows = stats_table.find_all('tr')
                    for row in rows:
                        cols = row.find_all(['th', 'td'])
                        if len(cols) >= 2:
                            key = cols[0].text.strip()
                            value = cols[1].text.strip()
                            stats_data[key] = value
                
                stats_data['Nombre'] = player_name
                return stats_data
            
            return None
        
        except requests.RequestException as e:
            print(f"Error fetching player {player_id}: {e}")
            return None

    def run(self, team_url):
        """Main scraping process"""
        print("Getting player IDs...")
        player_ids = self.get_player_ids(team_url)
        
        all_player_data = []
        print(f"Found {len(player_ids)} players. Starting to scrape player data...")
        
        for player_id in player_ids:
            print(f"Scraping player {player_id}...")
            player_data = self.get_player_data(player_id)
            if player_data:
                all_player_data.append(player_data)
            time.sleep(self.config['delay'])
        
        if all_player_data:
            df = pd.DataFrame(all_player_data)
            output_file = os.path.join(self.config['output_dir'], 'player_statistics.csv')
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"Data saved to {output_file}")
        else:
            print("No data was collected")

def main():
    team_url = "https://resultadosffcv.isquad.es/equipo_plantilla.php?id_temp=20&id_modalidad=33327&id_competicion=903498407&id_equipo=20477&torneo_equipo=903498408&id_torneo=903498408"
    scraper = FootballScraper()
    scraper.run(team_url)

if __name__ == "__main__":
    main()