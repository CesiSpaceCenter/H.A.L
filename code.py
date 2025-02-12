import time
import board
import busio
import digitalio
from baro import Barometer

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

baro = Barometer()

# Gestion du numéro de vol
try:
    with open('flight_number.txt', 'r') as f:
        flight_number = int(f.read()) + 1
except OSError:
    
    flight_number = 0

with open('flight_number.txt', 'w') as f:
    f.write(str(flight_number))

# Fichier de stockage des données
filename = f'flight_{flight_number}.txt'

# Calibration du baromètre
led.value = True
baro_cal = baro.calibrate()


# Variables pour la gestion du mode de vol
mode = "decol"  # Modes possibles : "decol", "vol", "atterrissage"
altitude_precedente = None
temps_debut_atterrissage = None
buffer = b''
n_packets = 0
intervalle_mesure = 0.05
intervalle_enregistrement = 5  


while True:
    led.value = True
    data = []
    timestamp_unix = time.time()
    timestamp_monotonic = time.monotonic()
    data.append(timestamp_unix)
    data.append(timestamp_monotonic)

    try:
        altitude = mesures["altitude"]
        pressure = mesures["pressure"]

        if altitude_precedente is not None:
            vitesse = (altitude - altitude_precedente) / intervalle_mesure
        else:
            vitesse = 0

        altitude_precedente = altitude

        data.append(pressure)
        data.append(altitude)
        data.append(vitesse)


        if mode == "decol" and (abs(vitesse) > 5):
            mode = "vol"
            intervalle_enregistrement = 0.01
            
        elif mode == "vol" and altitude < 5 and abs(vitesse) < 1:
            if temps_debut_atterrissage is None:
                temps_debut_atterrissage = time.time()
            elif time.time() - temps_debut_atterrissage > 90:  
                mode = "atterrissage"
                intervalle_enregistrement = 5  
        else:
            temps_debut_atterrissage = None  

    except Exception as e:
        data.extend([None, None, None])

  
    packet = (",".join([str(val) for val in data])).encode() + b'\n'
    buffer += packet


    if n_packets == 10:
        try:
            with open(filename, 'ab') as file:
                file.write(buffer)
                file.flush
            buffer = b''
       except Exception as e:

        n_packets = 0

    n_packets += 1
    led.value = False
    time.sleep(intervalle_mesure)  
