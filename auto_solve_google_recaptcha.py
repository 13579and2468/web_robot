from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import speech_recognition as sr
from pydub import AudioSegment
import os
import requests

     
def google_recaptcha_solve(driver):

    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,'iframe[title="reCAPTCHA"]')))
    driver.find_element_by_css_selector("#recaptcha-anchor > div.recaptcha-checkbox-border").click()
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='recaptcha challenge']")))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#recaptcha-audio-button"))).click()
    i = 1
    while True:
        ## the play button will change id
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"button#\:{i*2}")))
        driver.switch_to.default_content()
        cookie = driver.get_cookies() #get cookie
        session = requests.Session()
        headers = {
        'authority': 'www.google.com',
        'Connection': 'close',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer' : driver.execute_script('''return document.querySelector("iframe[title='recaptcha challenge']").src'''),
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-TW,zh-CN;q=0.9,zh;q=0.8,ja-JP;q=0.7,ja;q=0.6,en-US;q=0.5,en;q=0.4'}

        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='recaptcha challenge']")))
        sound_recaptcha_rcurl = driver.execute_script("return document.getElementById('audio-source').src")
        for c in cookie:  # I dont know why didn't need cookie
            session.cookies.set(c['name'], c['value'])
        response = session.get(sound_recaptcha_rcurl,headers=headers)

        dir = 'temp_audio.mp3'
        with open(dir, 'wb') as file:
            file.write(response.content)
            file.flush()

        src = "temp_audio.mp3"
        dst = "temp_audio.wav"
        sound = AudioSegment.from_mp3(src)
        sound.export(dst,format='wav')

        r = sr.Recognizer()                        #預設辨識英文
        with sr.WavFile("temp_audio.wav") as source:    #讀取wav檔
            audio = r.record(source)
            try:
                recaptcha_ans = r.recognize_sphinx(audio)
                print("Transcription: " + recaptcha_ans)
                driver.find_element_by_id('audio-response').send_keys(recaptcha_ans)
                driver.find_element_by_id('recaptcha-verify-button').click()

            except LookupError:
                print("Could not understand audio")

        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,'iframe[title="reCAPTCHA"]')))
        try:
            driver.find_element_by_css_selector("#recaptcha-anchor > div.recaptcha-checkbox-checkmark").click()
            driver.switch_to.default_content()
            return 
        except:
            driver.switch_to.default_content()
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='recaptcha challenge']")))
            i+=1



