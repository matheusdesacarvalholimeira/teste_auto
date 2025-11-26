# tests/test_calc.py
import os
import time
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))  # assume tests/ está em pasta do projeto
HTML_PATH = 'file://' + os.path.abspath(os.path.join(ROOT, 'calculator.html'))
SCREEN_DIR = os.path.join(ROOT, 'screenshots')
os.makedirs(SCREEN_DIR, exist_ok=True)

def open_calc(driver):
    driver.get(HTML_PATH)
    time.sleep(0.3)

def read_results(driver):
    inss = driver.find_element(By.ID, 'inss').text
    irrf = driver.find_element(By.ID, 'irrf').text
    liquido = driver.find_element(By.ID, 'liquido').text
    # convert to float or None
    def to_float(t):
        t = t.strip()
        if t == '-' or t == '':
            return None
        return float(t.replace(',','.'))
    return to_float(inss), to_float(irrf), to_float(liquido)

def screenshot(driver, name):
    path = os.path.join(SCREEN_DIR, name)
    driver.save_screenshot(path)
    return path

@pytest.fixture(scope='module')
def driver():
    # Use Chrome WebDriver (chromedriver) - ensure chromedriver is in PATH
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()

def test_ct_01_salario_faixa_baixa(driver):
    open_calc(driver)
    driver.find_element(By.ID, 'salario').send_keys('2000')
    driver.find_element(By.ID, 'calcular').click()
    time.sleep(0.2)
    inss, irrf, liquido = read_results(driver)
    screenshot(driver, 'CT-01.png')
    assert pytest.approx(inss, rel=1e-3) == 157.23
    assert irrf == 0.0
    assert pytest.approx(liquido, rel=1e-3) == 1842.77

def test_ct_02_salario_intermediario(driver):
    open_calc(driver)
    s = driver.find_element(By.ID, 'salario')
    s.clear()
    s.send_keys('4500')
    driver.find_element(By.ID, 'calcular').click()
    time.sleep(0.2)
    inss, irrf, liquido = read_results(driver)
    screenshot(driver, 'CT-02.png')
    assert pytest.approx(inss, rel=1e-3) == 439.59
    assert pytest.approx(irrf, rel=1e-3) == 238.10
    assert pytest.approx(liquido, rel=1e-3) == 3822.31

def test_ct_03_salario_proximo_teto(driver):
    open_calc(driver)
    s = driver.find_element(By.ID, 'salario')
    s.clear()
    s.send_keys('7500')
    driver.find_element(By.ID, 'calcular').click()
    time.sleep(0.2)
    inss, irrf, liquido = read_results(driver)
    screenshot(driver, 'CT-03.png')
    assert pytest.approx(inss, rel=1e-3) == 859.59
    assert pytest.approx(irrf, rel=1e-3) == 917.38
    assert pytest.approx(liquido, rel=1e-3) == 5723.03

def test_ct_04_input_invalido(driver):
    open_calc(driver)
    s = driver.find_element(By.ID, 'salario')
    s.clear()
    s.send_keys('texto invalido')
    driver.find_element(By.ID, 'calcular').click()
    time.sleep(0.2)
    # expects error message visible
    err = driver.find_element(By.ID, 'err')
    screenshot(driver, 'CT-04.png')
    assert err.is_displayed()
    assert 'Insira um valor numérico válido' in err.text
