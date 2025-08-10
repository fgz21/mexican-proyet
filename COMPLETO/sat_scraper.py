from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_sat_data(rfc, id_cif):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(f"https://siat.sat.gob.mx/app/qr/faces/pages/mobile/validadorqr.jsf?D1=10&D2=1&D3={id_cif}_{rfc}")
        
        # Esperar y hacer clic en el botón de búsqueda
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "form1:botonBuscar"))
        ).click()
        
        # Esperar a que carguen los resultados
        time.sleep(3)
        
        # Extraer datos
        data = {
            'nombre': driver.find_element(By.XPATH, '//span[contains(text(),"Nombre:")]/following-sibling::span').text,
            'rfc': driver.find_element(By.XPATH, '//span[contains(text(),"RFC:")]/following-sibling::span').text,
            'fecha_nacimiento': driver.find_element(By.XPATH, '//span[contains(text(),"Fecha de nacimiento:")]/following-sibling::span').text
        }
        
        return data
    except Exception as e:
        print(f"Error durante scraping: {str(e)}")
        return None
    finally:
        driver.quit()