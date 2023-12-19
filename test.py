from pyais import decode
def read_ais_file():
    """Generator function to read AIS data file line by line."""
    with open('db/ais data.txt', 'r') as file:
        for line in file:
            yield line.strip()



for line in read_ais_file():
    try:
        decoded_msg = decode(str.encode(line)).asdict()
    except:
        continue

    msg_type = decoded_msg.get('msg_type')
    if msg_type == 4:
        user_id = decoded_msg.get('mmsi')
        lat = decoded_msg.get('lat')
        lon = decoded_msg.get('lon')
        print(user_id, lat, lon)
        print(decoded_msg)
